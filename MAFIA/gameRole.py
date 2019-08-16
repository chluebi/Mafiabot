import discord
from discord.ext import commands
import random
#Parent
class GameR:
    def __init__(self, user):
        self.user = user
        self.target = None
        self.reactionList = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯', '🇰', '🇱', '🇲', '🇳', '🇴', '🇵']
        self.alive = True
        self.targets = None
        self.victim = None
    async def makePompt(self, targets, title, descr , image_url, footer =" ", color = discord.Colour.orange()):
        self.targets = targets
        embed = discord.Embed(title = title, description = descr, colour = color)
        embed.set_image(url = image_url)
        embed.set_footer(text = footer)
        embed.add_field(name = ":regional_indicator_a:- Choose no one tonight", value = "React A!", inline= False)
        letter = 'B'
        count = 1
        for item in targets:
            embed.add_field(name = ":regional_indicator_"+letter.lower()+": " + str(item), value = "React {}!".format(letter), inline = False)
            count+=1
            letter = chr(ord(letter) + 1)
        message = await self.user.send(embed = embed)

        letter = 'A'
        rCount = 0
        for _ in range(count):
            await message.add_reaction(self.reactionList[rCount])
            rCount+=1
        return message
    
    async def getResult(self, msg, tempList = []):
        cache_msg = await self.user.fetch_message(msg.id)
        answerEmoji = None
        found = False
        for reaction in cache_msg.reactions:
            async for user in reaction.users():
                if user.id != 511786918783090688 and reaction.emoji in self.reactionList:
                    answerEmoji = reaction.emoji
                    await self.user.send(answerEmoji)
                    found = True
                    break
            
            if found:
                break
            
            
        
        if answerEmoji and answerEmoji != '🇦':
            index = self.reactionList.index(answerEmoji)
            print(index)
            print(tempList[index-1])
            target = tempList[index-1]
            if str(target) == "Activiate all currently planted bombs?":
                target = "activate all the bombs tonight."
            embed = discord.Embed(title = "Your choice is " + target, colour = discord.Colour.greyple())
            await self.user.send(embed = embed)
            return tempList[index-1]
        else:
            embed = discord.Embed(title = "You didn't choose anything lmao. You ok?", colour = discord.Colour.greyple())
            await self.user.send(embed = embed)
            return None

        
        

#All children classes below
class Mafia(GameR):
    def __init__(self, user):
        GameR.__init__(self, user)
        self.side = "mafia"

        self.name = "mafia"


class Godfather(GameR):
    def __init__(self, user):
        GameR.__init__(self, user)
        self.side = "mafia"
        self.message = None
        self.mafiaPlayers = []
        self.mafiatargets = []

        self.name = "godfather"
    async def sendPrompt(self, currentP, dmTime):
        self.mafiatargets = []
        for player, data in currentP.items():
            if data.roleName != "mafia" and data.roleName != "godfather" and data.roleName != "framer" and data.alive:
                self.mafiatargets.append(player.name.lower())
        
        self.message = await GameR.makePompt(self, self.mafiatargets, "Who would you like to kill tonight Godfather?", "React with the associated emoji to choose your target!", "https://www.mobafire.com/images/champion/skins/landscape/graves-mafia.jpg", "You have {} seconds to choose.".format(dmTime), discord.Colour.red())

    async def getTarget(self):
        self.victim = await GameR.getResult(self, self.message, self.mafiatargets)
        if self.victim:
            if self.mafiaPlayers and self.mafiaPlayers[0].user:
                killer = random.choice(self.mafiaPlayers)
                killer.victim = self.victim
                self.victim = None
                embed = discord.Embed(title = "The GodFather have sent {} to attack {}".format(killer.user.name, killer.victim), colour = discord.Colour.red())
                for role in self.mafiaPlayers:
                    await role.user.send(embed = embed)
                
                await self.user.send(embed = embed)
            else:
                embed = discord.Embed(title = "You have decided to attack {}".format(self.victim))
                await self.user.send(embed = embed)
        
            
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


