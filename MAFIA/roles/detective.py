import discord
from discord.ext import commands
import random
import sys
sys.path.insert(1, 'C:/Users/Ernest/Desktop/Mafiabot/Mafiabot-1/MAFIA')
import gameRole as ParentR
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

    def check(self, visitor_role_obj):
        return

    async def perform(self, currentP):
        if not self.victim:
            return
        
        victimRoleObj = self.findRoleObj(self.victim, currentP)
        if victimRoleObj.check(self):
            return
        
        mafiabois = ["mafia", "framer", "godfather"]
        if victimRoleObj.name in mafiabois:
            embedDet = self.makeEmbed("Yes. That person is on the mafia's side. Now try to convince the others. Please return to the mafia chat now.")
            embedDet.set_thumbnail(url = "http://www.clker.com/cliparts/P/S/9/I/l/S/234-ed-s-sd-md.png")
        else:
            embedDet = self.makeEmbed("Sorry. That person is not the mafia. Please return to the mafia chat now.")
            embedDet.set_thumbnail(url = "https://iconsplace.com/wp-content/uploads/_icons/ff0000/256/png/thumbs-down-icon-14-256.png")
        await self.user.send(embed = embedDet)
        
