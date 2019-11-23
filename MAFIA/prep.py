import discord
from discord.ext import commands
import asyncio
import os
import random
from random import randint
"""
import MAFIA.playerinfo as playerinfo
import MAFIA.gvar as gvar
"""
from roles import *

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
        self.villagerR = ["villager", "doctor", "detective", "PI", "mayor", "vigilante", "spy"]
        self.mafiaR = ["mafia", "godfather", "framer"]
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
        crazyRoles = ["executioner", "mayor", "vigilante"]
        chaosRoles = ["spy", "PI", "distractor"]
        if size > 5:
            crazyRoles.append("framer")
        if size > 6:
            chaosRoles.append("baiter")
            chaosRoles.append("bomber")
            
        if size > 7:
            self.setRole("mafia", unassignedPlayers)
            chaosRoles.append("dictator")

        #big boi mafia
        self.setRole("godfather", unassignedPlayers)

        
        doctorCount = 1 # see above
        for _ in range(doctorCount):
            self.setRole("doctor", unassignedPlayers)

        detectiveCount = 1 # see above
        for _ in range(detectiveCount):
            self.setRole("detective", unassignedPlayers)
        
        #balance out sides for chaos mode (I've seen a lot of salt)
        if size > 10 and self.mode == "chaos":
            for _ in range(3):
                self.setRole("villager", unassignedPlayers)
        roleList = []
        if self.mode == "crazy":
            roleList = crazyRoles
        
        if self.mode == "chaos":
            roleList = crazyRoles + chaosRoles
        random.shuffle(roleList)
        if (self.mode != "classic"):
            count = len(unassignedPlayers)

            while (count > 0 and len(roleList) != 0):
                role = random.choice(roleList)
                self.setRole(role, unassignedPlayers)
                roleList.remove(role)
                count-=1
        for _ in range(len(unassignedPlayers)):
            self.setRole("villager", unassignedPlayers)
            
        # WARNING: Number of people in the game needs to be higher than the sum of the _____counts
        # Ex. mafiaCount + doctorCount + detectiveCount + politicianCount = 4, so if there are more
        # than 4 people playing then it will fail to allocate roles. Maybe add feature that doesn't
        # have certain roles if the number of players is too low.
 
        
