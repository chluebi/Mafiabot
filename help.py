import discord
from discord.ext import commands

class helpC:
    def __init__(self, bot):
        self.bot = bot


    @commands.command(pass_context = True)
    async def info(self, ctx):
        info = discord.Embed(title = "Mafiabot", colour = discord.Colour.orange())
        info.set_thumbnail(url = self.bot.user.avatar_url)
        info.add_field(name = "What I do:", value = "Play mafia on your discord server!", inline = False)
        info.add_field(name = "What are my commands?", value = "My commands can be found with m.helpC.", inline = False)
        info.add_field(name = "Library", value = "discord.py", inline = True)
        info.add_field(name = "Currently on:", value = "{} servers!".format(len(self.bot.servers)), inline = True)
        info.add_field(name = "Creator:", value = "<@217380909815562241>", inline = True)
        info.add_field(name = "Upvote me!", value = "https://discordbots.org/bot/511786918783090688", inline = False)
        info.add_field(name = "Invite me!", value = "https://discordapp.com/oauth2/authorize?client_id=511786918783090688&scope=bot&permissions=272641040", inline = False)
        info.add_field(name = "Join the support server!", value = "https://discord.gg/4KAqmWM", inline = False)
        info.add_field(name = "The bot stopped working during a game of mafia. What do I do?", value = "Just delete the mafia channel created by the bot, and server unmute everyone. You can report this to the Mafiabot support discord and we will help you. Usually it's because the bot shut down during your game, or an error has occured that caused the game to freeze(Blame linkboi).", inline = False)
        await self.bot.send_message(ctx.message.channel, embed = info)
    @commands.command(pass_context = True)
    async def help(self, ctx):
        stuff = discord.Embed(title = "Info on the game has been sent to your dm!", colour = discord.Colour.orange())
        await self.bot.send_message(ctx.message.channel, embed = stuff)
        embed = discord.Embed(title = "Mafia Game", colour = discord.Colour.orange())
        embed.set_image(url = "https://i0.wp.com/static.lolwallpapers.net/2015/11/Braum-Safe-Breaker-Fan-Art-Skin-By-Karamlik.png")
        embed.add_field(name = "How to play:", value = "To play, there must be at least 5 people in the Mafia party.", inline = False)
        embed.add_field(name = "#1", value = "When the game starts, each player will receive their role through dm.", inline = False)
        embed.add_field(name = "#2", value = "Everyone will go to sleep. The Mafia would be the first to wake up, and through dm he/she can choose which player to kill.", inline = False)
        embed.add_field(name = "#3", value = "After, the doctor will wake up, and he/she can choose a person to save through dm.", inline = False)
        embed.add_field(name = "#4", value = "Finally, the detective will wake up and choose a person to accuse through dm. He/she would be informed if the person is the Mafia. If he/her investigates the suspect, then he/she will be informed that the suspect is the mafia.", inline = False)
        embed.add_field(name = "#5", value = "Everybody wakes up and the bot will inform you through the mafia channel who was killed. The group has a minute to discuss who is the Mafia.", inline = False)
        embed.add_field(name = "#6", value = "Everyone then nominate and vote on people to lynch. The most voted person will then be lynched.")
        embed.add_field(name = "#7", value = "The cycle continues until only if the number of mafias are greater than villagers, the mafia kills everyone, or all the mafia dies.")
        embed.set_footer(text = "For more information, type m.helpR for roles, m.helpC for commands, and m.helpGame for setup.")
        await self.bot.send_message(ctx.message.author, embed = embed)

    @commands.command(pass_context = True)
    async def helpR(self, ctx):
        stuff = discord.Embed(title = "Info on mafia roles has been sent to your dm!", colour = discord.Colour.orange())
        await self.bot.send_message(ctx.message.channel, embed = stuff)
        embed = discord.Embed(title = "Mafia Roles", colour = discord.Colour.orange())
        
        embed.add_field(name = "Mafia", value = "Side: Mafia. Your role is to kill everyone. And don't get caught.", inline = False)
        embed.add_field(name = "Doctor", value = "Side: Villager. Your role is to save people. You cannot save the same person twice in a row.", inline = False)
        embed.add_field(name = "Detective", value = "Side: Villager. Your role is to find the mafia and tell everyone.", inline = False)
        embed.add_field(name = "Suspect", value = "Side: Villager. When inspected by the detective, the suspect would return Mafia, even though the suspect is on the villager's side. The suspect won't know that he/she is a suspect. There must be at least 6 people to have a chance of gaining this role.", inline = False)
        embed.add_field(name = "Jester", value = "Side: Neutral. Your goal is to get lynched by the mob in order to win.", inline = False)
        embed.set_footer(text = "For more information, type m.help for how the game works, m.helpC for commands, and m.helpGame for setup.")
        await self.bot.send_message(ctx.message.author, embed = embed)
    
    @commands.command(pass_context = True)
    async def helpC(self, ctx):
        stuff = discord.Embed(title = "Info on the commands has been sent to your dm!", description = "Note: I am case sensitive(working on that)", colour = discord.Colour.orange())
        await self.bot.send_message(ctx.message.channel, embed = stuff)
        embed = discord.Embed(title = "Mafia Commands", colour = discord.Colour.orange())
        embed.add_field(name = "m.info", value = "Shows the bot's information!", inline = False)
        embed.add_field(name = "m.join", value = "Joins the current mafia party.", inline = False)
        embed.add_field(name = "m.leave", value = "Leaves the current mafia party.", inline = False)
        embed.add_field(name = "m.party", value = "Displays current party.", inline = False)
        embed.add_field(name = "m.setGame", value = "Sets up the game.(Must do before m.start)", inline = False)
        embed.add_field(name = "m.start", value = "Starts the game with the current people in the mafia party. Must do m.setGame first.", inline = False)
        embed.add_field(name = "m.record @person", value = "Reveals information about a person's game record.", inline = False)
        embed.set_footer(text = "For more information, type m.help for how the game works, m.helpGame for setup, and m.helpAdmin to see admin commands.")
        await self.bot.send_message(ctx.message.author, embed = embed)
    
    @commands.command(pass_context = True)
    async def helpAdmin(self, ctx):
      stuff = discord.Embed(title = "Info on admin commands has been sent to your dm!", colour = discord.Colour.orange())
      await self.bot.send_message(ctx.message.channel, embed = stuff)
      embed = discord.Embed(title = "Admin Commands", colour = discord.Colour.orange())
      embed.add_field(name = "m.clearParty", value = "Clears current party.")
      embed.add_field(name = "m.stopGame", value = "With this command, the bot will stop the current game after the round finishes.")
      embed.set_footer(text = "For more information, type m.helpC for commands, m.helpR for roles, m.helpC for commands, and m.helpGame for setup.")
      await self.bot.send_message(ctx.message.author, embed = embed)

    @commands.command(pass_context = True)
    async def helpGame(self, ctx):
        stuff = discord.Embed(title = "Info on setting the game has been sent to your dm!", colour = discord.Colour.orange())
        await self.bot.send_message(ctx.message.channel, embed = stuff)
        embed = discord.Embed(title = "Mafia Setup", colour = discord.Colour.orange())
        embed.add_field(name = "Requirement:", value = "There must be at least 5 people in the mafia party and no more than 10.", inline = False)
        embed.add_field(name = "Setting the Game:", value = "Everyone playing must enter m.join to join the party. Type m.leave to leave the party.", inline = False)
        embed.add_field(name = "Step 1", value = "Enter m.setGame to set up and assign the roles for the game.(Roles are sent through dm.", inline = False)
        embed.add_field(name = "Step 2", value = "Enter m.start to start the game.", inline = False)
        embed.add_field(name = "Step 3", value = "Play", inline = False)
        embed.set_footer(text = "For more information, type m.helpR for roles, m.helpC for commands, and m.help for how the game works.")
        await self.bot.send_message(ctx.message.author, embed = embed)
def setup(bot):
    bot.add_cog(helpC(bot))