import discord
from discord.ext import commands
import asyncio
import json
import os
import random
import logging
import traceback

import MAFIA.dbl as dblthing
bot = commands.Bot(command_prefix='m.')
bot.remove_command('help')

extensions = ['mafia', 'Points', 'help']
players = {}
@bot.event
async def on_ready():
    dblthing.DiscordBotsOrgAPI(bot)
    servers = len(list(bot.servers))
    print ("Currently on {} servers!".format(servers))
    
    await bot.change_presence(game = discord.Game(name="m.help", type=1))
    print("Mafiabot is online!")

@bot.event
async def on_message(message):
    if message.author != bot.user:
        await bot.process_commands(message)

@bot.event
async def on_server_join(server):
    await bot.send_message(discord.Object(550923896858214446), "Joined server ({}: {} members) ".format(server.name, len(server.members)))
    print ("Joined server ({}: {} members) ".format(server.name, len(server.members)))



@bot.event
async def on_server_remove(server):
    await bot.send_message(discord.Object(550923896858214446), "Left server ({}: {} members) ".format(server.name, len(server.members)))
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
    bot.run(thing)