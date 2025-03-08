import vector
import itertools

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
        
    
    def cleanup(self):
        for troop in self.troops:
            troop.cleanup(self)
        for attack in self.active_attacks:
            attack.cleanup(self)
        for spell in self.spells:
            spell.cleanup(self)

        #do collision checks
        applyVelocity = {}

        # Handle troop-to-troop collisions
        for troop, c_troop in itertools.combinations(self.troops, 2):
            dist = vector.distance(c_troop.position, troop.position)
            if dist < (c_troop.collision_radius + troop.collision_radius):
                vec = c_troop.position.subtracted(troop.position)  # troop to ctroop vector
                vec.scale(((c_troop.collision_radius + troop.collision_radius) / vec.magnitude()) - 1)  # scale to avoid collision
                
                mass_ratio_troop = troop.mass / (c_troop.mass + troop.mass)
                mass_ratio_ctroop = c_troop.mass / (c_troop.mass + troop.mass)
                
                applyVelocity[troop] = applyVelocity.get(troop, vector.Vector(0, 0)).added(vec.scaled(-mass_ratio_ctroop))
                applyVelocity[c_troop] = applyVelocity.get(c_troop, vector.Vector(0, 0)).added(vec.scaled(mass_ratio_troop))

        # Handle troop-to-building and troop-to-tower collisions
        for troop in self.troops:
            for building in self.buildings + self.towers:
                dist = vector.distance(troop.position, building.position)
                if dist < (building.collision_radius + troop.collision_radius):
                    vec = troop.position.subtracted(building.position)  # building to troop vector
                    vec.scale((building.collision_radius + troop.collision_radius) / vec.magnitude())
                    
                    applyVelocity[troop] = applyVelocity.get(troop, vector.Vector(0, 0)).added(vec)

        # Apply velocity adjustments
        for troop, vel in applyVelocity.items():
            troop.position.add(vel)