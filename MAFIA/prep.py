import discord
from discord.ext import commands
import asyncio
import os
import random
from random import randint
import MAFIA.playerinfo as playerinfo
import MAFIA.gvar as gvar

class prepare:

    def randInt(self, chance, whole):
        result = random.randint(chance, whole)
        if result <= chance:
            return True
        else:
            return False

    def __init__(self, bot, mafiaPlayers, mode):
        self.mafiaPlayers = mafiaPlayers
        self.mode = mode
        self.bot = bot
        
    def setRole(self, roleName, unassignedPlayers):
        randthing = random.randint(3, 150)
        for _ in range(randthing):
            sel = random.choice(unassignedPlayers)
        self.mafiaPlayers[sel] = playerinfo.Player(roleName, True)
        unassignedPlayers.remove(sel)

    def assignRoles(self):

        unassignedPlayers = list(self.mafiaPlayers.keys())
        size = len(unassignedPlayers)
        random.shuffle(unassignedPlayers)
        extraRoles = ["executioner", "mayor", "vigilante", "distractor", "spy", "PI",]
        if size>5:
            extraRoles.append("framer")
            extraRoles.append("dictator")
        if size > 6:
            extraRoles.append("baiter")
            extraRoles.append("bomber")
            self.setRole("mafia", unassignedPlayers)


        self.setRole("godfather", unassignedPlayers)

        
        doctorCount = 1 # see above
        for _ in range(doctorCount):
            self.setRole("doctor", unassignedPlayers)

        detectiveCount = 1 # see above
        for _ in range(detectiveCount):
            self.setRole("detective", unassignedPlayers)
        if (self.mode == "crazy"):
            count = len(unassignedPlayers)
            
            while (count > 0 and len(extraRoles) != 0):
                role = random.choice(extraRoles)
                self.setRole(role, unassignedPlayers)
                print(role)
                extraRoles.remove(role)
                count-=1
        for _ in range(len(unassignedPlayers)):
            self.setRole("villager", unassignedPlayers)
            
        # WARNING: Number of people in the game needs to be higher than the sum of the _____counts
        # Ex. mafiaCount + doctorCount + detectiveCount + politicianCount = 4, so if there are more
        # than 4 people playing then it will fail to allocate roles. Maybe add feature that doesn't
        # have certain roles if the number of players is too low.
 
        
