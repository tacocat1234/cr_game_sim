class Arena:
    def __init__(self):
        self.troops = []
        self.active_attacks = []
        self.spells = []
        self.buildings = []
        self.towers = []
    
    def tick(self):
        for spell in self.spells:
            spell.tick(self)
        for troop in self.troops:
            troop.tick(self)
        for attack in self.active_attacks:
            attack.tick(self)
        for troop in self.troops:
            troop.cleanup(self)
        for attack in self.active_attacks:
            attack.cleanup(self)
        for spell in self.spells:
            spell.cleanup(self)