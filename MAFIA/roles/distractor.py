import discord
from discord.ext import commands
import random
import MAFIA.gameRole as ParentR
GameR = ParentR.GameR

class Distractor(GameR):
    def __init__(self, user):
        GameR.__init__(self, user)
        self.side = "villager"
        self.message = None
        self.cooldown = False
        self.disTargets = None
        self.name = "distractor"


    async def sendPrompt(self, currentP, dmTime):
        self.disTargets = []
        for player, data in currentP.items():
            if data.roleName != "distractor" and data.alive:
                self.disTargets.append(player.name.lower())
        if not self.cooldown:
            self.message = await GameR.makePompt(self, self.disTargets, "Who do you want to distract tonight?", "React with the associated emoji to choose your target!",  "https://www.dolmanlaw.com/wp-content/uploads/2017/03/The-Many-Types-of-Technology-that-can-Cause-Distracted-Driving-1.jpg", "You have {} seconds to choose.".format(dmTime), discord.Colour.orange())
        else:
            embed = discord.Embed(title = "You need some rest tonight...", description = "Maybe you can distract someone again tomorrow...", colour = discord.Colour.dark_blue())
            embed.set_image(url = "https://cdn2.iconfinder.com/data/icons/real-estate-set-2/512/721303-16-512.png")
            await self.user.send(embed = embed)
    
    async def getTarget(self):
        if not self.cooldown:
            self.victim = await GameR.getResult(self, self.message, self.disTargets)
            if self.victim:
                self.cooldown = True
        else:
            self.victim = None
            self.cooldown = False