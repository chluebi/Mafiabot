import discord
from discord.ext import commands
import random
import sys
sys.path.insert(1, 'C:/Users/Ernest/Desktop/Mafiabot/Mafiabot-1/MAFIA')
import gameRole as ParentR
GameR = ParentR.GameR

class Exe(GameR):
    def __init__(self, user):
        GameR.__init__(self, user)
        self.side = "neutral"
        self.target = None
        self.name = "executioner"

