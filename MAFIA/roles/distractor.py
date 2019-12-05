import discord
from discord.ext import commands
import random
import sys

import MAFIA.gameRole as ParentR
GameR = ParentR.GameR

class Distractor(GameR):
    def __init__(self):
        GameR.__init__(self)
        self.side = "villager"
        self.message = None
        self.cooldown = False
        self.disTargets = None
        self.name = "distractor"

    async def sendInfo(self):
        embed = discord.Embed(title = "You are the Distractor. You can stop one person from using their role each night.", description = "Side: Villager", colour = discord.Color.orange())
        embed.set_image(url = "https://media.wired.com/photos/59a459d3b345f64511c5e3d4/master/pass/MemeLoveTriangle_297886754.jpg")
        await self.user.send(embed = embed)

    async def sendPrompt(self, currentP, dmTime):
        self.disTargets = []
        for role in currentP.values():
            if role.name != "distractor" and role.alive:
                self.disTargets.append(role.user.name.lower())
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

    async def check(self, visitor_role_obj):
        return
    
    async def perform(self, currentP):
        if not self.victim:
            return
        victimRoleObj = self.findRoleObj(currentP, self.victim)
        checkTest = await victimRoleObj.check(self)
        if checkTest:
            return checkTest
        if victimRoleObj.victim:
            victimEmbed = discord.Embed(title = "Sorry, you got distracted tonight...", description = "Hey look a butterfly...:butterfly:", colour = discord.Colour.blurple())
            victimEmbed.set_thumbnail(url = "https://images.complex.com/complex/image/upload/c_limit,dpr_auto,q_90,w_720/fl_lossy,pg_1/krabs_rag3do.jpg")
            await victimRoleObj.user.send(embed = victimEmbed)
            embed = self.makeEmbed("You have successfully distracted {} tonight".format(self.victim))
            embed.set_thumbnail(url = victimRoleObj.user.avatar_url)
            await self.user.send(embed = embed)
            victimRoleObj.victim = None
        else:
            await self.user.send("Lol that person didn't do anything tonight...")
        
        