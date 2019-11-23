import discord
from discord.ext import commands
import random
import sys
sys.path.insert(1, 'C:/Users/Ernest/Desktop/Mafiabot/Mafiabot-1/MAFIA')
import gameRole as ParentR
class Vig(ParentR.GameR):
    def __init__(self, user):
        ParentR.GameR.__init__(self, user)
        self.side = "villager"
        self.message = None

        self.name = "vigilante"
    async def sendPrompt(self, currentP, dmTime):
        self.vigTargets = []
        for player, data in currentP.items():
            if data.roleName != "vigilante" and data.alive:
                self.vigTargets.append(player.name.lower())
        
        self.message = await ParentR.GameR.makePompt(self, self.vigTargets, "Who do you want to shoot tonight?", "React with the associated emoji to choose your target!",  "https://pmcdeadline2.files.wordpress.com/2018/03/arrow.png?w=446&h=299&crop=1", "You have {} seconds to choose.".format(dmTime), discord.Colour.green())
    async def getTarget(self):
        self.victim = await ParentR.GameR.getResult(self, self.message, self.vigTargets)

    
    async def perform(self):
        return