import discord
from discord.ext import commands
from discord import Webhook, AsyncWebhookAdapter
import aiohttp
import asyncio
import json
import dbl
import MAFIA.turns as turn
import role as roleObj
class helpC(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjUxMTc4NjkxODc4MzA5MDY4OCIsImJvdCI6dHJ1ZSwiaWF0IjoxNTQ2NjU0ODk3fQ.hADbMQxWCw0czaTDcVUpqAdCUzEpHngQUw-HtQeHVV8'  #  set this to your DBL token
        self.dblpy = dbl.DBLClient(self.bot, self.token)
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
        
        with open("chaosRole.txt") as f:
            for line in f:
                (name, ability, goal, side, img_url) = line.split(" : ")
                self.roleList.append(roleObj.Role(name, ability, goal, side, "chaos", img_url))

        with open('commands.json') as f:
            self.commandDict = json.load(f)

                
    @commands.command(pass_context = True)
    async def getVoters(self, ctx):
        temp = []
        for item in await self.dblpy.get_bot_upvotes():
            temp.append(item['username'])
        await ctx.message.channel.send(temp)


    @commands.command(name = "patch", aliases = ['updates', 'update', 'patches', "changes"])
    async def patch(self, ctx):
        update = discord.Embed(title = "Latest Mafia Updates", description = "Patch 1.9999", colour = discord.Colour.blue())

        update.add_field(name = "New feature", value = "You can now designate a category where I create the text channel! Type m.custom category `category id `!")
        update.add_field(name = "Adjusted modes", value = "Crazy mode now has less roles, but have no fear...")
        update.add_field(name = "New game mode: Chaos!", value = "Every role is in play!")
        update.add_field(name = "Balanced roles", value = "In a party with 13 or more people, there will be a certain amount of villagers to balance out the sides.")
        update.add_field(name = "Adjusted command: m.gamemode", value = "Shows a list of available game modes. To change the game mode, use m.custom!")
        update.add_field(name = "Bug fixes!(I hope)", value = "Fixed bugs with vigi and baiter. Plz tell me if there are more bugs through the support server.")
        update.add_field(name = "Dictator has been removed.", value = "You're welcome.")
        update.add_field(name = "Balance changes", value = "Party size requirements for roles have changed for mafia, framer, baiter and bomber.")
        update.add_field(name = "Command change", value = "Admin can also use m.setup, m.start and m.remove without being party leader.")
        update.set_image(url = "https://i.pinimg.com/originals/9a/6f/3d/9a6f3d0fd2eaccccb22f244e985f5468.jpg")
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
        info.add_field(name = "Find out what's the latest update with the command:", value = "m.updates", inline = False)
        info.add_field(name = "Library", value = "discord.py", inline = True)
        info.add_field(name = "Currently on:", value = "{} servers!".format(len(self.bot.guilds)), inline = True)
        info.add_field(name = "Creator:", value = "<@217380909815562241>", inline = True)
        info.add_field(name = "Here are some cool links!", value = "[Link to my upvote page!](https://discordbots.org/bot/511786918783090688)\n[Invite me to your cool server!](https://discordapp.com/oauth2/authorize?client_id=511786918783090688&scope=bot&permissions=272641041)\n[Join the support server!](https://discord.gg/2bnpcx8)", inline = False)
        
        await ctx.channel.send(embed = info)
    
    @commands.command(name = "invite", aliases = ["link"])
    async def invite(self, ctx):
        await ctx.channel.send("[Here's a very cool link to invite me to your server!]https://discordapp.com/oauth2/authorize?client_id=511786918783090688&scope=bot&permissions=272641040")
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
        embed.add_field(name = "#2", value = "Everyone will go to sleep. People with active roles will then be prompted to choose targets by reacting.", inline = False)
        embed.add_field(name = "#5", value = "Everybody wakes up and the bot will inform you through the mafia channel who was killed. The group will have time to discuss who is the Mafia.", inline = False)
        embed.add_field(name = "#6", value = "Everyone then vote on people to lynch. The most voted person will then be lynched.")
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
                    classicRoleStr += item.name +" : " + item.side + "\n"
            
            crazyRoleStr = ""
            for item in self.roleList:
                if item.mode == "crazy":
                    crazyRoleStr += item.name + " : " + item.side + "\n"
            chaosRoleStr = ""
            for item in self.roleList:
                if item.mode == "chaos":
                    chaosRoleStr += item.name + " : " + item.side + "\n"

            embed.add_field(name= "Classic roles: ", value = classicRoleStr)
            embed.add_field(name = "Crazy roles: ", value = crazyRoleStr)
            embed.add_field(name = "Chaos roles: ", value = chaosRoleStr)
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
    async def win(self, ctx):
        embed = discord.Embed(title = "Win conditions:trophy:", colour = discord.Colour.red())
        embed.add_field(name = "All threats eliminated", value = "Villager wins", inline = False)
        embed.add_field(name = "# of mafias > # of villagers", value = "Mafia wins", inline = False)
        embed.add_field(name = "# of mafias = # of villagers", value = "Mafia wins", inline = False)
        embed.add_field(name = "Executioner's target gets lynched", value = "Executioner wins", inline = False)
        embed.add_field(name = "Jester gets lynched", value = "Jester wins")
        embed.add_field(name = "All people dead (maybe except bomber)", value = "Bomber wins", inline = False)
        await ctx.send(embed = embed)

    @commands.command(pass_context = True)
    async def help(self, ctx, *args):
        if len(args) == 0:
            commandGame_str = ""
            for item in self.commandDict.keys():
                commandGame_str += item + "\n"

            embed = discord.Embed(title = "Mafia Commands", colour = discord.Colour.orange())
            for commandType in self.commandDict.keys():
                tempStr = ""
                for c in self.commandDict[commandType].keys():
                    tempStr += c + "\n"
                embed.add_field(name = commandType, value = tempStr)

            embed.add_field(name = "Customizable settings: ", value = "dmTime\ntalkTime\nvoteTime\ngamemode")
            embed.set_footer(text = "For more information, type m.help 'command' to see more!")
            embed.set_thumbnail(url = self.bot.user.avatar_url)
            await ctx.channel.send(embed = embed)
            return
        elif len(args) == 1:
            try:
                for commandType in self.commandDict.keys():
                    if args[0] in self.commandDict[commandType].keys():

                        embed = discord.Embed(title = "Command: " + args[0], description = self.commandDict[commandType][args[0]], colour = discord.Colour.orange())
                        await ctx.channel.send(embed = embed)
                        return
            except:
                await ctx.channel.send("Lol that's not a command.")




    @commands.command(pass_context = True)
    async def support(self, ctx):
        embed = discord.Embed(title = "The Official Mafiabot Support Server!", description = "[Click here!](https://discord.gg/2bnpcx8)", colour = discord.Colour.blue())
        embed.add_field(name = "Got a question? A suggestion? A story submission? Lonely? Want to play mafia?",  value = "Click on that link above!")
        embed.set_thumbnail(url = self.bot.user.avatar_url)
        await ctx.send(embed = embed)
    
    @commands.command(pass_context = True)
    async def upvote(self, ctx):
        embed = discord.Embed(title = "Upvote Mafiabot on discordbots.org! Just click on that tiny link below. (Psst, my creator will give you 30 points whenever you upvote if you're in the support server...)", description = "[Click me!](https://discordbots.org/bot/511786918783090688)", colour = discord.Colour.blue())
        embed.set_thumbnail(url = self.bot.user.avatar_url)
        await ctx.send(embed = embed)
    


def setup(bot):
    bot.add_cog(helpC(bot))