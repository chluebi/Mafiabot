import discord
from discord.ext import commands
import asyncio
import os
import json
import logging
class Points(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context = True)
    async def record(self, ctx, user: discord.Member):
        server = ctx.guild
        channel = ctx.channel
        if user == None:
            person = ctx.message.author
        else:
            person = user
        
        with open('players.json', 'r') as f:
            players = json.load(f)
        if not str(server.id) in players.keys():
            players[str(server.id)] = {}
        if not str(person.id) in players[str(server.id)].keys():
            players[str(server.id)][str(person.id)] = {}
            players[str(server.id)][str(person.id)]["Wins"] = 0
            players[str(server.id)][str(person.id)]["Games"] = 0
        with open('players.json', 'w') as f:
            json.dump(players, f)

        if str(person.id) in players[str(server.id)].keys():
            wins = players[str(server.id)][str(person.id)]["Wins"]
            games = players[str(server.id)][str(person.id)]["Games"]
            embed = discord.Embed(title = "{}'s info".format(person.name), colour = discord.Colour.gold())
            embed.add_field(name = "Total wins", value = "{}".format(wins), inline = True)
            embed.add_field(name = "Total games played", value = "{}".format(games))
            embed.set_thumbnail(url = person.avatar_url)

        await channel.send(embed = embed)
def setup(bot):
    bot.add_cog(Points(bot))