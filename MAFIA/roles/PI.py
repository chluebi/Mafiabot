import discord
from discord.ext import commands
import random
import sys

import MAFIA.gameRole as ParentR
GameR = ParentR.GameR

class PI(GameR):
    def __init__(self):
        GameR.__init__(self)
        self.side = "villager"
        self.message = None
        self.PITargets = []
        self.name = "PI"
        self.finalTargets = []
    async def sendInfo(self):
        embed = discord.Embed(title = "You are the PI. You can choose two players each night to see if they are on the same side.", description = "Side: Villager", colour = discord.Colour.purple())
        embed.set_image(url = "https://www.charlestonlaw.net/wp-content/uploads/2018/01/private-investigator.jpg")
        await self.user.send(embed = embed)

    async def sendPrompt(self, currentP, dmTime):
        self.PITargets = []
        for role in currentP.values():
            if role.name != "PI" and role.alive:
                self.PITargets.append(role.user.name.lower())
        
        self.message = await GameR.makePompt(self, self.PITargets, "Which two people do you want to investigate tonight?", "React with the associated emoji to choose your targets!",  "https://i.pinimg.com/originals/08/64/a5/0864a55a5c3b2b8e0e2b1b8c231c93a3.jpg", "You have {} seconds to choose.".format(dmTime), discord.Colour.blurple())

    async def getTarget(self):
        cache_msg = await self.user.fetch_message(self.message.id)
        answerEmojis = []
        count = 0
        for reaction in cache_msg.reactions:
            async for user in reaction.users():
                if user.id != 511786918783090688 and reaction.emoji in self.reactionList:
                    answerEmojis.append(reaction.emoji)
                    count+=1
                    if count == 2:
                        break
                    
        reactionList = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯', '🇰', '🇱', '🇲', '🇳', '🇴', '🇵']
        
        if  len(answerEmojis) ==2 and '🇦' not in answerEmojis:
            index1 = reactionList.index(answerEmojis[0])
            index2 = reactionList.index(answerEmojis[1])
            await self.user.send("You chose " + self.PITargets[index1-1] + " and " + self.PITargets[index2-1])

            self.finalTargets = [self.PITargets[index1-1], self.PITargets[index2-1]]
        else:
            self.finalTargets = []
            await self.user.send("You chose nothing. Lmao.")
            
        return
    
    async def check(self, visitor_role_obj):
        return
    
    async def perform(self, currentP):
        if not self.finalTargets:
            return
            
        target1 = self.findRoleObj(currentP, self.finalTargets[0])
        checkTest = await target1.check(self)
        if checkTest:
            return checkTest
        target2 = self.findRoleObj(currentP, self.finalTargets[1])
        checkTest = await target2.check(self)
        if checkTest:
            return checkTest
            
        if target1.side == target2.side:
            embed = discord.Embed(title = "Yes. {} and {} are both on the same side. It's up to you to figure out what side though lol.".format(target1.user.name,  target2.user.name), colour = discord.Colour.green())
            embed.set_thumbnail(url = "http://www.clker.com/cliparts/P/S/9/I/l/S/234-ed-s-sd-md.png")
        else:
            embed =  discord.Embed(title = "No. {} and {} are not on the same side. Hmmmmmmmmmm.".format(target1.user.name,  target2.user.name), colour = discord.Colour.red())
            embed.set_thumbnail(url = "https://iconsplace.com/wp-content/uploads/_icons/ff0000/256/png/thumbs-down-icon-14-256.png")
        await self.user.send(embed = embed)
        return