import discord
from discord.ext import commands
import random
import sys
import MAFIA.story as story
import MAFIA.gameRole as ParentR
GameR = ParentR.GameR

class Mafia(GameR):
    def __init__(self):
        GameR.__init__(self)
        self.side = "mafia"
        self.name = "mafia"
    async def sendInfo(self):
        embed = discord.Embed(title = "You are the Mafia. You carry out the Godfather's kill commands. (AKA you do the Godfather's dirty work)", description = "Side: mafia(duh)", colour = discord.Colour.red())
        embed.set_image(url = "https://g-plug.pstatic.net/20180227_146/1519712112754O5VoQ_JPEG/JackR_skin_02.jpg?type=wa1536_864")
        await self.user.send( embed = embed)
    async def check(self, visitor_role_obj):
        return
    
    async def perform(self, currentP):
        if self.victim:
            victimRoleObj = self.findRoleObj(currentP, self.victim)
            if not victimRoleObj.alive:
                return
            checkTest = await victimRoleObj.check(self)
            if checkTest:
                return checkTest
            victimRoleObj.alive = False
            aStory = story.storyTime("dead", self.victim)
            storyEmbed = discord.Embed(title = "{} was attacked by the mafia :(".format(self.victim), description = "{}".format(aStory), colour = discord.Colour.red())
            storyEmbed.set_image(url = "https://i.ytimg.com/vi/j_nV2jcTFvA/hqdefault.jpg")
            storyEmbed.set_thumbnail(url = victimRoleObj.user.avatar_url)
            return storyEmbed
        
        

