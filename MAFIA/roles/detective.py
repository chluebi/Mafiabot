import discord
from discord.ext import commands
import random
import sys

import MAFIA.gameRole as ParentR
GameR = ParentR.GameR

class Det(GameR):
    def __init__(self):
        GameR.__init__(self)
        self.side = "villager"
        self.message = None
        self.detTargets = None

        self.name = "detective"
    
    async def sendInfo(self):
        embed = discord.Embed(title = "You are the Detective. Your job is to find the Mafia.", description = "Side: Villager", colour = discord.Colour.orange())
        embed.set_image(url = "https://media.altpress.com/uploads/2019/02/Screen-Shot-2019-02-26-at-1.20.38-PM.png")
        await self.user.send( embed = embed)
    async def sendPrompt(self, currentP, dmTime):
        self.detTargets = []
        for role in currentP.values():
            if role.name != "detective" and role.alive:
                self.detTargets.append(role.user.name.lower())
        
        self.message = await GameR.makePompt(self, self.detTargets, "Who do you suspect?", "React with the associated emoji to choose your target!", "https://na.leagueoflegends.com/sites/default/files/styles/scale_xlarge/public/upload/cops_1920.jpg?itok=-T6pbISx", "You have {} seconds to choose.".format(dmTime), discord.Colour.blue())

    async def getTarget(self):
        self.victim = await GameR.getResult(self, self.message, self.detTargets)

    async def check(self, visitor_role_obj):
        return

    async def perform(self, currentP):
        if not self.victim:
            return
        
        victimRoleObj = self.findRoleObj(currentP, self.victim)
        checkTest = await victimRoleObj.check(self)
        if checkTest:
            return checkTest
        framerObj = self.roleObjRolename(currentP, "framer")
        mafiabois = ["mafia", "framer", "godfather"]
        if framerObj and framerObj.victim:
            framerVictimObj = self.findRoleObj(currentP, framerObj.victim)
            mafiabois.append(framerVictimObj.name)
        if victimRoleObj.name in mafiabois:
            embedDet = self.makeEmbed("Yes. That person is on the mafia's side. Now try to convince the others. Please return to the mafia chat now.")
            embedDet.set_thumbnail(url = "http://www.clker.com/cliparts/P/S/9/I/l/S/234-ed-s-sd-md.png")
        else:
            embedDet = self.makeEmbed("Sorry. That person is not the mafia. Please return to the mafia chat now.")
            embedDet.set_thumbnail(url = "https://iconsplace.com/wp-content/uploads/_icons/ff0000/256/png/thumbs-down-icon-14-256.png")
        await self.user.send(embed = embedDet)
        
