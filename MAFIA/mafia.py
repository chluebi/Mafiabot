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

class mafia:
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
    @commands.command(pass_context = True)
    async def custom(self, ctx, var, number):
        server = ctx.message.server
        if server == None:
            await self.bot.send_message(ctx.message.channel, embed = self.makeEmbed("This ain't a discord server."))
        
        else:
            self.checkServer(server)
            if not var in self.serverStatus[server.id].keys() or var == "commandStop" or var == "gameOn" or var == "ready":
                await self.bot.send_message(ctx.message.channel, embed = self.makeEmbed("That's not something I can change."))
            else:
                if int(number) > 120:
                    await self.bot.send_message(ctx.message.channel, embed = self.makeEmbed("Sorry. The max time is 120 seconds."))
                elif int(number) < 15:
                    await self.bot.send_message(ctx.message.channel, embed = self.makeEmbed("Sorry. The min time is 15 seconds."))
                else:
                    try:
                        original = self.serverStatus[server.id][var]
                        self.serverStatus[server.id][var] = int(number)
                        await self.bot.send_message(ctx.message.channel, embed = self.makeEmbed("Got it. {} is now {} seconds".format(var, number)))
                        await self.bot.send_message(discord.Object(550923896858214446),"{} set to {} on {}".format(var, number, server.name))
                    except:
                        await self.bot.send_message(ctx.message.channel, embed = self.makeEmbed("Please enter a valid input."))
                        self.serverStatus[server.id][var] = original

    @commands.command(pass_context = True)
    async def setting(self, ctx):
        server = ctx.message.server
        if server == None:
            await self.bot.send_message(ctx.message.channel, embed = self.makeEmbed("This ain't a discord server."))
        
        else:
            self.checkServer(server)
            embed = discord.Embed(title = "Current settings on {}".format(server.name), description = "Customizable settings for Mafiabot!(m.custom (setting) (time))", colour = discord.Colour.blue())
            for setting in self.serverStatus[server.id]:
                if setting != "commandStop" and setting != "gameOn" and setting != "ready":
                    embed.add_field(name = setting, value = "{} seconds".format(self.serverStatus[server.id][setting]))
            embed.set_image(url = "https://pbs.twimg.com/media/DNgdaynV4AAEoQ7.jpg")
            await self.bot.send_message(ctx.message.channel, embed = embed)
    @commands.command(pass_context = True)
    async def stop(self, ctx):
      server = ctx.message.server
      if server == None:
            await self.bot.send_message(ctx.message.channel, embed = self.makeEmbed("This ain't a discord server."))
      elif not server.id in self.serverStatus:
        await self.bot.send_message(ctx.message.channel, embed = self.makeEmbed("You don't even have a game going on."))
      elif self.serverStatus[server.id]['commandStop'] == True:
        await self.bot.send_message(ctx.message.channel, embed = self.makeEmbed("There's already a request to stop the game."))
      elif self.serverStatus[server.id]["gameOn"] == False:
        await self.bot.send_message(ctx.message.channel, embed = self.makeEmbed("There's no game to stop lol."))
      else:
        self.serverStatus[server.id]['commandStop'] = True  
        await self.bot.send_message(ctx.message.channel, embed = self.makeEmbed("Got it. The current game will stop after this round ends."))

    @commands.command(pass_context = True)
    async def reset(self, ctx):
        server = ctx.message.server
        if server == None:
            await self.bot.send_message(ctx.message.channel, embed = self.makeEmbed("This ain't a discord server."))
        elif ctx.message.author.server_permissions.administrator == True:
            self.checkServer(server)
            await self.bot.send_message(ctx.message.channel, embed = self.makeEmbed("IMPORTANT: You are resetting the bot's current game status on this server. Everything will reset except players' progresses. If you have any current games playing right now it can really mess everything up. Do you wish to proceed?(y/n)"))
            answer = await self.bot.wait_for_message(author = ctx.message.author, channel = ctx.message.channel)
            if answer.content.lower() == "y" or answer.content.lower() == "yes":
                #deletes mafia text channel
                mafiaChannel = None
                for item in server.channels:
                    if item.name == 'mafia':
                        mafiaChannel = item
                try:
                    await self.bot.delete_channel(mafiaChannel)  
                except:
                    print ("duh")
                #reset variables      
                self.serverStatus[server.id]['commandStop'] = False
                self.serverStatus[server.id]["ready"] = False
                self.serverStatus[server.id]["gameOn"] = False
            
                await self.bot.send_message(ctx.message.channel, embed = self.makeEmbed("Reset complete. All conditions are cleared."))
                print ("Reset on {}".format(server.name))
                await self.bot.send_message(discord.Object(550923896858214446),"Reset on {}".format(server.name))
            else:
                await self.bot.send_message(ctx.message.channel, embed = self.makeEmbed("Ok. No reset."))
        elif ctx.message.author.server_permissions.administrator == False:
            await self.bot.send_message(ctx.message.channel, embed = self.makeEmbed("You don't have permission."))

    @commands.command(pass_context = True)
    async def clear(self, ctx):
      server = ctx.message.server
      if server is None:
        await self.bot.send_message(ctx.message.channel, embed = self.makeEmbed("This ain't a discord server."))
      elif not server.id in self.mafiaPlayers.keys():
        await self.bot.send_message(ctx.message.channel, embed = self.makeEmbed("There's no party to clear lol."))
      else:
          if self.serverStatus[server.id]["gameOn"] == True or self.serverStatus["ready" == True]:
              await self.bot.send_message(ctx.message.channel, embed = self.makeEmbed("Can't clear party right now. There is a game going on!"))
          else:

            await self.bot.send_message(discord.Object(550923896858214446),"Party cleared on {}".format(server.name))
            self.mafiaPlayers[server.id] = {}
            await self.bot.send_message(ctx.message.channel, embed = self.makeEmbed("The current party is now cleared."))

        
    @commands.command(pass_context = True)
    async def join(self, ctx):
        server = ctx.message.server
        if server is None:
            await self.bot.send_message(ctx.message.channel, embed = self.makeEmbed("This ain't a discord server."))
            
        else:
            self.checkServer(server)
            self.checkFile(ctx.message.author.id, server.id)
            if self.serverStatus[server.id]["gameOn"] == True:
                await self.bot.send_message(ctx.message.channel, embed = self.makeEmbed("You cannot currently join right now because there is a game going on."))
            elif self.serverStatus[server.id]["ready"] == True:
                await self.bot.send_message(ctx.message.channel, embed = self.makeEmbed("The is a game currently being set up!"))
            
            elif len(self.mafiaPlayers[server.id]) == self.maxPlayers:
                await self.bot.send_message(ctx.message.channel, embed = self.makeEmbed("Sorry. The max number of players is {}.".format(self.maxPlayers)))
            else:
                if not ctx.message.author in self.mafiaPlayers[server.id].keys():
                    print("{} joined group on {}--{}".format(ctx.message.author.name, server, len(server.members)))
                    embed = discord.Embed(title = "{} joined on {}".format(ctx.message.author.name, server.name), description = "Server size: {}".format(len(server.members)), colour = discord.Colour.dark_blue())
                    await self.bot.send_message(discord.Object(550923896858214446), embed = embed)
                    self.mafiaPlayers[server.id][ctx.message.author] = "" # add author to dictionary

                    await self.bot.send_message(ctx.message.channel, embed = self.makeEmbed("You have been added to the list."))
                    embed = discord.Embed(title = "Mafia Party:".format(), description = "IMPORTANT: Make sure everything is set up correctly. To view all required permissions use m.perms.", colour = discord.Colour.purple())
                    embed.set_thumbnail(url= "http://www.lol-wallpapers.com/wp-content/uploads/2018/08/Mafia-Braum-Miss-Fortune-by-wandakun-HD-Wallpaper-Background-Fan-Art-Artwork-League-of-Legends-lol.jpg")
                    for player in self.mafiaPlayers[server.id].keys():
                        embed.add_field(name = "Player:", value = "{}".format(player.name), inline = True)
                    embed.set_footer(text = "When you're ready type m.setup to start! (Helpful commands: m.help, m.clear and m.stop)")
                    await self.bot.send_message(ctx.message.channel, embed = embed)
                else:
                    await self.bot.send_message(ctx.message.channel, embed = self.makeEmbed("You are already in the party."))

    @commands.command(pass_context = True)
    async def leave(self, ctx):
        server = ctx.message.server
        if server is None:
            await self.bot.send_message(ctx.message.channel, embed = self.makeEmbed("This ain't a discord server."))
        else:
            self.checkServer(server)
            if self.serverStatus[server.id]["gameOn"] == True or self.serverStatus[server.id]["ready"] == True:
                await self.bot.send_message(ctx.message.channel, embed = self.makeEmbed("You cannot currently leave right now because there is a game going on."))
            else:
                
                if not ctx.message.author in self.mafiaPlayers[server.id].keys():
                    await self.bot.send_message(ctx.message.channel, embed = self.makeEmbed("You are not in the party."))
                else:
                    embed = discord.Embed(title = "{} left on {}".format(ctx.message.author.name, server.name), description = "{}".format(len(server.members)), colour = discord.Colour.dark_magenta())
                    await self.bot.send_message(discord.Object(550923896858214446), embed = embed)
                    print("{} left group on {}".format(ctx.message.author.name, server.name))
                    self.mafiaPlayers[server.id].pop(ctx.message.author, None)
                    await self.bot.send_message(ctx.message.channel, embed = self.makeEmbed("{} left the party.".format(ctx.message.author.name)))


    @commands.command(pass_context = True)
    async def party(self, ctx):
        server = ctx.message.server
        if server is None:
            await self.bot.send_message(ctx.message.channel, embed = self.makeEmbed("This ain't a discord server."))
        else:
            self.checkServer(server)
            embed = discord.Embed(title = "Mafia Party:".format(), description = "IMPORTANT: Make sure everything is set up correctly. To view all required permissions use m.perms.", colour = discord.Colour.purple())
            embed.set_thumbnail(url= "http://www.lol-wallpapers.com/wp-content/uploads/2018/08/Mafia-Braum-Miss-Fortune-by-wandakun-HD-Wallpaper-Background-Fan-Art-Artwork-League-of-Legends-lol.jpg")
            for player in self.mafiaPlayers[server.id].keys():
                embed.add_field(name = "Player:", value = "{}".format(player.name), inline = True)
            embed.set_footer(text = "When you're ready type m.setup to start! (Type m.help for commands!)")
            await self.bot.send_message(ctx.message.channel, embed = embed)



    @commands.command(pass_context = True)
    async def setup(self, ctx):
        server = ctx.message.server
        if server is None:
            await self.bot.send_message(ctx.message.channel, embed = self.makeEmbed("This ain't a discord server."))
        else:
            self.checkServer(server)
            
            if self.serverStatus[server.id]["ready"] == True:
                embed = discord.Embed(title = "You have already set up. Type m.start to begin.")
                await self.bot.send_message(ctx.message.channel, embed = embed)
            
            elif self.serverStatus[server.id]["gameOn"] == True:
                await self.bot.send_message(ctx.message.channel, embed = self.makeEmbed("There is already a game playing."))

            elif len(self.mafiaPlayers[server.id].keys()) < 5:
                embed = discord.Embed(title = "Sorry. You need at least 5 people to play the game. You only have {} players.".format(len(self.mafiaPlayers[server.id].keys())), colour = discord.Colour.red())
                await self.bot.send_message(ctx.message.channel, embed = embed)
            elif len(self.mafiaPlayers[server.id].keys())> self.maxPlayers:
                await self.bot.send_message(ctx.message.channel, embed = self.makeEmbed("Sorry. The max number of people is {}.".format(self.maxPlayers)))

            else:
                try:
                    print ("--Setting game on '{}'".format(server.name))
                    self.serverStatus[server.id]["ready"] = True

                    prepObj = prep.prepare(self.bot, self.mafiaPlayers[server.id])
                    prepObj.assignRoles()
                    # Finished settings roles

                    # Inform player of roles
                    for player, data in self.mafiaPlayers[server.id].items():
                        if(data.roleName == 'mafia'):
                            embed = discord.Embed(title = "You are the Mafia. Your job is to kill everyone. Pretty simple.", colour = discord.Colour.red())

                            embed.set_thumbnail(url = "https://images2.minutemediacdn.com/image/upload/c_scale,w_912,h_516,c_fill,g_auto/shape/cover/sport/5b73276e8f1752549a000001.jpeg")
                            await self.bot.send_message(player, embed = embed)
                        elif(data.roleName == 'doctor'):
                            embed = discord.Embed(title = "You are the Doctor. Your job is to save people. But you can't save the same person twice in a row.", colour = discord.Colour.blue())
                            embed.set_thumbnail(url = "https://res.cloudinary.com/teepublic/image/private/s--NyIx9Nop--/t_Preview/b_rgb:c62b29,c_limit,f_jpg,h_630,q_90,w_630/v1469022975/production/designs/592798_1.jpg")
                            await self.bot.send_message(player, embed = embed)
                        elif(data.roleName == 'detective'):
                            embed = discord.Embed(title = "You are the Detective. Your job is to find the Mafia.", colour = discord.Colour.orange())
                            embed.set_thumbnail(url = "https://78.media.tumblr.com/9681fb542682771069c3864dcbae7ef8/tumblr_o1mh5vUWe91r0sasuo1_400.gif")
                            await self.bot.send_message(player, embed = embed)
                        elif(data.roleName == 'vigilante'):
                            embed = discord.Embed(title = "You are the Vigilante. For five years, You were stranded on an island with only one goal: survive... blah blah blah. Just don't shoot the wrong person or you'll commit suicide.", colour = discord.Colour.green())
                            embed.set_image(url = "https://i2.wp.com/s3-us-west-1.amazonaws.com/dcn-wp/wp-content/uploads/2017/12/31015237/Arrow-CW.png?resize=740%2C431&ssl=1")
                            await self.bot.send_message(player, embed = embed)
                        elif (data.roleName == 'jester'):
                            embed = discord.Embed(title = "You are the Jester. Your win condition is to get the town to lynch you.", colour = discord.Colour.teal())
                            embed.set_thumbnail(url = "https://runes.lol/image/generated/championtiles/Shaco.jpg")
                            await self.bot.send_message(player, embed = embed)
                        else:
                            embed = discord.Embed(title = "You are just a normal innocent villager who might get accused for crimes you didn't commit ¯\_(ツ)_/¯ ", colour = discord.Colour.dark_gold())
                            embed.set_thumbnail(url = "https://www.ssbwiki.com/images/thumb/a/ac/Villager_SSBU.png/250px-Villager_SSBU.png")
                            await self.bot.send_message(player, embed = embed)

                    everyone_perms = discord.PermissionOverwrite(send_messages=False)
                    my_perms = discord.PermissionOverwrite(send_messages=True)

                    everyone = discord.ChannelPermissions(target=server.default_role, overwrite=everyone_perms)
                    mine = discord.ChannelPermissions(target=server.me, overwrite=my_perms)
                    for player in self.mafiaPlayers[server.id].keys():
                        await self.bot.server_voice_state(player, mute = False)
                    await self.bot.create_channel(server, "mafia", everyone, mine)
                    self.serverStatus[server.id]["ready"] = True
                    
                except discord.Forbidden:
                    print("Forbidden error. Resetting...")
                    self.serverStatus[server.id]["ready"] = False
                    embed = discord.Embed(title = "Error. Missing required permissions. Please check all of my required permissions with m.perms and try again.", colour = discord.Colour.red())

                    await self.bot.send_message(ctx.message.channel, embed = embed)
                else:
                    embed = discord.Embed(title = "Everything's ready! Everyone join a voice chat and type m.start to start the game! Make sure you know how the game works! (Info can be found with m.game)", colour = discord.Colour.green())
                    embed.set_thumbnail(url = "https://pbs.twimg.com/media/DWVbyz5WsAA93-y.png")
                    await self.bot.send_message(ctx.message.channel, embed = self.makeEmbed("Everything's ready! Everyone join a voice chat and type m.start to start the game! Make sure you know how the game works! (Info can be found with m.game)"))

    
    @commands.command(pass_context = True)
    async def start(self, ctx):
        server = ctx.message.server
        if server is None:
            await self.bot.send_message(ctx.message.channel, embed = self.makeEmbed("This ain't a discord server."))
        
        self.checkServer(server)
        currentP = self.mafiaPlayers[server.id]
        
        if self.serverStatus[server.id]["ready"] == False:
            await self.bot.send_message(ctx.message.channel, embed = self.makeEmbed("You didn't set up yet. Type m.setup first."))
        
        elif self.serverStatus[server.id]["gameOn"] == True:
            await self.bot.send_message(ctx.message.channel, embed = self.makeEmbed("There is already a game going on!"))
        else:
            
            print("A game has started on {}".format(server.name))
            try:
                embed = discord.Embed(title = "A game has started on {}.".format(server.name), description = "Group size: {}".format(len(currentP.keys())), colour = discord.Colour.dark_green())
                embed.add_field(name = "Server id: ", value = "{}".format(server.id), inline = False)
                
                await self.bot.send_message(discord.Object(id='534564704937574400'), embed = embed)
                await self.bot.send_message(ctx.message.channel, embed = self.makeEmbed("Everyone please navigate to the mafia text channel!"))
                channel = self.findChannel(server)
                pastHeal = None
                self.serverStatus[server.id]["gameOn"] = True
                for player in currentP.keys():
                    await self.bot.send_message(channel, player.mention)

                #intro
                intro = discord.Embed(title = "Welcome to Mafia!", description = "If you haven't read the rules yet, please type m.game to view them in your dm!", colour = discord.Colour.dark_purple())
                intro.add_field(name = "Important!", value = "Please do not type in this chat unless it is the voting phase. Please keep all conversations to the voice chat or other text channels. Thank you.")
                intro.add_field(name = "Some useful commands: ", value = "m.stop, m.reset, m.help.")
                intro.set_footer(text = "Note: Parts of the game can be customized with m.custom *setting* *time*! To view current settings use m.settings.")
                intro.set_image(url = "https://pre00.deviantart.net/5183/th/pre/i/2018/011/f/5/league_of_legends___mafia_miss_fortune_by_snatti89-dbznniv.jpg")
                await self.bot.send_message(channel, embed = intro)
                await asyncio.sleep(5)

                #messages mafias
                await self.bot.send_message(channel, embed = self.makeEmbed("Alright! Let the game begin!"))
                await asyncio.sleep(1)
                mafiaList = []
                mafiaCount = 0
                for player, data in currentP.items():
                    if(data.roleName == 'mafia'):
                        mafiaList.append(player)
                        mafiaCount += 1
                if mafiaCount > 1:
                    embed = discord.Embed(title = "Here are the mafias in this game:", colour = discord.Colour.dark_gold())
                    for item in mafiaList:
                        embed.add_field(name = "{}".format(item.name), value = "I'm a mafia!", inline = False)
                    embed.set_footer(text = "Cooporate with your fellow mafias through dm to make strategies!")
                    for item in mafiaList:
                        await self.bot.send_message(item, embed = embed)
                    await asyncio.sleep(4)

                #big boi loop for game
                while True:
                    if self.serverStatus[server.id]['commandStop'] == True:
                        await self.bot.send_message(channel, embed = self.makeEmbed("Due to the admin's request, I will end this game now."))
                        print("Requested stop on {}".format(server.name))
                        
                        await asyncio.sleep(5)
                        await self.bot.delete_channel(channel)
                        break
                    dmTime = self.serverStatus[server.id]["dmTime"]
                    voteTime = self.serverStatus[server.id]["voteTime"]
                    talkTime = self.serverStatus[server.id]["talkTime"]
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
                    deadEmbed = self.makeEmbed("Currently Dead:")
                    for player in temp:
                        aliveEmbed.add_field(name = "{}".format(player), value = "Alive", inline = False)
                    for player in tempDead:
                        deadEmbed.add_field(name = "{}".format(player), value = "Dead", inline = False)
                    await self.bot.send_message(channel, embed = aliveEmbed)
                    await self.bot.send_message(channel, embed = deadEmbed)

                    await asyncio.sleep(2)
                    embed = self.makeEmbed("It is now night time, time to go to sleep...")
                    await self.bot.send_message(channel, embed = embed)
                    for player in currentP.keys():
                        await self.bot.server_voice_state(player, mute = True)
                    await asyncio.sleep(3)
                    await self.bot.send_message(channel, embed = self.makeEmbed("Mafias please check your dm."))


                    #Mafia turn
                    
                    mafiaNames = []
                    mafias = []
                    for player, data in currentP.items():
                        if data.roleName == "mafia" and data.alive == True:
                            mafiaNames.append(player.name.lower())
                            mafias.append(player)
                    
                    isSame = False
                    voteTurn = 0
                    while isSame == False:
                        if voteTurn != 0:
                            await self.bot.send_message(player, embed = self.makeEmbed("The vote for the victim is not unanimous. Please coordinate among yourselves through dm and decide on a victim."))
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
                                await self.bot.send_message(player, embed = other)
                            
                            embed = self.makeEmbed("Targets:")
                            embed.add_field(name = "Who is your target?(Votes must be unanimous)", value = "Just type the name. Be sure to include any numbers and spaces. You have {} seconds to answer.".format(dmTime), inline = False)
                            for item in tempM:
                                embed.add_field(name = "{}".format(item), value = "Kill me!", inline = True)
                            embed.set_image(url = "https://www.mobafire.com/images/champion/skins/landscape/graves-mafia.jpg")
                            await self.bot.send_message(player, embed = embed)

                            answer = await self.bot.wait_for_message(author = player, timeout = dmTime)
                            #take mafia input
                            while True:
                                if answer == None:
                                    await self.bot.send_message(player, embed = self.makeEmbed("You ran out of time."))
                                    break
                                elif answer.content.lower() in tempM:
                                    mafiaKillVote.append(answer.content.lower())
                                    await self.bot.send_message(player, embed = self.makeEmbed("Gotcha. Please wait."))
                                    break
                                else:
                                    await self.bot.send_message(player, embed = self.makeEmbed("Error. Please check your spelling. Be sure to include any spaces, and numbers!"))
                                    answer = await self.bot.wait_for_message(author = player)
                        if mafiaKillVote:
                            kill = mafiaKillVote[0]
                            isSame = True
                            for item in mafiaKillVote:
                                if item != kill:
                                    isSame = False
                                    break
                        else:
                            kill = None
                            break
                        voteTurn += 1
                    if kill != None:
                        embed = self.makeEmbed("Your target is {}".format(kill))
                        for player in mafias:
                            await self.bot.send_message(player, embed = embed)
                    victim = kill

                    
                    
                    #Doctor turn
                    
                    for player, data in currentP.items():
                        if(data.roleName == 'doctor') and data.alive == True:
                            doctorUser = player
                            doctorAlive = True

                    # Only if doc is alive
                    if doctorAlive == True:
                        await self.bot.send_message(channel, embed = self.makeEmbed("Doctor please check your dm."))
                        embed = discord.Embed(title = "Targets", value = "Who do you want to save? If your target has some weird name just copy and paste them.(30s remaining)", colour = discord.Colour.purple())
                        embed.set_footer(text = "You cannot heal the same person twice in a row")
                        tempD = []
                        for stuff in temp:
                            if stuff.lower() != pastHeal:
                                tempD.append(stuff)
                        for item in tempD:
                            embed.add_field(name = "{}".format(item), value = "Save me!", inline = False)
                            
                        embed.set_image(url = "https://vignette.wikia.nocookie.net/leagueoflegends/images/f/f7/Akali_NurseSkin_old.jpg/revision/latest?cb=20120609043410")
                        await self.bot.send_message(doctorUser, embed = embed)  
                        
                        answer = await self.bot.wait_for_message(author = doctorUser, timeout = dmTime)
                        while True:
                                if answer == None:
                                    await self.bot.send_message(doctorUser, embed = self.makeEmbed("You ran out of time."))
                                    break
                                elif answer.content.lower() == pastHeal:
                                    await self.bot.send_message(doctorUser, embed = self.makeEmbed("You cannot heal the same person twice in a row!"))
                                    answer = await self.bot.wait_for_message(author = doctorUser)
                                elif answer.content.lower() in tempD:
                                    healVictim = answer.content.lower()
                                    pastHeal = answer.content.lower()
                                    await self.bot.send_message(doctorUser, embed = self.makeEmbed("Gotcha. You may now return to the mafia channel."))
                                    await self.bot.send_message(channel, embed = self.makeEmbed("Got it Doctor."))
                                    break
                                else:
                                    await self.bot.send_message(doctorUser, embed = self.makeEmbed("Error. Please check your spelling. Be sure to include any spaces and numbers!"))
                                    answer = await self.bot.wait_for_message(author = doctorUser)
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
                                    await self.bot.send_message(vigilanteUser, embed = embed)
                    if vigilanteAlive == True:
                        #await self.bot.send_message(channel, embed = self.makeEmbed("Vigilante please check your dm."))
                        embed = discord.Embed(title = "Targets", value = "Who do you want to shoot? (30 seconds remaining)", colour = discord.Colour.dark_green())
                        embed.set_footer(text = "Note: If you shoot the wrong person you WILL commit suicide.")
                        tempV = []
                        for player in temp:
                            if player.lower() != vigilanteUser.name.lower():
                                tempV.append(player)
                                embed.add_field(name = "{}".format(player), value = "Shoot me!", inline = False)
                        embed.add_field(name = "Don't shoot anyone tonight:", value = "Type none (Or just wait for the timer to run out.)", inline = False)
                        embed.set_image(url = "https://pmcdeadline2.files.wordpress.com/2018/03/arrow.png?w=446&h=299&crop=1")
                        await self.bot.send_message(vigilanteUser, embed = embed)

                        answer = await self.bot.wait_for_message(author = vigilanteUser, timeout = dmTime)
                        while True:
                                if answer == None:
                                    await self.bot.send_message(vigilanteUser, embed = self.makeEmbed("Time's up. You didn't shoot anyone."))
                                    break
                                elif answer.content.lower() == "none":
                                    await self.bot.send_message(vigilanteUser, embed = self.makeEmbed("Alright. You're not shooting anyone tonight."))
                                    break
                                elif answer.content.lower() in tempV:
                                    vgTarget = answer.content.lower()
                                    await self.bot.send_message(vigilanteUser, embed = self.makeEmbed("Gotcha. You may now return to the mafia channel."))
                                    break
                                else:
                                    await self.bot.send_message(vigilanteUser, embed = self.makeEmbed("Error. Please check your spelling. Be sure to include any spaces and numbers!"))
                                    answer = await self.bot.wait_for_message(author = vigilanteUser)
                    #Detective turn
                    
                    for player, data in currentP.items():
                        if(data.roleName == 'detective') and data.alive == True:
                            detUser = player
                            detAlive = True
                    
                    # only if det is alive
                    if detAlive == True:
                        tempDT = []
                        for item in temp:
                            if item != detUser.name:
                                tempDT.append(item)
                        msg = self.makeEmbed("Detective please check your DMs.")
                        await self.bot.send_message(channel, embed = msg)

                        embed = self.makeEmbed("Targets:")
                        embed.add_field(name = "Who do you suspect?", value = "Please include all spaces and numbers.", inline = False)
                        for item in tempDT:
                            embed.add_field(name = "{}".format(item), value = "Pick me!", inline = True)
                        embed.set_image(url = "https://na.leagueoflegends.com/sites/default/files/styles/scale_xlarge/public/upload/cops_1920.jpg?itok=-T6pbISx")
                        await self.bot.send_message(detUser, embed = embed)
                        for stuff in temp:
                            if stuff != detUser.name:
                                tempDT.append(stuff)
                        suspect = "adsaskd"
                        for player, data in currentP.items(): #finds suspect
                            if(data.roleName == 'suspect'):
                                suspect = player.name.lower()
                        answer = await self.bot.wait_for_message(author = detUser, timeout = dmTime)
                        while True:
                                if answer == None:
                                    await self.bot.send_message(detUser, embed = self.makeEmbed("You ran out of time."))
                                    break
                                elif answer.content.lower() in tempDT:
                                    if answer.content.lower() in mafiaNames or answer.content.lower() == suspect: #if target is actually mafia or suspect
                                        embedDet = self.makeEmbed("Yes. That person is on the mafia's side. Now try to convince the others. Please return to the mafia chat now.")
                                        embedDet.set_thumbnail(url = "http://www.clker.com/cliparts/P/S/9/I/l/S/234-ed-s-sd-md.png")
                                        
                                    else:
                                        embedDet = self.makeEmbed("Sorry. That person is not the mafia. Please return to the mafia chat now.")
                                        embedDet.set_thumbnail(url = "https://iconsplace.com/wp-content/uploads/_icons/ff0000/256/png/thumbs-down-icon-14-256.png")
                                    
                                    await self.bot.send_message(detUser, embed = embedDet)
                                    break
                                else:
                                    embed = self.makeEmbed("Error. Please check your spelling. Be sure to include any spaces, and numbers!")
                                    await self.bot.send_message(detUser, embed = embed)
                                    answer = await self.bot.wait_for_message(author = detUser)

                    

                    #Storytime
                    await self.bot.send_message(channel, embed = self.makeEmbed("Alright everybody get your ass back here. It's storytime."))
                    for player, data in currentP.items():
                        if data.alive == True:
                            await self.bot.server_voice_state(player, mute = False)
                        else:
                            await self.bot.server_voice_state(player, mute = True)

                    await asyncio.sleep(3)
                    if saved == None:
                        await self.bot.send_message(channel, embed = self.makeEmbed("The mafia was too lazy to kill anyone this night."))
                    else:
                        story1 = discord.Embed(title = "Story", description = "All of these stories are written by linkboi and the submissions from Mafiabot Support Server.", colour = discord.Colour.purple())
                        await self.bot.send_message(channel, embed = story1)
                        if saved == True:
                            aStory = story.storyTime("alive", victim)
                            storyEmbed = discord.Embed(title = "{} lives!".format(victim), description = "{}".format(aStory), colour = discord.Colour.green())
                            storyEmbed.set_thumbnail(url = "https://vignette.wikia.nocookie.net/dragonfable/images/f/f1/Heal_Icon.png/revision/latest?cb=20130329031111")
                        else:
                            aStory = story.storyTime("dead", victim)
                            storyEmbed = discord.Embed(title = "{} died :(".format(victim), description = "{}".format(aStory), colour = discord.Colour.red())
                            storyEmbed.set_thumbnail(url = "https://image.flaticon.com/icons/png/512/155/155266.png")
                            for player, data in currentP.items():
                                if (player.name.lower() == victim):
                                    data.alive = False
                                    await self.bot.server_voice_state(player, mute=True)
                                    temp.remove(player.name.lower())
                                    overwrite = discord.PermissionOverwrite()
                                    overwrite.send_messages = False
                                    await self.bot.edit_channel_permissions(channel, player, overwrite)
                                    storyEmbed.add_field(name = "{}'s role is:".format(player.name), value = "{}".format(data.roleName))
                        
                        
                        await self.bot.send_message(channel, embed = storyEmbed)


                    await asyncio.sleep(5)

                    #vg's news
                    if vigilanteAlive == True:

                        if vgTarget == None:
                            print("duh")
                        

                        #if vg shot a mafia
                        elif vgTarget in mafiaNames:
                            embed = discord.Embed(title = "Wait, what's this?", description = "The vigilante shot a mafia!!", colour = discord.Colour.green())
                            embed.add_field(name = "The mafia shot was...", value = "{}!".format(vgTarget))
                            embed.set_image(url = "https://vignette.wikia.nocookie.net/michaelbaybatman/images/e/ea/Bac-gotham-rooftop.jpg/revision/latest?cb=20140223174240")
                            for player, data in currentP.items():
                                if (player.name.lower() == vgTarget):
                                    data.alive = False
                                    await self.bot.server_voice_state(player, mute=True)
                                    temp.remove(player.name.lower())
                                    overwrite = discord.PermissionOverwrite()
                                    overwrite.send_messages = False
                                    await self.bot.edit_channel_permissions(channel, player, overwrite)
                        #if vg shot an innocent boi
                        elif not vgTarget in mafiaNames:
                            embed = discord.Embed(title = "Wait, what's this?", description = "The vigilante shot the innocent {}! The vigilante has commited suicide out of guilt!".format(vgTarget), colour = discord.Colour.red())
                            
                            embed.set_image(url = "https://res.cloudinary.com/teepublic/image/private/s--N6Q7m5Pj--/t_Preview/b_rgb:191919,c_limit,f_jpg,h_630,q_90,w_630/v1493744453/production/designs/1556060_1.jpg")
                            embed.set_footer(text =  "{} was the vigilante!".format(vigilanteUser.name))
                            for player, data in currentP.items():
                                if (player.name.lower() == vgTarget or player.name.lower() == vigilanteUser.name.lower()):
                                    embed.add_field(name = "{}'s role was ".format(player.name), value = "{}".format(data.roleName))
                                    data.alive = False
                                    await self.bot.server_voice_state(player, mute=True)
                                    temp.remove(player.name.lower())
                                    overwrite = discord.PermissionOverwrite()
                                    overwrite.send_messages = False
                                    await self.bot.edit_channel_permissions(channel, player, overwrite)
                        #if vg shot the mafia's victim            
                        elif vgTarget == victim.lower():
                            embed = discord.Embed(title = "Wait, what's this?", description = "The vigilante also shot the mafia's victim! The vigilante has commited suicide out of shame!", colour = discord.Colour.orange())
                            embed.set_image(url = "https://i.ytimg.com/vi/lhckuhUxcgA/hqdefault.jpg")
                            embed.set_footer(text = "{} was the vigilante!".format(vigilanteUser.name))
                            
                            for player, data in currentP.items():
                                if (player.name.lower() == vigilanteUser.name.lower()):
                                    data.alive = False
                                    await self.bot.server_voice_state(player, mute=True)
                                    temp.remove(player.name.lower())
                                    overwrite = discord.PermissionOverwrite()
                                    overwrite.send_messages = False
                                    await self.bot.edit_channel_permissions(channel, player, overwrite)
                                elif (player.name.lower() == victim.lower()):
                                    if saved == True:
                                        data.alive = False
                                        await self.bot.server_voice_state(player, mute = True)
                                        temp.remove(player.name.lower())
                                        overwrite.send_messages = False
                                        await self.bot.edit_channel_permissions(channel, player, overwrite)
                                            

                        

                        
                        await self.bot.send_message(channel, embed = embed)
                    check = self.checkWin(mafiaCount, server.id, currentP)

                    await asyncio.sleep(5)
                    if check == "mafia":
                        for player in currentP.keys():
                            await self.bot.server_voice_state(player, mute = False)
                        embed = discord.Embed(title = "The mafia(s) win!", colour = discord.Colour.red())
                        self.updateWin(currentP, server.id, check)
                        break


                    elif check == "villager":
                        for player in currentP.keys():
                            await self.bot.server_voice_state(player, mute = False)
                            embed = discord.Embed(title = "The villagers win!", colour = discord.Colour.green())
                            self.updateWin(currentP, server.id, check)
                        break

                    elif check == "none": # lynch
                        tempC = []
                        for player, data in currentP.items():
                            if data.alive == True:
                                tempC.append(player.name.lower())
                        await self.bot.send_message(channel, embed = self.makeEmbed("Now I'll give you guys {} seconds to talk.".format(talkTime)))
                        await asyncio.sleep(talkTime)
                        nominateList = []
                        # nomination
                        nom = discord.Embed(title = "Players:", colour = discord.Colour.purple())

                        embed = self.makeEmbed("Alright! Any nominations? Just type them in the chat. You have {} seconds to submit each nomination.".format(voteTime))
                        embed.add_field(name = "Want to change the timer? ", value = "Use m.custom (setting) (time) to customize your games!")
                        embed.set_footer(text = "IMPORTANT: The timer resets everytime a message is sent, so please don't use this channel to chat.")
                        await self.bot.send_message(channel, embed = embed)

                        for item in tempC:
                            nom.add_field(name = "{}".format(item.lower()), value = "Pick me!", inline = False)

                        await self.bot.send_message(channel, embed = nom)
                        await asyncio.sleep(3)
                        overwrite = discord.PermissionOverwrite()
                        overwrite = discord.PermissionOverwrite()

                        #Gives permission to type in chat
                        for player, data in currentP.items():
                            if data.alive == True:
                                overwrite.send_messages = True
                                await self.bot.edit_channel_permissions(channel, player, overwrite)
                            else:
                                overwrite.send_messages = False
                                await self.bot.edit_channel_permissions(channel, player, overwrite)

                        nomination = await self.bot.wait_for_message(timeout = voteTime, channel = channel)
                        embed = discord.Embed(title = "Nominations", colour = discord.Colour.purple())
                        #Takes nominations until timer runs out(Resets timer everytime there's an input)
                        while True:
                            if nomination == None:
                                await self.bot.send_message(channel, embed = self.makeEmbed("The nomination time is closed."))
                                if nominateList:
                                    await self.bot.send_message(channel, embed = embed)
                                break
                            
                            elif nomination.author == self.bot.user:
                                nomination = await self.bot.wait_for_message(timeout = voteTime, channel = channel)
                                
                            elif not nomination.author.name.lower() in temp:
                                await self.bot.send_message(channel, embed = self.makeEmbed("You're not in the game."))
                                nomination = await self.bot.wait_for_message(timeout = voteTime, channel = channel)

                            elif nomination.content.lower() in tempC and not nomination.content.lower() in nominateList and nomination.author.name.lower() in tempC:
                                nominateList.append(nomination.content.lower())
                                embed.add_field(name = "{}".format(nomination.content.lower()), value = "Nominated to die!", inline = False)

                                overwrite = discord.PermissionOverwrite()
                                overwrite.send_messages = False
                                await self.bot.edit_channel_permissions(channel, nomination.author, overwrite)
                                await self.bot.send_message(channel, embed = self.makeEmbed("{} has been added to the nomination list. Any other ones?".format(nomination.content.lower())))
                                #sends list of nominations
                                await self.bot.send_message(channel, embed = embed)
                                    
                                nomination = await self.bot.wait_for_message(timeout = voteTime, channel = channel)
                            elif not nomination.content.lower() in temp or nomination.content.lower() in nominateList:
                                await self.bot.send_message(channel, embed = self.makeEmbed("Error. Not valid nomination. This person either doesn't exist or is already in the nomination list."))
                                nomination = await self.bot.wait_for_message(timeout = voteTime, channel = channel)
                            else:
                                await self.bot.send_message(channel, embed = self.makeEmbed("Error. Unknown error has occured. You're probably dead or something lol."))
                                nomination = await self.bot.wait_for_message(timeout = voteTime, channel = channel)
                        
                        await asyncio.sleep(5)


                        # voting time
                        if nominateList:
                            
                            overwrite = discord.PermissionOverwrite()
                            aliveCount = 0
                            for player, data in currentP.items():
                                if data.alive == True:
                                    overwrite.send_messages = True
                                    await self.bot.edit_channel_permissions(channel, player, overwrite)
                                    aliveCount += 1
                                else:
                                    overwrite.send_messages = False
                                    await self.bot.edit_channel_permissions(channel, player, overwrite)
                            
                            reqVote = int(aliveCount/1.5) #rounds number down
                            if reqVote < 2:
                                reqVote = 2 #make sure the reqVote is not below 2
                            authors = []
                            scoreName = []
                            score = []
                            embed = self.makeEmbed("Ok! Now it's time to vote!")
                            embed.add_field(name = " The person with the most votes dies.", value = "However, the person must have at least {} or more votes.".format(reqVote))
                            await self.bot.send_message(channel, embed = embed)
                            await asyncio.sleep(3)
                            for item in nominateList:
                                person = None
                                for player in currentP.keys():
                                    if player.name.lower() == item:
                                        person = player
                                
                                scoreName.append(item)
                                votes = 0
                                embed = self.makeEmbed("Who wants to vote for {}? Type v to vote.".format(item))
                                embed.set_thumbnail(url = person.avatar_url)
                                embed.set_footer(text = "IMPORTANT: The timer will reset everytime someone sends a message, so stop sending messages when you're done please.")
                                await self.bot.send_message(channel, embed = embed)
                                vote = await self.bot.wait_for_message(timeout = voteTime, content = "v", channel = channel)

                                #prompt votes
                                while True:
                                    if vote == None:
                                        break
                                    elif vote.author == self.bot.user:
                                        vote = await self.bot.wait_for_message(timeout = voteTime, content = "v", channel = channel)
                                    elif vote.author.name in authors:

                                        await self.bot.send_message(channel, embed = self.makeEmbed("You have voted already. Or your input was incorrect."))
                                        vote = await self.bot.wait_for_message(timeout = voteTime, content = "v", channel = channel)
                                        
                                    elif not vote.author.name.lower() in tempC:
                                        await self.bot.send_message(channel, embed = self.makeEmbed("You are not in the game, or you're dead."))
                                        vote = await self.bot.wait_for_message(timeout = voteTime, content = "v", channel = channel)

                                    elif vote.author.name.lower() == vote.content.lower():
                                        await self.bot.send_message(channel, embed = self.makeEmbed("You can't vote for yourself."))
                                
                                        vote = await self.bot.wait_for_message(timeout = voteTime, content = "v", channel = channel)
                                    elif not vote.author.name.lower() in authors and vote.author.name.lower() in temp:
                                        authors.append(vote.author.name)
                                        votes+=1
                                        await self.bot.send_message(channel, embed = self.makeEmbed("One vote has been put into {}".format(item)))

                                        overwrite = discord.PermissionOverwrite()
                                        overwrite.send_messages = False
                                        await self.bot.edit_channel_permissions(channel, vote.author, overwrite)

                                        vote = await self.bot.wait_for_message(timeout = voteTime, content = "v", channel = channel)
                                    
                                score.append(votes)
                                embed = discord.Embed(title = "Total votes for {}".format(item), description = "{}".format(votes), colour = discord.Colour.purple())
                                await self.bot.send_message(channel, embed = embed)
                            

                            # finds largest vote
                            largestVote = 0
                            for item in score:
                                if item > largestVote and item > (reqVote-1):
                                    largestVote = item
                                elif item == largestVote:
                                    largestVote = 0
                            
                            # kills nominated
                            
                            if largestVote != 0:
                                deadGuy = scoreName[score.index(largestVote)]
                                embed = discord.Embed(title = "{} has been hanged by the village. Press f to pay respect.".format(deadGuy), colour = discord.Colour.red())
                                embed.set_image(url = "https://cdn.shopify.com/s/files/1/0895/0864/products/42-47714084_1024x1024.jpeg?v=1451772538")
                                await self.bot.send_message(channel, embed = embed)
                                await asyncio.sleep(3)
                                for player, data in currentP.items():
                                    if (player.name.lower() == deadGuy.lower()):
                                        data.alive = False
                                        await self.bot.server_voice_state(player, mute=True)
                                        await self.bot.send_message(channel, embed = self.makeEmbed("{}'s role was {}".format(player.name, data.roleName)))
                            elif largestVote == 0:
                                await self.bot.send_message(channel, embed = self.makeEmbed("No one was hanged."))
                                        
                        else:
                            await self.bot.send_message(channel, embed = self.makeEmbed("No one was hanged."))
                        overwrite = discord.PermissionOverwrite()
                        overwrite.send_messages = False
                        role = discord.utils.get(server.roles, name='@everyone')
                        await self.bot.edit_channel_permissions(channel, role, overwrite)
                        check = self.checkWin(mafiaCount, server.id, currentP)
                        
                        jesterWins = False
                        if deadGuy != None:
                            for player, data in currentP.items():
                                if player.name.lower() == deadGuy and data.roleName == "jester":
                                    jesterWins = True

                        #check conditions 
                        #check returns string mafia or villager
                        if jesterWins == True:
                            for player in currentP.keys():
                                await self.bot.server_voice_state(player, mute = False)
                                embed = discord.Embed(title = "Uh oh! The Jester wins!", colour = discord.Colour.purple())
                                embed.set_thumbnail(url = "https://runes.lol/image/generated/championtiles/Shaco.jpg")
                                self.updateWin(currentP, server.id, "jester")
                            break
                        elif check == "mafia":
                            for player in currentP.keys():
                                await self.bot.server_voice_state(player, mute = False)
                                embed = discord.Embed(title = "The mafia(s) win!", colour = discord.Colour.purple())
                                self.updateWin(currentP, server.id, check)
                            break
                        elif check == "villager":
                            for player in currentP.keys():
                                await self.bot.server_voice_state(player, mute = False)
                                embed = discord.Embed(title = "The villagers win!", colour = discord.Colour.purple())
                                self.updateWin(currentP, server.id, check)
                            break
                #unmutes all players
                for player in currentP.keys():
                    await self.bot.server_voice_state(player, mute = False)

                    #Only if the game did not end with commandStop
                if self.serverStatus[server.id]['commandStop'] == False:
                    self.displayAllR(embed, currentP)
                    await self.bot.send_message(channel, embed = embed)
                    await self.bot.send_message(channel, embed = self.makeEmbed("Thank you all for playing! Deleting this channel in 10 seconds"))
                    await asyncio.sleep(10)
                    await self.bot.delete_channel(channel)
                self.serverStatus[server.id]["ready"] = False
                self.serverStatus[server.id]["gameOn"] = False
                self.serverStatus[server.id]['commandStop'] = False  
                embed = discord.Embed(title = "A game has finished on {}.".format(server.name), description = "Group size: {}".format(len(currentP.keys())), colour = discord.Colour.dark_purple())
                embed.add_field(name = "Server id: ", value = "{}".format(server.id))
 
                await self.bot.send_message(discord.Object(id='534564704937574400'), embed = embed)
                    
            except Exception as e:
                if isinstance(e, discord.Forbidden):
                    await self.bot.send_message(ctx.message.channel, "Error. Missing permission to mute members!(Or some other permissions idk)")
                else:
                    await self.bot.send_message(ctx.message.channel, "Error. Something weird happened. Might just be a missing comma someone forgot to put in my code lol. Might want to do m.reset just in case.(If this keeps happening report it to the Mafia Support Server)")
                
                embed = discord.Embed(title = "An error has occured on {}.".format(server.name), description = "Server id: {}".format(server.id), colour = discord.Colour.red())
                embed.add_field(name = "Error:", value = "{}".format(traceback.format_exc()))
                await self.bot.send_message(discord.Object(id='534564704937574400'), embed = embed)
                self.serverStatus[server.id]["ready"] = False
                self.serverStatus[server.id]["gameOn"] = False
                self.serverStatus[server.id]["commandStop"] = False
                mafiaChannel = None
                for item in server.channels:
                    if item.name == 'mafia':
                        mafiaChannel = item
                try:
                    await self.bot.delete_channel(mafiaChannel)  
                except:
                    print("duh")
                embed = discord.Embed(title = "Resetting...", colour = discord.Colour.red())
                await self.bot.send_message(ctx.message.channel, embed = embed)
               
    
        
    def checkServer(self, server):
      if not server.id in self.mafiaPlayers.keys():
        self.mafiaPlayers[server.id] = {}
        self.serverStatus[server.id] = {}
        self.serverStatus[server.id]["ready"] = False
        self.serverStatus[server.id]["gameOn"] = False
        self.serverStatus[server.id]['commandStop'] = False  
        self.serverStatus[server.id]['dmTime'] = 30
        self.serverStatus[server.id]['voteTime'] = 20
        self.serverStatus[server.id]['talkTime'] = 60
    def findChannel(self, server):
        for item in server.channels:
            if item.name == 'mafia':
                return item
    
    #returns number of people alive in the side of mafia or village
    def checkGame(self, current, isMafia):
        num = 0
        if isMafia == True:
            for player, data in current.items():
                if data.roleName == "mafia" and data.alive == True:
                    num += 1
        else:
            for player, data in current.items():
                if data.roleName != "mafia" and data.alive == True:
                    num+=1
        return num
    #returns who wins
    def checkWin(self, mafiaCount, id, currentList):
        mLive = self.checkGame(currentList, True)
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

    def displayAllR(self, embed, mafiaList):
        embed.set_image(url = "https://wallpapers.wallhaven.cc/wallpapers/full/wallhaven-323086.png")
        for player, data in mafiaList.items():
            embed.add_field(name = "{}".format(player.name), value = "{}".format(data.roleName), inline = True)
    def setRoles(self, ctx, group, role):
        role = random.choice(group)
        group.remove(role)

    def makeEmbed(self, message):
      embed = discord.Embed(title = message, colour = discord.Colour.orange())
      return embed
    def displayMember(self, server, group):
        embed = discord.Embed(title = "Targets", colour = discord.Colour.purple())
        for item in group.keys():
            name = server.get_member(item)
            embed.add_field(name = "{}".format(name), value = "Kill me!", inline = False)
        return embed

    def checkSide(self, role):
        if role == "mafia": #checks what side the role belongs to
            return "mafia"
        elif role == "jester":
            return "jester"
        else:
            return "villager"

    def checkFile(self, playerID, serverID):
        with open('players.json', 'r') as f:
            players = json.load(f)
        if not serverID in players:
            players[serverID] = {}
        if not playerID in players[serverID].keys():
            players[serverID][playerID] = {}
            players[serverID][playerID]["Wins"] = 0
            players[serverID][playerID]["Games"] = 0
        with open('players.json', 'w') as f:
            json.dump(players, f)
    
    def updateWin(self, mafiaList, serverID, winner):
        with open('players.json', 'r') as f:
            players = json.load(f)

        #finds players with the winning role (winner is a string) and adds one point to their record
        for player, data in mafiaList.items():
            side = self.checkSide(data.roleName)
            if side == winner:
                players[serverID][player.id]["Wins"] += 1
            players[serverID][player.id]["Games"] += 1

        with open('players.json', 'w') as f:
            json.dump(players, f)                
    
    
def setup(bot):
    bot.add_cog(mafia(bot))