import discord
from discord.ext import commands
import random
import sys

import MAFIA.gameRole as ParentR
class Vig(ParentR.GameR):
    def __init__(self):
        ParentR.GameR.__init__(self)
        self.side = "villager"
        self.message = None

        self.name = "vigilante"
    
    async def sendInfo(self):
        embed = discord.Embed(title = "You are the Vigilante. For five years, You were stranded on an island with only one goal: survive... blah blah blah. Just don't shoot the wrong person or you'll commit suicide.", description = "Side: Villager", colour = discord.Colour.green())
        embed.set_image(url = "https://i2.wp.com/s3-us-west-1.amazonaws.com/dcn-wp/wp-content/uploads/2017/12/31015237/Arrow-CW.png?resize=740%2C431&ssl=1")
        await self.user.send(embed = embed)

    async def sendPrompt(self, currentP, dmTime):
        self.vigTargets = []
        for role in currentP.values():
            if role.name != "vigilante" and role.alive:
                self.vigTargets.append(role.user.name.lower())
        
        self.message = await ParentR.GameR.makePompt(self, self.vigTargets, "Who do you want to shoot tonight?", "React with the associated emoji to choose your target!",  "https://pmcdeadline2.files.wordpress.com/2018/03/arrow.png?w=446&h=299&crop=1", "You have {} seconds to choose.".format(dmTime), discord.Colour.green())
    async def getTarget(self):
        self.victim = await ParentR.GameR.getResult(self, self.message, self.vigTargets)

    async def check(self, visitor_role_obj):
        return

    async def perform(self, currentP):
        if not self.victim:
            return
        victimRole = self.findRoleObj(currentP, self.victim)
        checkTest = await victimRole.check(self)
        if checkTest:
            return checkTest
        
        if not self.alive:
            await self.user.send("Oof, you died tonight before you could do anything...")
            return
        #so anyways I just started blasting
        if victimRole.side == "mafia":
            
            await victimRole.die()
            embed = discord.Embed(title = "Wait, what's this?", description = "The vigilante shot a mafia!!!", colour = discord.Colour.green())
            embed.add_field(name = "The mafia shot was...", value = "{}!".format(self.victim))
            embed.set_image(url = "https://vignette.wikia.nocookie.net/michaelbaybatman/images/e/ea/Bac-gotham-rooftop.jpg/revision/latest?cb=20140223174240")
            return embed
        
        if victimRole.side == "neutral":
            await victimRole.die()
            embed = discord.Embed(title = "Wait, what's this?", description = "The vigilante shot a neutral role!", colour = discord.Colour.green())
            embed.set_image(url = "https://vignette.wikia.nocookie.net/michaelbaybatman/images/e/ea/Bac-gotham-rooftop.jpg/revision/latest?cb=20140223174240")
            return embed
        embed = discord.Embed(title = "Wait, what's this?", description = "The vigilante shot the innocent {}! The vigilante has commited suicide out of guilt!".format(self.victim), colour = discord.Colour.red())
        embed.set_image(url = "https://res.cloudinary.com/teepublic/image/private/s--N6Q7m5Pj--/t_Preview/b_rgb:191919,c_limit,f_jpg,h_630,q_90,w_630/v1493744453/production/designs/1556060_1.jpg")
        await victimRole.die()
        await self.die()
        return embed
        
        