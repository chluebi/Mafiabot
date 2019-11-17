import discord
from discord.ext import commands
import random
import MAFIA.gameRole as ParentR
GameR = ParentR.GameR

class Framer(GameR):
    def __init__(self, user):
        GameR.__init__(self, user)
        self.side = "mafia"
        self.message = None

        self.name = "framer"
    async def sendPrompt(self, currentP, dmTime):
        self.framerTargets = []
        for player, data in currentP.items():
            if data.roleName != "mafia" and data.roleName !="framer" and data.roleName != "godfather" and data.alive:
                self.framerTargets.append(player.name.lower())
        
        self.message = await GameR.makePompt(self, self.framerTargets, "Who do you want to frame?", "React with the associated emoji to choose your target!", "https://cdn.drawception.com/images/panels/2017/12-17/zKXCDSXfeA-4.png", "You have {} seconds to choose.".format(dmTime), discord.Colour.red())

    async def getTarget(self):
        self.victim = await GameR.getResult(self, self.message, self.framerTargets)