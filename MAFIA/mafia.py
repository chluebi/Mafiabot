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

class mafia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.userList = []
        for filename in os.listdir("/home/ubuntu/users"):
            self.userList.append(self.makeUser(filename))

    def makeUser(self, dir):
        tempList = []
        with open("/home/ubuntu/users/" + dir) as f:
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
    mafiaList = [] #Names 
    DDList = [] #Names
    liveList = [] #names
    nominateList = []

    testVar= "Boi"
    gameModes = ["classic", "crazy"]
    
    patch = "1.8"
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
                supportChannel = self.bot.get_channel(534564704937574400)
                #await supportChannel.send("Reset on {}".format(server.name))

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
              #await supportChannel.send("Party cleared on {}".format(server.name))
              self.mafiaPlayers[server.id] = {}
              await channel.send(embed = self.makeEmbed("The current party is now cleared."))

    @commands.command(name = "gamemode", aliases = ["setmode", "mode"])
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
            self.checkFile(ctx.message.author.id)
            if self.serverStatus[server.id]["gameOn"] == True:
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

            
            if self.serverStatus[server.id]["gameOn"] == True or self.serverStatus[server.id]["ready"] == True:
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
        for mode in self.gameModes:
            
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

    @commands.command(pass_context = True)
    async def linkboi(self, ctx):
        if ctx.author.name == "linkboi":

            await ctx.channel.send("Everyone's roles are send to your dm sir.")
        else:
            await ctx.channel.send("You're not linkboi.")
    @commands.command(name = "setup", aliases = ["prep"])
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
            elif self.serverStatus[server.id]["setting"] == True:
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
                            elif (data.roleName == 'executioner'):
                                embed = discord.Embed(title = "You are the executioner. You will be given a target, and your job is to convince the town to lynch your target to win. If you target is killed by other ways you will turn into a Jester.", colour = discord.Colour.teal())
                                embed.set_image(url = "https://www.mobafire.com/images/champion/skins/landscape/dr-mundo-executioner.jpg")
                                await player.send(embed = embed)
                            elif (data.roleName == 'distractor'):
                                embed = discord.Embed(title = "You are the distractor. You can stop one person from using their role each night.", colour = discord.Color.orange())
                                embed.set_image(url = "https://media.wired.com/photos/59a459d3b345f64511c5e3d4/master/pass/MemeLoveTriangle_297886754.jpg")
                                await player.send(embed = embed)
                            else:
                                embed = discord.Embed(title = "You are just a normal innocent villager who might get accused for crimes you didn't commit ¯\_(ツ)_/¯ ", colour = discord.Colour.dark_gold())
                                embed.set_image(url = "https://www.lifewire.com/thmb/0V5cpFjHpDgs5-c3TLP_V29SNL4=/854x480/filters:fill(auto,1)/uFiT1UL-56a61d203df78cf7728b6ae2.png")
                                await player.send( embed = embed)

                        overwrites = {
                            server.default_role: discord.PermissionOverwrite(send_messages=False),
                            server.me: discord.PermissionOverwrite(send_messages=True),
                            server.me: discord.PermissionOverwrite(read_messages = True),
                            server.default_role: discord.PermissionOverwrite(read_messages = False)
                        }
                        self.serverStatus[server.id]["mafiaChannel"] = await ctx.guild.create_text_channel("mafia", overwrites = overwrites)

                        for player in self.mafiaPlayers[server.id].keys():
                            try:
                                await player.edit(mute = False)
                            except discord.HTTPException:
                                print("duh")
                        
                        
                    except discord.Forbidden:

                        print("Forbidden error. Resetting...")
                        self.serverStatus[server.id]["ready"] = False
                        self.serverStatus[server.id]["setting"] = False
                        embed = discord.Embed(title = "Error. Missing required permissions. Please check all of my required permissions with m.perms and try again.", colour = discord.Colour.red())

                        await channel.send(embed = embed)
                    else:
                        self.serverStatus[server.id]["ready"] = True
                        self.serverStatus[server.id]["setting"] = False
                        embed = discord.Embed(title = "Everything's ready! Everyone feel free to join a voice chat and type m.start to start the game!", description = "Make sure you understand how the game works! (Info can be found with m.game)", colour = discord.Colour.green())
                        embed.set_thumbnail(url = "https://pbs.twimg.com/media/DWVbyz5WsAA93-y.png")
                        await channel.send(embed = embed)


    

        
        


            
            
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
            elif self.serverStatus[server.id]["setting"] == True:
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
                    pastHeal = None
                    
                    for player in currentP.keys():
                        await channel.send(player.mention)

                    #intro
                    intro = discord.Embed(title = "Welcome to Mafia!", description = "If you haven't read the rules yet, please type m.game to view them in your dm!", colour = discord.Colour.dark_purple())
                    intro.add_field(name = "Important!", value = "Please do not type in this chat unless instructed to do so. Admins please don't abuse your godly powers and talk when other people can't. Thank you.")
                    intro.add_field(name = "To those who are dead: ", value = "Please do not talk. I know it's hard to grasp but dead people can't talk.")
                    intro.add_field(name = "Some important rules: ", value = "Screen shots are not permitted and would only ruin the game. However you CAN claim roles to either coordinate among yourselves or trick other people. Just NO SCREENSHOTS.")
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
                            embed.add_field(name = "{}".format(item.name), value = "Role: {}".format(turn.getRole(currentP, item.name.lower())), inline = False)
                        embed.set_footer(text = "Cooporate with your fellow mafias through dm to make strategies!")
                        for item in mafiaList:
                            await item.send(embed = embed)
                        
                        await asyncio.sleep(4)
                    exePlayer = mFunctions.findPlayerWithRole(currentP, "executioner")
                    exeTarget = None
                    if  exePlayer != None:
                        exeTarget = None
                        while True:
                            exeTarget = random.choice(list(currentP.keys()))
                            if mFunctions.getRole(currentP, exeTarget.name.lower()) != "mafia" and mFunctions.getRole(currentP, exeTarget.name.lower()) != "framer" and exeTarget.name.lower() != exePlayer.name.lower():
                                exeEmbed = discord.Embed(title = "Alright executioner. Your target is {}. Convince the town to lynch {} and you win. Ezpz.".format(exeTarget.name, exeTarget.name), description = "If your target is killed any other way you will become a Jester.", colour = discord.Colour.light_grey())
                                exeEmbed.set_thumbnail(url = exeTarget.avatar_url)

                                await exePlayer.send(embed = exeEmbed)
                                break 
                    origFramer = mFunctions.findPlayerWithRole(currentP, "framer")
                    revealed = False
                    mayorShown = False
                    distractorCooldown = False
                    #big boi loop for game
                    while True:
                        if self.serverStatus[server.id]['commandStop'] == True:
                            await channel.send(embed = self.makeEmbed("Due to a request, I will end this game now."))
                            print("Requested stop on {}".format(server.name))
                            #await supportChannel.send(embed = discord.Embed(title = "A game has stopped on {}".format(server.name), description = "{}".format(server.id), colour = discord.Colour.dark_magenta()))
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
                        distractorPlayer = None
                        distractorAlive = False
                        temp = [] # names
                        tempDead = [] # names
                        healVictim = None
                        victim = None
                        distractedP = None
                        lastDistract = None
                        
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
                        await mFunctions.muteAll(currentP)
                        
                        await asyncio.sleep(2)
                        embed = discord.Embed(title = "It is now night time, time to go to sleep...", description = "Don't panick, I muted all of you", colour = discord.Colour.blue())
                        embed.set_image(url = "https://www.nih.gov/sites/default/files/news-events/research-matters/2019/20190312-sleep.jpg")
                        await channel.send(embed = embed)
                        
                        await asyncio.sleep(3)
                        #distractor turn
                        distractorAlive = False
                        for player, data in currentP.items():
                            if(data.roleName == 'distractor') and data.alive == True:
                                distractorPlayer = player
                                distractorAlive = True

                        if distractorAlive and not distractorCooldown:
                            distractedP = await mFunctions.distractorTurn(distractorPlayer, temp, dmTime, lastDistract)
                            lastDistract = distractedP
                            distractorCooldown = True
                        
                        else:
                            distractorCooldown = False
                        await channel.send(embed = self.makeEmbed("Mafia(s) please check your dm."))


                        #Mafia turn
                        framer = mFunctions.findPlayerWithRole(currentP, "framer")
                        
                        mafiaNum = 0
                        framerCount = 0
                        for player, data in currentP.items():
                            if (data.roleName == "mafia" and data.alive == True):
                                mafiaNum+=1
                            elif data.roleName == "framer" and data.alive == True:

                                framerCount +=1

                        if mafiaNum == 0 and framerCount >0:
                            await mFunctions.findPlayerWithRole(currentP, "framer").send("Since there are no more mafias, you are now a mafia.")
                            currentP[mFunctions.findPlayerWithRole(currentP, "framer")].roleName = "mafia"
                            framer = None
                                    
                        
                        mafiaNames = []
                        mafias = []
                        mafiaTargets = []
                        
                        for player, data in currentP.items():
                            
                            if ((data.roleName == "mafia")and data.alive == True):
                                if player.name.lower() == distractedP:
                                    await player.send("Sorry. You got distracted tonight...")
                                else:
                                    mafiaNames.append(player.name.lower())
                                    mafias.append(player)
                            else:
                                if (data.roleName != "framer" and data.alive == True):
                                    mafiaTargets.append(player.name.lower())
                        
                        victim = await mFunctions.mafiaturn(currentP, mafiaTargets, dmTime, mafiaNames, mafias)
                        framerVictim = None

                        

                        if framer != None and mFunctions.isAlive(currentP, framer.name.lower()) == True:
                            if distractedP != None and framer.name.lower() == distractedP:
                                await framer.send("Sorry. You got distracted tonight...")
                            else:
                                framerVictim = await mFunctions.framerTurn(currentP, framer, dmTime)
                        

                        
                        
                        #Doctor turn
                        
                        for player, data in currentP.items():
                            if(data.roleName == 'doctor') and data.alive == True:
                                doctorUser = player
                                doctorAlive = True

                        # Only if doc is alive
                        if distractedP != None and doctorUser.name.lower() == distractedP:
                            await doctorUser.send("Sorry. You got distracted tonight...")
                        elif doctorAlive == True:
                            await channel.send("Doctor please check your DM.")
                            healVictim = await mFunctions.doctorTurn(doctorUser, temp, dmTime, pastHeal)
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
                            if vigilanteUser.name.lower() == distractedP:
                                await vigilanteUser.send("Sorry. You got distracted tonight...")
                            else:
                                vgTarget = await mFunctions.vigTurn(vigilanteUser, temp, dmTime)
                            
                        
                        #mayor turn
                        mayor = mFunctions.findPlayerWithRole(currentP, "mayor")
                        
                        if mayor != None and revealed == False:
                            if distractedP != None and mayor.name.lower() == distractedP:
                                await mayor.send("Sorry. You got distracted tonight...")
                            else:
                                try:
                                    revealed = await mFunctions.mayorTurn(mayor, dmTime)
                                except asyncio.TimeoutError:
                                    await mayor.send("You ran out of time.")
                        #Detective turn
                        
                        for player, data in currentP.items():
                            if(data.roleName == 'detective') and data.alive == True:
                                detUser = player
                                detAlive = True
                        
                        # only if det is alive

                        if detAlive == True:
                            await channel.send(embed = self.makeEmbed("Detective please check your DM"))
                            if distractedP != None and detUser.name.lower() == distractedP:
                                await detUser.send("Sorry. You got distracted tonight...")
                            else:
                                
                                await mFunctions.detTurn(detUser, temp, dmTime, mafiaList, framerVictim, framer)


                        

                        #Storytime
                        await channel.send(embed = self.makeEmbed("Alright everybody get your ass back here. It's storytime."))
                        await mFunctions.muteDead(currentP)

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
                                        storyEmbed.set_thumbnail(url = player.avatar_url)

                                        storyEmbed.add_field(name = "{}'s role is:".format(player.name), value = "{}".format(data.roleName))
                                await mFunctions.killPlayer(currentP, victim)
                                


                                temp.remove(victim)
                            
                            
                            await channel.send(embed = storyEmbed)


                        await asyncio.sleep(5)

                        if revealed and mayorShown ==False:
                            mayorEmbed = discord.Embed(title = "The mayor has shown himself/herself to be {}!".format(mFunctions.findPlayerWithRole(currentP, "mayor")), description = "Now the mayor's vote counts twice!", colour = discord.Colour.green())
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
                                vgTargetObj = mFunctions.getPlayer(currentP, vgTarget)
                                embed.set_footer(text = "{} was a {}".format(vgTarget, currentP[vgTargetObj].roleName))
                                await mFunctions.killPlayer(currentP, vgTarget)
                                temp.remove(vgTarget)
                                await channel.send(embed = embed)
                            #if vg shot an innocent boi
                            elif not vgTarget in mafiaNames:
                                embed = discord.Embed(title = "Wait, what's this?", description = "The vigilante shot the innocent {}! The vigilante has commited suicide out of guilt!".format(vgTarget), colour = discord.Colour.red())
                                
                                embed.set_image(url = "https://res.cloudinary.com/teepublic/image/private/s--N6Q7m5Pj--/t_Preview/b_rgb:191919,c_limit,f_jpg,h_630,q_90,w_630/v1493744453/production/designs/1556060_1.jpg")
                                vgTargetObj = mFunctions.getPlayer(currentP, vgTarget)
                                embed.set_footer(text =  "{} was the vigilante and {}'s role was {}!".format(vigilanteUser.name, vgTarget, currentP[vgTargetObj].roleName))
                                await mFunctions.killPlayer(currentP, vgTarget)
                                await mFunctions.killPlayer(currentP, vigilanteUser.name.lower())
                                await channel.send(embed = embed)
                                
                            #if vg shot the mafia's victim            
                            elif vgTarget == victim.lower():
                                embed = discord.Embed(title = "Wait, what's this?", description = "The vigilante also shot the mafia's victim! The vigilante has commited suicide out of shame!", colour = discord.Colour.orange())
                                embed.set_image(url = "https://i.ytimg.com/vi/lhckuhUxcgA/hqdefault.jpg")
                                vgTargetObj = mFunctions.getPlayer(currentP, vgTarget)
                                embed.set_footer(text = "{} was the vigilante and {} was a {}!".format(vigilanteUser.name,  vgTarget, currentP[vgTargetObj].roleName))
                                
                                await mFunctions.killPlayer(currentP, vigilanteUser.name.lower())
                                if saved == True:
                                    await mFunctions.killPlayer(currentP, vgTarget)
                                await channel.send(embed = embed)                

                            

                            
                            
                        check = self.checkWin(mafiaCount, server.id, currentP)

                        await asyncio.sleep(2)
                        if check == "mafia":
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

                        elif check == "none": # lynch

                            #checks executioner
                            if exePlayer != None:
                                if mFunctions.isAlive(currentP, exeTarget.name.lower()) == False and mFunctions.isAlive(currentP, exePlayer.name.lower()):
                                    embed = discord.Embed(title = "You are now the Jester. Your win condition is to get the town to lynch you.", colour = discord.Colour.teal())
                                    embed.set_image(url = "https://runes.lol/image/generated/championtiles/Shaco.jpg")
                                    await exePlayer.send( embed = embed)
                                    currentP[exePlayer].roleName = "jester"
                            tempC = []
                            for player, data in currentP.items():
                                if data.alive == True:
                                    tempC.append(player.name.lower())
                            embed = discord.Embed(title = "Now I'll give you guys {} seconds to talk. ".format(talkTime), description = "Want to claim a role? Accuse someone? Confess? Do that now!", colour = discord.Colour.magenta())
                            for player, data in currentP.items():
                                if data.alive == True:
                                    embed.add_field(name = player.name, value = "Alive!")
                
                            embed.set_image(url = "https://blog.oup.com/wp-content/uploads/2016/11/Witchcraft_at_Salem_Village2.jpg")
                            await channel.send(embed = embed)
                            #Gives permission to type in chat
                            overwrite = discord.PermissionOverwrite(send_messages = True, read_messages = True)
                            overwriteMute = discord.PermissionOverwrite(send_messages = False, read_messages = True)


                            for player, data in currentP.items():
                                if data.alive == True:
                                    await channel.set_permissions(player, overwrite = overwrite)
                     
                                else:
                                    await channel.set_permissions(player, overwrite = overwriteMute)
                            await asyncio.sleep(talkTime)
                            minVote = int(len(temp)/1.5)

                            if minVote < 2:
                                minVote = 2
                            embed = discord.Embed(title = "Alright! It's time to vote! Vote for a person by reacting to the message associated with your target. (A person must have a min of {} votes to be lynched)".format(str(minVote)), description = "Note: If you try to be sneaky and vote more than once your vote will only count once to the first message the bot reads.", colour = discord.Colour.green())
                            
                            embed.set_footer(text = "You have {} seconds to vote.".format(voteTime))


                            await channel.send(embed = embed)
                            lynchPerson = await mFunctions.vote(currentP, channel, voteTime, mayor, revealed, minVote)

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
                                            print("duh")
                                        await player.send("Hey, you're dead! Feel free to spectate the rest of the game but PLEASE do not talk nor give away important information to those still playing. Thank you!")
                                        await channel.send(embed = self.makeEmbed("{}'s role was {}".format(player.name, data.roleName)))
                                        break
                            else:
                                await channel.send(embed = self.makeEmbed("No one was hanged."))
                        
                                

                              
                                
                            for player, data in currentP.items():
                                await channel.set_permissions(player, overwrite = overwriteMute)
                            check = self.checkWin(mafiaCount, server.id, currentP)
                            
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
                            if jesterWins == True:
                                await mFunctions.unMuteAll(currentP)
                                embed = discord.Embed(title = "Uh oh! The Jester wins!", colour = discord.Colour.purple())
                                embed.set_thumbnail(url = "https://runes.lol/image/generated/championtiles/Shaco.jpg")
                                embed.set_footer(text = "hehehehe....")
                                await self.updateWin(currentP, server.id, "jester")
                                break
                            elif exeWins == True:
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
                    #unmutes all players
                    await mFunctions.unMuteAll(currentP)

                        #Only if the game did not end with commandStop
                    if self.serverStatus[server.id]['commandStop'] == False:
                        self.displayAllR(embed, currentP, origFramer)
                        embed.set_footer(text = "Enjoyed the game? Support Mafiabot by upvoting me on discordbots.org so my creator would be more inspired to create new content!!", icon_url = self.bot.user.avatar_url)
                        await ctx.channel.send(embed = embed)
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
            self.serverStatus[server.id]["setting"] = False
            
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
        if role == "mafia" or role == "framer": #checks what side the role belongs to
            return "mafia"
        elif role == "jester":
            return "jester"
        elif role == "executioner":
            return "executioner"
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
                reward = random.randint(5, 11)
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
        path = "/home/ubuntu/users"
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