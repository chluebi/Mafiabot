import discord
from discord.ext import commands
import random


#Parent
class GameR:
    user = None
    def __init__(self):
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
                    found = True
                    break
            
            if found:
                break
        
        if answerEmoji and answerEmoji != '🇦':
            index = self.reactionList.index(answerEmoji)
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
    
    def findRoleObj(self, currentP, username):
        for role in currentP.values():
            if role.user.name.lower() == username.lower():
                return role
    
    def roleObjRolename(self, currentP, rolename):
        for roleObj in currentP.values():
            if roleObj.name == rolename:
                return roleObj
        return
    async def checkDistracted(self, currentP):
        for roleObj in currentP.value():
            if roleObj.name == "distractor" and roleObj.target == self.user.name.lower():
                await self.user.send("Sorry. You got distracted tonight...")
                self.target = None
                return 
    
    async def die(self):
        embed = discord.Embed(title = "Hey, you died! Feel free to spectate the rest of the game but PLEASE do not talk nor give away important information to those still playing. Thank you!", description = "Pssss I can play mini games while you wait! Type m.mini to check it out!", colour = discord.Colour.blue())
        embed.set_thumbnail(url = "https://i.imgflip.com/p3mcp.jpg")
        await self.user.send(embed = embed) 
        self.alive = False
        
    
    def makeEmbed(self, txt):
        embed = discord.Embed(title = txt, colour = discord.Colour.orange())
        return embed

        