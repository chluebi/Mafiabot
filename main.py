import discord
from discord.ext import commands
import asyncio
import json
import os
import random
import traceback
import MAFIA.dbl as dblthing
bot = commands.Bot(command_prefix='m.')
bot.remove_command('help')

extensions = ['mafia', 'Points', 'help']
players = {}
@bot.event
async def on_ready():
    dblthing.DiscordBotsOrgAPI(bot)
    await bot.change_presence(game = discord.Game(name="m.help", type=1))
    print("I'm in")

@bot.event
async def on_message(message):
    with open('players.json', 'r') as f:
        players = json.load(f)
    if not message.server is None:
        if not message.server.id in players:
            players[message.server.id] = {}
    with open('players.json', 'w') as f:
        json.dump(players, f)
    if message.author != bot.user:
        await bot.process_commands(message)

@bot.event
async def on_server_join(server):
    print ("Joined server ({})".format(server.name))

@bot.event
async def on_server_remove(server):
    print ("Left server ({})".format(server.name))
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