

class MafiaUser:
    
    def __init__(self, userID = 0, wins = 0, games = 0, points = 0, titles = [], currentTitle = " "):
        self.id = userID
        self.wins = wins
        self.games = games
        self.points = points
        self.titles = titles
        self.currentTitle = currentTitle

    def addWin(self):
        self.wins+= 1
    
    def addGame(self):
        self.games += 1
    
    def addPoints(self, amount):
        self.points+=amount
    
    def addTitle(self, title):
        self.titles.append(title)
    