class Doctor(GameR):
    def __init__(self, user):
        GameR.__init__(self, user)
        self.lastHeal = None
        self.side = "villager"
        self.message = None
        self.docTargets = None

        self.name= "doctor"
    async def sendPrompt(self, currentP, dmTime):
        self.docTargets = []
        for player, data in currentP.items():
            if player.name.lower() != self.lastHeal and data.alive:
                self.docTargets.append(player.name.lower())
        
        self.message = await GameR.makePompt(self, self.docTargets, "Who do you want to save?", "React with the associated emoji to choose your target!", "https://vignette.wikia.nocookie.net/leagueoflegends/images/f/f7/Akali_NurseSkin_old.jpg/revision/latest?cb=20120609043410", "You have {} seconds to choose.".format(dmTime), discord.Colour.blue())

    async def getTarget(self):
        self.victim = await GameR.getResult(self, self.message, self.docTargets)
        


class Mayor(GameR):
    def __init__(self, user):
        GameR.__init__(self, user)
        self.revealed = False
        self.alreadyShown = False
        self.side = "villager"
        self.message = None
        self.name = "mayor"
        
    async def sendPrompt(self, currentP, dmTime):
        if not self.revealed:
            embed = discord.Embed(title = "Hello mayor. Would you like to reveal yourself the next morning to gain two votes?", description = "React :regional_indicator_y: or :regional_indicator_n:!", colour = discord.Colour.green())
            embed.set_image(url = "https://vignette.wikia.nocookie.net/familyguy/images/c/cf/Adam_We.JPG/revision/latest?cb=20060929205011")
            embed.set_footer(text = "You have {} seconds to answer.".format(dmTime))
            self.message = await self.user.send(embed = embed)
            await self.message.add_reaction('🇾')
            await self.message.add_reaction('🇳')


    async def getTarget(self):
        if not self.revealed:
            cache_msg = await self.user.fetch_message(self.message.id)
            answerEmoji = None
            for reaction in cache_msg.reactions:
                async for user in reaction.users():
                    if user.id != 511786918783090688 and (reaction.emoji == '🇾' or reaction.emoji == '🇳'):
                        answerEmoji = reaction.emoji
                        break
            if answerEmoji != '🇳':
                self.revealed = True
                await self.user.send("You have decided to reveal yourself tomorrow.")
        
class Framer(GameR):
    def __init__(self, user):
        GameR.__init__(self, user)
        self.side = "mafia"
        self.message = None

        self.name = "framer"
    async def sendPrompt(self, currentP, dmTime):
        self.framerTargets = []
        for player, data in currentP.items():
            if data.roleName != "mafia" and data.roleName !="framer" and data.roleName != "godfather" and data.alive:
                self.framerTargets.append(player.name.lower())
        
        self.message = await GameR.makePompt(self, self.framerTargets, "Who do you want to frame?", "React with the associated emoji to choose your target!", "https://cdn.drawception.com/images/panels/2017/12-17/zKXCDSXfeA-4.png", "You have {} seconds to choose.".format(dmTime), discord.Colour.red())

    async def getTarget(self):
        self.victim = await GameR.getResult(self, self.message, self.framerTargets)
class Vig(GameR):
    def __init__(self, user):
        GameR.__init__(self, user)
        self.side = "villager"
        self.message = None

        self.name = "vigilante"
    async def sendPrompt(self, currentP, dmTime):
        self.vigTargets = []
        for player, data in currentP.items():
            if data.roleName != "vigilante" and data.alive:
                self.vigTargets.append(player.name.lower())
        
        self.message = await GameR.makePompt(self, self.vigTargets, "Who do you want to shoot tonight?", "React with the associated emoji to choose your target!",  "https://pmcdeadline2.files.wordpress.com/2018/03/arrow.png?w=446&h=299&crop=1", "You have {} seconds to choose.".format(dmTime), discord.Colour.green())
    async def getTarget(self):
        self.victim = await GameR.getResult(self, self.message, self.vigTargets)
class Distractor(GameR):
    def __init__(self, user):
        GameR.__init__(self, user)
        self.side = "villager"
        self.message = None
        self.cooldown = False
        self.disTargets = None
        self.name = "distractor"


    async def sendPrompt(self, currentP, dmTime):
        self.disTargets = []
        for player, data in currentP.items():
            if data.roleName != "distractor" and data.alive:
                self.disTargets.append(player.name.lower())
        if not self.cooldown:
            self.message = await GameR.makePompt(self, self.disTargets, "Who do you want to distract tonight?", "React with the associated emoji to choose your target!",  "https://www.dolmanlaw.com/wp-content/uploads/2017/03/The-Many-Types-of-Technology-that-can-Cause-Distracted-Driving-1.jpg", "You have {} seconds to choose.".format(dmTime), discord.Colour.orange())
        else:
            embed = discord.Embed(title = "You need some rest tonight...", description = "Maybe you can distract someone again tomorrow...", colour = discord.Colour.dark_blue())
            embed.set_image(url = "https://cdn2.iconfinder.com/data/icons/real-estate-set-2/512/721303-16-512.png")
            await self.user.send(embed = embed)
    
    async def getTarget(self):
        if not self.cooldown:
            self.victim = await GameR.getResult(self, self.message, self.disTargets)
            self.cooldown = True
        else:
            self.victim = None
            self.cooldown = False
        

