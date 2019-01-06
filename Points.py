import discord
from discord.ext import commands
import asyncio
import os
import json

class Points:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context = True)
    async def info(self, ctx, user: discord.Member):
        server = ctx.message.server
        if user == None:
            person = ctx.message.author
        else:
            person = user
        
        with open('players.json', 'r') as f:
            players = json.load(f)

        if person.id in players[server.id].keys():
            wins = players[server.id][person.id]["Wins"]
            games = players[server.id][person.id]["Games"]
            embed = discord.Embed(title = "{}'s info".format(person.name), colour = discord.Colour.gold())
            embed.add_field(name = "Total wins", value = "{}".format(wins), inline = True)
            embed.add_field(name = "Total games played", value = "{}".format(games))
            embed.set_thumbnail(url = person.avatar_url)
        else:
            embed = discord.Embed(title = "You don't have any records. Finish a game of Mafia to start!", colour = discord.Colour.gold())
        await self.bot.send_message(ctx.message.channel, embed = embed)


def setup(bot):
    bot.add_cog(Points(bot))