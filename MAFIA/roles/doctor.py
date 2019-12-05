import discord
from discord.ext import commands
import random
import sys
# insert at 1, 0 is the script path (or '' in REPL)

import MAFIA.gameRole as ParentR
GameR = ParentR.GameR

class Doctor(GameR):
    def __init__(self):
        GameR.__init__(self)
        self.lastHeal = None
        self.side = "villager"
        self.message = None
        self.docTargets = None

        self.name= "doctor"
    
    async def sendInfo(self):
        embed = discord.Embed(title = "You are the Doctor. Your job is to save people. But you can't save the same person twice in a row.", description = "Side: Villager", colour = discord.Colour.blue())
        embed.set_image(url = "https://i.chzbgr.com/full/9099359744/h095998C9/")
        await self.user.send( embed = embed)
        
    async def sendPrompt(self, currentP, dmTime):
        self.docTargets = []
        for role in currentP.values():
            if role.user.name.lower() != self.lastHeal and role.alive:
                self.docTargets.append(role.user.name.lower())
        
        self.message = await GameR.makePompt(self, self.docTargets, "Who do you want to save?", "React with the associated emoji to choose your target!", "https://vignette.wikia.nocookie.net/leagueoflegends/images/f/f7/Akali_NurseSkin_old.jpg/revision/latest?cb=20120609043410", "You have {} seconds to choose.".format(dmTime), discord.Colour.blue())

    async def getTarget(self):
        self.victim = await GameR.getResult(self, self.message, self.docTargets)
    
    async def check(self, visitor_role_obj):
        return
    
    async def perform(self, currentP):
        self.lastHeal = self.victim
        if not self.victim:
            return
        

        if self.victim == self.user.name.lower():
            victimRoleObj = self
        else:
            victimRoleObj = self.findRoleObj(currentP, self.victim)
            checkTest = await victimRoleObj.check(self)
            if checkTest:
                return checkTest
        
        mafiaObj = self.roleObjRolename(currentP, "mafia")
        godfatherObj = self.roleObjRolename(currentP, "godfather")
        mafiaTarget = None
        if mafiaObj:
            mafiaTarget = mafiaObj.victim
        elif godfatherObj:
            mafiaTarget = godfatherObj.victim
        
            
        if mafiaTarget and mafiaTarget == self.victim:
            if mafiaTarget == self.user.name.lower():
                self.alive = True
            else:
                victimRoleObj.alive = True
            print("duh")
            return self.makeEmbed("Wait a minute...The doctor somehow used the magical powers of medicine and saved {} from death!".format(self.victim))
        
        if mafiaTarget:
            print("huh")
            if mafiaTarget == self.user.name.lower():
                await self.die()
                return
            mafiaVictimObj = self.findRoleObj(currentP, mafiaTarget)
            await mafiaVictimObj.die()
            return
        
