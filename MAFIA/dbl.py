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
        self.token = ''  #  set this to your DBL token
        self.dblpy = dbl.DBLClient(self.bot, self.token)
        self.bot.loop.create_task(self.update_stats())

    async def update_stats(self):
        """This function runs every 30 minutes to automatically update your server count"""

        while True:
            print('attempting to post server count')
            try:
                await self.dblpy.post_guild_count()
                print('posted server count')
            except Exception as e:
                print('Failed to post server count\n{}: {}'.format(type(e).__name__, e))
            await asyncio.sleep(1800)


def setup(bot):
    global logger
    logger = logging.getLogger('bot')
    bot.add_cog(DiscordBotsOrgAPI(bot))