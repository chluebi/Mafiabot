import discord
from discord.ext import commands
import random
import sys
sys.path.insert(1, 'C:/Users/Ernest/Desktop/Mafiabot/Mafiabot-1/MAFIA')
import gameRole as ParentR
GameR = ParentR.GameR

class PI(GameR):
    def __init__(self, user):
        GameR.__init__(self, user)
        self.side = "villager"
        self.message = None
        self.PITargets = []
        self.name = "PI"
        self.targets = []

    async def sendPrompt(self, currentP, dmTime):
        self.PITargets = []
        for player, data in currentP.items():
            if data.roleName != "PI" and data.alive:
                self.PITargets.append(player.name.lower())
        
        self.message = await GameR.makePompt(self, self.PITargets, "Which two people do you want to investigate tonight?", "React with the associated emoji to choose your targets!",  "https://i.pinimg.com/originals/08/64/a5/0864a55a5c3b2b8e0e2b1b8c231c93a3.jpg", "You have {} seconds to choose.".format(dmTime), discord.Colour.blurple())

    async def getTarget(self):
        cache_msg = await self.user.fetch_message(self.message.id)
        answerEmojis = []
        count = 0
        for reaction in cache_msg.reactions:
            async for user in reaction.users():
                if user.id != 480553111971430420 and reaction.emoji in self.reactionList:
                    answerEmojis.append(reaction.emoji)
                    count+=1
                    if count == 2:
                        break
                    
        reactionList = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯', '🇰', '🇱', '🇲', '🇳', '🇴', '🇵']
        
        if  len(answerEmojis) ==2 and '🇦' not in answerEmojis:
            index1 = reactionList.index(answerEmojis[0])
            index2 = reactionList.index(answerEmojis[1])
            await self.user.send("You chose " + self.PITargets[index1-1] + " and " + self.PITargets[index2-1])

            self.PITargets = [self.PITargets[index1-1], self.PITargets[index2-1]]
            print(self.PITargets)
        else:
            self.PITargets = []
            await self.user.send("You chose nothing. Lmao.")
            
        return