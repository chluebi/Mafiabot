import discord
from discord.ext import commands
import random
import sys
import MAFIA.story as story
import MAFIA.gameRole as ParentR
GameR = ParentR.GameR

class Godfather(GameR):


    def __init__(self):
        GameR.__init__(self)
        self.MAFIAPLAYER = None
        self.side = "mafia"
        self.message = None
        self.mafiatargets = []
        self.name = "godfather"
        self.mafiaSide = ["mafia", "godfather", "framer"]
    
    async def sendInfo(self):
        embed = discord.Embed(title = "You are the Godfather. You decide who to kill. If you have a mafia, they will do the dirty work for you. Otherwise you will have to do it yourself.", description = "Side: mafia", colour = discord.Colour.red())
        embed.set_image(url = "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/8173394d-de95-430a-a448-f57211a61abf/d4s8rj1-3ba39658-06af-48e3-8a3d-c1fb95ea7156.png?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7InBhdGgiOiJcL2ZcLzgxNzMzOTRkLWRlOTUtNDMwYS1hNDQ4LWY1NzIxMWE2MWFiZlwvZDRzOHJqMS0zYmEzOTY1OC0wNmFmLTQ4ZTMtOGEzZC1jMWZiOTVlYTcxNTYucG5nIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmZpbGUuZG93bmxvYWQiXX0.YmYoOCuQk1uWaDXmf2CVWDHJA9GzNwQuMcW_-SkXaiI")
        await self.user.send(embed = embed)

    async def sendPrompt(self, currentP, dmTime):
        self.mafiatargets = []
        for role in currentP.values():
            if not role.side == "mafia" and role.alive:
                self.mafiatargets.append(role.user.name.lower())
        
        self.message = await GameR.makePompt(self, self.mafiatargets, "Who would you like to kill tonight Godfather?", "React with the associated emoji to choose your target!", "https://www.mobafire.com/images/champion/skins/landscape/graves-mafia.jpg", "You have {} seconds to choose.".format(dmTime), discord.Colour.red())

    async def getTarget(self):
        self.victim = await GameR.getResult(self, self.message, self.mafiatargets)
        if self.victim:
            if self.MAFIAPLAYER and self.MAFIAPLAYER.alive:
                self.MAFIAPLAYER.victim = self.victim
                self.victim = None
                embed = discord.Embed(title = "The GodFather have sent {} to attack {}".format(self.MAFIAPLAYER.user.name, self.MAFIAPLAYER.victim), colour = discord.Colour.red())
                await self.MAFIAPLAYER.user.send(embed = embed)
            else:
                embed = discord.Embed(title = "You have decided to attack {}".format(self.victim))

            await self.user.send(embed = embed)
    
    async def check(self, visitor_role_obj):
        return
    
    async def perform(self, currentP):

        if self.MAFIAPLAYER and self.MAFIAPLAYER.alive:
            return await self.MAFIAPLAYER.perform(currentP)

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
        
        embed = discord.Embed(title = "The mafia was too lazy to kill anyone lmao...", colour = discord.Colour.red())
        return embed
            