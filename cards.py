from card_factory import get_elixir

evo_cycles = {
    "knight" : 2,
    "archers" : 2,
    "musketeer" : 2,
    "goblincage" : 1,
    "skeletons" : 2,
    "bomber" : 2,
    "valkyrie" : 2,
    "barbarians" : 1,
    "battleram" : 2,
    "cannon" : 2,
    "wizard" : 1,
    "bats" : 2,
    "zap" : 2,
    "mortar" : 2
}

class Card:
    def __init__(self, side, name, level, evo=False):
        self.side = side
        self.name = name
        self.level = level
        self.is_evo = evo
        self.cycles = int(evo_cycles.get(self.name, -1))
        self.cycles_left = self.cycles #if not self.is_evo else 0

        error = False
        try:
            self.elixir_cost = get_elixir(self.name)
        except KeyError:
            error = True
        if error:
            error_msg = "You spelled \"" + self.name + "\" wrong. Make sure its all lowercase with no spaces, and is as appears in README.md."
            raise Exception(error_msg)
    
    def cycle_evo(self):
        if self.is_evo:
            if self.cycles_left <= 0:
                self.cycles_left = self.cycles
            else:
                self.cycles_left -= 1