import discord
from discord.ext import commands
import asyncio
import os
import json
import random

class Slot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    choices = [":gem:", ":heart:", ":cherries:", ":poop:"]
    @commands.command(name = "slot", aliases = ["slots", "casino"])
    async def slot(self, ctx, *args):
        cog = self.bot.get_cog("mafia")
        cog.checkFile(ctx.author.id)
        playerObj = cog.findUser(ctx.author.id)
        if len(args) == 0:
            bet = 10
        elif len(args) == 1:
            bet = int(args[0])
        if int(bet) < 10:
            await ctx.channel.send("Boi that's not enough. The minimum bet is 10 Mafia points. Cheapsake.")
            return
        if int(bet) > playerObj.points:
            await ctx.channel.send("Boi, you don't have that much points. Nice try.")
            return
        playerObj.points -= bet
        e1 = self.showRandom("a")
        e2 = self.showRandom("a")
        e3 = self.showRandom("a")
        strSum = e1 + e2 + e3
        embed = self.slotEmbed(strSum, bet)
        message = await ctx.channel.send(embed = embed)
        for _ in range(3):
            await asyncio.sleep(0.5)
            e1 = self.showRandom("a")
            e2 = self.showRandom("a")
            e3 = self.showRandom("a")
            strSum = e1 + e2 + e3
            embed = self.slotEmbed(strSum, bet)
            await message.edit(embed =embed)
        e1 = self.showRandom("a")
        for _ in range(3):
            await asyncio.sleep(0.5)
            e2 = self.showRandom(e1)
            e3 = self.showRandom("a")
            strSum = e1 + e2 + e3
            embed = self.slotEmbed(strSum, bet)
            await message.edit(embed =embed)
        e2 = self.showRandom(e1)
        for _ in range(3):
            await asyncio.sleep(0.5)
            e3 = self.showRandom(e2)
            strSum = e1 + e2 + e3
            embed = self.slotEmbed(strSum, bet)

            await message.edit(embed =embed)
        cherryC = 0
        poopC = 0
        heartC = 0
        gemC = 0
        finalList = [e1, e2, e3]
        for item in finalList:
            if item == ":cherries:":
                cherryC +=1
            elif item == ":poop":
                poopC += 1
            elif item == ":heart:":
                heartC += 1
            elif item == ":gem:":
                gemC += 1
        
        reward = 0
        if cherryC >1:
            if cherryC == 2:
                reward = bet
            else:
                reward = 2 * bet
        elif poopC > 1:
            if poopC == 2:
                reward = 0.1 * bet
            else:
                reward = 0.5 * bet
        elif heartC >1:
            if heartC == 2:
                reward = 2 * bet
            else:
                reward = 4 * bet
        elif gemC > 1:
            if gemC == 2:
                reward = 5 * bet
            else:
                reward = 10 * bet
        
        playerObj.points += reward
        embed = self.slotEmbed(strSum, bet)
        if reward < bet:
            embed.add_field(name = "You lose!", value = "Profit: -" + str(bet-reward) + " :moneybag:")
        elif reward > bet:
            embed.add_field(name = "You win!", value = "Profit: +" + str(reward - bet) + " :moneybag:")
        else:
            embed.add_field(name = "You win....nothing!", value = "Profit: 0 :moneybag:")
        await message.edit(embed = embed)
        cog.editFile(playerObj)
        

        print("done")
    @commands.command(name = "combinations", aliases = ["combination", "combo"])
    async def combinations(self, ctx):
        embed = discord.Embed(title = "Slot info", colour = discord.Colour.purple())
        embed.add_field(name = "Nothing", value = "0 x bet", inline =False)
        embed.add_field(name = ":poop: x 2", value = "0.1 x bet", inline =False)
        embed.add_field(name = ":poop: x 3", value = "0.5 x bet", inline =False)
        embed.add_field(name = ":cherries: x 2", value = "1 x bet", inline =False)
        embed.add_field(name = ":cherries: x 3", value = "2 x bet", inline =False)
        embed.add_field(name = ":heart: x 2", value = "2 x bet", inline =False)
        embed.add_field(name = ":heart: x 3", value = "4 x bet", inline =False)
        embed.add_field(name = ":gem: x 2", value = "5 x bet", inline =False)
        embed.add_field(name = ":gem: x 3", value = "10 x bet", inline =False)
        
        await ctx.channel.send(embed = embed)

    def showRandom(self, prevSelection):
        temp_choice =  random.choice(self.choices)
        while True:
            if temp_choice != prevSelection or random.randint(0, 10) < 7:
                break
            temp_choice =  random.choice(self.choices)    

        return temp_choice
    
    def slotEmbed(self, descr, bet):
      embed = discord.Embed(title = "Slot Machine:slot_machine: \nBet: " + str(bet)  + ":moneybag:", description = descr, colour = discord.Colour.green())
      return embed  
    
def setup(bot):
    bot.add_cog(Slot(bot))