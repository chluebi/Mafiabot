import discord
from discord.ext import commands
import asyncio

class Troll(commands.Cog):


    def __init__(self, bot):
        self.bot = bot

    #What can I say, I like to troll xd
    #I lost a bet
    @commands.command(pass_context = True)
    async def reveal(self, ctx, user: discord.Member):
        if user.id == 327260671458803713:
            await ctx.channel.send("This person's role is detective")
        elif user.id == 217380909815562241:
            await ctx.channel.send("This person's role is the almighty linkboi")
        elif user.id == 252655058733367296:
            await ctx.channel.send("This person's role is jester")
        elif user.id == 359200842563190787:
            await ctx.send("A weeb.")
        elif user.id == 124745315902291968:
            await ctx.send("Joe.")
        elif user.id == 216800764927016960:
            await ctx.send("BTS Fan.")
        else:
            await ctx.channel.send("Idk lol")

    @commands.command(pass_context = True)
    async def say(self, ctx, *, args):
        if ctx.author.id != 217380909815562241 and ctx.author.id != 124745315902291968:
            return
        await ctx.send(args)
        try:
            await ctx.message.delete()
        except Exception as e:
            print(str(e))

    @commands.command(pass_context = True)
    async def killAll(self, ctx):
        channel = ctx.channel
        await channel.send("Running `killAll.exe`...")
        await asyncio.sleep(5)
        await channel.send("Error.\nTraceback (most recent call last):\n`self.killAll(server)`\nraise `NotFound(r, data)`\ndiscord.errors.NotFound: 404 NOT FOUND(error code 10003): Everyone is already dead inside.")


    @commands.command(pass_context = True)
    async def linkboi(self, ctx):
        if ctx.author.name == "linkboi":

            await ctx.channel.send("Everyone's roles are send to your dm sir.")
        else:
            await ctx.channel.send("You're not linkboi.")


    @commands.command(pass_context = True)
    async def blacklist(self, ctx, user:discord.Member):
        if ctx.author.id != 217380909815562241:
            await ctx.channel.send("You're not linkboi.")
            return
        await ctx.channel.send(user.name + " has been added to the Blacklist. Feelsbad.")
    
def setup(bot):
    bot.add_cog(Troll(bot))