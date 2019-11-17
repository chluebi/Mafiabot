

class Record:
    def __init__(self, id):
        self.id = id
        self.games = 0
        self.wins = 0
    
    def addGame(self, didWin):
        self.games += 1
        if didWin:
            self.wins +=1
    
    def getGames(self):
        return self.games
    def getWins(self):
        return self.wins
    
    def __str__(self):
        return str(self.id) + str(self.games) +str( self.wins)