import discord
from discord.ext import commands
import random
import sys

import MAFIA.gameRole as ParentR
GameR = ParentR.GameR

class Exe(GameR):
    def __init__(self):
        GameR.__init__(self)
        self.side = "neutral"
        self.target = None
        self.name = "executioner"
    async def sendInfo(self):
        embed = discord.Embed(title = "You are the executioner. You will be given a target, and your job is to convince the town to lynch your target to win. If you target is killed by other ways you will turn into a Jester.", description = "Side: Neutral", colour = discord.Colour.teal())
        embed.set_image(url = "https://www.mobafire.com/images/champion/skins/landscape/dr-mundo-executioner.jpg")
        await self.user.send(embed = embed)
    async def check(self, visitor_role_obj):
        return
    
    async def perform(self, currentP):
        return

