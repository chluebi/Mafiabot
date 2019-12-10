import discord
from discord.ext import commands
import asyncio
import os
from os.path import dirname
import json
import random
import logging
import traceback
import MAFIA.story as story
import MAFIA.prep as prep
import MAFIA.gvar as gvar
import MAFIA.turns as turn
import USER.user as userObj
import MAFIA.gameRole as roles
from MAFIA.roles import *
class mafia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.userList = []
        tempDir = dirname(__file__)[:-6]
        self.userDir = tempDir + "\\users"
        self.premiumBois = self.openJson(tempDir + "\\USER\\premium.json")
        print(self.userDir)
        for filename in os.listdir(self.userDir):
            self.userList.append(self.makeUser(filename))


    def makeUser(self, dir):
        tempList = []
        with open(self.userDir + "\\" + dir) as f:
            count = 0
            for line in f:                
                if count != 4 or count != 5:
                    tempList.append(line[:-1])           
                else:
                    tempList.append(line)
                count+=1
            
            tempList[4] = list(tempList[4].split())

        tempPremium = None
        customRoles = []
        for premium, userID in self.premiumBois.items():
            if userID == int(tempList[0]):
                tempPremium = premium
                customRoles = self.premiumBois[userID]
                break
        return userObj.MafiaUser(int(tempList[0]), int(tempList[1]), int(tempList[2]), int(tempList[3]), tempList[4], tempList[5], tempPremium, customRoles)
    
    
    maxPlayers = 20    
    patch = "1.9999"
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
                    embed = discord.Embed(title = "Got it. {}'s game mode has been set to {}! Have fun!".format(server.name, number), colour = discord.Colour.green())
                    embed.set_thumbnail(url = server.icon_url)
                    self.dumpJson("servers.json", sList)
                    await ctx.send(embed = embed)
                else:
                    await channel.send(embed = self.makeEmbed("Lol idk what mode that is. Type m.gamemodes to view all available game modes!"))
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
                self.mafiaPlayers[server.id] = {}

                await channel.send(embed = self.makeEmbed("Reset complete. All conditions are cleared."))
                print ("Reset on {}".format(server.name))
                supportChannel = self.bot.get_channel(604716684955353098)
                try:
                    await supportChannel.send("Reset on {}".format(server.name))
                except:
                    pass

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
              try:
                await supportChannel.send("Party cleared on {}".format(server.name))
              except:
                  pass
              self.mafiaPlayers[server.id] = {}
              await channel.send(embed = self.makeEmbed("The current party is now cleared."))


    @commands.command(name = "gamemode", aliases = ["gamemodes", "mode", "modes"])
    async def gamemode(self, ctx):
        server = ctx.guild
        if server is None:
            await ctx.author.send(embed = self.makeEmbed("This ain't a discord server."))
            return
        
        embed = discord.Embed(title = "Avaliable Game Modes!", description = "To set a gamemode, type m.custom gamemode `mode`", colour = discord.Colour.blue())
        embed.add_field(name = "Classic:grinning::champagne_glass:", value = "The classic mafia you play with friends! Recommended for small parties.", inline = False)
        embed.add_field(name = "Crazy:grimacing::dagger:", value = "Fun roles to spice up your boring classic games! Recommended for medium size parties(>6).", inline = False)
        embed.add_field(name = "Chaos:smiling_imp::fire:", value = "Absolute chaos where every role is in play. Recommended for big parties(>9).", inline = False)
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
                    try:
                        await supportChannel.send(embed = embed)
                    except:
                        pass
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
                    try:
                        await supportChannel.send(embed = embed)
                    except:
                        pass
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
        if memberList[0] != ctx.author and not ctx.author.guild_permissions.administrator:
            await channel.send("Boi, you ain't the party leader or the admin. Your party leader is {}.".format(memberList[0].name))
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
                if memberList.index(ctx.author) != 0 and not ctx.author.guild_permissions.administrator:
                    await channel.send("Boi, you ain't the party leader or the admin. Your party leader is {}.".format(memberList[0]))
                else:
                    
                    try:
                        self.checkServer(server)
                        sList = self.openJson("servers.json")
                        currentMode = sList[str(server.id)]["game mode"]
                        self.serverStatus[server.id]["setting"] = True
                        await channel.send(embed = discord.Embed(title = "Please wait. Setting game with mode: {}".format(currentMode), colour = discord.Colour.dark_gold()))
                        print ("--Setting game on '{}'".format(server.name))
                        

                        prepObj = prep.prepare(self.bot, self.mafiaPlayers[server.id], currentMode)
                        await prepObj.assignRoles()
                        # Finished settings roles

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
        for role in roleList.values():
            if role.user.name.lower() == name.lower():
                return role
        return None

    def findRoleObjName(self, roleList, rolename):
        for role in roleList.values():
            if role.name == rolename:
                return role
                

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
                if memberList[0] != ctx.author and not ctx.author.guild_permissions.administrator:
                    await channel.send("Boi, you ain't the party leader or the admin. The party leader is {}".format(memberList[0].name))
                    return

                try:
                    mFunctions = turn.Turns(self.bot)

                    self.serverStatus[server.id]["gameOn"] = True
                    embed = discord.Embed(title = "A game has started on {}.".format(server.name), description = "Group size: {}".format(len(currentP.keys())), colour = discord.Colour.dark_green())
                    embed.add_field(name = "Server id: ", value = "{}".format(server.id), inline = False)
                    embed.add_field(name = "Mode: ", value = self.getMode(server.id))
                    embed.set_thumbnail(url = server.icon_url)
                    try:
                        await supportChannel.send(embed = embed)
                    except:
                        pass
                    embed = self.makeEmbed("Everyone please navigate to the mafia text channel!")
                    embed.set_image(url = "https://cdn.aarp.net/content/dam/aarp/money/budgeting_savings/2016/06/1140-navigating-medicare-mistakes.imgcache.revdd9dcfe7710d97681da985118546c1a9.jpg")
                    await channel.send(embed = embed)
                    
                    channel = self.serverStatus[server.id]["mafiaChannel"]
                    overwrite = discord.PermissionOverwrite(send_messages = False, read_messages = True)

                    for player in currentP.keys():
                        await channel.set_permissions(player, overwrite=overwrite)
                        await channel.send(player.mention)


                    #intro
                    intro = discord.Embed(title = ":hand_splayed:Welcome to Mafia!", description = ":closed_book:If you haven't read the rules yet, please type m.game to view them in your dm!", colour = discord.Colour.dark_purple())
                    intro.add_field(name = ":exclamation: HEY LISTEN UP", value = ":anger:Please do not type in this chat unless instructed to do so. Admins please don't abuse your godly powers and talk when other people can't. Thank you.", inline = False)
                    intro.add_field(name = ":skull: To those who are dead: ", value = "Please do not talk. I know it's hard to grasp but dead people can't talk. Also no reactions, because, you know, dead people also can't react.", inline = False)
                    intro.add_field(name = ":eyes:Some important rules: ", value = ":no_entry_sign:Screen shots are not permitted and would only ruin the game. However you CAN claim roles to either coordinate among yourselves or trick other people. Just NO SCREENSHOTS.", inline = False)
                    intro.add_field(name = ":speaking_head:Some useful commands: ", value = "m.stop, m.reset, m.help.")
                    intro.set_footer(text = "Note: Parts of the game can be customized with m.custom *setting* *time*! To view current settings use m.settings.")
                    intro.set_image(url = "https://pre00.deviantart.net/5183/th/pre/i/2018/011/f/5/league_of_legends___mafia_miss_fortune_by_snatti89-dbznniv.jpg")
                    await channel.send(embed = intro)
                    

                    #messages mafias                    
                    mafiaList = []
                    mafiaCount = 0
                    mafiaBois = ["mafia", "godfather", "framer"]
                    for role in currentP.values():
                        if(role.name in mafiaBois):
                            mafiaList.append(role)
                            mafiaCount += 1
                    if mafiaCount > 1:
                        embed = discord.Embed(title = "Here are the mafias in this game:", colour = discord.Colour.dark_gold())
                        for role in mafiaList:
                            embed.add_field(name = "{}".format(role.user.name), value = "Role: {}".format(role.name), inline = False)
                        embed.set_footer(text = "Cooporate with your fellow mafias through dm to make strategies!")
                        for role in mafiaList:
                            await role.user.send(embed = embed)
                        await asyncio.sleep(4)
                    exeObj = self.findRoleObjName(currentP, "executioner")
                    exeTarget = None
                    if exeObj:
                        exeNonoList = ["executioner", "mafia", "framer", "godfather", "baiter", "dictator", "bomber"]
                        while True:
                            exeTarget = random.choice(list(currentP.values()))
                            if not exeTarget.name in exeNonoList: 
                                exeEmbed = discord.Embed(title = "Alright executioner. Your target is {}. Convince the town to lynch {} and you win. Ezpz.".format(exeTarget.user.name, exeTarget.user.name), description = "If your target is killed any other way you will become a Jester.", colour = discord.Colour.light_grey())
                                exeEmbed.set_thumbnail(url = exeTarget.user.avatar_url)
                                await exeObj.user.send(embed = exeEmbed)
                                break 
                    origFramer = self.findRoleObjName(currentP, "framer")

                    await asyncio.sleep(1)

                    await channel.send(embed = self.makeEmbed("Alright! Let the game begin!"))
                    await asyncio.sleep(1)
                    #big boi loop for game
                    night = 1
                    while True:
                        if self.serverStatus[server.id]['commandStop']:
                            await channel.send(embed = self.makeEmbed("Due to a request, I will end this game now."))
                            print("Requested stop on {}".format(server.name))
                            try:
                                await supportChannel.send(embed = discord.Embed(title = "A game has stopped on {}".format(server.name), description = "{}".format(server.id), colour = discord.Colour.dark_magenta()))
                            except:
                                pass
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
                        

                        for role in currentP.values():
                            if (role.alive):
                                temp.append(role.user.name.lower())
                            else:
                                tempDead.append(role.user.name.lower())

                        await mFunctions.muteAll(currentP, channel)

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

        
                        
                        
                        await asyncio.sleep(2)
                        embed = discord.Embed(title = "It is now night time, time to go to sleep...", description = "Don't panic, I muted all of you", colour = discord.Colour.blue())
                        embed.set_image(url = "https://www.nih.gov/sites/default/files/news-events/research-matters/2019/20190312-sleep.jpg")
                        await channel.send(embed = embed)
                        
                        gfObj = self.findRoleObjName(currentP, "godfather")
                        framerObj = self.findRoleObjName(currentP, "framer")
                        mafiaObj = self.findRoleObjName(currentP, "mafia")
                        if not gfObj.alive:
                            if mafiaObj and mafiaObj.alive:
                                tempGfObj = godfather.Godfather()
                                tempGfObj.user = mafiaObj.user
                                currentP[mafiaObj.user] = tempGfObj
                                tempGfObj.MAFIAPLAYER = None
                                await tempGfObj.user.send(embed = self.makeEmbed("Since the godfather is dead, YOU are now the godfather. GL lol."))
                            elif framerObj and framerObj.alive:
                                tempGfObj = godfather.Godfather()
                                tempGfObj.user = framerObj.user
                                currentP[framerObj.user] = tempGfObj
                                tempGfObj.MAFIAPLAYER = None
                                await tempGfObj.user.send(embed = self.makeEmbed("Since the godfather is dead, YOU are now the godfather. GL lol."))
                        await asyncio.sleep(3)
                        currentPCopy = currentP.copy()
                        

                        noneDmRoles = ["executioner", "jester", "mafia", "baiter", "villager", "dictator"]
                        
                        dmAnnounce = discord.Embed(title = "Everyone with a useful role please check your dm!", description = "Jk all roles are useful...", colour = discord.Colour.blue())
                        dmAnnounce.set_image(url = "https://miro.medium.com/max/1080/1*We3cuit-POpN4Sa-GU-9lw.jpeg")
                        await channel.send(embed = dmAnnounce)


                        #Send prompts
                        for role in currentP.values():
                            if role.alive and not role.name.lower() in noneDmRoles:
                                await role.sendPrompt(currentP, str(dmTime))
                        
                        await asyncio.sleep(dmTime)

                        #Store prompt answers
                        for role in currentP.values():
                            if role.alive and not role.name.lower() in noneDmRoles:
                                await role.getTarget()
                        
                        storyList = []
                        #Executes each role's actions and if perform() is successful returns an embed
                        priorityRoles = ["distractor", "bomber", "godfather", "doctor", "framer"]
                        for pRole in priorityRoles:
                            tempRole = self.findRoleObjName(currentP, pRole)
                            if tempRole and (tempRole.alive or pRole == "doctor"):
                                tempEmbed = await tempRole.perform(currentP)
                                if tempEmbed:
                                    storyList.append(tempEmbed)
                                
                        
                        for role in currentP.values():
                            if not role.name in priorityRoles and role.alive and role.name != "mafia":
                                tempEmbed = await role.perform(currentP)
                                if tempEmbed:
                                    storyList.append(tempEmbed)
                    


                        
                        #Storytime
                        await channel.send(embed = self.makeEmbed("Alright everybody get your ass back here. It's storytime."))
                        
                        await asyncio.sleep(3)

                        for embed in storyList:
                            await channel.send(embed = embed)
                            await asyncio.sleep(5)
                        
                        bomberObj = self.findRoleObjName(currentP, "bomber")
                        if bomberObj and not bomberObj.alive and not bomberObj.alreadyExploded:
                            try:
                                await channel.send(embed = await bomberObj.onDeath(currentP))
                                await asyncio.sleep(3)
                            except:
                                pass

                        deadList = discord.Embed(title = "Currently ded: ", colour = discord.Colour.red())
                        deadList.set_thumbnail(url = "https://i.pinimg.com/474x/e3/1e/1f/e31e1f9ea2322decd31dfbb8874ee551.jpg")
                        deadCount = 0
                        for role in currentP.values():
                            if not role.alive:
                                deadCount += 1
                                deadList.add_field(name = role.user.name, value = role.name)
                        if deadCount > 0:
                            await channel.send(embed = deadList)
                                
                        check = self.checkWin(mafiaCount, server.id, currentP)

                        print(check)
                        await asyncio.sleep(2)
                        if check == "bomber":
                            await mFunctions.unMuteAll(currentP)
                            await self.updateWin(currentP, server.id, "bomber")
                            bombObj = self.findRoleObjName(currentP.values(), "bomber")
                            embed = discord.Embed(title = "Everyone died except the bomber. The bomber wins!", description = bombObj.user.name + " is the bomber!", colour = discord.Colour.dark_grey())
                            embed.set_thumbnail(url = "https://www.mobafire.com/images/avatars/ziggs-classic.png")
                            break
                        elif check == "baiter":
                            await mFunctions.unMuteAll(currentP)
                            await self.updateWin(currentP, server.id, "baiter")
                            embed = discord.Embed(title = "The baiter wins!", colour = discord.Colour.dark_grey())  
                            break
                        elif check == "no wins":
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
                        elif check == "none": # lynch time bois
                            exePlayer = self.findRoleObjName(currentP, "executioner")
                            #checks executioner
                            if exePlayer:
                                if not exeTarget.alive and exePlayer.alive:
                                    embed = discord.Embed(title = "You are now the Jester. Your win condition is to get the town to lynch you.", colour = discord.Colour.teal())
                                    embed.set_image(url = "https://runes.lol/image/generated/championtiles/Shaco.jpg")
                                    await exePlayer.user.send( embed = embed)
                                    jesterObj = jester.Jester()
                                    jesterObj.user = exePlayer.user
                                    currentP[exePlayer.user]= jesterObj
                            
                            
                            embed = discord.Embed(title = "Now I'll give you guys {} seconds to talk. ".format(talkTime), description = "Want to claim a role? Accuse someone? Confess? Do that now!", colour = discord.Colour.magenta())
                            aliveCount = 0
                            for role in currentP.values():
                                if role.alive:
                                    aliveCount += 1
                                    embed.add_field(name = role.user.name, value = "Alive!")
                            embed.set_image(url = "https://blog.oup.com/wp-content/uploads/2016/11/Witchcraft_at_Salem_Village2.jpg")
                            await channel.send(embed = embed)

                            await mFunctions.muteDead(currentP, channel)

                            await mFunctions.muteDead(currentP, channel)
                            await asyncio.sleep(talkTime)


                            minVote = int(aliveCount/1.5)
                            #special occasion cuz I'm too lazy to math
                            if aliveCount == 4:
                                minVote = 3


                            if aliveCount < 4:
                                minVote = 2


                            embed = discord.Embed(title = "Alright! It's time to vote! Vote for a person by reacting to the message associated with your target. (A person must have a min of {} votes to be lynched)".format(str(minVote)), description = "Note: If you try to be sneaky and vote more than once your vote will only count once to the first message the bot reads.", colour = discord.Colour.green())
                            embed.set_footer(text = "You have {} seconds to vote.".format(voteTime))
                            await channel.send(embed = embed)

                            mayorObj = self.findRoleObjName(currentP, "mayor")
                            #Gets the lynched target
                            lynchPerson = await mFunctions.vote(currentP, channel, voteTime, mayorObj, minVote)


                            await asyncio.sleep(3)


                            if lynchPerson != None:
                                embed = discord.Embed(title = "{} has been hanged by the village. Press f to pay respect.".format(lynchPerson.name), colour = discord.Colour.red())
                                embed.set_image(url = "https://cdn.shopify.com/s/files/1/0895/0864/products/42-47714084_1024x1024.jpeg?v=1451772538")
                                await channel.send(embed = embed)
                                await asyncio.sleep(2)
                                for role in currentP.values():
                                    if (role.user.name.lower() == lynchPerson.name.lower()):
                                        await role.die()
                                        try:
                                            await channel.send(embed = await role.onDeath(currentP))
                                        except:
                                            pass
                                        await mFunctions.muteDead(currentP, channel)
                                        await channel.send(embed = self.makeEmbed("{}'s role was {}".format(role.user.name, role.name)))
                                        break
                            else:
                                await channel.send(embed = self.makeEmbed("No one was hanged."))
                        
                        
                              
                                
                            


                            check = self.checkWin(mafiaCount, server.id, currentP)
                            
                            
                            #checks lynched target for jester and executioner role
                            jesterWins = False
                            exeWins = False
                            if lynchPerson != None:
                                for role in currentP.values():
                                    if role.user.name.lower() == lynchPerson.name.lower() and role.name == "jester":
                                        jesterWins = True
                                    elif exeTarget != None and exeTarget.user.name.lower() == lynchPerson.name.lower() and role.name == "executioner" and role.alive:
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
                                embed.set_thumbnail(url = "https://en.meming.world/images/en/thumb/2/2c/Surprised_Pikachu_HD.jpg/300px-Surprised_Pikachu_HD.jpg")
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


                            #Resets all role obj's victim variable
                            for role in currentP.values():
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
                        baiterObj = self.findRoleObjName(currentP, "baiter")
                        if check != "baiter" and baiterObj and baiterObj.killCount >= 3:
                            baiterEmbed = discord.Embed(title = "The baiter is " + baiterObj.user.name+ "!", description = "The baiter has a kill count of " + str(baiterObj.killCount) + ", so " + baiterObj.user.name + " also wins!")
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
                    try:
                        await supportChannel.send(embed = embed)
                    except:
                        pass
                    for role in currentP.values():
                        role = None

                        
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
                    
                    try:
                        await supportChannel.send( embed = embed)
                    except:
                        pass
                        
                    self.serverStatus[server.id]["ready"] = False
                    self.serverStatus[server.id]["gameOn"] = False
                    self.serverStatus[server.id]["commandStop"] = False
                    self.serverStatus[server.id]["setting"] = False
                    await mFunctions.unMuteAll(currentP)

                    try:
                        await mafiaChannel.delete() 
                    except Exception as e:
                        print(e)
                    embed = discord.Embed(title = "Resetting...", colour = discord.Colour.red())
                    #await channel.send(embed = embed)       
    
        
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
    def checkWin(self, mafiaCount, id, currentList):
        aliveCount = 0
        aliveList = []
        threatCount = 0
        mafiaCount = 0
        hasBaiter = False
        baiterWins = False
        for role in currentList.values():
            if role.alive:
                aliveCount+=1
                aliveList.append(role)
                if role.side == "mafia" or role.name == "bomber":
                    threatCount += 1
                if role.side == "mafia":
                    mafiaCount += 1
                if role.name == "baiter":
                    hasBaiter = True
                    if role.killCount >= 3:
                        baiterWins = True
        
        if threatCount == 0:
            return "villager"
        
        if mafiaCount > aliveCount-mafiaCount or mafiaCount == aliveCount-mafiaCount:
            return "mafia"
        
        if aliveCount == 0 or (aliveCount == 1 and aliveList[0].name == "bomber"):
            return "bomber"
        
        if aliveCount < 2 and hasBaiter and baiterWins:
            if baiterWins:
                return "baiter"
            else:
                return "no wins"
        
        return "none"
        '''
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
        '''

    def randInt(self, chance, whole):
        result = random.randint(chance, whole)
        if result <= chance:
            return True
        else:
            return False


    def displayAllR(self, embed, mafiaList, framer):
        embed.set_image(url = "https://wallpapers.wallhaven.cc/wallpapers/full/wallhaven-323086.png")
        for role in mafiaList.values():
            player = role.user
            cog = self.bot.get_cog("Points")
            title = cog.getCTitle(player.id)
            if title == "" or title == " ":
                nameThing = player.name
            else:
                nameThing = player.name + '\n"' + title+'"'
            if framer and player.name.lower() == framer.user.name.lower():
                embed.add_field(name = nameThing, value = "framer", inline = True)
            else:
                embed.add_field(name =nameThing, value = "{}".format(role.name), inline = True)


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
        
        for role in mafiaList.values():
            self.checkFile(role.user.id)
            side = self.checkSide(role.name)
            tempUser = self.findUser(role.user.id)
            if side == winner:
                tempUser.wins += 1
                reward = random.randint(10, 30)
                tempUser.points += reward
                embed = discord.Embed(title = "You have received {} Mafia points!:moneybag:".format(str(reward)), description = "Spend mafia points at the store! Check your account with m.record @user!", colour = discord.Colour.green())
                embed.set_image(url = "https://images2.minutemediacdn.com/image/upload/c_fill,g_auto,h_1248,w_2220/f_auto,q_auto,w_1100/v1555271785/shape/mentalfloss/500940-Amazon_0.png")
                await role.user.send(embed = embed)
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
        path = self.userDir + "\\"
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