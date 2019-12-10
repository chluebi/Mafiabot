import discord
from discord.ext import commands
import asyncio
import os
import json

class Premium(commands.Cog):
    premiumPath = "USER/premium.json"
    premiumID = [606066491028275213]
    def __init__(self, bot):
        self.bot = bot
        with open(self.premiumPath, 'r') as f:
            self.premium = json.load(f)
        
    
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        beforeRoleList = [role.id for role in before.roles]
        afterRoleList = [role.id for role in after.roles]
        checkBefore = any(roleID in self.premiumID for roleID in beforeRoleList)
        checkAfter = any(roleID in self.premiumID for roleID in afterRoleList)
        print(checkBefore, checkAfter)
        if checkBefore and not checkAfter:
            for pLevel in self.premium.values():
                if before.id in pLevel:
                    pLevel.remove(before.id)
                    self.dumpPremium()
                    return

        if not checkBefore and checkAfter:
            for pLevel, pList in self.premium.items():
                if int(pLevel) in afterRoleList and not after.id in pList:
                    self.premium[pLevel].append(after.id)
                    self.dumpPremium()
                    return
    
    def dumpPremium(self):
        with open(self.premiumPath, 'w') as f:
            json.dump(self.premium, f)


def setup(bot):
    bot.add_cog(Premium(bot))
        
        