import discord
from discord.ext import commands
import asyncio
import os
import json
import random
import logging
import traceback
import MAFIA.story as story
import MAFIA.prep as prep
import MAFIA.gvar as gvar

class mafia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    maxPlayers = 15
    mafiaList = [] #Names 
    DDList = [] #Names
    liveList = [] #names
    nominateList = []

    
    serverStatus = {}
    mafiaPlayers = {}
    playingServer = None
    victim = None
    healVictim = None
    pastHeal = None

    gamemodes = ["classic", "crazy"]
    @commands.command(pass_context = True)
    async def custom(self, ctx, var, number):
        server = ctx.guild
        channel = ctx.channel
        if server == None:
            await ctx.author.send(embed = self.makeEmbed("This ain't a discord server."))
        
        else:
            with open('servers.json', 'r') as f:
                sList = json.load(f)
            self.checkServer(server)
            if not var in sList[str(server.id)].keys():
                await channel.send(embed = self.makeEmbed("That's not something I can change."))
            else:
                if int(number) > 120:
                    await channel.send(embed = self.makeEmbed("Sorry. The max time is 120 seconds."))
                elif int(number) < 15:
                    await channel.send(embed = self.makeEmbed("Sorry. The min time is 15 seconds."))
                else:
                    try:
                        original = sList[str(server.id)][var]
                        sList[str(server.id)][var] = int(number)
                        await channel.send(embed = self.makeEmbed("Got it. {} is now {} seconds".format(var, number)))
                        ##await self.bot.send(discord.Object(550923896858214446),"{} set to {} on {}".format(var, number, server.name))
                        with open('servers.json', 'w') as f:
                            json.dump(sList, f) 
                    except:
                        await channel.send(embed = self.makeEmbed("Please enter a valid input."))
                        sList[str(server.id)][var] = original

    @commands.command(pass_context = True)
    async def setting(self, ctx):
        server = ctx.guild
        channel = ctx.channel
        if server == None:
            await ctx.author.send(embed = self.makeEmbed("This ain't a discord server."))
        
        else:
            self.checkServer(server)
            with open('servers.json', 'r') as f:
                sList = json.load(f)
            embed = discord.Embed(title = "Current settings on {}".format(server.name), description = "Customizable settings for Mafiabot!(m.custom (setting) (time))", colour = discord.Colour.blue())
            for setting in sList[str(server.id)]:
                embed.add_field(name = setting, value = "{}".format(sList[str(server.id)][setting]))
            embed.set_image(url = "https://pbs.twimg.com/media/DNgdaynV4AAEoQ7.jpg")
            await channel.send(embed = embed)
    @commands.command(pass_context = True)
    async def stop(self, ctx):
      server = ctx.guild
      channel = ctx.channel
      if server == None:
            await ctx.author.send(embed = self.makeEmbed("This ain't a discord server."))
      elif not server.id in self.serverStatus:
        await channel.send(embed = self.makeEmbed("You don't even have a game going on."))
      elif self.serverStatus[server.id]['commandStop'] == True:
        await channel.send(embed = self.makeEmbed("There's already a request to stop the game."))
      elif self.serverStatus[server.id]["gameOn"] == False:
        await channel.send(embed = self.makeEmbed("There's no game to stop lol."))
      elif not ctx.author in self.mafiaPlayers[server.id].keys():
          self.checkServer(server)
          await channel.send(embed = self.makeEmbed("Boi, you're not in the party."))
      else:
        self.serverStatus[server.id]['commandStop'] = True  
        await channel.send(embed = self.makeEmbed("Got it. The current game will stop after this round ends."))


    @commands.command(pass_context = True)

    async def reset(self, ctx):
        server = ctx.guild
        channel = ctx.channel
        self.checkServer(server)
        self.checkFile(ctx.author.id, server.id)
        if server == None:
            await ctx.author.send(embed = self.makeEmbed("This ain't a discord server."))
        elif not ctx.author in self.mafiaPlayers[server.id].keys():
            self.checkServer(server)
            await channel.send(embed =self.makeEmbed("Boi, you're not in the party."))
        else:

            await channel.send(embed = self.makeEmbed("IMPORTANT: You are resetting the bot's current game status on this server. Everything will reset except players' progresses. If you have any current games playing right now it can really mess everything up. Do you wish to proceed?(y/n)"))
            answer = await self.bot.wait_for('message',check =lambda message: message.author == ctx.author )
            if answer.content.lower() == "y" or answer.content.lower() == "yes":
                #deletes mafia text channel
                mafiaChannel = None
                mafiaChannel = self.serverStatus[server.id]["mafiaChannel"]
                try:
                    await mafiaChannel.delete()
                except:
                    print ("duh")
                #reset variables      
                self.serverStatus[server.id]['commandStop'] = False
                self.serverStatus[server.id]["ready"] = False
                self.serverStatus[server.id]["gameOn"] = False
            
                await channel.send(embed = self.makeEmbed("Reset complete. All conditions are cleared."))
                print ("Reset on {}".format(server.name))
                supportChannel = self.bot.get_channel(534564704937574400)
                await supportChannel.send("Reset on {}".format(server.name))

            else:
                await channel.send(embed = self.makeEmbed("Ok. No reset."))

    @commands.command(pass_context = True)
    async def clear(self, ctx):
      server = ctx.guild
      channel = ctx.channel
      if server is None:
        await ctx.author.send(embed = self.makeEmbed("This ain't a discord server."))
      elif not server.id in self.mafiaPlayers.keys():
        await channel.send(embed = self.makeEmbed("There's no party to clear lol."))
      else:
          if not (ctx.author in self.mafiaPlayers[server.id].keys()):
              await channel.send("Boi you're not in the party.")
          elif self.serverStatus[server.id]["gameOn"] == True or self.serverStatus[server.id]["ready"] == True:
              await channel.send(embed = self.makeEmbed("Can't clear party right now. There is a game going on!"))
          else:
              supportChannel = self.bot.get_channel(550923896858214446)
              await supportChannel.send("Party cleared on {}".format(server.name))
          self.mafiaPlayers[server.id] = {}
          await channel.send(embed = self.makeEmbed("The current party is now cleared."))

    @commands.command(pass_context = True)
    async def gamemode(self, ctx, mode):
        server = ctx.guild
        channel = ctx.channel
        if server is None:
            await ctx.author.send(embed = self.makeEmbed("This ain't a discord server."))
        elif not mode.lower() in self.gamemodes:
            await channel.send(embed = self.makeEmbed("Invalid game mode."))
        elif mode.lower() in self.gamemodes:
            with open('servers.json', 'r') as f:
                sList = json.load(f)
            self.checkServer(server)
            sList[str(server.id)]["game mode"] = mode.lower()
            with open('servers.json', 'w') as f:
                json.dump(sList, f) 
            await channel.send(embed = self.makeEmbed("Game mode set to {}".format(mode.lower())))
    @commands.command(pass_context = True)
    async def join(self, ctx):
        server = ctx.guild
        channel = ctx.channel
        if server is None:
            await ctx.author.send(embed = self.makeEmbed("This ain't a discord server."))
            
        else:
            self.checkServer(server)
            self.checkFile(ctx.message.author.id, server.id)
            if self.serverStatus[server.id]["gameOn"] == True:
                await channel.send(embed = self.makeEmbed("You cannot currently join right now because there is a game going on."))
            elif self.serverStatus[server.id]["ready"] == True:
                await channel.send(embed = self.makeEmbed("The is a game currently being set up!"))
            
            elif len(self.mafiaPlayers[server.id]) == self.maxPlayers:
                await channel.send(embed = self.makeEmbed("Sorry. The max number of players is {}.".format(self.maxPlayers)))
            else:
                if not ctx.message.author in self.mafiaPlayers[server.id].keys():
                    print("{} joined group on {}--{}".format(ctx.message.author.name, server, len(server.members)))
                    embed = discord.Embed(title = "{} joined on {}".format(ctx.message.author.name, server.name), description = "Server size: {}".format(len(server.members)), colour = discord.Colour.dark_blue())
                    embed.set_thumbnail(url = server.icon_url)
                    supportChannel = self.bot.get_channel(550923896858214446)
                    await supportChannel.send(embed = embed)
                    self.mafiaPlayers[server.id][ctx.message.author] = "" # add author to dictionary

                   
                    embed = discord.Embed(title = "{} has joined the party.".format(ctx.message.author.name), description = "IMPORTANT: Make sure everything is set up correctly. To view all required permissions use m.perms.", colour = discord.Colour.purple())
                    embed.set_thumbnail(url= "http://www.lol-wallpapers.com/wp-content/uploads/2018/08/Mafia-Braum-Miss-Fortune-by-wandakun-HD-Wallpaper-Background-Fan-Art-Artwork-League-of-Legends-lol.jpg")
                    playerStr = ""
                    for player in self.mafiaPlayers[server.id].keys():
                        playerStr = playerStr+player.name+"\n"
                    embed.add_field(name = "Players:", value = "{}".format(playerStr), inline = True)
                    embed.add_field(name = "Current gamemode: ", value = "{}".format(self.getMode(server.id)))
                    embed.set_footer(text = "When you're ready type m.setup to start! (Helpful commands: m.help, m.clear m.stop, m.gamemode)")
                    await channel.send(embed = embed)
                else:
                    await channel.send(embed = self.makeEmbed("You are already in the party."))

    @commands.command(pass_context = True)
    async def leave(self, ctx):
        server = ctx.guild
        channel = ctx.channel
        if server is None:
            await ctx.author.send(embed = self.makeEmbed("This ain't a discord server."))
        else:
            self.checkServer(server)
            if self.serverStatus[server.id]["gameOn"] == True or self.serverStatus[server.id]["ready"] == True:
                await channel.send(embed = self.makeEmbed("You cannot currently leave right now because there is a game going on."))
            else:
                
                if not ctx.message.author in self.mafiaPlayers[server.id].keys():
                    await channel.send(embed = self.makeEmbed("You are not in the party."))
                else:
                    embed = discord.Embed(title = "{} left on {}".format(ctx.message.author.name, server.name), description = "{}".format(len(server.members)), colour = discord.Colour.dark_magenta())
                    embed.set_thumbnail(url = server.icon_url)
                    supportChannel = self.bot.get_channel(550923896858214446)
                    await supportChannel.send(embed = embed)
                    print("{} left group on {}".format(ctx.message.author.name, server.name))
                    self.mafiaPlayers[server.id].pop(ctx.message.author, None)
                    await channel.send(embed = self.makeEmbed("{} left the party.".format(ctx.message.author.name)))


    @commands.command(pass_context = True)
    async def party(self, ctx):
        server = ctx.guild
        channel = ctx.channel
        if server is None:
            await ctx.author.send(embed = self.makeEmbed("This ain't a discord server."))
        
        else:
            self.checkServer(server)
            self.checkFile(ctx.message.author.id, server.id)
            if len(self.mafiaPlayers[server.id].keys()) == 0:
                await channel.send(embed = self.makeEmbed("There's no party lmao."))
            else:

                embed = discord.Embed(title = "Mafia Party:".format(), description = "IMPORTANT: Make sure everything is set up correctly. To view all required permissions use m.perms.", colour = discord.Colour.purple())
                embed.set_thumbnail(url= "http://www.lol-wallpapers.com/wp-content/uploads/2018/08/Mafia-Braum-Miss-Fortune-by-wandakun-HD-Wallpaper-Background-Fan-Art-Artwork-League-of-Legends-lol.jpg")
                playerStr = ""
                for player in self.mafiaPlayers[server.id].keys():
                    playerStr = playerStr+player.name+"\n"
                embed.add_field(name = "Players:", value = "{}".format(playerStr), inline = True)
                embed.add_field(name = "Current gamemode: ", value = "{}".format(self.getMode(server.id)))
                embed.set_footer(text = "When you're ready type m.setup to start! (Helpful commands: m.help, m.clear m.stop, m.gamemode)")
                await channel.send(embed = embed)



    @commands.command(pass_context = True)
    async def setup(self, ctx):
        server = ctx.guild
        channel = ctx.channel
        if server is None:
            await ctx.author.send(embed = self.makeEmbed("This ain't a discord server."))
        else:
            channel = ctx.channel
            self.checkServer(server)
            
            if self.serverStatus[server.id]["ready"] == True:
                embed = discord.Embed(title = "You have already set up. Type m.start to begin.")
                await channel.send(embed = embed)
            
            elif self.serverStatus[server.id]["gameOn"] == True:
                await channel.send(embed = self.makeEmbed("There is already a game playing."))

            elif len(self.mafiaPlayers[server.id].keys()) < 5:
                embed = discord.Embed(title = "Sorry. You need at least 5 people to play the game. You only have {} players.".format(len(self.mafiaPlayers[server.id].keys())), colour = discord.Colour.red())
                await channel.send(embed = embed)
            elif len(self.mafiaPlayers[server.id].keys())> self.maxPlayers:
                await channel.send(embed = self.makeEmbed("Sorry. The max number of people is {}.".format(self.maxPlayers)))
            elif not ctx.author in self.mafiaPlayers[server.id].keys():
    
                await channel.send(embed =self.makeEmbed("Boi, you're not in the party."))
            else:
                try:
                    self.checkServer(server)
                    sList = self.openJson("servers.json")
                    currentMode = sList[str(server.id)]["game mode"]
                    await channel.send(embed = discord.Embed(title = "Please wait. Setting game with mode: {}".format(currentMode), colour = discord.Colour.dark_gold()))
                    print ("--Setting game on '{}'".format(server.name))
                    

                    prepObj = prep.prepare(self.bot, self.mafiaPlayers[server.id], currentMode)
                    prepObj.assignRoles()
                    # Finished settings roles

                    # Inform player of roles
                    for player, data in self.mafiaPlayers[server.id].items():
                        if(data.roleName == 'mafia'):
                            embed = discord.Embed(title = "You are the Mafia. Your job is to kill everyone. Pretty simple.", colour = discord.Colour.red())

                            embed.set_image(url = "https://g-plug.pstatic.net/20180227_146/1519712112754O5VoQ_JPEG/JackR_skin_02.jpg?type=wa1536_864")
                            await player.send( embed = embed)
                        elif (data.roleName == 'framer'):
                            embed = discord.Embed(title = "You're the framer. Your job is to frame innocent people to look like mafias to the detective. ", colour = discord.Colour.red())
                            embed.set_image(url = "https://i.ytimg.com/vi/Cgj4Mkl6lHs/maxresdefault.jpg")
                            await player.send( embed = embed)
                        elif (data.roleName == 'mayor'):
                            embed = discord.Embed(title = "You're the mayor. You get two votes if you reveal your role. ", colour = discord.Colour.red())
                            embed.set_image(url = "https://shawglobalnews.files.wordpress.com/2017/06/adam-west-family-guy.jpg?quality=70&strip=all&w=372")
                            await player.send( embed = embed)
                        elif(data.roleName == 'doctor'):
                            embed = discord.Embed(title = "You are the Doctor. Your job is to save people. But you can't save the same person twice in a row.", colour = discord.Colour.blue())
                            embed.set_image(url = "https://i.chzbgr.com/full/9099359744/h095998C9/")
                            await player.send( embed = embed)
                        elif(data.roleName == 'detective'):
                            embed = discord.Embed(title = "You are the Detective. Your job is to find the Mafia.", colour = discord.Colour.orange())
                            embed.set_image(url = "https://media.altpress.com/uploads/2019/02/Screen-Shot-2019-02-26-at-1.20.38-PM.png")
                            await player.send( embed = embed)
                        elif(data.roleName == 'vigilante'):
                            embed = discord.Embed(title = "You are the Vigilante. For five years, You were stranded on an island with only one goal: survive... blah blah blah. Just don't shoot the wrong person or you'll commit suicide.", colour = discord.Colour.green())
                            embed.set_image(url = "https://i2.wp.com/s3-us-west-1.amazonaws.com/dcn-wp/wp-content/uploads/2017/12/31015237/Arrow-CW.png?resize=740%2C431&ssl=1")
                            await player.send( embed = embed)
                        elif (data.roleName == 'jester'):
                            embed = discord.Embed(title = "You are the Jester. Your win condition is to get the town to lynch you.", colour = discord.Colour.teal())
                            embed.set_image(url = "https://runes.lol/image/generated/championtiles/Shaco.jpg")
                            await player.send( embed = embed)
                        else:
                            embed = discord.Embed(title = "You are just a normal innocent villager who might get accused for crimes you didn't commit ¯\_(ツ)_/¯ ", colour = discord.Colour.dark_gold())
                            embed.set_image(url = "https://www.lifewire.com/thmb/0V5cpFjHpDgs5-c3TLP_V29SNL4=/854x480/filters:fill(auto,1)/uFiT1UL-56a61d203df78cf7728b6ae2.png")
                            await player.send( embed = embed)

                    overwrites = {
                        server.default_role: discord.PermissionOverwrite(send_messages=False),
                        server.me: discord.PermissionOverwrite(send_messages=True)
                    }
                    self.serverStatus[server.id]["mafiaChannel"] = await ctx.guild.create_text_channel("mafia", overwrites = overwrites)

                    for player in self.mafiaPlayers[server.id].keys():
                        try:
                            await player.edit(mute = False)
                        except discord.HTTPException:
                            print("duh")
                    self.serverStatus[server.id]["ready"] = True
                    
                except discord.Forbidden:
                    print("Forbidden error. Resetting...")
                    self.serverStatus[server.id]["ready"] = False
                    embed = discord.Embed(title = "Error. Missing required permissions. Please check all of my required permissions with m.perms and try again.", colour = discord.Colour.red())

                    await channel.send(embed = embed)
                else:
                    embed = discord.Embed(title = "Everything's ready! Everyone join a voice chat and type m.start to start the game!", description = "Make sure you understand how the game works! (Info can be found with m.game)", colour = discord.Colour.green())
                    embed.set_thumbnail(url = "https://pbs.twimg.com/media/DWVbyz5WsAA93-y.png")
                    await channel.send(embed = embed)


    async def dmNight(self, player, dmTime, targets, title, description, colour, img):
        print(player)
        dmEmbed = discord.Embed(title = title, description = description, colour = colour)
        dmEmbed.set_footer(text = "You have {} seconds to answer".format(str(dmTime)))
        dmEmbed.set_image(url = img)
        dmEmbed.add_field(name = "0", value = "Choose no one tonight.", inline = False)

        for item in targets:
            dmEmbed.add_field(name = str(targets.index(item)+1), value = item, inline = False)
        await player.send(embed = dmEmbed)

        answer = await self.bot.wait_for('message', check=lambda message: message.author == player, timeout = dmTime)
        while True:
            try:
                answerIndex = int(answer.content)
                if (answerIndex <= len(targets) and answerIndex >= 0):
                    await player.send("Got it.")
                    if (answerIndex == 0):
                        return None
                    
                    return targets[answerIndex-1]
                else:
                    await player.send("Unknown index. Try again.")
                    
            except ValueError:
                await player.send("That's not a valid number.")
            answer = await self.bot.wait_for('message', check=lambda message: message.author == player, timeout = dmTime)
                
    async def mafiaturn(self, players, temp, dmTime, mafiaNames, mafias):
        
        isSame = False
        voteTurn = 0
        while isSame == False:
            if voteTurn != 0:
                for player in mafias:
                    await player.send( embed = self.makeEmbed("The vote for the victim is not unanimous. Please coordinate among yourselves through dm and decide on a victim."))
            mafiaKillVote = []
            for player in mafias:
                
                tempM = []

                for thing in temp:
                    if not thing in mafiaNames:
                        tempM.append(thing)
                
                other = self.makeEmbed("Candidates chosen by other mafias:")
                if mafiaKillVote:
                    for item in mafiaKillVote:
                        other.add_field(name = "{}".format(item), value = "Hi!", inline = True)
                    await player.send( embed = other)

                try:
                    answer = await self.dmNight(player, dmTime, tempM, "Here are you targets mafia.", "Enter the number associated with your target.", discord.Colour.red(), "https://www.mobafire.com/images/champion/skins/landscape/graves-mafia.jpg")
                    mafiaKillVote.append(answer)
                except asyncio.TimeoutError:
                    print('duh')


            if mafiaKillVote:
                kill = mafiaKillVote[0]
                isSame = True
                for item in mafiaKillVote:
                    if item != None and item != kill:
                        isSame = False
                        break
            else:
                kill = None
                break
            voteTurn += 1
        if kill != None:
            embed = self.makeEmbed("Your target is {}".format(kill))
            for player in mafias:
                await player.send( embed = embed)
        return kill
    
    async def doctorTurn(self, doctor, temp, dmTime, lastHeal):
        doctList = []
        for person in temp:
            if  person != lastHeal and person != doctor.name.lower():
                doctList.append(person)
        try:
            answer = await self.dmNight(doctor, dmTime, doctList, "Doctor, who would you want to save tonight? (You cannot save the same person twice in a row)", "Enter the number associated with your target.", discord.Colour.blue(), "https://vignette.wikia.nocookie.net/leagueoflegends/images/f/f7/Akali_NurseSkin_old.jpg/revision/latest?cb=20120609043410")
        except asyncio.TimeoutError:
            answer = None
            await doctor.send("You ran out of time. Feelsbad.")
        return answer
    async def framerTurn(self, players, framer, dmTime):
        framerList = []

        for player, data in players.items():
            if data.roleName != "framer" and data.roleName != "mafia" and data.alive == True:
                framerList.append(player.name.lower())
        try:
            answer = await self.dmNight(framer, dmTime, framerList, "Framer, who would you like to frame tonight?", "Enter the number associated with your target.", discord.Colour.red(), "https://cdn.drawception.com/images/panels/2017/12-17/zKXCDSXfeA-4.png")
        except asyncio.TimeoutError:
            answer = None
            await framer.send("You ran out of time. Feelsbad.")
        return answer
    async def detTurn(self, detective, temp, dmTime, mafiaList, framerVictim, framer):
        tempDT = []
        for item in temp:
            if item.lower() != detective.name.lower():
                tempDT.append(item)
        try:
            answer = await self.dmNight(detective, dmTime, tempDT, "Who do you suspect?", "Enter the number associated with your target.", discord.Colour.orange(), "https://na.leagueoflegends.com/sites/default/files/styles/scale_xlarge/public/upload/cops_1920.jpg?itok=-T6pbISx")
            if answer == None:
                await detective.send("Ok wise guy.")
            else:
                if (answer.lower() in mafiaList or (framerVictim != None and answer.lower() == framerVictim.lower() ) or (framer != None and answer.lower()== framer.name.lower())):
                    embedDet = self.makeEmbed("Yes. That person is on the mafia's side. Now try to convince the others. Please return to the mafia chat now.")
                    embedDet.set_thumbnail(url = "http://www.clker.com/cliparts/P/S/9/I/l/S/234-ed-s-sd-md.png")
                else:
                    embedDet = self.makeEmbed("Sorry. That person is not the mafia. Please return to the mafia chat now.")
                    embedDet.set_thumbnail(url = "https://iconsplace.com/wp-content/uploads/_icons/ff0000/256/png/thumbs-down-icon-14-256.png")
                await detective.send(embed = embedDet)
        except asyncio.TimeoutError:
            await detective.send("You ran out of time.")

    async def vigTurn(self, vig, temp, dmTime):
        #await channel.send(embed = self.makeEmbed("Vigilante please check your dm."))
        tempV = []
        for player in temp:
            if player.lower() != vig.name.lower():
                tempV.append(player.lower())
                
        try:
            answer = await self.dmNight(vig, dmTime, tempV, "Vigilante, who do you want to shoot? (If you shoot an innocent boi you will commit suicide)", "Enter the number associated with your target.", discord.Colour.green(), "https://pmcdeadline2.files.wordpress.com/2018/03/arrow.png?w=446&h=299&crop=1")
        except asyncio.TimeoutError:
            answer = None
        return answer
                        
    async def mayorTurn(self, mayor, dmTime):
        
        revealed = False
        
        embed = discord.Embed(title = "Hi mayor. Would you like to reveal yourself next morning to have two votes? (y/n)", colour = discord.Colour.dark_gold())
        embed.set_image(url = "https://vignette.wikia.nocookie.net/familyguy/images/c/cf/Adam_We.JPG/revision/latest?cb=20060929205011")
        await mayor.send( embed = embed)
        def mcheck(m):
            return m.author == mayor
        answer = await self.bot.wait_for('message', check = mcheck, timeout = dmTime)
        while True:
            if answer == None:
                await mayor.send( embed = self.makeEmbed("Time's up. No reveal today."))
                break
            elif answer.content.lower() == "y" or answer.content.lower() == "yes":
                await mayor.send(embed = self.makeEmbed("Alright. You will be revealed and gain two votes each voting phase."))
                revealed = True
                break
            elif answer.content.lower() == "n" or answer.content.lower() == "no":
                await mayor.send(embed = self.makeEmbed("Alright, not revealing yourself yet."))
                break
            else:
                await mayor.send( embed = self.makeEmbed("Error. Idk what you typed but it's not the right input."))
                answer = await self.bot.wait_for('message', check = mcheck, timeout = dmTime)
        
        return revealed
    #returns player object
    def getPlayer(self, players, person):
        for player, data in players.items():
            if (player.name.lower() == person):
                return player
        return None
    #returns player role name
    def getRole(self, players, person):
        for player, data in players.items():
            if (player.name.lower() == person):
                return data.roleName
        return None
    def findPlayerWithRole(self, players, role):
        for player, data in players.items():
            if (data.roleName == role):
                return player
        return None
    async def killPlayer(self, party, person):
        target = self.getPlayer(party, person)
        party[target].alive = False
        await target.send("Hey, you're dead! Feel free to spectate the rest of the game but PLEASE do not talk nor give away important information to those still playing. Thank you!")
        try:
            await target.edit(mute = True)
        except discord.HTTPException:
            print("duh")

    async def muteAll(self, party):
        for player in party.keys():
            try:
                await player.edit(mute = True)
            except discord.HTTPException:
                print("duh")
    async def unMuteAll(self, party):
        for player in party.keys():
            try:
                await player.edit(mute = False)
            except discord.HTTPException:
                print("duh")
    async def muteDead(self, party):
        for player, data in party.items():
            if data.alive == False:
                try:
                    await player.edit(mute = True)
                except discord.HTTPException:
                    print("duh")  
            
            elif data.alive == True:
                try:
                    await player.edit(mute = False)
                 
                except discord.HTTPException:
                    print("duh") 
    
    async def vote(self, party, channel, voteTime, mayor, mRevealed):
        groupSize = len(party.keys())
        minVote = 2*groupSize/3
        if minVote < 2:
            minVote = 2
        alivePeople = []
        
       #objects
        targets = {}
        #messages
        alreadyVoted = []
        for player, data in party.items():
            if data.alive == True:
                targets[player] = {}
                alivePeople.append(player)
        for item in targets:
            targetE = discord.Embed(colour = discord.Colour.purple())
            targetE.add_field(name = item.name, value = "React to this message to vote for me!")
            targetE.set_thumbnail(url = item.avatar_url)
            voteMsg = await channel.send(embed = targetE)
            await voteMsg.add_reaction('\U0001F44D')
            targets[item]["message"] = voteMsg
            targets[item]["count"] = 0
        
        await asyncio.sleep(voteTime)

        bigVote = 0
        currentTarget = None

        for person in targets.keys():
            
            msg = targets[person]["message"]
            cache_msg = await channel.fetch_message(msg.id)
            for reaction in cache_msg.reactions:
                async for user in reaction.users():

                    if not user.name.lower() in alreadyVoted and user in alivePeople:
                        if mRevealed and mayor != None and mayor.name.lower() == user.name.lower():
                            targets[person]["count"]+=2
                        else:
                            targets[person]["count"] += 1
                        alreadyVoted.append(user.name.lower())
            
            if targets[person]["count"] > bigVote:
                bigVote = targets[person]["count"]
                currentTarget = person
            elif targets[person]["count"] == bigVote:
                currentTarget = None
        totalVotes = discord.Embed(title = "Final tally.", colour = discord.Colour.orange())
        for item in targets.keys():
            totalVotes.add_field(name = item.name, value = targets[item]["count"])
        await channel.send(embed = totalVotes)
        if bigVote < minVote:
            currentTarget = None
        if currentTarget != None:
            await channel.send("The town decided to lynch {}".format(currentTarget.name))
        return currentTarget

        
        


            
            
    @commands.command(pass_context = True)
    async def start(self, ctx):
        server = ctx.guild
        if server is None:
            await ctx.author.send(embed = self.makeEmbed("This ain't a discord server."))
        else:
            supportChannel = self.bot.get_channel(534564704937574400)
            self.checkServer(server)
            currentP = self.mafiaPlayers[server.id]
            channel = ctx.channel
            if self.serverStatus[server.id]["ready"] == False:
                await channel.send(embed = self.makeEmbed("You didn't set up yet. Type m.setup first."))
            
            elif self.serverStatus[server.id]["gameOn"] == True:
                channel = ctx.channel
                await channel.send(embed = self.makeEmbed("There is already a game going on!"))
            elif not ctx.message.author in self.mafiaPlayers[server.id].keys():
                channel = ctx.channel
                self.checkServer(server)
                await channel.send(embed = self.makeEmbed("Boi, you're not in the party."))
            else:
                
                print("A game has started on {}".format(server.name))
                try:
                    embed = discord.Embed(title = "A game has started on {}.".format(server.name), description = "Group size: {}".format(len(currentP.keys())), colour = discord.Colour.dark_green())
                    embed.add_field(name = "Server id: ", value = "{}".format(server.id), inline = False)
                    embed.add_field(name = "Mode: ", value = self.getMode(server.id))
                    embed.set_thumbnail(url = server.icon_url)
                    await supportChannel.send(embed = embed)
                    await channel.send(embed = self.makeEmbed("Everyone please navigate to the mafia text channel!"))
                    channel = self.serverStatus[server.id]["mafiaChannel"]
                    pastHeal = None
                    self.serverStatus[server.id]["gameOn"] = True
                    for player in currentP.keys():
                        await channel.send(player.mention)

                    #intro
                    intro = discord.Embed(title = "Welcome to Mafia!", description = "If you haven't read the rules yet, please type m.game to view them in your dm!", colour = discord.Colour.dark_purple())
                    intro.add_field(name = "Important!", value = "Please do not type in this chat unless instructed to do so. Admins please don't abuse your godly powers and talk when other people can't. Thank you.")
                    intro.add_field(name = "To those who are dead: ", value = "Please do not talk. I know it's hard to grasp but dead people can't talk.")
                    intro.add_field(name = "Some useful commands: ", value = "m.stop, m.reset, m.help.")
                    intro.set_footer(text = "Note: Parts of the game can be customized with m.custom *setting* *time*! To view current settings use m.settings.")
                    intro.set_image(url = "https://pre00.deviantart.net/5183/th/pre/i/2018/011/f/5/league_of_legends___mafia_miss_fortune_by_snatti89-dbznniv.jpg")
                    await channel.send(embed = intro)
                    await asyncio.sleep(6)

                    #messages mafias
                    await channel.send(embed = self.makeEmbed("Alright! Let the game begin!"))
                    await asyncio.sleep(1)
                    mafiaList = []
                    mafiaCount = 0
                    
                    for player, data in currentP.items():
                        if(data.roleName == 'mafia' or data.roleName == 'framer'):
                            mafiaList.append(player)
                            mafiaCount += 1
                    if mafiaCount > 1:
                        embed = discord.Embed(title = "Here are the mafias in this game:", colour = discord.Colour.dark_gold())
                        for item in mafiaList:
                            embed.add_field(name = "{}".format(item.name), value = "Role: {}".format(self.getRole(currentP, item.name.lower())), inline = False)
                        embed.set_footer(text = "Cooporate with your fellow mafias through dm to make strategies!")
                        for item in mafiaList:
                            await item.send(embed = embed)
                        await asyncio.sleep(4)
                    origFramer = self.findPlayerWithRole(currentP, "framer")
                    revealed = False
                    mayorShown = False
                    #big boi loop for game
                    while True:
                        if self.serverStatus[server.id]['commandStop'] == True:
                            await channel.send(embed = self.makeEmbed("Due to a request, I will end this game now."))
                            print("Requested stop on {}".format(server.name))
                            await supportChannel.send(embed = discord.Embed(title = "A game has stopped on {}".format(server.name), description = "{}".format(server.id), colour = discord.Colour.dark_magenta()))
                            await asyncio.sleep(5)
                            await channel.delete()
                            break

                        serverSettings = self.openJson("servers.json")
                        dmTime = serverSettings[str(server.id)]["dmTime"]
                        voteTime = serverSettings[str(server.id)]["voteTime"]
                        talkTime = serverSettings[str(server.id)]["talkTime"]
                        vigilanteUser = None
                        vigilanteAlive = False
                        doctorAlive = False
                        detAlive = False
                        deadGuy = None
                        vgTarget = None
                        temp = [] # names
                        tempDead = [] # names
                        healVictim = None
                        victim = None
                        for player, data in currentP.items():
                            if (data.alive == True):
                                temp.append(player.name.lower())
                            else:
                                tempDead.append(player.name.lower())
                        aliveEmbed = self.makeEmbed("Currently Alive:")
                        aliveEmbed.set_thumbnail(url = "http://www.quickmeme.com/img/b2/b25979dd4d550657f628d7f77a9f7f67527bbc86dff6ab22508e2e58040e2282.jpg")
                        deadEmbed = self.makeEmbed("Currently Dead:")
                        deadEmbed.set_thumbnail(url = "https://scubasanmateo.com/images/coffin-clipart-rip-2.png")
                        for player in temp:
                            aliveEmbed.add_field(name = "{}".format(player), value = "Alive", inline = False)
                            
                        for player in tempDead:
                            deadEmbed.add_field(name = "{}".format(player), value = "Dead", inline = False)
                        await channel.send(embed = aliveEmbed)
                        await channel.send(embed = deadEmbed)
                        everyone_perms = discord.PermissionOverwrite(send_messages=False)
                        my_perms = discord.PermissionOverwrite(send_messages=True)
                        await self.muteAll(currentP)
                        
                        await asyncio.sleep(2)
                        embed = discord.Embed(title = "It is now night time, time to go to sleep...", description = "Don't panick, I muted all of you", colour = discord.Colour.blue())
                        embed.set_image(url = "https://www.nih.gov/sites/default/files/news-events/research-matters/2019/20190312-sleep.jpg")
                        await channel.send(embed = embed)
                        
                        await asyncio.sleep(3)
                        await channel.send(embed = self.makeEmbed("Mafia(s) please check your dm."))


                        #Mafia turn
                        framer = self.findPlayerWithRole(currentP, "framer")
                        mafiaNum = 0
                        framerCount = 0
                        for player, data in currentP.items():
                            if (data.roleName == "mafia" and data.alive == True):
                                mafiaNum+=1
                            elif data.roleName == "framer" and data.alive == True:
                                framerCount +=1

                        if mafiaNum == 0 and framerCount >0:
                            await self.findPlayerWithRole(currentP, "framer").send("Since there are no more mafias, you are now a mafia.")
                            currentP[self.findPlayerWithRole(currentP, "framer")].roleName = "mafia"
                            framer = None
                                    
                        
                        mafiaNames = []
                        mafias = []
                        mafiaTargets = []
                        for player, data in currentP.items():
                            if ((data.roleName == "mafia")and data.alive == True):
                                mafiaNames.append(player.name.lower())
                                mafias.append(player)
                            else:
                                if (data.roleName != "framer" and data.alive == True):
                                    mafiaTargets.append(player.name.lower())
                        victim = await self.mafiaturn(currentP, mafiaTargets, dmTime, mafiaNames, mafias)
                        framerVictim = None
                        if framer != None:
                            framerVictim = await self.framerTurn(currentP, framer, dmTime)
                        

                        
                        
                        #Doctor turn
                        
                        for player, data in currentP.items():
                            if(data.roleName == 'doctor') and data.alive == True:
                                doctorUser = player
                                doctorAlive = True

                        # Only if doc is alive
                        if doctorAlive == True:
                            await channel.send("Doctor please check your DM.")
                            healVictim = await self.doctorTurn(doctorUser, temp, dmTime, pastHeal)
                            pastHeal = healVictim
                            
                        #check if victim is saved
                        if victim == None:
                            saved = None
                        elif healVictim == None:
                            saved = False
                        elif victim == healVictim:
                            saved = True
                        else:
                            saved = False
                        #vigilante turn
                        
                        for player, data in currentP.items():
                            if(data.roleName == "vigilante") and data.alive == True:
                                vigilanteUser = player
                                vigilanteAlive = True
                                if victim != None:
                                    if vigilanteUser.name.lower() == victim and saved == False:
                                        vigilanteAlive = False
                                        embed = discord.Embed(title = "Sorry. The mafia killed you :(", colour = discord.Colour.dark_red())
                                        await vigilanteUser.send(embed = embed)
                        if vigilanteAlive == True:
                            vgTarget = await self.vigTurn(vigilanteUser, temp, dmTime)
                            
                        
                        #mayor turn
                        mayor = self.findPlayerWithRole(currentP, "mayor")
                        
                        if mayor != None and revealed == False:
                            revealed = await self.mayorTurn(mayor, dmTime)
                        #Detective turn
                        
                        for player, data in currentP.items():
                            if(data.roleName == 'detective') and data.alive == True:
                                detUser = player
                                detAlive = True
                        
                        # only if det is alive
                        if detAlive == True:
                            await channel.send(embed = self.makeEmbed("Detective please check your DM"))
                            await self.detTurn(detUser, temp, dmTime, mafiaList, framerVictim, framer)


                        

                        #Storytime
                        await channel.send(embed = self.makeEmbed("Alright everybody get your ass back here. It's storytime."))
                        await self.muteDead(currentP)

                        await asyncio.sleep(3)
                        if saved == None:
                            await channel.send(embed = self.makeEmbed("The mafia was too lazy to kill anyone this night."))
                        else:
                            story1 = discord.Embed(title = "Story", description = "All of these stories are written by linkboi and the submissions from Mafiabot Support Server.", colour = discord.Colour.purple())
                            await channel.send(embed = story1)
                            if saved == True:
                                aStory = story.storyTime("alive", victim)
                                storyEmbed = discord.Embed(title = "{} lives!".format(victim), description = "{}".format(aStory), colour = discord.Colour.green())
                                storyEmbed.set_thumbnail(url = "https://vignette.wikia.nocookie.net/dragonfable/images/f/f1/Heal_Icon.png/revision/latest?cb=20130329031111")
                            else:
                                aStory = story.storyTime("dead", victim)
                                storyEmbed = discord.Embed(title = "{} died :(".format(victim), description = "{}".format(aStory), colour = discord.Colour.red())
                                storyEmbed.set_image(url = "https://i.ytimg.com/vi/j_nV2jcTFvA/hqdefault.jpg")
                                for player, data in currentP.items():
                                    if player.name.lower() == victim:

                                        storyEmbed.add_field(name = "{}'s role is:".format(player.name), value = "{}".format(data.roleName))
                                await self.killPlayer(currentP, victim)

                                temp.remove(victim)
                            
                            
                            await channel.send(embed = storyEmbed)


                        await asyncio.sleep(5)

                        if revealed and mayorShown ==False:
                            mayorEmbed = discord.Embed(title = "The mayor has shown himself/herself to be {}!".format(self.findPlayerWithRole(currentP, "mayor")), description = "Now the mayor's vote counts twice!", colour = discord.Colour.green())
                            mayorEmbed.set_image(url = "https://upload.wikimedia.org/wikipedia/en/a/a3/Adam_West_on_Family_Guy.png")
                            await channel.send(embed = mayorEmbed)
                            mayorShown = True
                        #vg's news
                        if vigilanteAlive == True:

                            if vgTarget == None:
                                print("duh")
                            

                            #if vg shot a mafia
                            elif vgTarget in mafiaNames or (framer != None and vgTarget == framer.name.lower()):
                                embed = discord.Embed(title = "Wait, what's this?", description = "The vigilante shot a mafia!!", colour = discord.Colour.green())
                                embed.add_field(name = "The mafia shot was...", value = "{}!".format(vgTarget))
                                embed.set_image(url = "https://vignette.wikia.nocookie.net/michaelbaybatman/images/e/ea/Bac-gotham-rooftop.jpg/revision/latest?cb=20140223174240")
                                vgTargetObj = self.getPlayer(currentP, vgTarget)
                                embed.set_footer(text = "{} was a {}".format(vgTarget, currentP[vgTargetObj].roleName))
                                await self.killPlayer(currentP, vgTarget)
                                temp.remove(vgTarget)
                                await channel.send(embed = embed)
                            #if vg shot an innocent boi
                            elif not vgTarget in mafiaNames:
                                embed = discord.Embed(title = "Wait, what's this?", description = "The vigilante shot the innocent {}! The vigilante has commited suicide out of guilt!".format(vgTarget), colour = discord.Colour.red())
                                
                                embed.set_image(url = "https://res.cloudinary.com/teepublic/image/private/s--N6Q7m5Pj--/t_Preview/b_rgb:191919,c_limit,f_jpg,h_630,q_90,w_630/v1493744453/production/designs/1556060_1.jpg")
                                vgTargetObj = self.getPlayer(currentP, vgTarget)
                                embed.set_footer(text =  "{} was the vigilante and {}'s role was {}!".format(vigilanteUser.name, vgTarget, currentP[vgTargetObj].roleName))
                                await self.killPlayer(currentP, vgTarget)
                                await self.killPlayer(currentP, vigilanteUser.name.lower())
                                await channel.send(embed = embed)
                                
                            #if vg shot the mafia's victim            
                            elif vgTarget == victim.lower():
                                embed = discord.Embed(title = "Wait, what's this?", description = "The vigilante also shot the mafia's victim! The vigilante has commited suicide out of shame!", colour = discord.Colour.orange())
                                embed.set_image(url = "https://i.ytimg.com/vi/lhckuhUxcgA/hqdefault.jpg")
                                vgTargetObj = self.getPlayer(currentP, vgTarget)
                                embed.set_footer(text = "{} was the vigilante and {} was a {}!".format(vigilanteUser.name,  vgTarget, currentP[vgTargetObj].roleName))
                                
                                await self.killPlayer(currentP, vigilanteUser.name.lower())
                                if saved == True:
                                    await self.killPlayer(currentP, vgTarget)
                                await channel.send(embed = embed)                

                            

                            
                            
                        check = self.checkWin(mafiaCount, server.id, currentP)

                        await asyncio.sleep(5)
                        if check == "mafia":
                                await self.unMuteAll(currentP)
                                embed = discord.Embed(title = "The mafia(s) win!", colour = discord.Colour.red())
                                embed.set_image(url = "https://i0.wp.com/static.lolwallpapers.net/2015/11/Braum-Safe-Breaker-Fan-Art-Skin-By-Karamlik.png")
                                self.updateWin(currentP, server.id, check)
                                break
                        elif check == "villager":
                            await self.unMuteAll(currentP)
                            embed = discord.Embed(title = "The villagers win!", colour = discord.Colour.green())
                            embed.set_image(url = "https://www.landofthebrave.info/images/pilgrims--native-indians-massachusetts.jpg")
                            self.updateWin(currentP, server.id, check)
                            break

                        elif check == "none": # lynch
                            tempC = []
                            for player, data in currentP.items():
                                if data.alive == True:
                                    tempC.append(player.name.lower())
                            embed = discord.Embed(title = "Now I'll give you guys {} seconds to talk. ".format(talkTime), colour = discord.Colour.magenta())
                            embed.set_image(url = "https://blog.oup.com/wp-content/uploads/2016/11/Witchcraft_at_Salem_Village2.jpg")
                            await channel.send(embed = embed)
                            #Gives permission to type in chat
                            overwrite = discord.PermissionOverwrite()
                           
                            for player, data in currentP.items():
                                if data.alive == True:
                                    await channel.set_permissions(player, send_messages=True)
                     
                                else:
                                    await channel.set_permissions(player, send_messages=False)
                            await asyncio.sleep(talkTime)
                            
                            embed = discord.Embed(title = "Alright! It's time to vote! Vote for a person by reacting to the message associated with your target. (A person must have a min of {} votes to be lynched)".format(int(2*len(currentP.keys())/3)), description = "Note: If you try to be sneaky and vote more than once your vote will only count once to the first message the bot reads.", colour = discord.Colour.green())
                            
                            embed.set_footer(text = "You have {} seconds to vote.".format(voteTime))


                            await channel.send(embed = embed)
                            lynchPerson = await self.vote(currentP, channel, voteTime, mayor, revealed)

                            asyncio.sleep(2)
                            if lynchPerson != None:
                                embed = discord.Embed(title = "{} has been hanged by the village. Press f to pay respect.".format(lynchPerson.name), colour = discord.Colour.red())
                                embed.set_image(url = "https://cdn.shopify.com/s/files/1/0895/0864/products/42-47714084_1024x1024.jpeg?v=1451772538")
                                await channel.send(embed = embed)
                                await asyncio.sleep(3)
                                for player, data in currentP.items():
                                    if (player.name.lower() == lynchPerson.name.lower()):
                                        data.alive = False
                                        try:
                                            await player.edit(mute = True)
                                        except discord.HTTPException:
                                            print("duh")
                                        await player.send("Hey, you're dead! Feel free to spectate the rest of the game but PLEASE do not talk nor give away important information to those still playing. Thank you!")
                                        await channel.send(embed = self.makeEmbed("{}'s role was {}".format(player.name, data.roleName)))
                                        break
                            else:
                                await channel.send(embed = self.makeEmbed("No one was hanged."))
                            asyncio.sleep(1)
                        
                                

                              
                                
                            for player, data in currentP.items():
                                await channel.set_permissions(player, send_messages=False)
                            check = self.checkWin(mafiaCount, server.id, currentP)
                            
                            jesterWins = False
                            if lynchPerson != None:
                                for player, data in currentP.items():
                                    if player.name.lower() == lynchPerson.name.lower() and data.roleName == "jester":
                                        jesterWins = True

                            #check conditions 
                            #check returns string mafia or villager
                            if jesterWins == True:
                                await self.unMuteAll(currentP)
                                embed = discord.Embed(title = "Uh oh! The Jester wins!", colour = discord.Colour.purple())
                                embed.set_thumbnail(url = "https://runes.lol/image/generated/championtiles/Shaco.jpg")
                                embed.set_footer(text = "hehehehe....")
                                self.updateWin(currentP, server.id, "jester")
                                break
                            elif check == "mafia":
                                await self.unMuteAll(currentP)
                                embed = discord.Embed(title = "The mafia(s) win!", colour = discord.Colour.red())
                                embed.set_image(url = "https://i0.wp.com/static.lolwallpapers.net/2015/11/Braum-Safe-Breaker-Fan-Art-Skin-By-Karamlik.png")
                                self.updateWin(currentP, server.id, check)
                                break
                            elif check == "villager":
                                await self.unMuteAll(currentP)
                                embed = discord.Embed(title = "The villagers win!", colour = discord.Colour.green())
                                embed.set_image(url = "https://www.landofthebrave.info/images/pilgrims--native-indians-massachusetts.jpg")
                                self.updateWin(currentP, server.id, check)
                                break
                    #unmutes all players
                    await self.unMuteAll(currentP)

                        #Only if the game did not end with commandStop
                    if self.serverStatus[server.id]['commandStop'] == False:
                        self.displayAllR(embed, currentP, origFramer)
                        await ctx.channel.send(embed = embed)
                        await channel.send(embed = embed)
                        await channel.send(embed = self.makeEmbed("Thank you all for playing! Deleting this channel in 10 seconds"))
                        await asyncio.sleep(10)
                        await channel.delete()
                    self.serverStatus[server.id]["ready"] = False
                    self.serverStatus[server.id]["gameOn"] = False
                    self.serverStatus[server.id]['commandStop'] = False  
                    self.serverStatus[server.id]["mafiaChannel"] = None
                    embed = discord.Embed(title = "A game has finished on {}.".format(server.name), description = "Group size: {}".format(len(currentP.keys())), colour = discord.Colour.dark_purple())
                    embed.add_field(name = "Server id: ", value = "{}".format(server.id))
                    embed.set_thumbnail(url = server.icon_url)
                    await supportChannel.send(embed = embed)

                        
                except Exception as e:
                    if isinstance(e, discord.Forbidden):
                        await ctx.channel.send("Error. Missing permission to mute members!(Or some other permissions idk)")
                    elif isinstance(e, discord.NotFound):
                        await ctx.channel.send( "Boi, who deleted my mafia text channel...")
                    else:
                        await ctx.channel.send("Error. Something weird happened. (If this keeps happening report it to the Mafia Support Server)")
                    
                    embed = discord.Embed(title = "An error has occured on {}.".format(server.name), description = "Server id: {}".format(server.id), colour = discord.Colour.red())
                    embed.add_field(name = "Error:", value = "{}".format(traceback.format_exc()))
                    
                    await supportChannel.send( embed = embed)
                    self.serverStatus[server.id]["ready"] = False
                    self.serverStatus[server.id]["gameOn"] = False
                    self.serverStatus[server.id]["commandStop"] = False
                    mafiaChannel = None
                    for item in server.channels:
                        if item.name == 'mafia':
                            mafiaChannel = item
                    try:
                        await mafiaChannel.delete() 
                    except:
                        print("duh")
                    embed = discord.Embed(title = "Resetting...", colour = discord.Colour.red())
                    await channel.send(embed = embed)
               
    
        
    def checkServer(self, server):
        with open('servers.json', 'r') as f:
                sList = json.load(f)
        if not server.id in self.mafiaPlayers.keys():
            self.mafiaPlayers[server.id] = {}
        if not server.id in self.serverStatus.keys():
            self.serverStatus[server.id] = {}
            self.serverStatus[server.id]["ready"] = False
            self.serverStatus[server.id]["gameOn"] = False
            self.serverStatus[server.id]['commandStop'] = False  
            self.serverStatus[server.id]["mafiaChannel"] = None
        if not str(server.id) in sList.keys():
            
            sList[str(server.id)] = {}
            sList[str(server.id)]["game mode"] = "classic"
            sList[str(server.id)]['dmTime'] = 30
            sList[str(server.id)]['voteTime'] = 20
            sList[str(server.id)]['talkTime'] = 60
            with open('servers.json', 'w') as f:
                json.dump(sList, f) 
    def findChannel(self, server):
        for item in server.channels:
            if item.name == 'mafia':
                return item
    
    #returns number of people alive in the side of mafia or village
    def checkGame(self, current, isMafia):
        num = 0
        if isMafia == True:
            for player, data in current.items():
                if (data.roleName == "mafia" and data.alive == True) or (data.roleName == "framer" and data.alive == True):
                    num += 1
        else:
            for player, data in current.items():
                if data.roleName != "mafia" and data.alive == True and data.roleName != "framer":
                    num+=1
        return num
    #returns who wins
    def checkWin(self, mafiaCount, id, currentList):
        mLive = self.checkGame(currentList, True)
        print(mLive)
        vLive = self.checkGame(currentList, False)
        if mLive > vLive or (vLive ==1 and mLive >= 1):
            return "mafia"
        elif mLive == 0:
            return "villager"
        else:
            return "none"
    def randInt(self, chance, whole):
        result = random.randint(chance, whole)
        if result <= chance:
            return True
        else:
            return False

    def displayAllR(self, embed, mafiaList, framer):
        embed.set_image(url = "https://wallpapers.wallhaven.cc/wallpapers/full/wallhaven-323086.png")
        for player, data in mafiaList.items():
            if framer != None and player.name.lower() == framer.name.lower():
                embed.add_field(name = "{}".format(player.name), value = "framer", inline = True)
            else:
                embed.add_field(name = "{}".format(player.name), value = "{}".format(data.roleName), inline = True)
    def setRoles(self, ctx, group, role):
        role = random.choice(group)
        group.remove(role)

    def makeEmbed(self, message):
      embed = discord.Embed(title = message, colour = discord.Colour.green())
      return embed
    def displayMember(self, server, group):
        embed = discord.Embed(title = "Targets", colour = discord.Colour.purple())
        for item in group.keys():
            name = server.get_member(item)
            embed.add_field(name = "{}".format(name), value = "Kill me!", inline = False)
        return embed

    def checkSide(self, role):
        if role == "mafia" or "framer": #checks what side the role belongs to
            return "mafia"
        elif role == "jester":
            return "jester"
        else:
            return "villager"

    def checkFile(self, playerID, serverID):
        with open('players.json', 'r') as f:
            players = json.load(f)
        playerStr = str(playerID)
        serverStr = str(serverID)
        if not serverStr in players:
            players[serverStr] = {}
        if not playerStr in players[serverStr].keys():
            players[serverStr][playerStr] = {}
            players[serverStr][playerStr]["Wins"] = 0
            players[serverStr][playerStr]["Games"] = 0
        with open('players.json', 'w') as f:
            json.dump(players, f)
    
    def updateWin(self, mafiaList, serverID, winner):
        with open('players.json', 'r') as f:
            players = json.load(f)
        #finds players with the winning role (winner is a string) and adds one point to their record

        for player, data in mafiaList.items():
            self.checkFile(player.id, serverID)
            side = self.checkSide(data.roleName)
            if side == winner:
                players[str(serverID)][str(player.id)]["Wins"] += 1
            players[str(serverID)][str(player.id)]["Games"] += 1

        with open('players.json', 'w') as f:
            json.dump(players, f)                
    def getMode(self, serverID):
        servers = self.openJson("servers.json")
        return servers[str(serverID)]["game mode"]
    def openJson(self, file):
        with open(file, 'r') as f:
            fReturn = json.load(f)
        return fReturn

    def dumpJson(self, file, content):
        with open(file, 'w') as f:
            json.dump(content, f)
    
def setup(bot):
    bot.add_cog(mafia(bot))