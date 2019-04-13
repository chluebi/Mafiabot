import discord
from discord.ext import commands
import asyncio
import os
import json
import logging
class Points:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context = True)
    async def record(self, ctx, user: discord.Member):
        server = ctx.message.server
        if user == None:
            person = ctx.message.author
        else:
            person = user
        
        with open('players.json', 'r') as f:
            players = json.load(f)
        if not server.id in players:
            players[server.id] = {}
        if not person.id in players[server.id].keys():
            players[server.id][person.id] = {}
            players[server.id][person.id]["Wins"] = 0
            players[server.id][person.id]["Games"] = 0
        with open('players.json', 'w') as f:
            json.dump(players, f)

        if person.id in players[server.id].keys():
            wins = players[server.id][person.id]["Wins"]
            games = players[server.id][person.id]["Games"]
            embed = discord.Embed(title = "{}'s info".format(person.name), colour = discord.Colour.gold())
            embed.add_field(name = "Total wins", value = "{}".format(wins), inline = True)
            embed.add_field(name = "Total games played", value = "{}".format(games))
            embed.set_thumbnail(url = person.avatar_url)

        await self.bot.send_message(ctx.message.channel, embed = embed)

    @commands.command(pass_context = True)
    async def test(self, ctx):
        logging.basicConfig(filename = "mafia.log", filemode = 'w', format = '%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
        logging.debug("Hi")
        await self.bot.send_message(ctx.message.channel, "done")
def setup(bot):
    bot.add_cog(Points(bot))