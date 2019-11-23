import discord
from discord.ext import commands
import random
import sys
sys.path.insert(1, 'C:/Users/Ernest/Desktop/Mafiabot/Mafiabot-1/MAFIA')
import gameRole as ParentR
GameR = ParentR.GameR

class Bomber(GameR):
    side = "neutral"
    name = "bomber"
    activated = False
    plantedTargets = []
    bombTargets = []
    message = None
    cooldown = False

    def __init__(self, user):
        GameR.__init__(self, user)
        
    async def sendPrompt(self, currentP, dmTime):
        self.bombTargets = []
        if self.plantedTargets:
            self.bombTargets.append("Activiate all currently planted bombs?")
        if not self.cooldown:
            num = random.randint(1, 10)
            if num <=2:
                self.cooldown = True
        if not self.cooldown:
            for player, data in currentP.items():
                if data.roleName != "bomber" and player.name.lower() not in self.plantedTargets and data.alive:
                    self.bombTargets.append(player.name.lower())
            
            self.message = await GameR.makePompt(self, self.bombTargets, "Where do you want to plant the bomb tonight? Or do you want to activate the bombs?", "React with the associated emoji to choose your targets!", "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Ziggs_0.jpg", "You have {} seconds to choose".format(dmTime), discord.Colour.gold())
            if self.plantedTargets:
                embed = discord.Embed(title = "Currently planted bombs:", colour = discord.Colour.gold())
                for item in self.plantedTargets:
                    embed.add_field(name = item, value = "Bomb planted.", inline = False)
                await self.user.send(embed = embed)
        else:
            embed = discord.Embed(title = "Oops! You accidently strapped a bomb to yourself! You'll need tonight to make sure you don't go big boom...", colour = discord.Colour.orange())
            embed.set_image(url = "https://i.kym-cdn.com/photos/images/newsfeed/001/239/583/e38.png")
            await self.user.send(embed = embed)
            self.message = None
            self.bombTargets = []

    async def getTarget(self):
        if not self.cooldown:
            self.victim = await GameR.getResult(self, self.message, self.bombTargets)
            if self.victim == "Activiate all currently planted bombs?":
                self.victim = None
                self.activated = True
        else:
            self.victim = None
            self.cooldown = False
        try:
            self.bombTargets.remove("Activiate all currently planted bombs?")
        except:
            pass