import discord
from discord.ext import commands
import random
import MAFIA.gameRole as ParentR
GameR = ParentR.GameR

class Mafia(GameR):
    def __init__(self, user):
        GameR.__init__(self, user)
        self.side = "mafia"
        self.name = "mafia"
    
    def deathCheck(self, killer_role):
        """
        Key:
        0 = Kill successful
        1 = Kill unsuccessful
        """
        

