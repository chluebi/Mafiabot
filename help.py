import discord
from discord.ext import commands
import dbl
class helpC:
    def __init__(self, bot):
        self.bot = bot
        self.token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjUxMTc4NjkxODc4MzA5MDY4OCIsImJvdCI6dHJ1ZSwiaWF0IjoxNTQ2NjU0ODk3fQ.hADbMQxWCw0czaTDcVUpqAdCUzEpHngQUw-HtQeHVV8'
        self.dblpy = dbl.Client(self.bot, self.token)


    @commands.command(pass_context = True)
    async def perms(self, ctx):
        
        req = discord.Embed(title = "Mafiabot Permissions:", colour = discord.Colour.blue())
        req.add_field(name = "Server Permissions:", value = "Send Messages, Manage Roles, Manage Chanels, Read Text Channels, Send Messages, Manage Messages, and Mute Members.")
        req.add_field(name = "Additional Permissions:", value = "Every player MUST have 'Allow Direct Messages from Server Members' ON in personal Privacy settings to play.")
        req.add_field(name = "Do NOT have any other text or voice channels named 'mafia'", value = "And try not to have same nicknames on the server.")
        try:
            await self.bot.send_message(ctx.message.channel, embed = req)
        except discord.Forbidden:
                    embed = discord.Embed(title = "Error. Missing required permissions. Please check all of my required permissions with m.perms.", colour = discord.Colour.red())
                    await self.bot.send_message(ctx.message.channel, embed = embed)
    @commands.command(pass_context = True)
    async def info(self, ctx):
        
        info = discord.Embed(title = "Mafiabot", colour = discord.Colour.orange())
        info.set_thumbnail(url = self.bot.user.avatar_url)
        info.add_field(name = "What I do:", value = "Host mafia on your discord server!", inline = False)
        info.add_field(name = "What are my commands?", value = "My commands can be found with m.help.", inline = False)
        info.add_field(name = "Library", value = "discord.py", inline = True)
        info.add_field(name = "Currently on:", value = "{} servers!".format(len(self.bot.servers)), inline = True)
        info.add_field(name = "Creator:", value = "<@217380909815562241>", inline = True)
        info.add_field(name = "Upvote me!", value = "https://discordbots.org/bot/511786918783090688", inline = False)
        info.add_field(name = "Invite me!", value = "https://discordapp.com/oauth2/authorize?client_id=511786918783090688&scope=bot&permissions=272641040", inline = False)
        info.add_field(name = "Join the support server!", value = "https://discord.gg/4KAqmWM", inline = False)
        info.add_field(name = "The bot stopped working during a game of mafia. What do I do?", value = "Use the m.reset command and report it to the Mafiabot Support Discord.", inline = False)
        
        await self.bot.send_message(ctx.message.channel, embed = info)
    @commands.command(pass_context = True)
    async def game(self, ctx):
        stuff = discord.Embed(title = "Info on the game has been sent to your dm!", colour = discord.Colour.orange())
        await self.bot.send_message(ctx.message.channel, embed = stuff)
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
        await self.bot.send_message(ctx.message.author, embed = embed)

    @commands.command(pass_context = True)
    async def roles(self, ctx):
        stuff = discord.Embed(title = "Info on mafia roles has been sent to your dm!", colour = discord.Colour.orange())
        await self.bot.send_message(ctx.message.channel, embed = stuff)
        embed = discord.Embed(title = "Mafia Roles", colour = discord.Colour.orange())
        embed.set_thumbnail(url = "https://www.mobafire.com/images/avatars/graves-mafia.png")
        embed.add_field(name = "Mafia", value = "Side: Mafia. Your role is to kill everyone. And don't get caught.", inline = False)
        embed.add_field(name = "Doctor", value = "Side: Villager. Your role is to save people. You cannot save the same person twice in a row.", inline = False)
        embed.add_field(name = "Detective", value = "Side: Villager. Your role is to find the mafia and tell everyone.", inline = False)
        embed.add_field(name = "Suspect", value = "Side: Villager. When inspected by the detective, the suspect would return Mafia, even though the suspect is on the villager's side. The suspect won't know that he/she is a suspect. There must be at least 6 people to have a chance of gaining this role.", inline = False)
        embed.add_field(name = "Jester", value = "Side: Neutral. Your goal is to get lynched by the mob in order to win.", inline = False)
        embed.add_field(name = "Vigilante", value = "Side: Villager. Your goal is shoot all the mafias. However if you shoot the wrong person you commit suicide.", inline = False)
        embed.set_footer(text = "For more information, type m.game for how the game works, m.help for commands.")
        await self.bot.send_message(ctx.message.author, embed = embed)
    
    @commands.command(pass_context = True)
    async def help(self, ctx):
        stuff = discord.Embed(title = "Info on the commands has been sent to your dm!", description = "Note: I am case sensitive(working on that)", colour = discord.Colour.orange())
        await self.bot.send_message(ctx.message.channel, embed = stuff)
        embed = discord.Embed(title = "Mafia Commands", colour = discord.Colour.orange())
        embed.add_field(name = "m.info", value = "Shows the bot's information!", inline = False)
        embed.add_field(name = "m.perms", value = "Shows the bot's required permissions and stuff in order to function correctly in the server!", inline = False)
        embed.add_field(name = "m.join", value = "Joins the current mafia party.", inline = False)
        embed.add_field(name = "m.leave", value = "Leaves the current mafia party.", inline = False)
        embed.add_field(name = "m.party", value = "Displays current party.", inline = False)
        embed.add_field(name = "m.setup", value = "Sets up the game.(Must do before m.start)", inline = False)
        embed.add_field(name = "m.start", value = "Starts the game with the current people in the mafia party. Must do m.setup first.", inline = False)
        embed.add_field(name = "m.record @person", value = "Reveals information about a person's game record.", inline = False)
        embed.set_footer(text = "For more information, type m.game for how the game works, m.roles for roles and m.helpAdmin to see admin commands.")
        try:
            await self.bot.send_message(ctx.message.author, embed = embed)
        except discord.Forbidden:
            
            embed = discord.Embed(title = "Error. Missing required permissions. Please check all of my required permissions with m.perms.", colour = discord.Colour.red())
            await self.bot.send_message(ctx.message.channel, embed = embed)
    
    @commands.command(pass_context = True)
    async def helpAdmin(self, ctx):
      stuff = discord.Embed(title = "Info on admin commands has been sent to your dm!", colour = discord.Colour.orange())
      await self.bot.send_message(ctx.message.channel, embed = stuff)
      embed = discord.Embed(title = "Admin Commands", colour = discord.Colour.orange())
      embed.add_field(name = "m.clearParty", value = "Clears current party.")
      embed.add_field(name = "m.stopGame", value = "With this command, the bot will stop the current game after the round finishes.")
      embed.add_field(name = "m.reset", value = "Resets ALL Mafiabot's variables(setup, stopGame). ONLY USE THIS WHEN THE BOT HAS CRASHED. DO NOT USE THIS WHEN A GAME IS RUNNING JUST FINE.")
      embed.set_footer(text = "For more information, type m.help for commands, m.roles for roles, and m.game for game rules.")
      await self.bot.send_message(ctx.message.author, embed = embed)


def setup(bot):
    bot.add_cog(helpC(bot))