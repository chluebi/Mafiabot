import dbl
import discord
from discord.ext import commands

import aiohttp
import asyncio
import logging


class DiscordBotsOrgAPI:
    """Handles interactions with the discordbots.org API"""

    def __init__(self, bot):
        self.bot = bot
        self.token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjUxMTc4NjkxODc4MzA5MDY4OCIsImJvdCI6dHJ1ZSwiaWF0IjoxNTQ2NjU0ODk3fQ.hADbMQxWCw0czaTDcVUpqAdCUzEpHngQUw-HtQeHVV8'  #  set this to your DBL token
        self.dblpy = dbl.Client(self.bot, self.token, webhook_path='/dblwebhook', webhook_auth='lin0805', webhook_port=5000)
        self.bot.loop.create_task(self.update_stats())

    async def update_stats(self):
        """This function runs every 30 minutes to automatically update your server count"""

        while True:
            print('attempting to post server count')
            try:
                await self.dblpy.post_server_count()
                print('posted server count')
            except Exception as e:
                print('Failed to post server count\n{}: {}'.format(type(e).__name__, e))
            await asyncio.sleep(1800)

    @commands.Cog.listener()
    async def on_dbl_vote(self, data):
        print(data)
    @commands.command(pass_context = True)
    async def getVoters(self, ctx):
        
        await ctx.channel.send(await self.dblpy.get_upvote_info())

def setup(bot):
    global logger
    logger = logging.getLogger('bot')
    bot.add_cog(DiscordBotsOrgAPI(bot))