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
import MAFIA.turns as turn
import user as userObj
import MAFIA.gameRole as roles
class mafia(commands.Cog):


    def __init__(self, bot):
        self.bot = bot
        self.userList = []
        for filename in os.listdir("C:/Users/Ernest/Desktop/Mafiabot/MafiaBot-1/users"):
            self.userList.append(self.makeUser(filename))


    def makeUser(self, dir):
        tempList = []
        with open("C:/Users/Ernest/Desktop/Mafiabot/MafiaBot-1/users/" + dir) as f:
            count = 0
            for line in f:
                
                if count != 4 or count != 5:
                    tempList.append(line[:-1])

                
                else:
                    tempList.append(line)
                count+=1
            
            tempList[4] = list(tempList[4].split())


            
        return userObj.MafiaUser(int(tempList[0]), int(tempList[1]), int(tempList[2]), int(tempList[3]), tempList[4], tempList[5])
    
    
    maxPlayers = 15    
    patch = "2.0"
    serverStatus = {}
    mafiaPlayers = {}
    gamemodes = ["classic", "crazy", "chaos"]


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
            if var == "gamemode" or var == "mode":
                if number in self.gamemodes:
                    sList[str(server.id)]["game mode"] = number
                    await ctx.send("Got it. Game mode has been set to " + number)
                    self.dumpJson("servers.json", sList)
                else:
                    await channel.send(embed = self.makeEmbed("Lol idk what mode that is. Type m.gamemodes to see!"))
                return
            if not var in sList[str(server.id)].keys() and not var.lower() == "gamemode":
                await channel.send(embed = self.makeEmbed("That's not something I can change."))
                return
            if var == "category":
                if self.bot.get_channel(int(number)):
                    category = self.bot.get_channel(int(number))
                    sList[str(server.id)]["category"] = int(number)
                    await channel.send(embed = self.makeEmbed("Got it. I will now create text channels at " + str(category) + " from now on."))
                    self.dumpJson("servers.json", sList)
                    return
                else:
                    await channel.send(embed = self.makeEmbed("Lol, that's not a category ID."))
                    return

            if int(number) > 120:
                await channel.send(embed = self.makeEmbed("Sorry. The max time is 120 seconds."))
                return
            if int(number) < 15:
                await channel.send(embed = self.makeEmbed("Sorry. The min time is 15 seconds."))
                return
            try:
                original = sList[str(server.id)][var]
                sList[str(server.id)][var] = int(number)
                await channel.send(embed = self.makeEmbed("Got it. {} is now {} seconds".format(var, number)))
                #await self.bot.send(discord.Object(550923896858214446),"{} set to {} on {}".format(var, number, server.name))
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
            embed = discord.Embed(title = "Current settings on {}".format(server.name), description = "Customizable settings for Mafiabot!(m.custom (setting) (#))", colour = discord.Colour.blue())
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
      elif self.serverStatus[server.id]['commandStop']:
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
        self.checkFile(ctx.author.id)
        if server == None:
            await ctx.author.send(embed = self.makeEmbed("This ain't a discord server."))
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
                self.serverStatus[server.id]["setting"] = False
                self.serverStatus[server.id]["mafiaChannel"] = None
                
            
                await channel.send(embed = self.makeEmbed("Reset complete. All conditions are cleared."))
                print ("Reset on {}".format(server.name))
                supportChannel = self.bot.get_channel(604716684955353098)
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
          elif self.serverStatus[server.id]["gameOn"] or self.serverStatus[server.id]["ready"]:
              await channel.send(embed = self.makeEmbed("Can't clear party right now. There is a game going on!"))
          else:
              supportChannel = self.bot.get_channel(550923896858214446)
              await supportChannel.send("Party cleared on {}".format(server.name))
              self.mafiaPlayers[server.id] = {}
              await channel.send(embed = self.makeEmbed("The current party is now cleared."))


    @commands.command(name = "gamemode", aliases = ["gamemodes", "mode", "modes"])
    async def gamemode(self, ctx):
        server = ctx.guild
        if server is None:
            await ctx.author.send(embed = self.makeEmbed("This ain't a discord server."))
            return
        
        embed = discord.Embed(title = "Avaliable Game Modes!", description = "To set a gamemode, type m.custom gamemode `mode`", colour = discord.Colour.blue())
        embed.add_field(name = "Classic:grinning::champagne_glass:", value = "The classic mafia you play with friends! Recommended for small parties.")
        embed.add_field(name = "Crazy:grimacing::dagger:", value = "Fun roles to spice up your boring classic games! Recommended for medium size parties.")
        embed.add_field(name = "Chaos:smiling_imp::fire:", value = "Absolute chaos where every role is in play. Recommended for big parties.")
        with open('servers.json', 'r') as f:
            sList = json.load(f)
        self.checkServer(server)
        currentMode = sList[str(server.id)]["game mode"]
        embed.set_footer(text = "Current game mode: " + currentMode.upper())
        embed.set_image(url = "http://www.lol-wallpapers.com/wp-content/uploads/2018/06/Gangster-Twitch-Splash-Art-Update-HD-4k-Wallpaper-Background-Official-Art-Artwork-League-of-Legends-lol.jpg")
        await ctx.send(embed = embed)


    @commands.command(pass_context = True)
    async def join(self, ctx):
        server = ctx.guild
        channel = ctx.channel
        if server is None:
            await ctx.author.send(embed = self.makeEmbed("This ain't a discord server."))
            
        else:
            self.checkServer(server)
            self.checkFile(ctx.message.author.id)
            if self.serverStatus[server.id]["gameOn"]:
                embed = self.makeEmbed("Sorry, there's a game currently going on! Wait for the game to finish to join.")
                embed.set_image(url = "https://i.imgflip.com/2tdam9.png")
                await channel.send(embed = embed)
            elif self.serverStatus[server.id]["ready"] or self.serverStatus[server.id]["setting"]:
                embed = self.makeEmbed("There is a game currently being set up! If someone started before you can join and everyone agrees, type m.reset to restart so you can join.")
                embed.set_image(url = 'https://i.imgflip.com/2tdam9.png')
                await channel.send(embed = embed)
            
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

                   
                    embed = discord.Embed(title = "{} has joined the party.".format(ctx.message.author.name), description = "IMPORTANT: Make sure everything is set up correctly. To view all required permissions use m.perms. (Current patch: {})".format(self.patch), colour = discord.Colour.purple())
                    await self.showParty(embed, server, channel)
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

            
            if self.serverStatus[server.id]["gameOn"] or self.serverStatus[server.id]["ready"]:
                await channel.send(embed = self.makeEmbed("You cannot currently leave right now because there is a game going on."))
            elif self.serverStatus[server.id]["ready"] or self.serverStatus[server.id]["setting"]:
                await channel.send(embed = self.makeEmbed("You can't leave. There's a game being set up! If you really need to leave, use m.reset and leave."))
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

                
    @commands.command(name = "remove", aliases = ["kick"])
    async def remove(self, ctx, user: discord.Member):
        server = ctx.guild
        if server is None:
            await ctx.author.send(embed = self.makeEmbed("This ain't a discord server."))
            return
        self.checkServer(server)
        channel = ctx.channel
        memberList = list(self.mafiaPlayers[server.id].keys())
        if memberList[0] != ctx.author:
            await channel.send("Boi, you ain't the party leader. Your party leader is {}.".format(memberList[0].name))
            return
        if self.serverStatus[server.id]["gameOn"]:
            await channel.send("There is a game currently playing! Wait for the game to end and then remove this boi.")
            return
        if self.serverStatus[server.id]["ready"]:
            await channel.send("There is a game set up already! Wait for the game to be over plz.")
            return

        

        
        if not user in memberList:
            await channel.send("Lol that's not someone who's in the party.")
            return
        
        self.mafiaPlayers[server.id].pop(user, None)
        await channel.send(embed = self.makeEmbed("{} has been :boot: off the party.".format(user)))
        

    async def showParty(self, embed, server, channel):
        embed.set_thumbnail(url= "http://www.lol-wallpapers.com/wp-content/uploads/2018/08/Mafia-Braum-Miss-Fortune-by-wandakun-HD-Wallpaper-Background-Fan-Art-Artwork-League-of-Legends-lol.jpg")
        playerStr = ""
        cog = self.bot.get_cog("Points")
        count = 1
        for player in self.mafiaPlayers[server.id].keys():
            if count == 1:
                playerStr += "Party leader: "
            count+=1
            if cog.getCTitle(player.id) != "" and cog.getCTitle(player.id) != " ":
                titleStr = ' - "The '+cog.getCTitle(player.id) + '"'
            else:
                titleStr = cog.getCTitle(player.id)
            print( cog.getCTitle(player.id))
            playerStr = playerStr+player.name+titleStr + "\n"
        mode_str = ""
        for mode in self.gamemodes:
            
            mode_str += mode
            if self.getMode(server.id) == mode:
                mode_str += ":white_check_mark:"
            mode_str += "\n"
        embed.add_field(name = "Players({})".format(str(len(self.mafiaPlayers[server.id].keys()))), value = "{}".format(playerStr), inline = True)
        embed.add_field(name = "Current gamemode: ", value = mode_str)
        embed.set_footer(text = "When you're ready type m.setup to start! (Helpful commands: m.help, m.game, m.clear m.stop, m.gamemode, m.support)")
        await channel.send(embed = embed)


    @commands.command(pass_context = True)
    async def party(self, ctx):
        server = ctx.guild
        channel = ctx.channel
        if server is None:
            await ctx.author.send(embed = self.makeEmbed("This ain't a discord server."))
        
        else:
            self.checkServer(server)
            self.checkFile(ctx.message.author.id)
            if len(self.mafiaPlayers[server.id].keys()) == 0:
                await channel.send(embed = self.makeEmbed("There's no party lmao."))
            else:

                embed = discord.Embed(title = "Mafia Party", description = "IMPORTANT: Make sure everything is set up correctly. To view all required permissions use m.perms. (Current patch: {})".format(self.patch), colour = discord.Colour.purple())
                await self.showParty(embed, server, channel)


    @commands.command(name = "setup", aliases = ["prep"])
    async def setup(self, ctx):
        server = ctx.guild
        channel = ctx.channel
        if server is None:
            await ctx.author.send(embed = self.makeEmbed("This ain't a discord server."))
        else:
            channel = ctx.channel
            self.checkServer(server)
            
            if self.serverStatus[server.id]["ready"]:
                embed = discord.Embed(title = "You have already set up. Type m.start to begin.")
                await channel.send(embed = embed)
            
            elif self.serverStatus[server.id]["gameOn"]:
                await channel.send(embed = self.makeEmbed("There is already a game playing."))
            elif self.serverStatus[server.id]["setting"]:
                await channel.send(embed =self.makeEmbed("Calm down, there's already a game being set up..."))

            elif len(self.mafiaPlayers[server.id].keys()) < 5:
                embed = discord.Embed(title = "Sorry. You need at least 5 people to play the game. You only have {} players. Type m.join to join the party.".format(len(self.mafiaPlayers[server.id].keys())), colour = discord.Colour.red())
                await channel.send(embed = embed)
            elif len(self.mafiaPlayers[server.id].keys())> self.maxPlayers:
                await channel.send(embed = self.makeEmbed("Sorry. The max number of people is {}.".format(self.maxPlayers)))
            elif not ctx.author in self.mafiaPlayers[server.id].keys():
    
                await channel.send(embed =self.makeEmbed("Boi, you're not in the party."))
            else:
                memberList = list(self.mafiaPlayers[server.id].keys())
                if memberList.index(ctx.author) != 0:
                    await channel.send("Boi, you ain't the party leader. Your party leader is {}.".format(memberList[0]))
                else:
                    try:
                        self.checkServer(server)
                        sList = self.openJson("servers.json")
                        currentMode = sList[str(server.id)]["game mode"]
                        self.serverStatus[server.id]["setting"] = True
                        await channel.send(embed = discord.Embed(title = "Please wait. Setting game with mode: {}".format(currentMode), colour = discord.Colour.dark_gold()))
                        print ("--Setting game on '{}'".format(server.name))
                        

                        prepObj = prep.prepare(self.bot, self.mafiaPlayers[server.id], currentMode)
                        prepObj.assignRoles()
                        # Finished settings roles

                        # Inform player of roles
                        for player, data in self.mafiaPlayers[server.id].items():
                            if(data.roleName == 'mafia'):
                                embed = discord.Embed(title = "You are the Mafia. You carry out the Godfather's kill commands. (AKA you do the Godfather's dirty work)", description = "Side: mafia(duh)", colour = discord.Colour.red())
                                embed.set_image(url = "https://g-plug.pstatic.net/20180227_146/1519712112754O5VoQ_JPEG/JackR_skin_02.jpg?type=wa1536_864")
                                await player.send( embed = embed)
                            elif data.roleName == "godfather":
                                embed = discord.Embed(title = "You are the Godfather. You decide who to kill. If you have a mafia, they will do the dirty work for you. Otherwise you will have to do it yourself.", description = "Side: mafia", colour = discord.Colour.red())
                                embed.set_image(url = "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/8173394d-de95-430a-a448-f57211a61abf/d4s8rj1-3ba39658-06af-48e3-8a3d-c1fb95ea7156.png?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7InBhdGgiOiJcL2ZcLzgxNzMzOTRkLWRlOTUtNDMwYS1hNDQ4LWY1NzIxMWE2MWFiZlwvZDRzOHJqMS0zYmEzOTY1OC0wNmFmLTQ4ZTMtOGEzZC1jMWZiOTVlYTcxNTYucG5nIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmZpbGUuZG93bmxvYWQiXX0.YmYoOCuQk1uWaDXmf2CVWDHJA9GzNwQuMcW_-SkXaiI")
                                await player.send(embed = embed)
                            elif (data.roleName == 'framer'):
                                embed = discord.Embed(title = "You're the framer. Your job is to frame innocent people to look like mafias to the detective. ", description = "Side: Mafia", colour = discord.Colour.red())
                                embed.set_image(url = "https://i.ytimg.com/vi/Cgj4Mkl6lHs/maxresdefault.jpg")
                                await player.send( embed = embed)
                            elif (data.roleName == 'mayor'):
                                embed = discord.Embed(title = "You're the mayor. You get two votes if you reveal your role. ", description = "Side: Villager", colour = discord.Colour.red())
                                embed.set_image(url = "https://shawglobalnews.files.wordpress.com/2017/06/adam-west-family-guy.jpg?quality=70&strip=all&w=372")
                                await player.send( embed = embed)
                            elif(data.roleName == 'doctor'):
                                embed = discord.Embed(title = "You are the Doctor. Your job is to save people. But you can't save the same person twice in a row.", description = "Side: Villager", colour = discord.Colour.blue())
                                embed.set_image(url = "https://i.chzbgr.com/full/9099359744/h095998C9/")
                                await player.send( embed = embed)
                            elif(data.roleName == 'detective'):
                                embed = discord.Embed(title = "You are the Detective. Your job is to find the Mafia.", description = "Side: Villager", colour = discord.Colour.orange())
                                embed.set_image(url = "https://media.altpress.com/uploads/2019/02/Screen-Shot-2019-02-26-at-1.20.38-PM.png")
                                await player.send( embed = embed)
                            elif(data.roleName == 'baiter'):
                                embed = discord.Embed(title = "You are the Baiter. You like to kill people, but you're a lazy killer. That's why you sit at home and kill whoever visits you. Kill 3 people to win.", description = "Side: Neutral", colour = discord.Colour.blurple())
                                embed.set_image(url = "https://i.kym-cdn.com/entries/icons/original/000/028/431/kirby.jpg")
                                await player.send(embed= embed)
                            elif(data.roleName == 'vigilante'):
                                embed = discord.Embed(title = "You are the Vigilante. For five years, You were stranded on an island with only one goal: survive... blah blah blah. Just don't shoot the wrong person or you'll commit suicide.", description = "Side: Villager", colour = discord.Colour.green())
                                embed.set_image(url = "https://i2.wp.com/s3-us-west-1.amazonaws.com/dcn-wp/wp-content/uploads/2017/12/31015237/Arrow-CW.png?resize=740%2C431&ssl=1")
                                await player.send( embed = embed)
                            elif data.roleName == "bomber":
                                embed = discord.Embed(title = "You are the Bomber. You like big boom, so every night you can plant one bomb in someone's house. If you get lynched one of your planted bombs will go off at random.", description = "Side: Neutral", colour =discord.Colour.dark_magenta())
                                embed.add_field(name = "*Note", value = "Every night, you have a 20 percent chance of attaching a bomb to yourself because you love big boom so much. You will have to spend that night deactivating the big boom.")
                                embed.set_image(url = "https://dotesports-media.nyc3.cdn.digitaloceanspaces.com/wp-content/uploads/2018/08/12042519/c40f3969-1d65-43e8-bf02-614730d065a3.jpg")
                                await player.send( embed = embed)
                            elif (data.roleName == 'jester'):
                                embed = discord.Embed(title = "You are the Jester. Your win condition is to get the town to lynch you.", description = "Side: Neutral", colour = discord.Colour.teal())
                                embed.set_image(url = "https://runes.lol/image/generated/championtiles/Shaco.jpg")
                                await player.send( embed = embed)
                            elif (data.roleName == 'executioner'):
                                embed = discord.Embed(title = "You are the executioner. You will be given a target, and your job is to convince the town to lynch your target to win. If you target is killed by other ways you will turn into a Jester.", description = "Side: Neutral", colour = discord.Colour.teal())
                                embed.set_image(url = "https://www.mobafire.com/images/champion/skins/landscape/dr-mundo-executioner.jpg")
                                await player.send(embed = embed)
                            elif (data.roleName == 'distractor'):
                                embed = discord.Embed(title = "You are the Distractor. You can stop one person from using their role each night.", description = "Side: Villager", colour = discord.Color.orange())
                                embed.set_image(url = "https://media.wired.com/photos/59a459d3b345f64511c5e3d4/master/pass/MemeLoveTriangle_297886754.jpg")
                                await player.send(embed = embed)
                            elif (data.roleName == "PI"):
                                embed = discord.Embed(title = "You are the PI. You can choose two players each night to see if they are on the same side.", description = "Side: Villager", colour = discord.Colour.purple())
                                embed.set_image(url = "https://www.charlestonlaw.net/wp-content/uploads/2018/01/private-investigator.jpg")
                                await player.send(embed = embed)
                            elif (data.roleName == "spy"):
                                embed = discord.Embed(title = "You are the spy. You can select a target each night and see which person they visit that night.", description = "Side: Villager", colour = discord.Colour.blurple())
                                embed.set_image(url = "https://na.leagueoflegends.com/sites/default/files/styles/scale_xlarge/public/upload/secret_agent_xinzhao_final_1920.jpg?itok=ulTb2lPD")
                                await player.send(embed = embed)
                            elif data.roleName == "dictator":
                                embed = discord.Embed(title = "You are the Dictator. After choosing a side, your goal is to sway the game and help your selected side win. If successful you win and the chosen side doesn't.", description = "Side: Neutral", colour = discord.Colour.blurple())
                                embed.add_field(name = "Immunities", value = "You are invulnerable to mafia and vigilante attacks. However you can be lynched or killed by the Bomber.")
                                embed.set_image(url = "https://www.mobafire.com/images/champion/skins/landscape/swain-northern-front.jpg")
                                await player.send(embed= embed)
                            else:
                                embed = discord.Embed(title = "You are just a normal innocent villager who might get accused for crimes you didn't commit ¯\_(ツ)_/¯ ", colour = discord.Colour.dark_gold())
                                embed.set_image(url = "https://www.lifewire.com/thmb/0V5cpFjHpDgs5-c3TLP_V29SNL4=/854x480/filters:fill(auto,1)/uFiT1UL-56a61d203df78cf7728b6ae2.png")
                                await player.send( embed = embed)


                        overwrites = {
                            server.default_role: discord.PermissionOverwrite(send_messages=False),
                            server.default_role: discord.PermissionOverwrite(read_messages = False),
                            server.me: discord.PermissionOverwrite(send_messages=True),
                            server.me: discord.PermissionOverwrite(read_messages = True),
                        }
                        try:
                            categoryID = sList[str(server.id)]["category"]
                            category = self.bot.get_channel(int(categoryID))
                        except:
                            categoryID = None
                            sList[str(server.id)]["category"] = None
                            category = None
                            self.dumpJson("servers.json", sList)
                        
                        self.serverStatus[server.id]["mafiaChannel"] = await ctx.guild.create_text_channel("mafia", category = category, overwrites = overwrites)

                        for player in self.mafiaPlayers[server.id].keys():
                            try:
                                await player.edit(mute = False)
                            except discord.HTTPException:
                                pass
                        
                        
                    except discord.Forbidden as e:
                        self.serverStatus[server.id]["ready"] = False
                        self.serverStatus[server.id]["setting"] = False
                        embed = discord.Embed(title = e.text, colour = discord.Colour.red())

                        await channel.send(embed = embed)

                    else:
                        self.serverStatus[server.id]["ready"] = True
                        self.serverStatus[server.id]["setting"] = False
                        embed = discord.Embed(title = "Everything's ready! Everyone feel free to join a voice chat and type m.start to start the game!", description = "Make sure you understand how the game works! (Info can be found with m.game)", colour = discord.Colour.green())
                        embed.set_thumbnail(url = "https://pbs.twimg.com/media/DWVbyz5WsAA93-y.png")
                        await channel.send(embed = embed)


    def inGame(self, currentP, role):
        for player, data in currentP.items():
            if data.roleName == role and data.alive:
                return player
        return None
    

    def findRoleObj(self, roleList, name):
        for role in roleList:
            if role.user.name.lower() == name.lower():
                return role
        return None
            

    @commands.command(pass_context = True)
    async def start(self, ctx):
        server = ctx.guild
        if server is None:
            await ctx.author.send(embed = self.makeEmbed("This ain't a discord server."))
        else:
            supportChannel = self.bot.get_channel(604716684955353098)
            self.checkServer(server)
            currentP = self.mafiaPlayers[server.id]
            channel = ctx.channel
            if self.serverStatus[server.id]["ready"] == False:
                await channel.send(embed = self.makeEmbed("You didn't set up yet. Type m.setup first."))
            
            elif self.serverStatus[server.id]["gameOn"]:
                channel = ctx.channel
                await channel.send(embed = self.makeEmbed("There is already a game going on!"))
            elif self.serverStatus[server.id]["setting"]:
                await ctx.channel.send(embed= self.makeEmbed("You got a game setting up right now. Hold on."))
            elif not ctx.message.author in self.mafiaPlayers[server.id].keys():
                channel = ctx.channel
                self.checkServer(server)
                await channel.send(embed = self.makeEmbed("Boi, you're not in the party."))
            else:
                memberList = list(self.mafiaPlayers[server.id].keys())
                if memberList[0] != ctx.author:
                    await channel.send("Boi, you ain't the party leader. The party leader is {}".format(memberList[0].name))
                    return

                try:
                    mFunctions = turn.Turns(self.bot)

                    self.serverStatus[server.id]["gameOn"] = True
                    embed = discord.Embed(title = "A game has started on {}.".format(server.name), description = "Group size: {}".format(len(currentP.keys())), colour = discord.Colour.dark_green())
                    embed.add_field(name = "Server id: ", value = "{}".format(server.id), inline = False)
                    embed.add_field(name = "Mode: ", value = self.getMode(server.id))
                    embed.set_thumbnail(url = server.icon_url)
                    await supportChannel.send(embed = embed)
                    embed = self.makeEmbed("Everyone please navigate to the mafia text channel!")
                    embed.set_image(url = "https://cdn.aarp.net/content/dam/aarp/money/budgeting_savings/2016/06/1140-navigating-medicare-mistakes.imgcache.revdd9dcfe7710d97681da985118546c1a9.jpg")
                    await channel.send(embed = embed)
                    
                    channel = self.serverStatus[server.id]["mafiaChannel"]
                    overwrite = discord.PermissionOverwrite(send_messages = False, read_messages = True)

                    for player in currentP.keys():
                        await channel.set_permissions(player, overwrite=overwrite)
                   
                    allRoles = []
                    mafiaUser = roles.Mafia(self.inGame(currentP, "mafia"))
                    gfUser = roles.Godfather(self.inGame(currentP, "godfather"))
                    detUser = roles.Det(self.inGame(currentP, "detective"))
                    docUser = roles.Doctor(self.inGame(currentP, "doctor"))
                    vigUser = roles.Vig(self.inGame(currentP, "vigilante"))
                    mayorUser = roles.Mayor(self.inGame(currentP, "mayor"))
                    frameUser = roles.Framer(self.inGame(currentP, "framer"))
                    distractUser = roles.Distractor(self.inGame(currentP, "distractor"))
                    spyUser = roles.Spy(self.inGame(currentP, "spy"))
                    PIUser = roles.PI(self.inGame(currentP, "PI"))
                    exeUser = roles.Exe(self.inGame(currentP, "executioner"))
                    jesterUser = roles.Jester(self.inGame(currentP, "jester"))
                    baiterUser = roles.Baiter(self.inGame(currentP, "baiter"))
                    bombUser = roles.Bomber(self.inGame(currentP, "bomber"))
                    dictUser = roles.Dictator(self.inGame(currentP, "dictator"))
                    if mafiaUser.user:
                        gfUser.mafiaPlayers.append(mafiaUser)
                    

                    allRoles.append(mafiaUser)
                    allRoles.append(gfUser)
                    allRoles.append(detUser)
                    allRoles.append(docUser)
                    allRoles.append(vigUser)
                    allRoles.append(mayorUser)
                    allRoles.append(frameUser)
                    allRoles.append(distractUser)
                    allRoles.append(spyUser)
                    allRoles.append(PIUser)
                    allRoles.append(exeUser)
                    allRoles.append(jesterUser)
                    allRoles.append(baiterUser)
                    allRoles.append(bombUser)
                    allRoles.append(dictUser)


                    for player, data in currentP.items():
                        if data.roleName == "villager":
                            allRoles.append(roles.Villager(player))

                    currentRoles = []


                    for item in allRoles:
                        if item.user:
                            currentRoles.append(item)
                        else:
                            item.alive = False


                    for player in currentP.keys():

                        await channel.send(player.mention)


                    if dictUser.user:
                        embed = discord.Embed(title = "Hello Dictator. What side would you like to favor this game?", description = "React 🔫 for mafia and 🎩 for villager.")
                        embed.set_image(url = "http://lol-wallpapers.com/wp-content/uploads/2016/12/Northern-Front-Swain-Splash-Art-League-of-Legends-Artwork-Wallpaper-lol.jpg")
                        embed.set_footer(text = "You have about 15 seconds to answer, so make it quick...")
                        dictMsg = await dictUser.user.send(embed= embed)
                        await dictMsg.add_reaction("🔫")
                        await dictMsg.add_reaction("🎩")


                    #intro
                    intro = discord.Embed(title = "Welcome to Mafia!", description = "If you haven't read the rules yet, please type m.game to view them in your dm!", colour = discord.Colour.dark_purple())
                    intro.add_field(name = "Important!", value = "Please do not type in this chat unless instructed to do so. Admins please don't abuse your godly powers and talk when other people can't. Thank you.")
                    intro.add_field(name = "To those who are dead: ", value = "Please do not talk. I know it's hard to grasp but dead people can't talk. Also no reactions, because, you know, dead people also can't react.")
                    intro.add_field(name = "Some important rules: ", value = "Screen shots are not permitted and would only ruin the game. However you CAN claim roles to either coordinate among yourselves or trick other people. Just NO SCREENSHOTS.")
                    intro.add_field(name = "Some useful commands: ", value = "m.stop, m.reset, m.help.")
                    intro.set_footer(text = "Note: Parts of the game can be customized with m.custom *setting* *time*! To view current settings use m.settings.")
                    intro.set_image(url = "https://pre00.deviantart.net/5183/th/pre/i/2018/011/f/5/league_of_legends___mafia_miss_fortune_by_snatti89-dbznniv.jpg")
                    await channel.send(embed = intro)
                    

                    #messages mafias                    
                    mafiaList = []
                    mafiaCount = 0
                    
                    for player, data in currentP.items():
                        if(data.roleName == 'mafia' or data.roleName == 'framer' or data.roleName == "godfather"):
                            mafiaList.append(player)
                            mafiaCount += 1
                    if mafiaCount > 1:
                        embed = discord.Embed(title = "Here are the mafias in this game:", colour = discord.Colour.dark_gold())
                        for item in mafiaList:
                            embed.add_field(name = "{}".format(item.name), value = "Role: {}".format(mFunctions.getRole(currentP, item.name.lower())), inline = False)
                        embed.set_footer(text = "Cooporate with your fellow mafias through dm to make strategies!")
                        for item in mafiaList:
                            await item.send(embed = embed)
                        await asyncio.sleep(4)
                    exePlayer = mFunctions.findPlayerWithRole(currentP, "executioner")
                    exeTarget = None
                    if exePlayer != None:
                        exeTarget = None
                        exeNonoList = ["mafia", "framer", "godfather", "baiter", "dictator", "bomber"]
                        while True:
                            exeTarget = random.choice(list(currentP.keys()))
                            if not mFunctions.getRole(currentP, exeTarget.name.lower()) in exeNonoList and exeTarget.name.lower() != exePlayer.name.lower():
                                exeEmbed = discord.Embed(title = "Alright executioner. Your target is {}. Convince the town to lynch {} and you win. Ezpz.".format(exeTarget.name, exeTarget.name), description = "If your target is killed any other way you will become a Jester.", colour = discord.Colour.light_grey())
                                exeEmbed.set_thumbnail(url = exeTarget.avatar_url)
                                await exePlayer.send(embed = exeEmbed)
                                break 
                    origFramer = mFunctions.findPlayerWithRole(currentP, "framer")
                    revealed = False

                    await asyncio.sleep(10)

                    #dictator response
                    if dictUser.user:
                        cache_msg = await dictUser.user.fetch_message(dictMsg.id)
                        answerEmoji = None


                        for reaction in cache_msg.reactions:
                            async for user in reaction.users():
                                if user.id != 480553111971430420 and (reaction.emoji == '🎩' or reaction.emoji == '🔫'):
                                    answerEmoji = reaction.emoji
                                    break

                        #Saves input
                        if answerEmoji:
                            if answerEmoji == '🔫':
                                dictUser.selectSide = "mafia"
                            else:
                                dictUser.selectSide = "villager"
                            await dictUser.user.send("You have chosen the " + dictUser.selectSide + " side.")
                        else:
                            dictUser.selectSide = "mafia"
                            await dictUser.user.send("Welp, since you didn't choose in time, I have chosen mafia for you. Lol tough luck.")

                        #Finds random person in currentRoles with the same side as the dictator's choice
                        while True:
                            randomPerson = random.choice(currentRoles)
                            if randomPerson.side == dictUser.selectSide:
                                embed = discord.Embed(title = "Here's a little hint: ", description = randomPerson.user.name + " is on the " + dictUser.selectSide + " side.", colour = discord.Colour.gold())
                                embed.set_thumbnail(url = randomPerson.user.avatar_url)
                                await dictUser.user.send(embed = embed)
                                break
                        
                            


                    

                    await channel.send(embed = self.makeEmbed("Alright! Let the game begin!"))
                    await asyncio.sleep(1)
                    #big boi loop for game
                    night = 1
                    while True:
                        if self.serverStatus[server.id]['commandStop']:
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
                        
                        
                        temp = [] # names
                        tempDead = [] # names
                        
                        
                        victim = None
                        

                        for player, data in currentP.items():
                            if (data.alive):
                                temp.append(player.name.lower())
                            else:
                                tempDead.append(player.name.lower())


                        aliveStr = ""
                        for player in temp:
                            aliveStr += player + "\n"
                        
                        deadStr = ""
                        for player in tempDead:
                            deadStr += player + "\n"
                        if not deadStr:
                            deadStr = "No one died yet..."


                        dayEmbed = discord.Embed(title = "Night " + str(night), colour = discord.Colour.blue())
                        dayEmbed.add_field(name = "Currently Alive:", value = aliveStr)
                        dayEmbed.add_field(name = "Currently Dead: ", value = deadStr)
                        dayEmbed.set_image(url = "https://rachaelbarbash.files.wordpress.com/2016/09/wp-1473736998171.jpg")
                        await channel.send(embed = dayEmbed)

        
                        await mFunctions.muteAll(currentP)
                        
                        await asyncio.sleep(2)
                        embed = discord.Embed(title = "It is now night time, time to go to sleep...", description = "Don't panic, I muted all of you", colour = discord.Colour.blue())
                        embed.set_image(url = "https://www.nih.gov/sites/default/files/news-events/research-matters/2019/20190312-sleep.jpg")
                        await channel.send(embed = embed)
                        
                        await asyncio.sleep(3)

                        for item in allRoles:
                            item.victim = None
                        

                        for role in currentRoles:
                            if not role.alive:
                                if bombUser.user and role.user.name.lower() in bombUser.plantedTargets:
                                    bombUser.plantedTargets.remove(role.user.name.lower())
                                role.user = None
                                currentRoles.remove(role)
                                
                        

                        if mafiaUser.user and mafiaUser.alive and (gfUser and not gfUser.alive):
                            await mafiaUser.user.send("Since the Godfather is ded, you are now the Godfather. Kill whoever you like.")
                            gfUser.user = mafiaUser.user
                            gfUser.alive = True
                            mafiaUser.user = None
                            gfUser.mafiaPlayers = []
                            currentRoles.append(gfUser)
                            currentRoles.remove(mafiaUser)


                        if frameUser.user and (gfUser and not gfUser.alive):
                            await frameUser.user.send("Since the Godfather is ded, you have been promoted to Godfather!")
                            gfUser.user = frameUser.user
                            gfUser.alive = True
                            frameUser.user = None
                            currentRoles.append(gfUser)
                            currentRoles.remove(frameUser)    


                        noneDmRoles = ["executioner", "jester", "mafia", "baiter", "villager", "dictator"]
                        
                        dmAnnounce = discord.Embed(title = "Everyone with a useful role please check your dm!", description = "Jk all roles are useful...", colour = discord.Colour.blue())
                        dmAnnounce.set_image(url = "https://miro.medium.com/max/1080/1*We3cuit-POpN4Sa-GU-9lw.jpeg")
                        await channel.send(embed = dmAnnounce)


                        #Send prompts
                        for role in currentRoles:
                            if not role.name.lower() in noneDmRoles:
                                await role.sendPrompt(currentP, str(dmTime))
                        
                        await asyncio.sleep(dmTime)

                        #Store prompt answers
                        for role in currentRoles:
                            if not role.name.lower() in noneDmRoles:
                                await role.getTarget()
                        
                        
                        saved = False
                        PIRoles = []


                        baiterName = None
                        #checks baiter and distractor targets first and set the role's victim to None
                        for role in currentRoles:
                            #distractor
                            if role.user and distractUser.victim == role.user.name.lower() and role.victim:
                                if role.name.lower() != "pi":
                                    role.victim = None
                                else:
                                    role.PITargets = []
                                embed = discord.Embed(title = "Sorry, you got distracted tonight and couldn't use your role...", colour = discord.Colour.greyple())
                                embed.set_thumbnail(url = "http://blogs.studentlife.utoronto.ca/lifeatuoft/files/2018/01/krabs.jpg")
                                await role.user.send(embed = embed)
                            #finds baiter name
                            if role.user and role.name == "baiter" and role.alive:
                                baiterName = role.user.name.lower()
                                
                         
                        #Sets mafia target
                        if mafiaUser.victim:
                            victim = mafiaUser.victim
                        elif gfUser.victim:
                            victim = gfUser.victim
                        
                        if victim and victim == baiterName:
                            victim = None

                        if victim and dictUser.user and victim == dictUser.user.name.lower():
                            for role in currentRoles:
                                if role.side == "mafia":
                                    await role.user.send("Uh oh, you were unable to kill {} tonight...".format(victim))
                            victim = None

                        #Determines if doctor saved the mafia victim
                        if not victim:
                            saved = None
                        elif docUser.victim and victim == docUser.victim:
                            saved = True
                        else:
                            saved = False

                        
                        #Checks other roles with victims to carry out their abilities
                        baiterVictims = []
                        for role in currentRoles:
                            #Baiter
                            if role.victim and role.victim == baiterName and role.user.name.lower() != victim:
                                baiterVictims.append(role)
                                embed = discord.Embed(title = role.user.name + " visited you last night and died! One kill down...", colour = discord.Colour.red())
                                embed.set_image(url = "https://pre00.deviantart.net/aaf4/th/pre/f/2019/036/0/6/kirby_knife_blood_by_blankseima-dcyzbt3.png")
                                await baiterUser.user.send(embed = embed)
                            elif role.user:
                                #Detective
                                if detUser.victim and detUser.victim == role.user.name.lower():
                                    if role.name == "mafia" or role.name == "framer" or (frameUser and frameUser.victim and frameUser.victim == role.user.name.lower()):
                                        embedDet = self.makeEmbed("Yes. That person is on the mafia's side. Now try to convince the others. Please return to the mafia chat now.")
                                        embedDet.set_thumbnail(url = "http://www.clker.com/cliparts/P/S/9/I/l/S/234-ed-s-sd-md.png")
                                    else:
                                        embedDet = self.makeEmbed("Sorry. That person is not the mafia. Please return to the mafia chat now.")
                                        embedDet.set_thumbnail(url = "https://iconsplace.com/wp-content/uploads/_icons/ff0000/256/png/thumbs-down-icon-14-256.png")
                                    await detUser.user.send(embed = embedDet)
                                #Spy
                                elif spyUser.victim and spyUser.victim == role.user.name.lower():
                                    if role.name.lower() != "pi" and role.victim:
                                        embed = discord.Embed(title = "Your target {} visited {} tonight. Good luck figuring out the rest lmao.".format(spyUser.victim, role.victim), colour = discord.Colour.blue())
                                        embed.set_thumbnail(url = mFunctions.getPlayer(currentP, role.victim.lower()).avatar_url)
                                        await spyUser.user.send(embed = embed)
                                    else:
                                        await spyUser.user.send("Your target did not visit anyone tonight. Feelsbad.")
                                #Vigilante
                                elif victim and vigUser.victim and vigUser.victim == role.user.name.lower():
                                    #Checks if vig is able to kill 
                                    if (victim == vigUser.user.name.lower() and not saved) or (baiterUser.user and baiterUser.user.name.lower() == vigUser.victim):
                                        await vigUser.user.send("Sorry. You were killed tonight before you could shoot anyone.")
                                        vigUser.victim = None
                                    elif dictUser.user and vigUser.victim == dictUser.user.name.lower():
                                        await vigUser.user.send("Sorry. You were unable to kill your target tonight....")
                                        vigUser.victim = None
                          

                        if bombUser.user and bombUser.alive and bombUser.victim:
                            #Adds bomb victim to the planted list
                            bombUser.plantedTargets.append(bombUser.victim)
                            await bombUser.user.send("Bomb has been successfully planted on " + bombUser.victim)
                        
                        
                        if docUser.user and docUser.victim:
                            #saves doctor's last heal
                            docUser.lastHeal = docUser.victim
                        
                        
                        if PIUser.user and PIUser.alive and len(PIUser.PITargets)==2:                            
                            #Gets the side of each PI target and return whether they are on the same side
                            for role in currentRoles:
                                if role.user.name.lower() in PIUser.PITargets:
                                    PIRoles.append(role)
                            if frameUser.user and frameUser.victim and PIRoles[0].user.name.lower() == frameUser.victim.lower():
                                s1 = "mafia"
                            else:
                                s1 = PIRoles[0].side 

                            if frameUser.user and frameUser.victim and PIRoles[1].user.name.lower() == frameUser.victim.lower():
                                s2 = "mafia"
                            else:                               
                                s2 = PIRoles[1].side
                            isSame = s1 == s2
                            if isSame:
                                embed = discord.Embed(title = "Yes. {} and {} are both on the same side. It's up to you to figure out what side though lol.".format(PIRoles[0].user.name,  PIRoles[1].user.name), colour = discord.Colour.green())
                                embed.set_thumbnail(url = "http://www.clker.com/cliparts/P/S/9/I/l/S/234-ed-s-sd-md.png")
                            else:
                                embed =  discord.Embed(title = "No. {} and {} are not on the same side. Hmmmmmmmmmm.".format(PIRoles[0].user.name,  PIRoles[1].user.name), colour = discord.Colour.red())
                                embed.set_thumbnail(url = "https://iconsplace.com/wp-content/uploads/_icons/ff0000/256/png/thumbs-down-icon-14-256.png")
                            await PIUser.user.send(embed = embed)

                        
                        #Storytime
                        await channel.send(embed = self.makeEmbed("Alright everybody get your ass back here. It's storytime."))
                        await mFunctions.muteDead(currentP)
                        await asyncio.sleep(3)


                        #Mayor news
                        if mayorUser and mayorUser.revealed and mayorUser.alreadyShown ==False:
                            mayorEmbed = discord.Embed(title = "The mayor has shown himself/herself to be {}!".format(mayorUser.user.name), description = "Now the mayor's vote counts twice!", colour = discord.Colour.green())
                            mayorEmbed.set_image(url = "https://upload.wikimedia.org/wikipedia/en/a/a3/Adam_West_on_Family_Guy.png")
                            await channel.send(embed = mayorEmbed)
                            mayorUser.alreadyShown = True
                        await asyncio.sleep(3)


                        #Mafia kill story
                        if gfUser.user and gfUser.alive:
                            if victim == None:
                                await channel.send(embed = self.makeEmbed("The mafia was too lazy to kill anyone this night."))
                            else:
                                story1 = discord.Embed(title = "Story", description = "All of these stories are written by linkboi and the submissions from Mafiabot Support Server.", colour = discord.Colour.purple())
                                await channel.send(embed = story1)
                                if saved:
                                    aStory = story.storyTime("alive", victim)
                                    storyEmbed = discord.Embed(title = "{} lives!".format(victim), description = "{}".format(aStory), colour = discord.Colour.green())
                                    storyEmbed.set_thumbnail(url = "https://vignette.wikia.nocookie.net/dragonfable/images/f/f1/Heal_Icon.png/revision/latest?cb=20130329031111")
                                else:
                                    aStory = story.storyTime("dead", victim)
                                    storyEmbed = discord.Embed(title = "{} died :(".format(victim), description = "{}".format(aStory), colour = discord.Colour.red())
                                    storyEmbed.set_image(url = "https://i.ytimg.com/vi/j_nV2jcTFvA/hqdefault.jpg")
                                    for player, data in currentP.items():
                                        if player.name.lower() == victim:
                                            storyEmbed.set_thumbnail(url = player.avatar_url)
                                            storyEmbed.add_field(name = "{}'s role is:".format(player.name), value = "{}".format(data.roleName))
                                            for role in currentRoles:
                                                if role.name.lower() == data.roleName.lower():
                                                    role.alive = False
                                                    break
                                            
                                            break
                                    await mFunctions.killPlayer(currentP, victim)
                                    temp.remove(victim)

                                
                               
                            

                                await channel.send(embed = storyEmbed)
                            await asyncio.sleep(5)
                        

                        #vg's news
                        if vigUser.victim:

                            #role obj
                            vgVictimRole = None
                            for role in currentRoles:
                                if role.user.name.lower() == vigUser.victim:
                                    vgVictimRole = role

                            #str
                            vgTarget = vigUser.victim
                            

                            #if vg shot a mafia
                            if vgVictimRole.side == "mafia":
                                embed = discord.Embed(title = "Wait, what's this?", description = "The vigilante shot a mafia!!", colour = discord.Colour.green())
                                embed.add_field(name = "The mafia shot was...", value = "{}!".format(vigUser.victim))
                                embed.set_image(url = "https://vignette.wikia.nocookie.net/michaelbaybatman/images/e/ea/Bac-gotham-rooftop.jpg/revision/latest?cb=20140223174240")
                                vgTargetObj = mFunctions.getPlayer(currentP, vigUser.victim)
                                embed.set_footer(text = "{} was a {}".format(vgTarget, currentP[vgTargetObj].roleName))
                                await mFunctions.killPlayer(currentP, vgTarget)
                                vgVictimRole.alive = False
                                temp.remove(vgTarget)
                                await channel.send(embed = embed)


                            #if vg shot an innocent boi
                            elif vgVictimRole.side == "neutral":
                                embed = discord.Embed(title = "Wait, what's this?", description = "The vigilante shot a neutral role!", colour = discord.Colour.green())
                                embed.set_image(url = "https://vignette.wikia.nocookie.net/michaelbaybatman/images/e/ea/Bac-gotham-rooftop.jpg/revision/latest?cb=20140223174240")
                                embed.set_footer(text = "The victim was a {}, who is {}!".format(vgVictimRole.name, vgVictimRole.user.name))
                                await channel.send(embed = embed)
                                await mFunctions.killPlayer(currentP, vgVictimRole.user.name.lower())
                                vgVictimRole.alive = False
                                temp.remove(vgTarget)
                                

                            #if vg shot mafia's victim too
                            elif victim and vigUser.victim == victim.lower():
                                embed = discord.Embed(title = "Wait, what's this?", description = "The vigilante also shot the mafia's victim! The vigilante has commited suicide out of shame!", colour = discord.Colour.orange())
                                embed.set_image(url = "https://i.ytimg.com/vi/lhckuhUxcgA/hqdefault.jpg")
                                vgTargetObj = mFunctions.getPlayer(currentP, vgTarget)
                                embed.set_footer(text = "{} was the vigilante and {} was a {}!".format(vigUser.user.name,  vgVictimRole.user.name, vgVictimRole.name))
                                
                                await mFunctions.killPlayer(currentP, vigUser.user.name.lower())
                                if saved:
                                    await mFunctions.killPlayer(currentP, vigUser.victim)
                                    temp.remove(vgTarget)
                                    vgVictimRole.alive = False
                                vigUser.alive = False
                                temp.remove(vigUser.user.name.lower())
                                await channel.send(embed = embed) 


                            else:
                                embed = discord.Embed(title = "Wait, what's this?", description = "The vigilante shot the innocent {}! The vigilante has commited suicide out of guilt!".format(vigUser.victim), colour = discord.Colour.red())
                                embed.set_image(url = "https://res.cloudinary.com/teepublic/image/private/s--N6Q7m5Pj--/t_Preview/b_rgb:191919,c_limit,f_jpg,h_630,q_90,w_630/v1493744453/production/designs/1556060_1.jpg")
                                vgTargetObj = mFunctions.getPlayer(currentP, vgTarget)
                                embed.set_footer(text =  "{} was the vigilante and {}'s role was {}!".format(vigUser.user.name, vigUser.victim, vgVictimRole.name))
                                await mFunctions.killPlayer(currentP, vigUser.victim)
                                await mFunctions.killPlayer(currentP, vigUser.user.name.lower())
                                vigUser.alive = False
                                vgVictimRole.alive = False
                                await channel.send(embed = embed)


                        #baiter news
                        if baiterVictims:

                            baiterUser.killCount += len(baiterVictims)
                            for killed in baiterVictims:
                                await asyncio.sleep(2)
                                embed = discord.Embed(title = killed.user.name + " mysteriously died last night...", description= "Apparently it was an accident...")
                                embed.set_image(url = "https://media.npr.org/assets/img/2012/12/17/mystery-list_custom-9c58a855ae7747d9f76edcebbf2c6e50d482a41d-s800-c85.jpg")
                                

                                for player, data in currentP.items():
                                        if player.name.lower() == killed.user.name.lower():
                                            embed.set_thumbnail(url = killed.user.avatar_url)
                                            embed.set_footer(text = killed.user.name + "'s role was " + killed.name)
                                            for role in currentRoles:
                                                if role.name.lower() == data.roleName.lower():
                                                    role.alive = False
                                                    break
                                            break                                
                                await mFunctions.killPlayer(currentP, killed.user.name.lower())
                                temp.remove(killed.user.name.lower())
                                await channel.send(embed = embed)
                                await asyncio.sleep(3)


                        #Removes dead people from Bomber planted list
                        for role in currentRoles:
                            if not role.alive:
                                if bombUser.user and role.user.name.lower() in bombUser.plantedTargets:
                                    bombUser.plantedTargets.remove(role.user.name.lower())

                        #bomber news
                        if bombUser.user and bombUser.activated:
                            embed = discord.Embed(title = "It was a quiet night in the village until.....BOOM!", description = "There were explosions everywhere!", colour = discord.Colour.red())
                            for name in bombUser.plantedTargets:
                                objPlayer = mFunctions.getPlayer(currentP, name)

                                embed.add_field(name = name + " died from the explosion!", value = name + "'s role was " + currentP[objPlayer].roleName + "!") 
                                await mFunctions.killPlayer(currentP, name)
                                temp.remove(name)
                                for role in currentRoles:
                                    if role.user.name.lower() == name:
                                        role.alive = False
                                        if role.victim:
                                            role.victim = None
                                        break
                                
                            embed.set_image(url = "https://i.ytimg.com/vi/9nnbWP82taM/maxresdefault.jpg")
                            await channel.send(embed = embed)
                            bombUser.activated = False
                            bombUser.plantedTargets = []
                            await asyncio.sleep(4)

                        
                                
                    

                            
                        
                        for role in currentRoles:
                            if not role.alive:
                                if bombUser.user and role.user.name.lower() in bombUser.plantedTargets:
                                    bombUser.plantedTargets.remove(role.user.name.lower())    


                        #if bomber ded
                        if bombUser.user and bombUser in currentRoles and not bombUser.alive and bombUser.plantedTargets:  
                            await asyncio.sleep(3)
                            randTarget = random.choice(bombUser.plantedTargets)    
                            await mFunctions.killPlayer(currentP, randTarget)
                            temp.remove(randTarget.lower())
                            embed = discord.Embed(title = "Moments before " + bombUser.user.name + "'s death, " + bombUser.user.name + " pulled out a trigger and with a click, created one last big boom.", description = randTarget + " was killed in the explosion.", colour = discord.Colour.dark_grey())
                            embed.set_footer(text = randTarget + "'s role was " + mFunctions.getRoleWName(currentP, randTarget))
                            embed.set_image(url = "https://i.kym-cdn.com/photos/images/original/001/487/493/db3.png")
                            await channel.send(embed = embed)
                            for role in currentRoles:
                                if role.user.name.lower() == randTarget:
                                    role.alive = False
                                    break
                            
                            currentRoles.remove(bombUser)
                            bombUser.plantedTargets = []
                            await asyncio.sleep(3)

                                
                        check = self.checkWin(mafiaCount, server.id, currentP, dictUser, baiterUser, bombUser)


                        await asyncio.sleep(2)
                        if check == "bomber":
                            await mFunctions.unMuteAll(currentP)
                            await self.updateWin(currentP, server.id, "bomber")
                            embed = discord.Embed(title = "Everyone died except the bomber. The bomber wins!", description = bombUser.user.name + " is the bomber!", colour = discord.Colour.dark_grey())
                            embed.set_thumbnail(url = "https://www.mobafire.com/images/avatars/ziggs-classic.png")
                            break
                        elif check == "baiter":
                            await mFunctions.unMuteAll(currentP)
                            if baiterUser.user and baiterUser.killCount >3:
                                await self.updateWin(currentP, server.id, "baiter")
                                embed = discord.Embed(title = "The baiter wins!", colour = discord.Colour.dark_grey())  
                            else:
                                embed = discord.Embed(title = "Looks like the baiter didn't kill enough people. No one wins :(", colour = discord.Colour.dark_grey())  
                            break
                        elif check == "mafia":
                                await mFunctions.unMuteAll(currentP)
                                embed = discord.Embed(title = "The mafia(s) win!", colour = discord.Colour.red())
                                embed.set_image(url = "https://vignette.wikia.nocookie.net/leagueoflegends/images/8/89/Graves_MafiaSkin_Ch.jpg/revision/latest/zoom-crop/width/480/height/480?cb=20120509133401")
                                await self.updateWin(currentP, server.id, check)
                                break
                        elif check == "villager":
                            await mFunctions.unMuteAll(currentP)
                            embed = discord.Embed(title = "The villagers win!", colour = discord.Colour.green())
                            embed.set_image(url = "https://www.fanbyte.com/wp-content/uploads/2018/12/Villager.jpg")
                            await self.updateWin(currentP, server.id, check)                           
                            break
                        elif check == "dictator":
                            await mFunctions.unMuteAll(currentP)
                            embed = discord.Embed(title = "The Dictator chose " + dictUser.selectSide + "! The Dictator wins!", description = "The Dictator was " + dictUser.user.name, colour = discord.Colour.blurple())
                            await self.updateWin(currentP, server.id, check)
                            break
                        elif check == "none": # lynch time bois


                            #checks executioner
                            if exePlayer != None:
                                if mFunctions.isAlive(currentP, exeTarget.name.lower()) == False and mFunctions.isAlive(currentP, exePlayer.name.lower()):
                                    embed = discord.Embed(title = "You are now the Jester. Your win condition is to get the town to lynch you.", colour = discord.Colour.teal())
                                    embed.set_image(url = "https://runes.lol/image/generated/championtiles/Shaco.jpg")
                                    await exePlayer.send( embed = embed)
                                    currentP[exePlayer].roleName = "jester"
                            
                            
                            embed = discord.Embed(title = "Now I'll give you guys {} seconds to talk. ".format(talkTime), description = "Want to claim a role? Accuse someone? Confess? Do that now!", colour = discord.Colour.magenta())
                            for player, data in currentP.items():
                                if data.alive:
                                    embed.add_field(name = player.name, value = "Alive!")
                            embed.set_image(url = "https://blog.oup.com/wp-content/uploads/2016/11/Witchcraft_at_Salem_Village2.jpg")
                            await channel.send(embed = embed)


                            #Gives permission to type in chat
                            overwrite = discord.PermissionOverwrite(send_messages = True, read_messages = True)
                            overwriteMute = discord.PermissionOverwrite(send_messages = False, read_messages = True)


                            for player, data in currentP.items():
                                if data.alive:
                                    await channel.set_permissions(player, overwrite = overwrite)
                                else:
                                    await channel.set_permissions(player, overwrite = overwriteMute)


                            await asyncio.sleep(talkTime)


                            minVote = int(len(temp)/1.5)
                            #special occasion cuz I'm too lazy to figure out the perfect number to divide group size with
                            if len(temp) == 4:
                                minVote = 3


                            if len(temp) < 4:
                                minVote = 2


                            embed = discord.Embed(title = "Alright! It's time to vote! Vote for a person by reacting to the message associated with your target. (A person must have a min of {} votes to be lynched)".format(str(minVote)), description = "Note: If you try to be sneaky and vote more than once your vote will only count once to the first message the bot reads.", colour = discord.Colour.green())
                            embed.set_footer(text = "You have {} seconds to vote.".format(voteTime))
                            await channel.send(embed = embed)


                            #Gets the lynched target
                            lynchPerson = await mFunctions.vote(currentP, channel, voteTime, mayorUser.user, mayorUser.revealed, minVote)


                            await asyncio.sleep(3)


                            if lynchPerson != None:
                                embed = discord.Embed(title = "{} has been hanged by the village. Press f to pay respect.".format(lynchPerson.name), colour = discord.Colour.red())
                                embed.set_image(url = "https://cdn.shopify.com/s/files/1/0895/0864/products/42-47714084_1024x1024.jpeg?v=1451772538")
                                await channel.send(embed = embed)
                                await asyncio.sleep(2)
                                for player, data in currentP.items():
                                    if (player.name.lower() == lynchPerson.name.lower()):
                                        data.alive = False
                                        try:
                                            await player.edit(mute = True)
                                        except discord.HTTPException:
                                            pass


                                        for role in currentRoles:
                                            if role.user.name.lower() == lynchPerson.name.lower():
                                                role.alive = False
                                                break
                                        await player.send("Hey, you're dead! Feel free to spectate the rest of the game but PLEASE do not talk nor give away important information to those still playing. Thank you!")
                                        await channel.send(embed = self.makeEmbed("{}'s role was {}".format(player.name, data.roleName)))
                                        break
                            else:
                                await channel.send(embed = self.makeEmbed("No one was hanged."))
                        
                        
                            #if bomber ded
                            for role in currentRoles:
                                if role.name == "bomber" and not role.alive and role.plantedTargets:
                                    await asyncio.sleep(1)
                                    randTarget = random.choice(role.plantedTargets)    
                                    await mFunctions.killPlayer(currentP, randTarget)
                                    embed = discord.Embed(title = "Moments before " + role.user.name + "'s death, " + role.user.name + " pulled out a trigger and with a click, created one last big boom.", description = randTarget + " was killed in the explosion.", colour = discord.Colour.dark_grey())
                                    embed.set_image(url = "https://i.kym-cdn.com/photos/images/original/001/487/493/db3.png")
                                    embed.set_footer(text = randTarget + "'s role was " + mFunctions.getRoleWName(currentP, randTarget))
                                    await channel.send(embed = embed)
                                    for role in currentRoles:
                                        if role.user.name.lower() == randTarget:
                                            role.alive = False
                                            break    
                                    currentRoles.remove(role)
                                    role.plantedTargets = []
                                    await asyncio.sleep(3)
                              
                                
                            for player, data in currentP.items():
                                await channel.set_permissions(player, overwrite = overwriteMute)


                            check = self.checkWin(mafiaCount, server.id, currentP, dictUser, baiterUser, bombUser)
                            
                            
                            #checks lynched target for jester and executioner role
                            jesterWins = False
                            exeWins = False
                            if lynchPerson != None:
                                for player, data in currentP.items():
                                    if player.name.lower() == lynchPerson.name.lower() and data.roleName == "jester":
                                        jesterWins = True
                                    elif exeTarget != None and player.name.lower() == lynchPerson.name.lower() and player.name.lower() == exeTarget.name.lower() and mFunctions.isAlive(currentP, exePlayer.name.lower()):
                                        exeWins = True


                            #check conditions 
                            #check returns string mafia or villager
                            if jesterWins:
                                await mFunctions.unMuteAll(currentP)
                                embed = discord.Embed(title = "Uh oh! The Jester wins!", colour = discord.Colour.purple())
                                embed.set_thumbnail(url = "https://runes.lol/image/generated/championtiles/Shaco.jpg")
                                embed.set_footer(text = "hehehehe....")
                                await self.updateWin(currentP, server.id, "jester")
                                
                                break
                            elif exeWins:
                                embed = discord.Embed(title = "Wait a minute...", description = "You've all been fooled!", colour = discord.Colour.dark_grey())
                                embed.add_field(name = "{} was the executioner's target!".format(exeTarget.name), value = "{} was the executioner!".format(exePlayer.name))
                                embed.set_image(url = "https://afinde-production.s3.amazonaws.com/uploads/3ee849bd-8cfc-40b3-98ba-2e39b2ec8c2f.png")
                                await channel.send(embed = embed)
                                await mFunctions.unMuteAll(currentP)
                                embed = discord.Embed(title = "The Executioner wins!", colour = discord.Colour.dark_grey())
                                embed.set_thumbnail(url = "")
                                await self.updateWin(currentP, server.id, "executioner")
                                
                                break
                            elif check == "mafia":
                                await mFunctions.unMuteAll(currentP)
                                embed = discord.Embed(title = "The mafia(s) win!", colour = discord.Colour.red())
                                embed.set_image(url = "https://vignette.wikia.nocookie.net/leagueoflegends/images/8/89/Graves_MafiaSkin_Ch.jpg/revision/latest/zoom-crop/width/480/height/480?cb=20120509133401")
                                await self.updateWin(currentP, server.id, check)
                                
                                break
                            elif check == "villager":
                                await mFunctions.unMuteAll(currentP)
                                embed = discord.Embed(title = "The villagers win!", colour = discord.Colour.green())
                                embed.set_image(url = "https://www.fanbyte.com/wp-content/uploads/2018/12/Villager.jpg")
                                await self.updateWin(currentP, server.id, check)
                                
                                break
                            elif check == "dictator":
                                await mFunctions.unMuteAll(currentP)
                                embed = discord.Embed(title = "The Dictator chose the " + dictUser.selectSide + " side and that side 'won'! Therefore the Dictator wins!", description = "The dictator was " + dictUser.user.name, colour = discord.Colour.blurple())
                                await self.updateWin(currentP, server.id, check)
                                break


                            #Resets all role obj's victim variable
                            for role in currentRoles:
                                if not role.name.lower() in noneDmRoles:
                                    role.victim = None
                            
                            night += 1


                    #unmutes all players
                    await mFunctions.unMuteAll(currentP)


                    #Only if the game did not end with commandStop
                    if self.serverStatus[server.id]['commandStop'] == False:
                        self.displayAllR(embed, currentP, origFramer)
                        embed.set_footer(text = "Enjoyed the game? Support Mafiabot by upvoting me on discordbots.org so my creator would be more inspired to create new content!!", icon_url = self.bot.user.avatar_url)
                        await ctx.channel.send(embed = embed)
                        if check != "baiter" and baiterUser.user and baiterUser.killCount >= 3:
                            baiterEmbed = discord.Embed(title = "The baiter is " + baiterUser.user.name+ "!", description = "The baiter has a kill count of " + str(baiterUser.killCount) + ", so " + baiterUser.user.name + " also wins!")
                            baiterEmbed.set_image(url = "https://i.kym-cdn.com/entries/icons/original/000/028/431/kirby.jpg")
                            await self.updateWin(currentP, server.id, "baiter")
                            await ctx.channel.send(embed = baiterEmbed)
                        await channel.send(embed = embed)
                        await channel.send(embed = self.makeEmbed("Thank you all for playing! Deleting this channel in 10 seconds"))
                        await asyncio.sleep(10)
                        await channel.delete()
                        


                    self.serverStatus[server.id]["ready"] = False
                    self.serverStatus[server.id]["gameOn"] = False
                    self.serverStatus[server.id]["setting"] = False
                    self.serverStatus[server.id]['commandStop'] = False  
                    self.serverStatus[server.id]["mafiaChannel"] = None
                    

                    embed = discord.Embed(title = "A game has finished on {}.".format(server.name), description = "Group size: {}".format(len(currentP.keys())), colour = discord.Colour.dark_purple())
                    embed.add_field(name = "Server id: ", value = "{}".format(server.id))
                    embed.set_thumbnail(url = server.icon_url)
                    await supportChannel.send(embed = embed)

                        
                except Exception as e:
                    mafiaChannel = self.serverStatus[server.id]["mafiaChannel"]
                    print("{}".format(traceback.format_exc()))
                    if isinstance(e, discord.Forbidden):
                        await ctx.channel.send("Error. Missing permissions! Check all my required permissions with m.perms.")

                    elif isinstance(e, discord.NotFound):
                        await ctx.channel.send( "Boi, who deleted my mafia text channel...")
                        mafiaChannel = None
                    else:
                        await ctx.channel.send("Error. Something weird happened. (If this keeps happening report it to the Mafia Support Server or use m.support to request support from the support server.)")
                        
                    embed = discord.Embed(title = "An error has occured on {}.".format(server.name), description = "Server id: {}".format(server.id), colour = discord.Colour.red())
                    embed.add_field(name = "Error:", value = "{}".format(traceback.format_exc()))
                    

                    await supportChannel.send( embed = embed)
                    self.serverStatus[server.id]["ready"] = False
                    self.serverStatus[server.id]["gameOn"] = False
                    self.serverStatus[server.id]["commandStop"] = False
                    self.serverStatus[server.id]["setting"] = False
                    await mFunctions.unMuteAll(currentP)

                    try:
                        await mafiaChannel.delete() 
                    except:
                        pass
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
            self.serverStatus[server.id]["setting"] = False
            
        if not str(server.id) in sList.keys():
            
            sList[str(server.id)] = {}
            sList[str(server.id)]["game mode"] = "classic"
            sList[str(server.id)]['dmTime'] = 30
            sList[str(server.id)]['voteTime'] = 20
            sList[str(server.id)]['talkTime'] = 60
            sList[str(server.id)]["category"] = None
            with open('servers.json', 'w') as f:
                json.dump(sList, f) 
    def findChannel(self, server):
        for item in server.channels:
            if item.name == 'mafia':
                return item
    

    #returns number of people alive in the side of mafia or village
    def checkGame(self, current, threat):
        num = 0
        threats = ["godfather", "mafia", "framer", "bomber"]
        if threat:
            for player, data in current.items():
                if data.alive and data.roleName in threats:
                    num += 1
        else:
            for player, data in current.items():
                if data.alive and not data.roleName in threats:
                    num+=1
        return num


    #returns who wins
    def checkWin(self, mafiaCount, id, currentList, dictUser, baiterUser, bombUser):
        aliveCount = 0

        for data in currentList.values():
            if data.alive:
                aliveCount+=1
        
        #Bomber has priority over baiter
        if (aliveCount < 2 and bombUser.user and bombUser.alive) or (aliveCount == 0 and bombUser.user):
            return "bomber"
        elif (aliveCount < 2 and baiterUser.user and bombUser.alive) or (aliveCount == 0 and baiterUser.user ):
            return "baiter"

        threatAlive = self.checkGame(currentList, True)
        normalAlive = self.checkGame(currentList, False)
        bombAlive = False
        for player, data in currentList.items():
            if data.alive and data.roleName == "bomber":
                bombAlive = True
        
        if (threatAlive > normalAlive or (normalAlive ==1 and threatAlive >= 1)) and not bombAlive:
            if dictUser.user and dictUser.alive and dictUser.selectSide == "mafia":
                return "dictator"
            else:
                return "mafia"
        elif threatAlive == 0:
            if dictUser.user and dictUser.alive and dictUser.selectSide == "villager":
                return "dictator"
            else:
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
            cog = self.bot.get_cog("Points")
            title = cog.getCTitle(player.id)
            if title == "" or title == " ":
                nameThing = player.name
            else:
                nameThing = player.name + '\n"' + title+'"'
            if framer != None and player.name.lower() == framer.name.lower():
                embed.add_field(name = nameThing, value = "framer", inline = True)
            else:
                embed.add_field(name =nameThing, value = "{}".format(data.roleName), inline = True)


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
        if role == "mafia" or role == "framer" or role == "godfather": #checks what side the role belongs to
            return "mafia"
        elif role == "jester":
            return "jester"
        elif role == "executioner":
            return "executioner"
        elif role == "baiter":
            return "baiter"
        elif role == "bomber":
            return "bomber"
        elif role == "dictator":
            return "dictator"
        else:
            return "villager"


    def checkFile(self, playerID):
        for user in self.userList:
            if user.id == playerID:
                return
        print("hi")
        newPlayer = userObj.MafiaUser(playerID)
        self.editFile(newPlayer)
        self.userList.append(newPlayer)

        
    def findUser(self, userID):
        for player in self.userList:
            if player.id == userID:
                return player
        return None


    async def updateWin(self, mafiaList, serverID, winner):
        #finds players with the winning role (winner is a string) and adds one point to their record
        
        for player, data in mafiaList.items():
            self.checkFile(player.id)
            side = self.checkSide(data.roleName)
            tempUser = self.findUser(player.id)
            if side == winner:
                
                tempUser.wins += 1
                reward = random.randint(10, 30)
                tempUser.points += reward
                embed = discord.Embed(title = "You have received {} Mafia points!:moneybag:".format(str(reward)), description = "Spend mafia points at the store! Check your account with m.record @user!", colour = discord.Colour.green())
                embed.set_image(url = "https://images2.minutemediacdn.com/image/upload/c_fill,g_auto,h_1248,w_2220/f_auto,q_auto,w_1100/v1555271785/shape/mentalfloss/500940-Amazon_0.png")
                await player.send(embed = embed)
            tempUser.games += 1
            self.editFile(tempUser) 
  
                  
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
    

    def editFile(self, userObj):
        path = "C:/Users/Ernest/Desktop/Mafiabot/MafiaBot-1/users/"
        completeName = os.path.join(path, str(userObj.id)+".txt")
        n = open(completeName, "w")
        data_str = str(userObj.id) + "\n" + str(userObj.wins) + "\n" + str(userObj.games) + "\n" + str(userObj.points) + "\n" 
        for item in userObj.titles:
            data_str += item+" "
        data_str += "\n"+userObj.currentTitle + " "
        n.write(data_str)
        n.close()
        
def setup(bot):
    bot.add_cog(mafia(bot))