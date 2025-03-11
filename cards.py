from card_factory import card_factory

class Card:
    def __init__(self, side, name, level):
        self.side = side
        self.name = name
        self.level = level
    
    def summon(position):
        return card_factory(self.side, position, self.name, self.level) 
