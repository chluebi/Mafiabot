import discord
from discord.ext import commands
import random
import MAFIA.gameRole as ParentR
GameR = ParentR.GameR

class Spy(GameR):
    def __init__(self, user):
        GameR.__init__(self, user)
        self.side = "villager"
        self.lastTarget = None
        self.message = None

        self.SpyTargets = None
        self.name = "spy"
    async def sendPrompt(self, currentP, dmTime):
        self.SpyTargets = []
        for player, data in currentP.items():
            if data.roleName != "spy" and data.alive:
                self.SpyTargets.append(player.name.lower())
        
        self.message = await GameR.makePompt(self, self.SpyTargets, "Who do you want to spy on tonight?", "React with the associated emoji to choose your targets!",  "https://cdn.vox-cdn.com/thumbor/I3GT91gn4U3jc4HmBY5LjowXzuM=/0x0:1215x717/1200x800/filters:focal(546x35:740x229)/cdn.vox-cdn.com/uploads/chorus_image/image/57172117/Evelynn_Splash_4.0.jpg", "You have {} seconds to choose.".format(dmTime), discord.Colour.blurple())
    
    async def getTarget(self):
        self.victim = await GameR.getResult(self, self.message, self.SpyTargets)