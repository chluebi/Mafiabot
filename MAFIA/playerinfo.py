class Player():
    def __init__(self, roleName, alive):
        self.roleName = roleName
        self.alive = alive
    
    def changeRole(self, role):
        self.roleName = role