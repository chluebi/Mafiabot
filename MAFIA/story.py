import discord
from discord.ext import commands
import asyncio
import os
import random

class storyTime:

    badS = [
    "{} was playing league one day, when suddenly all the electricity went out, and thye were found dead in front of the computer later. The teammates were not happy with the afk and {} received a 14 day ban. Oof.", 
    "{} decided to go to Comic Con this year. However they were stabbed by a Kirito cosplayer during the event, and no one could find {}'s killer."
    , "{} and their waifu are on a date, and they decide to go in a love tunnel. However, when they came out, only {}'s body remained. Turns out the waifu also works for the Mafia."
    , "One day {} was running across a bridge. All of a sudden, they see a child crying on the road. {} walks up to the child and asks whats wrong. After five minutes, they was found dead by a tunnel.",
    "{} is on a date (somehow). When {} asked the date what is their occupation they said 'Hired Gun' and shot him/her 3 times. What an unlucky boi.",
    "{} is at a concert one night with their friends. When the friends came back from the bathroom, {} was found strangled.",
    "{} was plagued by a dreams of slenderman. The one fateful night came. they were found in their room dead. When the cops analyzed the footage from their computer, there was no slenderman or supernatural force, it white light was shining above a suit. {} scared themselves so hard, they pissed themselves and died of a heartattack.",
    "{} was walking alone at night(because they has no friends) when suddenly a van pulled over and grabbed {}. The body was found later in a dumpster.",
    "{} was playing super smash bros one night, when suddenly their house exploded and {} lost to a level 1 CPU.",
    "{} was sitting in their room watching youtube, when suddenly they heard a doorbell. {} opened the door and saw a box on the ground. The box exploded.",
    "{} was found dead in a room. {} thought it was bdsm. Turns out, they were whipped to death.",
    "{} trained in martial arts by watching Bruce Lee movies, and now they decided that they are now the master of fighting. {} was later found dead in a dark alley. What a legend.", 
    "{} wanted to buy the fortnite battlepass, but they're out of money, so {} decided to loan some money from the Mafia. The body was found 2 hours later.",
    "{} was too busy playing fortnite and didn't hear the door open, {} was shot and didnt get that epic victory royale.", "A large birthday party was thrown for {} and all their friends were present. During the birthday song, a stranger snuck up behind {} and pantsed them. The victim, flushed with embarrassment, died instantly.", 
    "{} challenged the mafia to a 1v1 basketball match. Down by two points, the mafioso stepped behind the three-point line and shot. {} was later found dead with a bullet wound in his chest.",
    "{} went on holiday to see the ‘We Luv Pandas' panda zoo in China. While distracted, someone from behind pushes them beyond the barrier; before they could turn around {} was miserably flattened by a panda. Human pancakes, anyone?", "{} forgot to lock their door last night, which was why the Mafia was able to release a rabid duck into their house. Minutes later, the duck let out a quack of triumph.  It turns out that {} had an extreme fear of ducks, and died of shock.",
    "T’was the night before Christmas and all through the house, not a creature was stirring...unless you count {} collapsing to the ground after eating a poisoned cookie. Rip {}.",
    "{} was watching too much anime, so much anime they began having hallucinations. One hallucination was the waifu slashing a knife at {}. But the hallucination turned out to be real and the “waifu” was actually the mafia.",
    "{} was on a dating app and kept on swiping. they saw the most beautiful person in the most beautiful picture with a copyright watermark. {} got themselves a date. Too bad that the “beautiful person” had an obsession with knives. The beautiful person was actually the mafia. Seems they didn’t get the cutting point.",
    "One night {} was eating a steak in a restaurant. They are laughing while holding a knife. Then a waiter accidentally bumps {} and they stab themselves in the neck. Turns out the waiter was Mafia and the 'accident' wasn't an accident.",
    "One night {} was visited by the mafia and they played Russian Roulette, unfortunately  {} went first and the gun was fully loaded.", 
    "{} was granted one wish by the god fairy mafia. The mafia waved his wand and {} went bippity-boppity-boo.", 
    "{} accused a level 100 mafia boss of being a level 1 crook. {} was later found sleeping with the fishes while pushing up daisies because that's how mafia works.",
    "{} got lost in the woods looking for his spactula, and {} was never seen again.",
    "The mafia told {} that if you jumped off the top of the balcony you would float, as it was one of the places where zero gravity existed. {} tried it, but fell. Everybody thought he/she was dumb but at least it’s a warning that gravity exists. Take that flat earthers."]

    goodS = ["{} ate a cookie and started choking. Luckily the doctor was nearby and saved {}. Turns out someone replaced the chocolate chips with rocks. Ew.",
    "{} was playing hearthstone when suddenly the computer exploded. Thankfully the doctor was outside the house and saved him/her just in time. Sadly {} lost the match due to afk and is still stuck in rank 25.",
    "One day {} saw a kitten on the road. When they went over to pet it the kitten exploded. Thankfully {} survived because the doctor was there.",
    "{} was eating ice cream at a park when they started feeling ill and collapsed. Thankfully the doctor was there and took {} to a hospital quickly.",
    "{} went to Disneyland, but they was stabbed by a Micky Mouse. Thankfully the doctor was neaby and saved {} just in time.", "{} is filming a music video for their youtube channel when suddenly they was hit by a car. Luckily the doctor saved {} just in time.", "{} is studying for their AP exams, but {}'s house suddenly exploded. Looks like someone's not going to get 5s on their AP tests and go to Harvard."]
    def __init__(self, outcome, victim):
        if outcome == "alive":
            self.story = random.choice(self.goodS)
        else:
            self.story = random.choice(self.badS)
        self.victim = victim
    
    def __str__(self):
        return self.story.format(self.victim, self.victim)