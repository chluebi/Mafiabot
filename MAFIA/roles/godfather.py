import discord
from discord.ext import commands
import random
import sys
sys.path.insert(1, 'C:/Users/Ernest/Desktop/Mafiabot/Mafiabot-1/MAFIA')
import gameRole as ParentR
GameR = ParentR.GameR

class Godfather(GameR):
    def __init__(self, user):
        GameR.__init__(self, user)
        self.side = "mafia"
        self.message = None
        self.mafiaPlayers = []
        self.mafiatargets = []
        self.name = "godfather"
        self.mafiaSide = ["mafia", "godfather", "framer"]
    async def sendPrompt(self, currentP, dmTime):
        self.mafiatargets = []
        for player in currentP.keys():
            if not currentP[player].name in self.mafiaSide and player.alive:
                self.mafiatargets.append(player.user.name.lower())
        
        self.message = await GameR.makePompt(self, self.mafiatargets, "Who would you like to kill tonight Godfather?", "React with the associated emoji to choose your target!", "https://www.mobafire.com/images/champion/skins/landscape/graves-mafia.jpg", "You have {} seconds to choose.".format(dmTime), discord.Colour.red())

    async def getTarget(self):
        self.victim = await GameR.getResult(self, self.message, self.mafiatargets)
        if self.victim:
            if self.mafiaPlayers and self.mafiaPlayers[0].user:
                killer = random.choice(self.mafiaPlayers)
                killer.victim = self.victim
                self.victim = None
                embed = discord.Embed(title = "The GodFather have sent {} to attack {}".format(killer.user.name, killer.victim), colour = discord.Colour.red())
                for role in self.mafiaPlayers:
                    await role.user.send(embed = embed)
                
                await self.user.send(embed = embed)
            else:
                embed = discord.Embed(title = "You have decided to attack {}".format(self.victim))
                await self.user.send(embed = embed)