import discord
from discord.ext import commands
import random
import sys
sys.path.insert(1, 'C:/Users/Ernest/Desktop/Mafiabot/Mafiabot-1/MAFIA')
import gameRole as ParentR
GameR = ParentR.GameR

class Mafia(GameR):
    def __init__(self, user):
        GameR.__init__(self, user)
        self.side = "mafia"
        self.name = "mafia"
    
    def check(self, visitor_role_obj):
        return
    
    async def perform(self, currentP):
        victimRoleObj = self.findRoleObj(self.victim, currentP)
        victimRoleObj.check(self)
        

