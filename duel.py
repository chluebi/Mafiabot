import discord
from discord.ext import commands
import asyncio
import os
import json
import random

class Duel(commands.Cog):
    currentPlaying = []
    lightAtk = {"{} threw a jab at {}!": "https://thumbs.gfycat.com/PartialGenuineAbyssiniancat-max-1mb.gif",
    " {} smacked {} on the head!": "https://media1.giphy.com/media/Xj7aX90bEKoec/giphy.gif", 
    "{} threw a right hook at {}!":"https://media1.giphy.com/media/3ornk9vVI7DsFYNAR2/giphy.gif", 
    "{} threw a karate reverse punch at {}!": "https://66.media.tumblr.com/9e3ff679d0ad3ca25b553f6d55881055/tumblr_ocmsthRUSu1su3rezo1_400.gif",
    "{} kicked {}'s leg!": "http://theselfdefenceexpert.com/wp-content/uploads/2014/01/low-kick-gif-alves.gif",
    "{} used a palm strike on {}!": "https://media1.giphy.com/media/OLHy9ERaFUvzW/giphy.gif",
    "{} threw a capoeira handstand kick at {}!": "https://66.media.tumblr.com/282c8847ebbe7422135a0a57821dc44c/tumblr_p7hg2kQLuj1v6w3juo4_500.gif",
    "{} thew elbow strikes at {}!": "https://66.media.tumblr.com/c4f24c77e3d5dfc0e80ab8583fc65080/tumblr_pcqp5pM1R01rmrpdmo2_400.gif",
    "{} grabbed two swords and started stabbing {}!": "https://thumbs.gfycat.com/AcidicImmenseHapuku-size_restricted.gif",
    "{} landed two devastating punches at {}'s stomach!": "https://media.giphy.com/media/nD2mLa2S7Cz6/giphy.gif",
    "{} karate chopped {}!": "https://media1.tenor.com/images/a300542f540340d9b9b59eaf6a69d352/tenor.gif?itemid=5137929",
    "{} threw {} to the ground!": "https://media1.giphy.com/media/9lLbEiVBO3OY8/giphy.gif",
    "{} did a takedown on {}!": "http://i40.tinypic.com/291doup.gif",
    "{} slapped {}!": "https://thumbs.gfycat.com/DecentBelatedAntbear-size_restricted.gif",
    "{} threw a flurry of Wing Chun punches at {}!": "https://media2.giphy.com/media/Cf3ZcH9D3uHtK/giphy.gif",
    "{} kicked {}'s ass...literally.": "https://media2.giphy.com/media/xT5LMY2kXko8zjyiwU/source.gif",
    "{} headbutted {}!": "https://media1.tenor.com/images/b943da307642d8dedf3a495b6bdb48c4/tenor.gif?itemid=5114718",
    "{} punched {}'s throat!": "https://media.giphy.com/media/13HXKG2HGN8aPK/giphy.gif"
    }

    heavyAtk = {"{} threw a Muay Thai jumping elbow at {}!": "https://cdn.ebaumsworld.com/mediaFiles/picture/31430/81968730.gif",
    "{} threw a front kick straight into {}'s face!": "https://media.giphy.com/media/xT1R9JqCleRlz4jnvq/giphy.gif",
    "{} faked a spin kick and then threw another spin kick at {}!": "https://i.pinimg.com/originals/26/b3/72/26b372434422e37d39da16d99c792a87.gif",
    "{} threw an urumawashi geri (Karate hook kick) at {}!": "https://66.media.tumblr.com/92eae13144a2c558cddc611b7860ebc7/tumblr_ot6sigmrzp1smsd90o1_400.gif",
    "{} sweeped and slammed {} into the ground!": "https://66.media.tumblr.com/07ac5647d522cb71a06371def2216d32/tumblr_op12h97In01v6w3juo1_500.gif",
    "{} threw a flying knee at {}!": "https://i0.wp.com/78.media.tumblr.com/0f4fc9616b3113ad92eeb771950910e2/tumblr_oo0bwozKxH1rmrpdmo1_400.gif?resize=350%2C200&ssl=1",
    "{} lands a big uppercut at {}!": "https://media1.giphy.com/media/AM0NtWwYBdoxW/giphy.gif",
    "{} lands a flurry of punches at {}!": "https://i.redd.it/ouqn4rpssg901.gif",
    "{} lands a meia lua on {}'s face!": "http://i.imgur.com/6tpk9QG.gif",
    "{} hit {} with a flurry of punches and a spinning jump kick!": "https://static.fjcdn.com/gifs/Good+reaction+gif+brilredbig3also+what+would+you+call+the+finishing_1970c0_5251657.gif",
    "{} landed a fancy kick at {}'s face!": "https://66.media.tumblr.com/77e4d275d8c5541030364e95a250e4b2/tumblr_oqvll1zWfV1rmrpdmo1_400.gif",
    "{} side kicked {}!": "http://24.media.tumblr.com/f5da63478bde392418aebe858e19279e/tumblr_mgdokseHXu1r2xo28o1_500.gif",
    "{} lands an axe kick on {}'s face!": "https://media3.giphy.com/media/rQX1Ogknv7boI/giphy.gif",
    "{} lands a big roundhouse kick on {}!": "http://giant.gfycat.com/HarmlessBlueArawana.gif",
    "{} did some fancy flying kick at {}!": "https://moviesfilmsandflix.files.wordpress.com/2018/02/scott-adkins-kick-gif.gif",
    "{} kicked {} in the crotch!": "https://media1.tenor.com/images/60b54c9f2604313502c1971f4d3e7195/tenor.gif?itemid=5535907",
    "{} just punched {}'s....oof": "https://i.makeagif.com/media/10-25-2015/bsXHxC.gif",
    "{} lands a Do Mawashi Kaiten Geri on {}!": "https://i.pinimg.com/originals/70/3d/cf/703dcf86945f375ecfef5141e8e2aff5.gif",
    "{} did a fancy takedown on {}!": "https://i.makeagif.com/media/3-05-2016/5D6gCK.gif",
    "{} kicked {} multiple times in the chest!": "https://moviesfilmsandflix.files.wordpress.com/2017/09/tumblr_ou2idnirmf1v6w3juo4_500.gif",
    "{} distracted {} with a suitcase and threw a side kick!": "https://cdn.playbuzz.com/cdn/41ffd427-5d74-4fb7-8ea4-1ed2cb98eb87/0c74ec17-04ad-4c62-9e12-9e2fd5d693b4.gif",
    "{} did a flying capoeira kick at {}!": "https://i.imgflip.com/1tfgax.gif",
    "{} threw a 360 spin kick at {}!": "https://media.giphy.com/media/1QNIxRWZGKpgI/giphy.gif",
    "{} knocked {} out with a spinning kick thing!": "https://66.media.tumblr.com/d559f50518c1e57d8d1fb732fc6e55ce/tumblr_mqwnhx9ZTC1r61a7no2_250.gif",
    "{} misses a leg kick and still hits {} with a roundhouse kick!": "https://66.media.tumblr.com/tumblr_m3afej40m91ro43xzo1_400.gif",
    "{} hammer kicked a board and punched {} through the board!": "https://66.media.tumblr.com/2f3d497c2ae87e71037aaa06bf4724de/tumblr_ori1nrncjh1rmrpdmo1_400.gif",
    "{} punched {} through a statue!": "https://66.media.tumblr.com/0b595d67b9ecd1f56832c0d9cc84c3f0/tumblr_p2968hqraP1rmrpdmo4_400.gif",
    "{} used judo throw on {}!": "https://thumbs.gfycat.com/ImpishCompassionateAustraliancurlew-size_restricted.gif",
    "{} kicked {}'s legs while he/she was on a table! Don't stand on furnitures kids.": "https://66.media.tumblr.com/c76d877a93f725e446583f1af1cf2283/tumblr_or4b6u4Xno1syv3zao1_400.gif",
    "{} threw a spinning head kick at {}!":"https://media.giphy.com/media/gasmaAkDqzcFW/giphy.gif",
    "{} smashed {}'s head with two sticks!":"https://i.gifer.com/Im8u.gif",
    "{} threw big hooks at {}!":"https://i.makeagif.com/media/10-04-2015/2rtp-R.gif",
    "{} got some mad anime skills and {} took some heavy hits! Thank god the sword was blunt...":"https://i.gifer.com/Gpw9.gif",
    "{} pulled a Jackie Chan on {}!":"https://66.media.tumblr.com/4c9878322d4bc5315cc5fa6207b66e3f/tumblr_onooa9fsWG1v6w3juo1_500.gif"
    }
    
    blocks = {"{} blocked all of {}'s attacks!": "https://66.media.tumblr.com/6e29fc2555517475c055300480e56922/tumblr_p1643yvSA81rmrpdmo1_400.gif",
    "{} parried {}'s attacks!": "https://i2.wp.com/warriorpunch.com/wp-content/uploads/2017/08/mirror.gif?resize=595%2C335&ssl=1",
    "{} dodged all of {}'s attacks!": "https://media0.giphy.com/media/Tsl0wXsKDiu7S/giphy.gif",
    "{} grabbed a shield and blocked {}'s attacks!": "https://media.giphy.com/media/l0HlymZ7Jv6JoiYjC/giphy.gif",
    "{} blocked {}'s knife attack!": "https://media.giphy.com/media/E8FjnBF1TOpO0/giphy.gif",
    "{} pulled a Neo and blocked {}'s attacks with ease!": "https://media0.giphy.com/media/HTjQEEGqyQTXq/giphy.gif",
    "{} evaded {}'s attacks!":"https://media1.tenor.com/images/82e9b9f2152e7e375ac845aa52de8870/tenor.gif?itemid=7588651",
    "{} caught {}'s kick!": "https://media.giphy.com/media/7XujHz25hunSg/giphy.gif",
    "{} dodged {}'s leg sweep!": "http://mmafury.com/wp-content/uploads/2015/02/Muay-Thai-Fighter-goes-for-a-leg-sweep-but-nope...quick-little-jump-nice-balance-GIF.gif",
    "{} blocked {}'s attacks!": "https://66.media.tumblr.com/8addede13d1c6dd47bb33c2e7440136b/tumblr_pk3de2L4Sb1v6w3juo3_500.gif",
    "{} disarmed {}!": "https://media2.giphy.com/media/MnefNOdkdnDr2/giphy.gif",
    "{} blocked all of {}'s punches with elbows!": "https://i.imgur.com/nxxApiV.gif?noredirect",
    "{} ducked {}'s roundhouse kick!": "https://i.pinimg.com/originals/1f/70/d8/1f70d861132c952b7f2aeb794778025a.gif",
    "{} got drunk and dodged {}'s attacks!": "https://66.media.tumblr.com/dcc6b61ed548038911e915ea94c88078/tumblr_pbvql6zaHu1xthcgdo3_500.gif",
    "{} got mad at {} for interfering with his/her shopping!": "https://thumbs.gfycat.com/BraveFailingCrayfish-size_restricted.gif",
    "{} dodged all of {}'s punches!": "https://media1.tenor.com/images/70d2210f5419789e4342c603c210a09f/tenor.gif?itemid=11739995",
    "{} parried {}'s attacks!": "https://66.media.tumblr.com/3ad228014391bc9a8d87bd521b6c3d66/tumblr_n3m70z1qYv1tw9yl5o4_400.gif",
    "{} blocked and dodged {}'s three-section staff attacks! ": "https://i2.wp.com/78.media.tumblr.com/316497e5ade9bcb0c5ba94d9f12cbc68/tumblr_p96jtrEehi1wstc5to1_400.gif?w=605&ssl=1",
    "{} broke {}'s sword!":"https://thumbs.gfycat.com/MatureDecisiveHedgehog-size_restricted.gif",
    "{} ducked {}'s spinning kick!":"https://thumbs.gfycat.com/PoorReliableAddax-size_restricted.gif",
    "{} caught {}'s punch!":"https://media0.giphy.com/media/5jYeXVJRkf0mfOont4/giphy.gif",
    "{} parried all of {}'s punches and kicks!":"https://i.imgur.com/axgo0ye.gif?noredirect"
    }

    nothingUrl = ["https://thumbs.gfycat.com/PassionateRectangularBrahmancow-small.gif", "https://media.tenor.com/images/eb84105a1eb998307819b358ac485528/tenor.gif", "https://media0.giphy.com/media/tXL4FHPSnVJ0A/giphy.gif", 
    "https://media0.giphy.com/media/l2JhpjWPccQhsAMfu/giphy.gif",
    "https://i.kym-cdn.com/photos/images/newsfeed/001/057/927/eac.gif",
    "https://thumbs.gfycat.com/BogusFarawayBream-max-1mb.gif"
    ]
    def __init__(self, bot):
        self.bot = bot
    
    #linkboi command
    @commands.command(pass_context = True)
    async def give(self, ctx, user: discord.Member, amount):
        if ctx.author.id != 217380909815562241:
            await ctx.send("You're not my creator -.-")
        else:
            cog = self.bot.get_cog("mafia")
            await ctx.send("{} Mafia Points has been added to {}'s account sir.".format(str(amount), user.name))
            self.addPoint(user.id, int(amount), cog)
    
    #linkboi command
    @commands.command(pass_context = True)
    async def deduct(self, ctx, user: discord.Member, amount):
        if ctx.author.id != 217380909815562241:
            await ctx.send("You're not my creator -.-")
        else:
            cog = self.bot.get_cog("mafia")
            await ctx.send("{} Mafia Points has been removed from {}'s account sir.".format(str(amount), user.name))
            self.addPoint(user.id, -1*int(amount), cog)
    

    @commands.command(pass_context= True)
    async def transfer(self, ctx, user:discord.Member, amount:int):
        if user == ctx.author:
            await ctx.channel.send("Don't give money to yourself. That's just sad.")
            return
        
        if user.bot:
            await ctx.channel.send("Don't give a bot money. They prob don't want it lmao.")
            return
        if amount<0:
            await ctx.channel.send("Lol you can't give negative money. Go back to school kid.")
            return
        cog = self.bot.get_cog("mafia")
        cog.checkFile(user.id)
        cog.checkFile(ctx.author.id)
        giver = cog.findUser(ctx.author.id)
        receiver = cog.findUser(user.id)


        if giver.points < amount:
            await ctx.channel.send("Boi, you don't have that much money. Nice try.")
            return
        
        receiver.points += amount
        giver.points -= amount

        cog.editFile(receiver)
        cog.editFile(giver)

        embed = discord.Embed(title = str(amount) + ":moneybag: have been transferred from " + ctx.author.name + " to " + user.name + "'s account.", colour = discord.Colour.green())
        embed.add_field(name = ctx.author.name + "'s balance:", value = str(giver.points) + ":moneybag:")
        embed.add_field(name = user.name + "'s balance:", value = str(receiver.points) + ":moneybag: ")
        embed.set_thumbnail(url = user.avatar_url)
        embed.set_image(url = "https://www.retailgazette.co.uk/wp-content/uploads/shutterstock_465600824.jpg")
        await ctx.channel.send(embed = embed)

    @commands.command(pass_context = True)
    async def duel(self, ctx, victim: discord.Member):
        channel = ctx.channel
        player1 = ctx.author
        if victim.bot:
            await channel.send("You can't challenge a bot. You'll definitely lose!")
        elif victim in self.currentPlaying:
            await channel.send("{} is currently in a duel!".format(victim.name))
        elif player1 in self.currentPlaying:
            await channel.send("{} is currently in a duel!".format(player1.name))
        elif victim != player1:
            try:
                challenge = discord.Embed(title = "{}, {} has challenged you to a duel. Do you accept?".format(victim.name, player1.name), description = "y/n", colour = discord.Colour.red())
                challenge.set_author(name = player1.name, icon_url=player1.avatar_url)
                challenge.set_thumbnail(url = victim.avatar_url)
                challenge.set_image(url = "https://i.ytimg.com/vi/cb5DITStXlI/maxresdefault.jpg")
                await channel.send(embed = challenge)
                try:
                    self.currentPlaying.append(victim)
                    self.currentPlaying.append(player1)
                    answer = await self.bot.wait_for('message', check=lambda message: message.author == victim and (message.content == "y" or message.content == "n" or message.content == "yes" or message.content == "no"), timeout = 30)
                    if answer.content == "y" or answer.content == "yes":
                        
                        supportChannel = self.bot.get_channel(550923896858214446)
                        await supportChannel.send("{} started duel with {}!".format(player1.name, victim.name))
                        await channel.send("Let the duel begin!")
                        await self.playDuel(player1, victim, channel)
                        await supportChannel.send("{} ended duel with {}!".format(player1.name, victim.name))
                        
                    else:

                        await channel.send("{} declined the duel. Guess someone's too scared.".format(victim.name))
                    
                except asyncio.TimeoutError:
                    await channel.send("The session expired.")
                self.currentPlaying.remove(victim)
                self.currentPlaying.remove(player1)
            except:
                if victim in self.currentPlaying:
                    self.currentPlaying.remove(victim)
                if player1 in self.currentPlaying:
                    self.currentPlaying.remove(player1)
        else:
            await channel.send("You can't challenge yourself dummy.")
    
    async def playDuel(self, player1, player2, channel):

        moveList = [None, self.lightAtk, self.heavyAtk, self.blocks]
        p1Health = 100
        p2Health = 100
        p1Disabled = False
        p2Disabled = False
        await channel.send("{} please check your DM!".format(player1.name))
        while p1Health !=0 and p2Health!=0:
            if not p1Disabled:
                p1Moves = await self.getMoves(player1)
            else:
                p1Moves = None

            if not p2Disabled:
                p2Moves = await self.getMoves(player2)
            else:
                p2Moves = None
            p1Disabled = False
            p2Disabled = False
            count = 0

            await asyncio.sleep(2)
            #determines if p1 wins this round
            p1GetsTurn = await self.isWinner(player1, player2, p1Moves, p2Moves, count, channel)
            
            if p1GetsTurn == None:
                embed= discord.Embed(title = "Lol nothing happened.", colour= discord.Colour.red())
                embed.set_image(url = random.choice(self.nothingUrl))
                await channel.send(embed = embed)
                await asyncio.sleep(3)
            elif p1GetsTurn:
                p1MoveInt = int(p1Moves)
                damage = None
                if p1MoveInt == 1:
                    damage = random.randint(10, 20)
                    p2Health -= damage
                elif p1MoveInt == 2:
                    damage = random.randint(21, 30)
                    p2Health -= damage
                elif p1MoveInt == 3:
                    p2Disabled = True
                if p2Health < 0:
                    p2Health = 0
                moveType = moveList[p1MoveInt]
                content = random.choice(list(moveType.keys()))

                embed = discord.Embed(title = content.format(player1.name, player2.name), colour = discord.Colour.red())
                if damage != None:
                    embed.add_field(name = "{} took {} damage!".format(player2.name, str(damage)), value = "{} now has {} health!".format(player2.name, str(p2Health)))
                if p1MoveInt == 3:
                    embed.add_field(name = "{} is stunned next turn!".format(player2.name), value = "Oh boi...")
                embed.set_image(url = moveType[content])
                embed.set_author(name = player1.name, icon_url=player1.avatar_url)
                await channel.send(embed = embed)
                await asyncio.sleep(3)
            else:
                if p2Moves != None:
                    p2MoveInt = int(p2Moves)
                    damage = None
                    if p2MoveInt == 1:
                        damage = random.randint(10, 20)
                        p1Health -= damage
                    elif p2MoveInt == 2:
                        damage = random.randint(21, 30)
                        p1Health -= damage
                    elif p2MoveInt == 3:
                        p1Disabled = True
                    if p1Health < 0:
                        p1Health = 0
                    moveType = moveList[p2MoveInt]
                    content = random.choice(list(moveType.keys()))

                    embed = discord.Embed(title = content.format(player2.name, player1.name), colour = discord.Colour.red())
                    if damage != None:
                        embed.add_field(name = "{} took {} damage!".format(player1.name, str(damage)), value = "{} now has {} health!".format(player1.name, str(p1Health)))
                    embed.set_image(url = moveType[content])
                    embed.set_author(name = player2.name, icon_url=player2.avatar_url)
                    if p2MoveInt == 3:
                        embed.add_field(name = "{} is stunned next turn!".format(player1.name), value = "Oh boi...")
                    await channel.send(embed = embed)
                    await asyncio.sleep(3)
                else:
                    await channel.send("Guess no one's playing. Game over then.")
                    
                    break 
        cog = self.bot.get_cog("mafia")
        cog.checkFile(player1.id)
        cog.checkFile(player2.id)
    
        if p1Health == 0:
            randPoints = random.randint(10, 30)
            self.addPoint(player2.id, randPoints, cog)
            embed = discord.Embed(title = "{} wins the duel!".format(player2.name), colour = discord.Colour.blue())
            embed.set_thumbnail(url = player2.avatar_url)
            embed.add_field(name = "{} received:  ".format(player2.name), value = "{} Mafia points.".format(randPoints))
        elif p2Health == 0:
            randPoints = random.randint(10, 30)
            self.addPoint(player1.id, randPoints, cog)
            embed = discord.Embed(title ="{} wins the duel!".format(player1.name), colour = discord.Colour.blue())
            embed.set_thumbnail(url = player1.avatar_url)
            embed.add_field(name = "{} received:  ".format(player1.name), value = "{} Mafia points.".format(randPoints))
        else:
            embed = discord.Embed(title = "No contest.")
            embed.set_image(url = "https://thumbs.gfycat.com/FailingFavorableBaleenwhale-size_restricted.gif")
        await channel.send(embed = embed)
        
            


 
    async def getMoves(self, member):
        moves = None
        count = 1

        embed = discord.Embed(title = "Alright fighter, choose your move.", description = "Enter the number associated with your choice.", colour = discord.Colour.red())
        embed.add_field(name = "1. Light attack", value = "Beats a heavy attack, but can be blocked.")
        embed.add_field(name = "2. Heavy attack", value = "Beats a block, but can be interupted by a light attack.")
        embed.add_field(name = "3. Block", value = "Blocks light attack and stuns the opponent, but cannot block heavy attack.")
        embed.set_image(url = "https://art.ngfiles.com/images/332000/332918_phatalphd_cowboy-standoff.jpg?f1419452016")
        await member.send(embed = embed)
        try:
            answer = await self.bot.wait_for('message', check=lambda message: message.author == member and (message.content == "1" or message.content == "2" or message.content == "3"), timeout = 30)
            moves = answer.content
            await member.send("Got it. Return to the channel.")

        except asyncio.TimeoutError:
            await member.send("Boi you afk. You gonna die.")
            moves = None
        return moves
    
    async def isWinner(self, player1, player2, playerMoves1, playerMoves2, count, channel):
        #returns whether parameter player1 gets move
        moveNames = ["light attack", "heavy attack", "block"]
        if playerMoves1 == None:
            return False
        elif playerMoves2 == None:
            return True
        person = playerMoves1
        personInt = int(person)

        opponent = playerMoves2
        oppInt = int(opponent)
        embed = discord.Embed(title = "{} chose a {} and {} chose a {}!".format(player1.name, moveNames[personInt-1], player2.name, moveNames[oppInt-1]), colour = discord.Colour.red())
        await channel.send(embed = embed)

        if person == opponent: #If attacks are the same
            return None
        elif person == "3" and opponent == "1":
            return True
        elif (person == "1" and opponent == "3") or (int(person)> int(opponent)):
            return False
        else:
            return True
        
    def addPoint(self, userID, points, cog):
        user = cog.findUser(userID)
        user.points += points
        cog.editFile(user)



def setup(bot):
    bot.add_cog(Duel(bot))
