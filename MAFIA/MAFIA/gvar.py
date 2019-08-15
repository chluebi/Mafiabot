import os
import discord
from discord.ext import commands
import random

class glob:
    def __init__(self, bot, playerL):
        global gameID
        gameID = []
        self.playerL = playerL
        for item in self.playerL:
            thing = random.choice(self.playerL)
            gameID.append(thing)
            self.playerL.remove(item)
        