import discord
from discord.ext import commands
import random
import sys

import MAFIA.gameRole as ParentR
GameR = ParentR.GameR

class Jester(GameR):
    def __init__(self):
        GameR.__init__(self)
        self.side = "neutral"
        self.name = "jester"
        
    async def sendInfo(self):
        embed = discord.Embed(title = "You are the Jester. Your win condition is to get the town to lynch you.", description = "Side: Neutral", colour = discord.Colour.teal())
        embed.set_image(url = "https://runes.lol/image/generated/championtiles/Shaco.jpg")
        await self.user.send(embed = embed)

    async def check(self, visitor_role_obj):
        return
    
    async def perform(self, currentP):
        return