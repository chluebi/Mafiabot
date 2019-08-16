import discord
from discord.ext import commands
import asyncio
import os

class Turns():
    def __init__(self, bot):
        self.bot = bot
    async def dmNight(self, player, dmTime, targets, title, description, colour, img):
        print(player)
        dmEmbed = discord.Embed(title = title, description = description, colour = colour)
        dmEmbed.set_footer(text = "You have {} seconds to answer".format(str(dmTime)))
        dmEmbed.set_image(url = img)
        dmEmbed.add_field(name = "0- Choose no one tonight", value = "Pick me!", inline = False)

        for item in targets:
            dmEmbed.add_field(name = str(targets.index(item)+1) + "- " + item, value = "Pick me!", inline = False)
        await player.send(embed = dmEmbed)

        answer = await self.bot.wait_for('message', check=lambda message: message.author == player, timeout = dmTime)
        while True:
            try:
                answerIndex = int(answer.content)
                if (answerIndex <= len(targets) and answerIndex >= 0):
                    await player.send("Got it.")
                    if (answerIndex == 0):
                        return None
                    
                    return targets[answerIndex-1]
                else:
                    await player.send("Unknown index. Try again.")
                    
            except ValueError:
                await player.send("That's not a valid number.")
            answer = await self.bot.wait_for('message', check=lambda message: message.author == player, timeout = dmTime)
                
    async def mafiaturn(self, players, temp, dmTime, mafiaNames, mafias):
        
        isSame = False
        voteTurn = 0
        while isSame == False:
            if voteTurn != 0:
                for player in mafias:
                    await player.send( embed = self.makeEmbed("The vote for the victim is not unanimous. Please coordinate among yourselves through dm and decide on a victim."))
            mafiaKillVote = []
            for player in mafias:
                
                tempM = []

                for thing in temp:
                    if not thing in mafiaNames:
                        tempM.append(thing)
                
                other = self.makeEmbed("Candidates chosen by other mafias:")
                if mafiaKillVote:
                    for item in mafiaKillVote:
                        other.add_field(name = "{}".format(item), value = "Hi!", inline = True)
                    await player.send( embed = other)

                try:
                    answer = await self.dmNight(player, dmTime, tempM, "Here are you targets mafia.", "Enter the number associated with your target.", discord.Colour.red(), "https://www.mobafire.com/images/champion/skins/landscape/graves-mafia.jpg")
                    mafiaKillVote.append(answer)
                except asyncio.TimeoutError:
                    print('duh')
                    await player.send("Feelsbad, you ran out of time.")


            if mafiaKillVote:
                kill = mafiaKillVote[0]
                isSame = True
                for item in mafiaKillVote:
                    if item != None and item != kill:
                        isSame = False
                        break
            else:
                kill = None
                break
            voteTurn += 1
        if kill != None:
            embed = self.makeEmbed("Your target is {}".format(kill))
            for player in mafias:
                await player.send( embed = embed)
        return kill
    
    async def doctorTurn(self, doctor, temp, dmTime, lastHeal):
        doctList = []
        for person in temp:
            if  person != lastHeal:
                doctList.append(person)
        try:
            answer = await self.dmNight(doctor, dmTime, doctList, "Doctor, who would you want to save tonight? (You cannot save the same person twice in a row)", "Enter the number associated with your target.", discord.Colour.blue(), "https://vignette.wikia.nocookie.net/leagueoflegends/images/f/f7/Akali_NurseSkin_old.jpg/revision/latest?cb=20120609043410")
        except asyncio.TimeoutError:
            answer = None
            await doctor.send("You ran out of time. Feelsbad.")
        return answer
    async def framerTurn(self, players, framer, dmTime):
        framerList = []

        for player, data in players.items():
            if data.roleName != "framer" and data.roleName != "mafia" and data.alive == True:
                framerList.append(player.name.lower())
        try:
            answer = await self.dmNight(framer, dmTime, framerList, "Framer, who would you like to frame tonight?", "Enter the number associated with your target.", discord.Colour.red(), "https://cdn.drawception.com/images/panels/2017/12-17/zKXCDSXfeA-4.png")
        except asyncio.TimeoutError:
            answer = None
            await framer.send("You ran out of time. Feelsbad.")
        return answer
    async def detTurn(self, detective, temp, dmTime, mafiaMember, framerVictim, framer):
        mafiaList = []
        for item in mafiaMember:
            mafiaList.append(item.name.lower())
        tempDT = []
        for item in temp:
            if item.lower() != detective.name.lower():
                tempDT.append(item)
        try:
            answer = await self.dmNight(detective, dmTime, tempDT, "Who do you suspect?", "Enter the number associated with your target.(If you distract someone tonight, you will be on cooldown the next night)", discord.Colour.orange(), "https://na.leagueoflegends.com/sites/default/files/styles/scale_xlarge/public/upload/cops_1920.jpg?itok=-T6pbISx")
            if answer == None:
                await detective.send("Ok wise guy.")
            else:
                if (answer.lower() in mafiaList or (framerVictim != None and answer.lower() == framerVictim.lower() ) or (framer != None and answer.lower()== framer.name.lower())):
                    embedDet = self.makeEmbed("Yes. That person is on the mafia's side. Now try to convince the others. Please return to the mafia chat now.")
                    embedDet.set_thumbnail(url = "http://www.clker.com/cliparts/P/S/9/I/l/S/234-ed-s-sd-md.png")
                else:
                    embedDet = self.makeEmbed("Sorry. That person is not the mafia. Please return to the mafia chat now.")
                    embedDet.set_thumbnail(url = "https://iconsplace.com/wp-content/uploads/_icons/ff0000/256/png/thumbs-down-icon-14-256.png")
                await detective.send(embed = embedDet)
                return answer.lower()
        except asyncio.TimeoutError:
            await detective.send("You ran out of time.")
            return None

    async def vigTurn(self, vig, temp, dmTime):
        #await channel.send(embed = self.makeEmbed("Vigilante please check your dm."))
        tempV = []
        for player in temp:
            if player.lower() != vig.name.lower():
                tempV.append(player.lower())
                
        try:
            answer = await self.dmNight(vig, dmTime, tempV, "Vigilante, who do you want to shoot? (If you shoot an innocent boi you will commit suicide)", "Enter the number associated with your target.", discord.Colour.green(), "https://pmcdeadline2.files.wordpress.com/2018/03/arrow.png?w=446&h=299&crop=1")
        except asyncio.TimeoutError:
            answer = None
            await vig.send("Feelsbad you ran out of time.")
        return answer
                        
    async def mayorTurn(self, mayor, dmTime):
        
        revealed = False
        
        embed = discord.Embed(title = "Hi mayor. Would you like to reveal yourself next morning to have two votes? (y/n)", colour = discord.Colour.dark_gold())
        embed.set_image(url = "https://vignette.wikia.nocookie.net/familyguy/images/c/cf/Adam_We.JPG/revision/latest?cb=20060929205011")
        await mayor.send( embed = embed)
        def mcheck(m):
            return m.author == mayor
        try:
            answer = await self.bot.wait_for('message', check = mcheck, timeout = dmTime)
            while True:
                if answer == None:
                    await mayor.send( embed = self.makeEmbed("Time's up. No reveal today."))
                    break
                elif answer.content.lower() == "y" or answer.content.lower() == "yes":
                    await mayor.send(embed = self.makeEmbed("Alright. You will be revealed and gain two votes each voting phase."))
                    revealed = True
                    break
                elif answer.content.lower() == "n" or answer.content.lower() == "no":
                    await mayor.send(embed = self.makeEmbed("Alright, not revealing yourself yet."))
                    break
                else:
                    await mayor.send( embed = self.makeEmbed("Error. Idk what you typed but it's not the right input."))
                    answer = await self.bot.wait_for('message', check = mcheck, timeout = dmTime)
        except asyncio.TimeoutError:
            pass
        
        return revealed

    async def distractorTurn(self, distractor, temp, dmTime, lastVictim):
        tempD = []
        
        for player in temp:
            if player.lower() != distractor.name.lower():
                if lastVictim == None:
                    tempD.append(player.lower())
                elif not lastVictim.lower() == player.lower():
                    tempD.append(player.lower())
        
        if lastVictim != None:
            tempD.remove(lastVictim)
        try:
            answer = await self.dmNight(distractor, dmTime, tempD, "Distractor, who do you want to distract tonight?", "Enter the number associated with your target.(If you distract someone you have to wait one night before you can distract someone again)", discord.Colour.orange(), "https://www.dolmanlaw.com/wp-content/uploads/2017/03/The-Many-Types-of-Technology-that-can-Cause-Distracted-Driving-1.jpg")
        except asyncio.TimeoutError:
            answer = None
            await distractor.send("Feelsbad you ran out of time.")
        return answer

    async def PITurn(self, PI, currentL, currentP, dmTime, framerVictim):
        temp = []
        for player in currentL:
            if player.lower() != PI.name.lower():
                temp.append(player.lower())
        
        try:
            answer1 = await self.dmNight(PI, dmTime, temp, "Alright PI, who's your first suspect?", "Enter the number associated with your target.", discord.Colour.blurple(), "https://i.pinimg.com/originals/08/64/a5/0864a55a5c3b2b8e0e2b1b8c231c93a3.jpg")
        except asyncio.TimeoutError:
            answer1 = None
            await PI.send("Feelsbad you ran out of time.")
        
        if answer1 != None:
            temp.remove(answer1)
            try:
                answer2 = await self.dmNight(PI, dmTime, temp, "Alright PI, who's your second suspect?", "Enter the number associated with your target.", discord.Colour.blurple(), "https://i.pinimg.com/originals/08/64/a5/0864a55a5c3b2b8e0e2b1b8c231c93a3.jpg")
                if answer2 !=None:
                    cog = self.bot.get_cog("mafia")
                    role1 = self.getRoleWName(currentP, answer1)
                    role2 = self.getRoleWName(currentP, answer2)
                    side1 = cog.checkSide(role1)
                    side2 = cog.checkSide(role2)
                    if framerVictim == answer1:
                        side1 = "mafia"
                    elif framerVictim == answer2:
                        side2 = "mafia"

                    if side1 == side2:
                        embed = discord.Embed(title = "Yes. {} and {} are both on the same side. It's up to you to figure out what side though lol.".format(answer1, answer2), colour = discord.Colour.green())
                        embed.set_thumbnail(url = "http://www.clker.com/cliparts/P/S/9/I/l/S/234-ed-s-sd-md.png")
                    else:
                        embed =  discord.Embed(title = "No. {} and {} are not on the same side. Hmmmmmmmmmm.".format(answer1, answer2), colour = discord.Colour.red())
                        embed.set_thumbnail(url = "https://iconsplace.com/wp-content/uploads/_icons/ff0000/256/png/thumbs-down-icon-14-256.png")
                    await PI.send(embed = embed)
                else:
                    await PI.send("Ok wise guy.")
            except asyncio.TimeoutError:
                answer2 = None
                await PI.send("Feelsbad you ran out of time.")
            

    async def spyTurn(self, spy, tempList, dmTime):
        temp = []
        for item in tempList:
            if item.lower() != spy.name.lower():
                temp.append(item.lower())
        try:
            answer = await self.dmNight(spy, dmTime, temp, "Alright spy, who are you spying tonight?", "Enter the number associated with your target.", discord.Colour.blurple(),  "https://cdn.vox-cdn.com/thumbor/I3GT91gn4U3jc4HmBY5LjowXzuM=/0x0:1215x717/1200x800/filters:focal(546x35:740x229)/cdn.vox-cdn.com/uploads/chorus_image/image/57172117/Evelynn_Splash_4.0.jpg")
            await spy.send("You will be given the results after all the other roles have finished. Please navigate back to the mafia text channel and wait.")
        except asyncio.TimeoutError:
            answer = None
        
        return answer
         
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