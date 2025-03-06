class Arena:
    def __init__(self):
        self.troops = []
        self.active_attacks = []
        self.spells = []
        self.buildings = []
        self.towers = [KingTower(True), PrincessTower(True), PrincessTower(True), KingTower(False), PrincessTower(False), PrincessTower(False) ]
    
    def tick(self):
        for troop in self.troops:
            troop.tick(self)
        for attack in self.active_attacks:
            attack.tick(self)
        for spell in self.spells:
            spell.tick(self)
        for troop in self.troops:
            troop.cleanup(self)
        for attack in self.active_attacks:
            attack.cleanup(self)
        for spell in self.spells:
            spell.cleanup(self)

class AttackEntity:
    def __init__(self, s, d, v, l, i_p):
        self.side = s
        self.damage = d
        self.velocity = v
        self.lifespan = l
        self.position = i_p
        
        self.duration = l
        self.has_hit = []
        
    def tick(self, arena):
        self.position.add(self.velocity)
        hits = self.detect_hits(arena)
        for each in hits:
            new = True
            for h in self.has_hit:
                if each is h:
                    new = False
                    break
            if (new):
                each.hp -= self.damage
                self.has_hit.append(each)
        self.duration -= TICK_TIME
        
    def cleanup(self, arena): #also delete self if single target here in derived classes
        if self.duration <= 0:
            arena.active_attacks.remove(self)
        
    def detect_hits(self, arena): # to be overriden in derived
        return []
