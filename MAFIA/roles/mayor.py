import discord
from discord.ext import commands
import random
import MAFIA.gameRole as ParentR
GameR = ParentR.GameR

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
                    if user.id != 480553111971430420 and (reaction.emoji == '🇾' or reaction.emoji == '🇳'):
                        answerEmoji = reaction.emoji
                        break
            if answerEmoji == '🇾':
                self.revealed = True
                await self.user.send("You have decided to reveal yourself tomorrow.")
            else:
                await self.user.send("Alright, not revealing yourself yet...")