import discord
from discord.ext import commands
import random
import sys

import MAFIA.gameRole as ParentR
GameR = ParentR.GameR

class Spy(GameR):
    def __init__(self):
        GameR.__init__(self)
        self.side = "villager"
        self.lastTarget = None
        self.message = None

        self.SpyTargets = None
        self.name = "spy"
    
    async def sendInfo(self):
        embed = discord.Embed(title = "You are the spy. You can select a target each night and see which person they visit that night.", description = "Side: Villager", colour = discord.Colour.blurple())
        embed.set_image(url = "https://na.leagueoflegends.com/sites/default/files/styles/scale_xlarge/public/upload/secret_agent_xinzhao_final_1920.jpg?itok=ulTb2lPD")
        await self.user.send(embed = embed)
    async def sendPrompt(self, currentP, dmTime):
        self.SpyTargets = []
        for role in currentP.values():
            if role.name != "spy" and role.alive:
                self.SpyTargets.append(role.user.name.lower())
        
        self.message = await GameR.makePompt(self, self.SpyTargets, "Who do you want to spy on tonight?", "React with the associated emoji to choose your targets!",  "https://cdn.vox-cdn.com/thumbor/I3GT91gn4U3jc4HmBY5LjowXzuM=/0x0:1215x717/1200x800/filters:focal(546x35:740x229)/cdn.vox-cdn.com/uploads/chorus_image/image/57172117/Evelynn_Splash_4.0.jpg", "You have {} seconds to choose.".format(dmTime), discord.Colour.blurple())
    
    async def getTarget(self):
        self.victim = await GameR.getResult(self, self.message, self.SpyTargets)
    
    async def check(self, visitor_role_obj):
        return
    
    async def perform(self, currentP):
        if not self.victim:
            return
        role = self.findRoleObj(currentP, self.victim)
        checkTest = await role.check(self)
        if checkTest:
            return checkTest
        if role.name.lower() != "pi" and role.victim:
            embed = discord.Embed(title = "Your target {} visited {} tonight. Good luck figuring out the rest lmao.".format(self.victim, role.victim), colour = discord.Colour.blue())
            roleVisitedVictim = self.findRoleObj(currentP, role.victim)
            embed.set_thumbnail(url = roleVisitedVictim.user.avatar_url)
            await self.user.send(embed = embed)
        else:
            await self.user.send("Your target apparently didn't visit anyone tonight. Feelsbad.")
        return