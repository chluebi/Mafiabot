import discord
from discord.ext import commands
import asyncio
import os

class Turns():
    def __init__(self, bot):
        self.bot = bot
        
    #returns player object
    def getPlayer(self, players, person):
        for player, data in players.items():
            if (player.name.lower() == person.lower()):
                return player
        return None
    #returns player role name
    def getRole(self, players, person):
        for player, data in players.items():
            if (player.name.lower() == person):
                return data.roleName
        return None
    def getRoleWName(self, players, person):
        for player, data in players.items():
            if person.lower() == player.name.lower():
                return data.roleName
    def findPlayerWithRole(self, players, role):
        for player, data in players.items():
            if (data.roleName == role):
                return player
        return None
    async def killPlayer(self, party, person):
        target = self.getPlayer(party, person)
        party[target].alive = False
        embed = discord.Embed(title = "Hey, you're dead! Feel free to spectate the rest of the game but PLEASE do not talk nor give away important information to those still playing. Thank you!", description = "PS. If you're bored while waiting, I can also play mini games! Type m.mini to check it out!", colour = discord.Colour.blurple())
        embed.set_thumbnail(url = "https://i.kym-cdn.com/photos/images/newsfeed/000/883/622/d2e.png")
        await target.send(embed = embed)
        try:
            await target.edit(mute = True)
        except discord.HTTPException:
            pass

    async def muteAll(self, party):
        for player in party.keys():
            try:
                await player.edit(mute = True)
            except discord.HTTPException:
                pass
    async def unMuteAll(self, party):
        for player in party.keys():
            try:
                await player.edit(mute = False)
            except discord.HTTPException:
                pass
    async def muteDead(self, party):
        for player, data in party.items():
            if data.alive == False:
                try:
                    await player.edit(mute = True)
                except discord.HTTPException:
                    pass  
            
            elif data.alive == True:
                try:
                    await player.edit(mute = False)
                 
                except discord.HTTPException:
                    pass 
    
    def isAlive(self, party, person):
        for player, data in party.items():
            if person == player.name.lower():
                return data.alive

    async def vote(self, party, channel, voteTime, mayor, mRevealed, minVote):

        alivePeople = []
        
       #objects
        targets = {}
        #messages
        alreadyVoted = []
        for player, data in party.items():
            if data.alive == True:
                targets[player] = {}
                alivePeople.append(player)
        for item in targets:
            targetE = discord.Embed(colour = discord.Colour.purple())
            targetE.add_field(name = item.name, value = "React to this message to vote for me!")
            targetE.set_thumbnail(url = item.avatar_url)
            voteMsg = await channel.send(embed = targetE)
            await voteMsg.add_reaction('\U0001F44D')
            targets[item]["message"] = voteMsg
            targets[item]["count"] = 0
        
        await asyncio.sleep(voteTime)

        bigVote = 0
        currentTarget = None

        for person in targets.keys():
            
            msg = targets[person]["message"]
            cache_msg = await channel.fetch_message(msg.id)
            for reaction in cache_msg.reactions:
                async for user in reaction.users():

                    if not user.name.lower() in alreadyVoted and user in alivePeople:
                        if mRevealed and mayor != None and mayor.name.lower() == user.name.lower():
                            targets[person]["count"] += 2
                        else:
                            targets[person]["count"] += 1
                        alreadyVoted.append(user.name.lower())
            
            if targets[person]["count"] > bigVote:
                bigVote = targets[person]["count"]
                currentTarget = person
            elif targets[person]["count"] == bigVote:
                currentTarget = None
        totalVotes = discord.Embed(title = "Final tally.", colour = discord.Colour.orange())
        for item in targets.keys():
            totalVotes.add_field(name = item.name, value = targets[item]["count"])
        await channel.send(embed = totalVotes)
        if bigVote < minVote:
            currentTarget = None
        if currentTarget != None:
            await channel.send("The town decided to lynch {}".format(currentTarget.name))
        return currentTarget

    def makeEmbed(self, message):
      embed = discord.Embed(title = message, colour = discord.Colour.green())
      return embed
    
    async def duh(self, channel):
        await channel.send("duh")