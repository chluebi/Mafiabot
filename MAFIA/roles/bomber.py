import discord
from discord.ext import commands
import random
import sys
import MAFIA.gameRole as ParentR
GameR = ParentR.GameR

class Bomber(GameR):
    
    def __init__(self):
        GameR.__init__(self)
        self.side = "neutral"
        self.name = "bomber"
        self.activated = False
        self.plantedTargets = []
        self.bombTargets = []
        self.message = None
        self.cooldown = False
        self.alreadyExploded = False
    
    async def sendInfo(self):
        embed = discord.Embed(title = "You are the Bomber. You like big boom, so every night you plant one bomb in someone's house. If you get lynched one of your planted bombs will go off at random.", description = "Side: Neutral", colour =discord.Colour.dark_magenta())
        embed.add_field(name = "*Note", value = "Every night, you have a 20 percent chance of attaching a bomb to yourself because you love big boom so much. You will have to spend that night deactivating the big boom.")
        embed.set_image(url = "https://dotesports-media.nyc3.cdn.digitaloceanspaces.com/wp-content/uploads/2018/08/12042519/c40f3969-1d65-43e8-bf02-614730d065a3.jpg")
        await self.user.send(embed = embed)
    async def sendPrompt(self, currentP, dmTime):
        self.bombTargets = []
        if self.plantedTargets:
            self.bombTargets.append("Activiate all currently planted bombs?")
        if not self.cooldown:
            num = random.randint(1, 10)
            if num <=-1:
                self.cooldown = True
        if not self.cooldown:
            for role in currentP.values():
                if role.name != "bomber" and role.user.name.lower() not in self.plantedTargets and role.alive:
                    self.bombTargets.append(role.user.name.lower())
            
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
    
    async def check(self, visitor_role_obj):
        return
    
    async def perform(self, currentP):
        if not self.victim and not self.activated:
            return

        if self.victim:
            victimRoleObj = self.findRoleObj(currentP, self.victim)
            print(victimRoleObj)
            checkTest = await victimRoleObj.check(self)
            if checkTest:
                return checkTest
            self.plantedTargets.append(self.victim)
            await self.user.send("Big boom has been planted on {}".format(self.victim))
            return
        #if bombs go boom boom
        elif self.activated:
            embed = discord.Embed(title = "It was a quiet night in the village until.....BOOM!", description = "There were explosions everywhere!", colour = discord.Colour.red())
            embed.set_image(url = "https://media3.giphy.com/media/U6pavBhRsbNbPzrwWg/giphy.gif")
            for victim in self.plantedTargets:
                tempRoleObj = self.findRoleObj(currentP, victim)
                if tempRoleObj.alive:
                    embed.add_field(name = victim + " died from the explosion!", value = "Can we get some F's in the chat?")
                    await tempRoleObj.die()
            self.plantedTargets = []
            self.activated = False
            return embed
    
    async def onDeath(self, currentP):
        self.alreadyExploded = True
        print("Original targets: ", self.plantedTargets)
        for victim in self.plantedTargets:
            victimObj = self.findRoleObj(currentP, victim)
            if not victimObj.alive:
                self.plantedTargets.remove(victim)
        print("Planted targets: ", self.plantedTargets)
        if self.plantedTargets:
            randTarget = random.choice(self.plantedTargets)
            print("Random target: ", randTarget)
            embed = discord.Embed(title = "Moments before " + self.user.name + "'s death, " + self.user.name + " pulled out a trigger and with a click, created one last big boom.", description = randTarget + " was killed in the explosion.", colour = discord.Colour.dark_grey())
            embed.set_footer(text = randTarget + "'s role was " + self.findRoleObj(currentP, randTarget).name)
            embed.set_image(url = "https://i.kym-cdn.com/photos/images/original/001/487/493/db3.png")
            await self.findRoleObj(currentP, randTarget).die()
            return embed
