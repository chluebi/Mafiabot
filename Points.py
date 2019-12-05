import discord
from discord.ext import commands
import asyncio
import os
import json
import logging
class Points(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.titleList = {}
        with open("title.txt") as f:
            for line in f:
                (key, val) = line.split(":")
                self.titleList[key] = int(val)

    @commands.command(pass_context = True)
    async def record(self, ctx, user: discord.Member):
        channel = ctx.channel
        if user == None:
            person = ctx.message.author
        else:
            person = user
        
        cog = self.bot.get_cog("mafia")
        cog.checkFile(user.id)
        playerObj = cog.findUser(user.id)
        wins = str(playerObj.wins)
        games = str(playerObj.games)
        playerPoints = playerObj.points
        tempTitle = self.getCTitle(user.id)
        if tempTitle != "":
            tempTitle = 'The "' + tempTitle + '"'
        embed = discord.Embed(title = "{}'s info".format(person.name), description = tempTitle, colour = discord.Colour.gold())
        embed.add_field(name = "Total wins", value = "{}".format(wins), inline = True)
        embed.add_field(name = "Total games played", value = "{}".format(games))
        embed.add_field(name = "Mafia points", value = "{}".format(str(playerPoints)))
        embed.set_thumbnail(url = person.avatar_url)

        await channel.send(embed = embed)
    
    @commands.command(name = "points", aliases = ["point", "balance", "bal"])
    async def points(self, ctx):
        channel = ctx.channel
        user = ctx.author
        cog = self.bot.get_cog("mafia")
        cog.checkFile(user.id)
        playerObj = cog.findUser(user.id)
        points = playerObj.points
        tempTitle = self.getCTitle(user.id)
        if tempTitle != "":
            tempTitle = ' the ' + tempTitle 
        embed = discord.Embed(title = ":moneybag:" + user.name + tempTitle + ":moneybag:", description = "{} Mafia points.".format(str(points)), colour = discord.Colour.gold())
        embed.set_thumbnail(url = user.avatar_url)
        await channel.send(embed = embed)
        
    @commands.command(name = "shop", aliases = ["store"])
    async def shop(self, ctx):
        shopEmbed = discord.Embed(title = ":moneybag: Mafia Shop :moneybag: ", description = "Spend your Mafia points here!", colour = discord.Colour.purple())
        count = 1
        for title, price in self.titleList.items():
            shopEmbed.add_field(name = str(count) + ". Title: "+ title, value = str(price)+" Points", inline = True)
            count+=1
        shopEmbed.set_image(url = "https://www.hiddentriforce.com/wp-content/uploads/2018/01/Beedle_Breath_of_the_Wild.png")
        shopEmbed.set_footer(text = "Type m.buy (number) to buy the item associated with that number!")
        await ctx.channel.send(embed = shopEmbed)

    @commands.command(name= "buy", aliases = ["purchase"])
    async def buy(self, ctx, itemNumber: int):
        if itemNumber-1 > len(self.titleList.keys()):
            await ctx.channel.send("Boi that's not something you can buy.")
            return
        
        
        cog = self.bot.get_cog("mafia")
        cog.checkFile(ctx.author.id)
        playerObj = cog.findUser(ctx.author.id)

        title = list(self.titleList.keys())[itemNumber-1]
        price = int(self.titleList[title])
        print(playerObj.titles)
        if title in playerObj.titles:
            await ctx.channel.send("Lol don't waste your money. You already bought '{}'.".format(title))
            return

        if playerObj.points >= price:
            playerObj.points -= price
            embed = discord.Embed(title ="Congratulations {}! You now own the title {}!".format(ctx.author.name, title), description = "{} Mafia Points have been deducted from your account. (Thanks for the money lol)".format(str(price)), colour = discord.Colour.green())
            embed.set_image(url = "https://media3.giphy.com/media/3oz8xNiT2rlm5JGTCg/giphy.gif")
            embed.set_footer(text = "Check out your titles with m.titles and equip one with m.setTitle # !")
            await ctx.channel.send(embed = embed)
            playerObj.titles.append(title)
            cog.editFile(playerObj)
            supportChannel = self.bot.get_channel(550923896858214446)
            await supportChannel.send("{} bought {} on {}".format(ctx.author.name, title, ctx.guild.name))
            return
        
        await ctx.channel.send("Lol you don't have enough mafia points.")

    @commands.command(name = "titles", aliases = ["title", "Titles", "titleList", "titlelist"])
    async def titles(self, ctx):
        cog = self.bot.get_cog("mafia")
        cog.checkFile(ctx.author.id)
        playerObj = cog.findUser(ctx.author.id)
        embed = discord.Embed(title = "{}'s titles".format(ctx.author.name), description = "Current title: {}".format(playerObj.currentTitle), colour = discord.Colour.blue())

        print(playerObj.titles)
        count = 0
        for item in playerObj.titles:
            count+=1
            embed.add_field(name = str(count) + ".", value = item, inline = True)

        embed.set_footer(text = "Type m.setTitle (# associated with title) to set a title!"
        )
        embed.set_thumbnail(url = ctx.author.avatar_url)
        await ctx.channel.send(embed = embed)
    
    @commands.command(name = "setTitle", aliases = ["settitle", "set", "equip"])
    async def setTitle(self, ctx, index: int):
        cog = self.bot.get_cog("mafia")
        cog.checkFile(ctx.author.id)
        playerObj = cog.findUser(ctx.author.id)
        if index-1 < len(playerObj.titles):
            playerObj.currentTitle = playerObj.titles[index-1]
            embed = discord.Embed(title = "{}'s title is now '{}'".format(ctx.author.name, playerObj.currentTitle), description = "What a cool kid.", colour = discord.Colour.purple())
            embed.set_thumbnail(url = ctx.author.avatar_url)
            await ctx.channel.send(embed = embed)
            cog.editFile(playerObj)
            return
        await ctx.channel.send("Lol you don't have a title with that number. Type m.titles to check out all your owned titles.")
    
    @commands.command(pass_context = True)
    async def giveAll(self, ctx, amount, url, *, reason):
        if ctx.author.id != 217380909815562241:
            return
        embed = discord.Embed(title = "Congratulations! You have received " + str(amount) + " mafia points from the almighty linkboi!", description = "Message from linkboi: " + reason, colour = discord.Colour.green())
        embed.set_image(url = url)
        cog = self.bot.get_cog("mafia")
        for user in cog.userList:
            user.points += int(amount)
            try:
                player = self.bot.get_user(user.id)
                cog.editFile(user)
                await player.send(embed = embed)
            except:
                pass
            

    def getCTitle(self, ID):
        cog = self.bot.get_cog("mafia")
        cog.checkFile(ID)
        playerObj = cog.findUser(ID)
        return playerObj.currentTitle
def setup(bot):
    bot.add_cog(Points(bot))