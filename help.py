import discord
from discord.ext import commands
import asyncio
import dbl
import MAFIA.turns as turn
import role as roleObj
class helpC(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjUxMTc4NjkxODc4MzA5MDY4OCIsImJvdCI6dHJ1ZSwiaWF0IjoxNTQ2NjU0ODk3fQ.hADbMQxWCw0czaTDcVUpqAdCUzEpHngQUw-HtQeHVV8'  #  set this to your DBL token
        self.dblpy = dbl.Client(self.bot, self.token)
        self.commandsDict = {}
        self.roleList = []
        with open("classicRole.txt") as f:
            for line in f:
                
                (name, ability, goal, side, img_url) = line.split(" : ")
                
                self.roleList.append(roleObj.Role(name, ability, goal, side, "classic", img_url))
        
        with open("crazyRole.txt") as f:
            for line in f:
                (name, ability, goal, side, img_url) = line.split(" : ")
                self.roleList.append(roleObj.Role(name, ability, goal, side, "crazy", img_url))
        with open('commands.txt') as f:
            for line in f:
                (key, val) = line.split(" : ")
                self.commandsDict[key] = val
    commandGames = ["join", "leave", "setup", "start", "stop", "reset", "party", "clear", "custom", "gamemode", "duel"]
    commandOther = ["info", "perms", "updates", "mini"]
    testUsers = []
    @commands.command(pass_context = True)
    async def getVoters(self, ctx):
        temp = []
        for item in await self.dblpy.get_upvote_info():
            temp.append(item['username'])
        await ctx.message.channel.send(temp)
    @commands.command(name = "patch", aliases = ['updates', 'update', 'patches', "changes"])
    async def patch(self, ctx):
        update = discord.Embed(title = "Latest Mafia Updates: Bunch of new roles!", description = "Patch 1.9", colour = discord.Colour.blue())
        update.add_field(name = "New role: Godfather", value = "You decide who to kill. If you don't have a mafia you do it yourself.")
        update.add_field(name = "New role: PI", value = "Choose two players each night to see if they're on the same side!")
        update.add_field(name = "New role: Spy", value = "See who your target visits each night!")
        update.add_field(name = "New role: Bomber", value = "Blow stuff up and win!")
        update.add_field(name = "New role: Dictator", value = "Choose a side and try to get that side to win! If you succeed you win instead of that side!")
        update.add_field(name = "New role: Baiter", value = "Bait people to visit you so you can kill them! Kill three people to win (Doesn't affect flow of game)")
        update.add_field(name = "Mafia role change", value = "Mafia now only do what the Godfather commands. Also the chance of framer appearing requires a minimum of 6 people.")
        update.add_field(name = "Updated command: m.roles", value = "m.roles shows a list of all the roles. Do m.roles `role` to view specific information about a role!")
        
        update.add_field(name = "New DM System", value = "Now everyone responds to DM the same time. Also you select your target by reacting now. Yay time.")
        update.add_field(name = "Mafia points update", value = "You get more points now. Yay.")
        
        update.set_image(url = "http://www.lol-wallpapers.com/wp-content/uploads/2018/12/Odyssey-Ziggs-Splash-Art-HD-4k-Wallpaper-Background-Official-Art-Artwork-League-of-Legends-lol.jpg")
        await ctx.message.channel.send(embed = update)
    @commands.command(pass_context = True)
    async def perms(self, ctx):
        
        req = discord.Embed(title = "Mafiabot Permissions:", colour = discord.Colour.blue())
        req.add_field(name = "Server Permissions:", value = "Send Messages, Manage Roles, Manage Chanels, Read Text Channels, Send Messages, Manage Messages, and Mute Members.")
        req.add_field(name = "Additional Permissions:", value = "Every player MUST have 'Allow Direct Messages from Server Members' ON in personal Privacy settings to play.")
        try:
            await ctx.message.channel.send(embed = req)
        except discord.Forbidden:
            embed = discord.Embed(title = "Error. Can't send a DM. Check your privacy settings.", colour = discord.Colour.red())
            await ctx.message.channel.send(embed = embed)
    @commands.command(pass_context = True)
    async def mini(self, ctx):
        embed = discord.Embed(title = "Current mini games:", colour = discord.Colour.blue())
        embed.add_field(name = "Duel", value = "m.duel @user\n Challenge another member to a duel!")
        embed.add_field(name = "Slot machine", value = "m.slot `bet`\nDefault bet is 10 points. View the list of combinations with m.combinations.")
        embed.set_image(url = "https://render.fineartamerica.com/images/rendered/default/greeting-card/images/artworkimages/medium/1/1-38885-league-of-legends-mafia-jinx-anne-pool.jpg?&targetx=-94&targety=0&imagewidth=888&imageheight=500&modelwidth=700&modelheight=500&backgroundcolor=542821&orientation=0")
        try:

            await ctx.channel.send(embed = embed)
        except discord.Forbidden:
            await ctx.channel.send("Can't send a DM. Check your privacy settings.")
    @commands.command(pass_context = True)
    async def info(self, ctx):
        
        info = discord.Embed(title = "Mafiabot", colour = discord.Colour.orange())
        info.set_thumbnail(url = self.bot.user.avatar_url)
        info.add_field(name = "What I do:", value = "Host mafia on your discord server!", inline = False)
        info.add_field(name = "What are my commands?", value = "My commands can be found with m.help.", inline = False)
        info.add_field(name = "Find out what's the latest update with the command:", value = "m.updates", inline = False)
        info.add_field(name = "Library", value = "discord.py", inline = True)
        info.add_field(name = "Currently on:", value = "{} servers!".format(len(self.bot.guilds)), inline = True)
        info.add_field(name = "Creator:", value = "<@217380909815562241>", inline = True)
        info.add_field(name = "Upvote me!", value = "https://discordbots.org/bot/511786918783090688", inline = False)
        info.add_field(name = "Invite me!", value = "https://discordapp.com/oauth2/authorize?client_id=511786918783090688&scope=bot&permissions=272641041", inline = False)
        info.add_field(name = "Join the support server!", value = "https://discord.gg/Qdz3Cvu", inline = False)
        info.add_field(name = "The bot stopped working during a game of mafia. What do I do?", value = "Use the m.reset command and report it to the Mafiabot Support Discord.", inline = False)
        
        await ctx.channel.send(embed = info)
    
    @commands.command(name = "invite", aliases = ["link"])
    async def invite(self, ctx):
        await ctx.channel.send("https://discordapp.com/oauth2/authorize?client_id=511786918783090688&scope=bot&permissions=272641040")
    @commands.command(pass_context = True)
    async def game(self, ctx):
        stuff = discord.Embed(title = "Info on the game has been sent to your dm!", colour = discord.Colour.orange())
        await ctx.message.channel.send(embed = stuff)
        embed = discord.Embed(title = "Mafia Game", colour = discord.Colour.orange())
        embed.set_image(url = "https://i0.wp.com/static.lolwallpapers.net/2015/11/Braum-Safe-Breaker-Fan-Art-Skin-By-Karamlik.png")
        embed.add_field(name = "Requirement:", value = "At least 5 players, must have ALL required permissions, and everyone must have Allow Direct Messages from Server Members ON in personal Privacy settings", inline = False)
        embed.add_field(name = "Setting the Game:", value = "Everyone playing must enter m.join to join the party. Type m.leave to leave the party.", inline = False)
        embed.add_field(name = "Step 1", value = "Enter m.setup to set up and assign the roles for the game.(Roles are sent through dm.)", inline = False)
        embed.add_field(name = "Step 2", value = "Enter m.start to start the game.", inline = False)
        embed.add_field(name = "Step 3", value = "Play", inline = False)
        embed.add_field(name = "How to play:", value = "To play, there must be at least 5 people in the Mafia party.", inline = False)
        embed.add_field(name = "#1", value = "When the game starts, each player will receive their role through dm.", inline = False)
        embed.add_field(name = "#2", value = "Everyone will go to sleep. The Mafia would be the first to wake up, and through dm he/she can choose which player to kill.", inline = False)
        embed.add_field(name = "#3", value = "After, the doctor will wake up, and he/she can choose a person to save through dm.", inline = False)
        embed.add_field(name = "#4", value = "Finally, the detective will wake up and choose a person to accuse through dm. He/she would be informed if the person is the Mafia. If he/her investigates the suspect, then he/she will be informed that the suspect is the mafia.", inline = False)
        embed.add_field(name = "#5", value = "Everybody wakes up and the bot will inform you through the mafia channel who was killed. The group has a minute to discuss who is the Mafia.", inline = False)
        embed.add_field(name = "#6", value = "Everyone then nominate and vote on people to lynch. The most voted person will then be lynched.")
        embed.add_field(name = "#7", value = "The cycle continues until only if the number of mafias are greater than villagers, the mafia kills everyone, or all the mafia dies.")
        embed.set_footer(text = "For more information, type m.roles for roles, m.help for commands.")
        await ctx.message.author.send(embed = embed)

    @commands.command(name = "roles", aliases = ["role", "roleInfo", "roleinfo"])
    async def roles(self, ctx, *args):
        if len(args) == 0:
            embed  = discord.Embed(title = "Roles", description = "Classic roles will always be in play. Crazy roles will be randomized each game(Depending on the group size)", colour = discord.Colour.orange())
            classicRoleStr = ""
            for item in self.roleList:
                if item.mode == "classic":
                    classicRoleStr += item.name+" : " +item.side + "\n"
            
            crazyRoleStr = ""
            for item in self.roleList:
                if item.mode == "crazy":
                    crazyRoleStr += item.name + " : " +item.side + "\n"

            embed.add_field(name= "Classic roles: ", value = classicRoleStr, inline = True)
            embed.add_field(name = "Crazy roles: ", value = crazyRoleStr, inline = True)
            embed.set_thumbnail(url = self.bot.user.avatar_url)
            embed.set_footer(text = "For more information about each role, type m.role `role` to view more!")
            await ctx.channel.send(embed= embed)
            return
        
        if len(args) == 1:
            selectedRole = None
            for item in self.roleList:
                if args[0].lower() == item.name.lower():
                    selectedRole = item
            if selectedRole != None:
                embed = discord.Embed(title = selectedRole.name, description = selectedRole.mode, colour = discord.Colour.blurple())
                embed.add_field(name = "Ability:", value = selectedRole.ability, inline = False)
                embed.add_field(name = "Goal", value = selectedRole.goal)
                embed.add_field(name = "Side:", value = selectedRole.side)
                embed.set_thumbnail(url = selectedRole.image_url)
                await ctx.channel.send(embed = embed)
            else:
                await ctx.channel.send("That's not a role I know lmao.")


    @commands.command(pass_context = True)
    async def help(self, ctx, *args):
        if len(args) == 0:
            commandGame_str = ""
            for item in self.commandsDict.keys():
                commandGame_str += item + "\n"

            embed = discord.Embed(title = "Mafia Commands", colour = discord.Colour.orange())
            embed.add_field(name = "Game commands:", value = commandGame_str, inline = True)

            embed.add_field(name = "All customizable settings: ", value = "dmtime: amount of time people can respond to dm messages\n talkTime: amount of time for group discussion\n voteTime: Amount of time to vote.")
            embed.set_footer(text = "For more information, type m.help 'command' to see more!")
            embed.set_thumbnail(url = self.bot.user.avatar_url)
            await ctx.channel.send(embed = embed)
            return
        elif len(args) == 1:
            if args[0] in self.commandsDict.keys():
                embed = discord.Embed(title = args[0], description = self.commandsDict[args[0]], colour = discord.Colour.orange())
                await ctx.channel.send(embed = embed)
                return
            await ctx.channel.send("Boi that's not a command.")


    @commands.command(pass_context = True)
    async def support(self, ctx):
        await ctx.channel.send("Would you like to request a helper to help with your problems?(y/n)\n*Note: I will need permission to send invitations.(Make sure that I do before requesting)")
        answer = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author and (message.content.lower() == "y" or message.content.lower() == "yes" or message.content.lower() == "n" or message.content.lower() == "no"), timeout = 20)
        if not "n" in answer.content.lower():
            try:
                supportChannel = self.bot.get_channel(596963027597787157)
                invite = await ctx.channel.create_invite()
                await supportChannel.send(invite)
                await ctx.channel.send("Request sent! Now we wait...(Plz be patient not all our helpers will be on 24/7)")
                return
            except discord.Forbidden:
                await ctx.channel.send("Error. I can't create an invite lol.")
                return
        
        await ctx.channel.send("Lol ok. False alarm, I guess.")


def setup(bot):
    bot.add_cog(helpC(bot))