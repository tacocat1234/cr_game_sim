from card_factory import get_elixir, get_type

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
    "mortar" : 2,
    "pekka" : 1,
    "witch" : 1,
    "goblinbarrel" : 2,
    "royalgiant" : 1,
    "royalrecruits" : 1,
    "icespirit" : 2,
    "giantsnowball" : 2,
    "goblingiant" : 1,
    "dartgoblin" : 2,
    "hunter" : 2,
    "furnace" : 2,
    "tesla" : 2,
    "infernodragon" : 2,
    "megaknight" : 1,
    "firecracker" : 2,
    "electrodragon" : 1,
    "wallbreakers" : 2,
    "lumberjack" : 2,
    "goblindrill" : 2,
    "executioner" : 1,
    "skeletonbarrel" : 2
}

class Card:
    def __init__(self, side, name, level, evo=False):
        self.side = side
        self.name = name
        self.level = level
        self.is_evo = evo
        self.cycles = int(evo_cycles.get(self.name, -1))
        self.cycles_left = self.cycles #if not self.is_evo else 0
        self.type = get_type(name)

        error = False
        if self.name == "mirror":
            self.elixir_cost = float('inf')
        else:
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