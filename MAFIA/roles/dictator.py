import discord
from discord.ext import commands
import random
import MAFIA.gameRole as ParentR
GameR = ParentR.GameR

class Dictator(GameR):
    def __init__(self, user):
        GameR.__init__(self, user)
        self.side = "neutral"
        self.name = "Dictator"
        self.selectSide = None