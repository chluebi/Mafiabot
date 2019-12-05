import discord
from discord.ext import commands
import random
import sys

import MAFIA.gameRole as ParentR
GameR = ParentR.GameR

class Dictator(GameR):
    def __init__(self):
        GameR.__init__(self)
        self.side = "neutral"
        self.name = "Dictator"
        self.selectSide = None
    
