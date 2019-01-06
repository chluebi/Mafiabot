import discord
from discord.ext import commands

class helpC:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context = True)
    async def help(self, ctx):
        stuff = discord.Embed(title = "Info on the game has been sent to your dm!", colour = discord.Colour.orange())
        await self.bot.send_message(ctx.message.channel, embed = stuff)
        embed = discord.Embed(title = "Mafia Game", colour = discord.Colour.orange())
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
        embed = discord.Embed(title = "Mafia Roles", colour = discord.Colour.orange())
        embed.add_field(name = "Mafia", value = "Side: Mafia. Your role is to kill everyone. And don't get caught.", inline = False)
        embed.add_field(name = "Doctor", value = "Side: Villager. Your role is to save people. You cannot save the same person twice in a row.", inline = False)
        embed.add_field(name = "Detective", value = "Side: Villager. Your role is to find the mafia and tell everyone.", inline = False)
        embed.add_field(name = "Suspect", value = "Side: Villager. When inspected by the detective, the suspect would return Mafia, even though the suspect is on the villager's side. The suspect won't know that he/she is a suspect. There must be at least 6 people to have a chance of gaining this role.", inline = False)
        embed.add_field(name = "Jester", value = "Side: Neutral. Your goal is to get lynched by the mob in order to win.", inline = False)
        await self.bot.send_message(ctx.message.author, embed = embed)
    
    @commands.command(pass_context = True)
    async def helpC(self, ctx):
        embed = discord.Embed(title = "Mafia Commands", colour = discord.Colour.orange())
        embed.add_field(name = "m.join", value = "Joins the current mafia party.", inline = False)
        embed.add_field(name = "m.leave", value = "Leaves the current mafia party.", inline = False)
        embed.add_field(name = "m.party", value = "Displays current party.", inline = False)
        embed.add_field(name = "m.setGame", value = "Sets up the game.(Must do before m.start)", inline = False)
        embed.add_field(name = "m.start", value = "Starts the game with the current people in the mafia party. Must do m.setGame first.", inline = False)
        embed.add_field(name = "m.info @person", value = "Reveals information about a person's game record.", inline = False)
        embed.set_footer(text = "Type m.helpAdmin to see admin commands.")
        await self.bot.send_message(ctx.message.author, embed = embed)
    
    @commands.command(pass_context = True)
    async def helpAdmin(self, ctx):
      embed = discord.Embed(title = "Admin Commands", colour = discord.Colour.orange())
      embed.add_field(name = "m.clearParty", value = "Clears current party.")
      embed.add_field(name = "m.stopGame", value = "With this command, the bot will stop the current game after the round finishes.")
      await self.bot.send_message(ctx.message.author, embed = embed)

    @commands.command(pass_context = True)
    async def helpGame(self, ctx):
        embed = discord.Embed(title = "Mafia Setup", colour = discord.Colour.orange())
        embed.add_field(name = "Requirement:", value = "There must be at least 5 people in the mafia party.", inline = False)
        embed.add_field(name = "Joining the Game:", value = "Everyone playing must enter /join to join the party. Type /leave to leave the party.", inline = False)
        embed.add_field(name = "Step 1", value = "Enter m.setGame to set up and assign the roles for the game.", inline = False)
        embed.add_field(name = "Step 2", value = "Enter m.start to start the game.", inline = False)
        embed.add_field(name = "Step 3", value = "Play", inline = False)
        await self.bot.send_message(ctx.message.author, embed = embed)
def setup(bot):
    bot.add_cog(helpC(bot))