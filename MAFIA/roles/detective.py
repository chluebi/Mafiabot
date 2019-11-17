import discord
from discord.ext import commands
import random
import MAFIA.gameRole as ParentR
GameR = ParentR.GameR

class Det(GameR):
    def __init__(self, user):
        GameR.__init__(self, user)
        self.side = "villager"
        self.message = None
        self.detTargets = None

        self.name = "detective"
    async def sendPrompt(self, currentP, dmTime):
        self.detTargets = []
        for player, data in currentP.items():
            if data.roleName != "detective" and data.alive:
                self.detTargets.append(player.name.lower())
        
        self.message = await GameR.makePompt(self, self.detTargets, "Who do you suspect?", "React with the associated emoji to choose your target!", "https://na.leagueoflegends.com/sites/default/files/styles/scale_xlarge/public/upload/cops_1920.jpg?itok=-T6pbISx", "You have {} seconds to choose.".format(dmTime), discord.Colour.blue())

    async def getTarget(self):
        self.victim = await GameR.getResult(self, self.message, self.detTargets)
