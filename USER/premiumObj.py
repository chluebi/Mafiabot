import discord
from discord.ext import commands

class PremiumObj:

    def __init__(self, roleID = 0, customList = [], userID = 0):
        self.roleID = roleID 
        self.customList = customList
        self.userID = userID
        