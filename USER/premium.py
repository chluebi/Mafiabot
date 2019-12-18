import discord
from discord.ext import commands
import asyncio
import os
import json
import USER.premiumObj as pObj
class Premium(commands.Cog):
    premiumPath = "USER/premium.json"
    premiumID = [606066491028275213, 655264404941701133]
    addRoleOptions = ["vigilante", "framer", "pi", "spy", "executioner", "bomber", "baiter", "mayor", "distractor"]
    def __init__(self, bot):
        self.bot = bot
        with open(self.premiumPath, 'r') as f:
            premiumJson = json.load(f)
        self.premium = []

        for roleID in premiumJson.keys():
            for userID, customList in premiumJson[roleID].items():
                self.premium.append(pObj.PremiumObj(int(roleID), customList, int(userID)))

    def updatePremium(self):
        self.server = self.bot.get_guild(602070949449170974)
        for pLevelID in self.premiumID:
            for member in self.server.get_role(pLevelID).members:
                if not member.id in [p.userID for p in self.premium]:
                    self.addPremium(int(pLevelID), member.id)
                    return
        
        for premiumObj in self.premium:
            if not premiumObj.userID in [member.id for member in self.server.get_role(int(pLevelID)).members]:
                self.removePremium(premiumObj.userID)
                return
    @commands.command(pass_context = True)
    async def addcg(self, ctx, *args):
        if not len(args):
            return
        user = ctx.message.author
        mafiaCog = self.bot.get_cog("mafia")
        mafiaCog.checkFile(user.id)
        playerObj = mafiaCog.findUser(user.id)
        if not playerObj.premium:
            await ctx.send(user.mention + ", you do not have premium!")
            return
        customList = playerObj.premium.customList
        embed = discord.Embed(title = "New roles have been added to your custom game!", colour = discord.Colour.green())
        added = False
        for roleName in args:
            if roleName.lower() in customList:
                await ctx.send(user.mention + ", you already have {} in your custom list!".format(roleName))
                
            elif not roleName.lower() in self.addRoleOptions:
                await ctx.send(user.mention + ", {}'s not a role you can add lmao.".format(roleName))
            else:
                playerObj.premium.customList.append(roleName.lower())
                added = True
        if not added:
            return
        embed.set_author(name = user.name, icon_url=user.avatar_url)
        await ctx.send(embed = self.showCustomList(playerObj.premium.customList, ctx.author, embed))
        self.dumpPremium()
        return
    
    @commands.command(pass_context = True)
    async def clearcg(self, ctx):
        user = ctx.message.author
        mafiaCog = self.bot.get_cog("mafia")
        mafiaCog.checkFile(user.id)
        playerObj = mafiaCog.findUser(user.id)
        if not playerObj.premium:
            await ctx.send(user.mention + ", you do not have premium!")
            return
        
        playerObj.premium.customList = []
        self.dumpPremium()
        await ctx.send(ctx.author.mention + " your custom game roles have been cleared.")
    @commands.command(pass_context = True)
    async def removecg(self, ctx, *args):
        if not len(args):
            return
        user = ctx.message.author
        mafiaCog = self.bot.get_cog("mafia")
        mafiaCog.checkFile(user.id)
        playerObj = mafiaCog.findUser(user.id)
        if not playerObj.premium:
            await ctx.send(user.mention + ", you do not have premium!")
            return
        customList = playerObj.premium.customList
        tempStr = ""
        for roleName in args:
            if roleName.lower() in customList:
                playerObj.premium.customList.remove(roleName.lower())
                tempStr += roleName[0].upper() + roleName[1:] +"\n"
        embed = discord.Embed(title = "The following roles have been removed.", description = tempStr, colour = discord.Colour.red())
        embed.set_author(name = user.name, icon_url=user.avatar_url)
        await ctx.send(embed = embed)
        self.dumpPremium()
    @commands.command(pass_context = True)
    async def cg(self, ctx):
        user = ctx.message.author
        mafiaCog = self.bot.get_cog("mafia")
        mafiaCog.checkFile(user.id)
        playerObj = mafiaCog.findUser(user.id)
        if not playerObj.premium:
            await ctx.send("Lol you don't have premium.")
            return
        if not playerObj.premium.customList:
            await ctx.send("You haven't started customizing your custom game yet! Type addcg to start adding your roles!")
            return
        embed = discord.Embed(title = ctx.author.name + "'s Custom Game", description = "Hooo! Premium boi!", colour = discord.Colour.green())
        await ctx.send(embed = self.showCustomList(playerObj.premium.customList, ctx.author, embed))
    
    def showCustomList(self, list, user, embed):
        temp_str = ""
        count = 0
        for role in list:
            if count == 4:
                embed.add_field(name = ":football:", value = temp_str)
                temp_str = role[0].upper() + role[1:] + "\n"
                count = 0
            else:
                temp_str += role[0].upper() + role[1:]  + "\n"
                count+=1
        if temp_str:
            embed.add_field(name = ":football:", value = temp_str)
        embed.set_author(name = user.name, icon_url=user.avatar_url)
        return embed
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        
        beforeRoleList = [role.id for role in before.roles]
        afterRoleList = [role.id for role in after.roles]
        checkBefore = any(roleID in self.premiumID for roleID in beforeRoleList)
        checkAfter = any(roleID in self.premiumID for roleID in afterRoleList)
        if checkBefore and not checkAfter:
            self.removePremium(before.id)
            return

        if not checkBefore and checkAfter:
            for rID in self.premiumID:
                if rID in afterRoleList:
                    self.addPremium(rID, after.id)
                    return
    
    def dumpPremium(self):
        tempJson = {}
        for roleID in self.premiumID:
            tempJson[str(roleID)] = {}

        for premiumObj in self.premium:
            tempJson[str(premiumObj.roleID)] = {str(premiumObj.userID) : premiumObj.customList}
        print(tempJson)
        with open(self.premiumPath, 'w') as f:
            json.dump(tempJson, f)

    def addPremium(self, roleID, userID):
        tempPremium = pObj.PremiumObj(roleID, [], userID)
        self.premium.append(tempPremium)
        mafiaCog = self.bot.get_cog("mafia")
        user = mafiaCog.findUser(userID)
        user.premium = tempPremium
        self.dumpPremium()

    def removePremium(self, userID):
        mafiaCog = self.bot.get_cog("mafia")
        user = mafiaCog.findUser(userID)
        user.premium = None
        for pObj in self.premium:
            if pObj.userID == userID:
                self.premium.remove(pObj)
                break
        self.dumpPremium()
    
def setup(bot):
    bot.add_cog(Premium(bot))