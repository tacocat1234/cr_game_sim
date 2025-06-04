from card_factory import card_factory
from card_factory import get_elixir

class Card:
    def __init__(self, side, name, level):
        self.side = side
        self.name = name
        self.level = level

        error = False
        try:
            self.elixir_cost = get_elixir(self.name)
        except KeyError:
            error = True
        if error:
            error_msg = "You spelled \"" + self.name + "\" wrong. Make sure its all lowercase with no spaces, and is as appears in README.md."
            raise Exception(error_msg)
    
    def summon(self, position):
        return card_factory(self.side, position, self.name, self.level) 