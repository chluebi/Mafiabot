import discord
from discord.ext import commands
import random
import sys

import MAFIA.gameRole as ParentR
GameR = ParentR.GameR
class Baiter(GameR):
    def __init__(self):
        GameR.__init__(self)
        self.side = "neutral"
        self.name = "baiter"
        self.killCount = 0
    
    async def sendInfo(self):
        embed = discord.Embed(title = "You are the Baiter. You are the embodiment of pure chaos, but you're a lazy killer. That's why you sit at home and kill whoever visits you. Kill 3 people to win.", description = "Side: Neutral", colour = discord.Colour.blurple())
        embed.set_image(url = "https://i.kym-cdn.com/entries/icons/original/000/028/431/kirby.jpg")
        await self.user.send(embed= embed)
        
    async def check(self, visitor_role_obj):
        await visitor_role_obj.die()
        visitor_role_obj.victim = None
        self.killCount += 1
        await self.user.send(visitor_role_obj.user.name + " visited you last night. One kill down...")
        return discord.Embed(title = visitor_role_obj.user.name + " mysteriously died last night...", colour = discord.Colour.blue())
    
    async def perform(self, currentP):
        return
