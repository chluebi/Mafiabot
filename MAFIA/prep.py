import discord
from discord.ext import commands
import asyncio
import os
import random
import MAFIA.playerinfo as playerinfo
import MAFIA.gvar as gvar

class prepare:

    def randInt(self, chance, whole):
        result = random.randint(chance, whole)
        if result <= chance:
            return True
        else:
            return False

    def __init__(self, bot, mafiaPlayers):
        self.mafiaPlayers = mafiaPlayers
        self.bot = bot
        
    def setRole(self, roleName, unassignedPlayers):
        sel = random.choice(unassignedPlayers)
        self.mafiaPlayers[sel] = playerinfo.Player(roleName, True)
        unassignedPlayers.remove(sel)

    def assignRoles(self):
        unassignedPlayers = list(self.mafiaPlayers.keys())
        
        count = 0
        mafiaCount = 0
        for _ in range(len(unassignedPlayers)):
            if count == 3:
                mafiaCount += 1
                count = 0
            else:
                count += 1
        
        # Maybe add calculation to determine (1 mafia per 3 villagers etc)
        for _ in range(mafiaCount):
            self.setRole("mafia", unassignedPlayers)

        doctorCount = 1 # see above
        for _ in range(doctorCount):
            self.setRole("doctor", unassignedPlayers)

        detectiveCount = 1 # see above
        for _ in range(detectiveCount):
            self.setRole("detective", unassignedPlayers)


        if len(self.mafiaPlayers.keys()) > 5:
            chance = self.randInt(70, 100)
            if chance == True:
                self.setRole("suspect", unassignedPlayers)
        if len(self.mafiaPlayers.keys()) > 4:
            self.setRole("jester", unassignedPlayers)
        for _ in range(len(unassignedPlayers)):
            self.setRole("villager", unassignedPlayers)
            
        # WARNING: Number of people in the game needs to be higher than the sum of the _____counts
        # Ex. mafiaCount + doctorCount + detectiveCount + politicianCount = 4, so if there are more
        # than 4 people playing then it will fail to allocate roles. Maybe add feature that doesn't
        # have certain roles if the number of players is too low.
 
        
