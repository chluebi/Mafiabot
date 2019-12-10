

class MafiaUser:
    
    def __init__(self, userID = 0, wins = 0, games = 0, points = 0, titles = [], currentTitle = " ", premium = 0, customRoles = []):
        self.id = userID
        self.wins = wins
        self.games = games
        self.points = points
        self.titles = titles
        self.currentTitle = currentTitle
        self.premium = premium
        self.customRoles = customRoles
        
    def addWin(self):
        self.wins+= 1
    
    def addGame(self):
        self.games += 1
    
    def addPoints(self, amount):
        self.points+=amount
    
    def addTitle(self, title):
        self.titles.append(title)
    