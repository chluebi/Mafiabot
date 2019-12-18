import discord
from discord.ext import commands
import asyncio
import os
import random
from random import randint
from MAFIA.roles import *

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

    async def setRole(self, roleObj, unassignedPlayers):
        sel = random.choice(unassignedPlayers)
        roleObj.user = sel
        self.mafiaPlayers[sel] = roleObj
        await roleObj.sendInfo()
        unassignedPlayers.remove(sel)

    async def assignRoles(self):
        unassignedPlayers = list(self.mafiaPlayers.keys())
        size = len(unassignedPlayers)
        #if mode = custom
        if isinstance(self.mode, int):
            
            mafiaCog = self.bot.get_cog("mafia")
            customList = mafiaCog.findUser(self.mode).premium.customList.copy()
            roleKey = {
                    "framer" : framer.Framer(),
                    "vigilante" : vigilante.Vig(),
                    "executioner" : executioner.Exe(),
                    "mayor" : mayor.Mayor(),
                    "spy" : spy.Spy(),
                    "pi" : PI.PI(),
                    "distractor" : distractor.Distractor(),
                    "bomber" : bomber.Bomber(),
                    "baiter" : baiter.Baiter()
                }
            await self.setRole(doctor.Doctor(), unassignedPlayers)
            await self.setRole(detective.Det(), unassignedPlayers)
            #big boi mafia
            gfObj = godfather.Godfather()

            if size > 9:
                mafiaObj = mafiaR.Mafia()
                await self.setRole(mafiaObj, unassignedPlayers)
                gfObj.MAFIAPLAYER = mafiaObj
            await self.setRole(gfObj, unassignedPlayers)
            size = len(unassignedPlayers)
            while (size > 0 and len(customList) != 0):
                role = random.choice(customList)
                await self.setRole(roleKey[role], unassignedPlayers)
                customList.remove(role)
                print(role)
                size-=1
            for _ in range(len(unassignedPlayers)):
                await self.setRole(villager.Villager(), unassignedPlayers)
            return
        #if mode != custom
        crazyRoles = [executioner.Exe(), mayor.Mayor(), vigilante.Vig(), spy.Spy()]
        chaosRoles = [PI.PI(), distractor.Distractor()]

        if size > 7:
            crazyRoles.append(framer.Framer())
            chaosRoles.append(baiter.Baiter())
            chaosRoles.append(bomber.Bomber())

        #big boi mafia
        gfObj = godfather.Godfather()

        if size > 9:
            mafiaObj = mafiaR.Mafia()
            await self.setRole(mafiaObj, unassignedPlayers)
            gfObj.MAFIAPLAYER = mafiaObj

        await self.setRole(gfObj, unassignedPlayers)
        
        doctorCount = 1 # see above
        for _ in range(doctorCount):
            await self.setRole(doctor.Doctor(), unassignedPlayers)

        detectiveCount = 1 # see above
        for _ in range(detectiveCount):
            await self.setRole(detective.Det(), unassignedPlayers)
        
        #balance out sides for chaos mode (I've seen a lot of salt)
        if size > 13 and self.mode == "chaos":
            for _ in range(3):
                await self.setRole(villager.Villager(), unassignedPlayers)
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
                await self.setRole(role, unassignedPlayers)
                roleList.remove(role)
                count-=1
        #assign leftover bois to villagers
        for _ in range(len(unassignedPlayers)):
            await self.setRole(villager.Villager(), unassignedPlayers)
            
        # WARNING: Number of people in the game needs to be higher than the sum of the _____counts
        # Ex. mafiaCount + doctorCount + detectiveCount + politicianCount = 4, so if there are more
        # than 4 people playing then it will fail to allocate roles. Maybe add feature that doesn't
        # have certain roles if the number of players is too low.
 
        
