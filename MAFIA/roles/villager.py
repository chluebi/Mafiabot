import discord
from discord.ext import commands
import random
import sys

import MAFIA.gameRole as ParentR
GameR = ParentR.GameR

class Villager(GameR):
    def __init__(self):
        GameR.__init__(self)
        self.side = "villager"
        self.name = "villager"
    
    async def sendInfo(self):
        embed = discord.Embed(title = "You are just a normal innocent villager who might get accused for crimes you didn't commit ¯\_(ツ)_/¯ ", colour = discord.Colour.dark_gold())
        embed.set_image(url = "https://www.lifewire.com/thmb/0V5cpFjHpDgs5-c3TLP_V29SNL4=/854x480/filters:fill(auto,1)/uFiT1UL-56a61d203df78cf7728b6ae2.png")
        await self.user.send(embed = embed)

    async def check(self, visitor_role_obj):
        return
    
    async def perform(self, currentP):
        return