from card_factory import card_factory
from card_factory import get_elixir

class Card:
    def __init__(self, side, name, level):
        self.side = side
        self.name = name
        self.level = level

        self.elixir_cost = get_elixir(self.name)
    
    def summon(self, position):
        return card_factory(self.side, position, self.name, self.level) 