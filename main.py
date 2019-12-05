import discord
from discord.ext import commands
import asyncio
import json
import os
import random
import logging
import traceback
import MAFIA.dbl as dblthing
bot = commands.AutoShardedBot(command_prefix='m.', shard_count = 3, activity = discord.Game(name="m.help", type=1))
bot.remove_command('help')

extensions = ['mafia', 'Points', 'duel', 'slot', 'help', 'troll']
players = {}
boi = "boi"
@bot.event
async def on_ready():
    dblthing.DiscordBotsOrgAPI(bot)
    servers = len(list(bot.guilds))
    print ("Currently on {} servers!".format(servers))
    
    print("Mafiabot is online!")
    error = logging.getLogger('discord')
    error.setLevel(logging.ERROR)
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    error.addHandler(handler)

    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='debug.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

    info = logging.getLogger("discord")
    info.setLevel(logging.INFO)
    handler = logging.FileHandler(filename='info.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    info.addHandler(handler)

@bot.event
async def on_message(message):
    if message.author != bot.user:
        await bot.process_commands(message)

@bot.event
async def on_guild_join(server):

    supportChannel = bot.get_channel(550923896858214446)
    embed = discord.Embed(title = "Joined server {}".format(server.name), description = "{} members".format(len(server.members)), colour = discord.Colour.green())
    embed.set_thumbnail(url = server.icon_url)
    await supportChannel.send(embed = embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        if error.param.name == "user" or error.param.name == "victim":
            await ctx.channel.send("Looks like you forgot to @ someone.")
            return
        if error.param.name == "mode":
            await ctx.channel.send("Looks like you forgot to put a mode. The available modes are classic and crazy.")
            return
        await ctx.channel.send("Looks like you forgot a required argument: `{arg}`. lol.".format(
                    arg=error.param.name
                ))
    elif isinstance(error, commands.BadArgument):
        await ctx.channel.send("Call me stupid but I don't understand that input.")
    else:
        print(error)
 



@bot.event
async def on_guild_remove(server):
    supportChannel = bot.get_channel(550923896858214446)
    embed = discord.Embed(title = "Left server {}".format(server.name), description = "{} members".format(len(server.members)), colour = discord.Colour.red())
    embed.set_thumbnail(url = server.icon_url)
    await supportChannel.send(embed = embed)
    print ("Left server ({}: {} members) ".format(server.name, len(server.members)))

    
if __name__ == '__main__':
    for extension in extensions:
        try:
            if(extension == "mafia"):
                bot.load_extension(f"MAFIA.{extension}")
            else:
                bot.load_extension(extension)
        except Exception as error:
            print('{} cannot be loaded because {}'.format(extension, error))
    with open('key.json', 'r') as f:
        keys = json.load(f)
    thing = keys['key']
    testThing = keys['test']
    bot.run(thing)