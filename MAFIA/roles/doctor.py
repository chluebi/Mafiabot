import discord
from discord.ext import commands
import random
import MAFIA.gameRole as ParentR
GameR = ParentR.GameR

class Doctor(GameR):
    def __init__(self, user):
        GameR.__init__(self, user)
        self.lastHeal = None
        self.side = "villager"
        self.message = None
        self.docTargets = None

        self.name= "doctor"
    async def sendPrompt(self, currentP, dmTime):
        self.docTargets = []
        for player, data in currentP.items():
            if player.name.lower() != self.lastHeal and data.alive:
                self.docTargets.append(player.name.lower())
        
        self.message = await GameR.makePompt(self, self.docTargets, "Who do you want to save?", "React with the associated emoji to choose your target!", "https://vignette.wikia.nocookie.net/leagueoflegends/images/f/f7/Akali_NurseSkin_old.jpg/revision/latest?cb=20120609043410", "You have {} seconds to choose.".format(dmTime), discord.Colour.blue())

    async def getTarget(self):
        self.victim = await GameR.getResult(self, self.message, self.docTargets)
        