class PI(GameR):
    def __init__(self, user):
        GameR.__init__(self, user)
        self.side = "villager"
        self.message = None
        self.PITargets = []
        self.name = "PI"
        self.targets = []

    async def sendPrompt(self, currentP, dmTime):
        self.PITargets = []
        for player, data in currentP.items():
            if data.roleName != "PI" and data.alive:
                self.PITargets.append(player.name.lower())
        
        self.message = await GameR.makePompt(self, self.PITargets, "Which two people do you want to investigate tonight?", "React with the associated emoji to choose your targets!",  "https://i.pinimg.com/originals/08/64/a5/0864a55a5c3b2b8e0e2b1b8c231c93a3.jpg", "You have {} seconds to choose.".format(dmTime), discord.Colour.blurple())

    async def getTarget(self):
        cache_msg = await self.user.fetch_message(self.message.id)
        answerEmojis = []
        count = 0
        for reaction in cache_msg.reactions:
            async for user in reaction.users():
                if user.id != 511786918783090688 and reaction.emoji in self.reactionList:
                    answerEmojis.append(reaction.emoji)
                    count+=1
                    if count == 2:
                        break
                    
        reactionList = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯', '🇰', '🇱', '🇲', '🇳', '🇴', '🇵']
        
        if  len(answerEmojis) ==2 and '🇦' not in answerEmojis:
            index1 = reactionList.index(answerEmojis[0])
            index2 = reactionList.index(answerEmojis[1])
            await self.user.send("You chose " + self.PITargets[index1-1] + " and " + self.PITargets[index2-1])

            self.PITargets = [self.PITargets[index1-1], self.PITargets[index2-1]]
            print(self.PITargets)
        else:
            self.PITargets = []
            await self.user.send("You chose nothing. Lmao.")
            
        return
    

class Spy(GameR):
    def __init__(self, user):
        GameR.__init__(self, user)
        self.side = "villager"
        self.lastTarget = None
        self.message = None

        self.SpyTargets = None
        self.name = "spy"
    async def sendPrompt(self, currentP, dmTime):
        self.SpyTargets = []
        for player, data in currentP.items():
            if data.roleName != "spy" and data.alive:
                self.SpyTargets.append(player.name.lower())
        
        self.message = await GameR.makePompt(self, self.SpyTargets, "Who do you want to spy on tonight?", "React with the associated emoji to choose your targets!",  "https://cdn.vox-cdn.com/thumbor/I3GT91gn4U3jc4HmBY5LjowXzuM=/0x0:1215x717/1200x800/filters:focal(546x35:740x229)/cdn.vox-cdn.com/uploads/chorus_image/image/57172117/Evelynn_Splash_4.0.jpg", "You have {} seconds to choose.".format(dmTime), discord.Colour.blurple())
    
    async def getTarget(self):
        self.victim = await GameR.getResult(self, self.message, self.SpyTargets)

class Baiter(GameR):
    def __init__(self, user):
        GameR.__init__(self, user)
        self.side = "neutral"

        self.name = "baiter"
        self.killCount = 0


class Bomber(GameR):
    def __init__(self, user):
        GameR.__init__(self, user)
        self.side = "neutral"

        self.name = "bomber"
        self.activated = False
        self.plantedTargets = []
        self.bombTargets = []
        self.message = None
        self.cooldown = False
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
        

class Exe(GameR):
    def __init__(self, user):
        GameR.__init__(self, user)
        self.side = "neutral"
        self.target = None
        self.name = "executioner"


class Jester(GameR):
    def __init__(self, user):
        GameR.__init__(self, user)
        self.side = "neutral"
        self.name = "jester"

class Dictator(GameR):
    def __init__(self, user):
        GameR.__init__(self, user)
        self.side = "neutral"
        self.name = "Dictator"
        self.selectSide = None
class Villager(GameR):
    def __init__(self, user):
        GameR.__init__(self, user)
        self.side = "villager"
        self.name = "villager"



        