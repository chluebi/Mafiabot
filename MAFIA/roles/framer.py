import discord
from discord.ext import commands
import random
import sys

import MAFIA.gameRole as ParentR
GameR = ParentR.GameR

class Framer(GameR):
    def __init__(self):
        GameR.__init__(self)
        self.side = "mafia"
        self.message = None

        self.name = "framer"
    
    async def sendInfo(self):
        embed = discord.Embed(title = "You're the framer. Your job is to frame innocent people to look like mafias to the detective. ", description = "Side: Mafia", colour = discord.Colour.red())
        embed.set_image(url = "https://i.ytimg.com/vi/Cgj4Mkl6lHs/maxresdefault.jpg")
        await self.user.send( embed = embed)
        
    async def sendPrompt(self, currentP, dmTime):
        self.framerTargets = []
        for role in currentP.values():
            if role.side != "mafia" and role.alive:
                self.framerTargets.append(role.user.name.lower())
        
        self.message = await GameR.makePompt(self, self.framerTargets, "Who do you want to frame?", "React with the associated emoji to choose your target!", "https://cdn.drawception.com/images/panels/2017/12-17/zKXCDSXfeA-4.png", "You have {} seconds to choose.".format(dmTime), discord.Colour.red())

    async def getTarget(self):
        self.victim = await GameR.getResult(self, self.message, self.framerTargets)
    
    
    async def check(self, visitor_role_obj):
        return
    
    async def perform(self, currentP):
        if not self.victim:
            return
        victimRoleObj = self.findRoleObj(currentP, self.victim)
        checkTest = await victimRoleObj.check(self)
        if checkTest:
            return checkTest
        
    
    