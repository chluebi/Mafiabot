import discord
from discord.ext import commands
import asyncio
import os
import json
import logging
import re
class Points(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.titleList = {}
        with open("title.txt") as f:
            for line in f:
                (key, val) = line.split(":")
                self.titleList[key] = int(val)

    @commands.command(name = "record", aliases = ["p", "profile", "pf", "account"])
    async def record(self, ctx, *args):
        if len(args) == 0:
            user = ctx.message.author
        else:
            
            user = ctx.guild.get_member_named(str(args[0]))
            if not user:
                user = ctx.guild.get_member(int(re.search(r'\d+', args[0]).group()))
        channel = ctx.channel

        
        cog = self.bot.get_cog("mafia")
        cog.checkFile(user.id)
        playerObj = cog.findUser(user.id)
        wins = str(playerObj.wins)
        games = str(playerObj.games)
        playerPoints = playerObj.points
        tempTitle = self.getCTitle(user.id)
        if len(tempTitle) > 1:
            tempTitle = 'The "' + tempTitle + '"'
        if games:
            winrate = float(int(wins)/int(games)) * 100
        embed = discord.Embed(title = "{}'s info".format(user.name), description = tempTitle, colour = discord.Colour.gold())
        embed.add_field(name = "Wins", value = wins, inline = True)
        embed.add_field(name = "Games played", value = games, inline = True)
        embed.add_field(name = "Winrate", value = "%.2f" % winrate + "%")
        embed.add_field(name = "Mafia points", value = "{}".format(str(playerPoints)))
        if playerObj.premium:
            embed.add_field(name = "Premium:", value = "Yes")
        else:
            embed.add_field(name = "Premium:", value = "No")
        embed.set_thumbnail(url = user.avatar_url)

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