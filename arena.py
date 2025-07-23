from abstract_classes import TICK_TIME
from abstract_classes import Troop
from abstract_classes import Spell
import card_factory
import vector
import itertools

class Arena:
    def __init__(self):
        self.troops = []
        self.active_attacks = []
        self.spells = []
        self.buildings = []
        self.towers = []
        self.died = []
        self.p1_elixir = 7
        self.p2_elixir = 7
        self.preplace = None
        self.preplace_side = None
        self.timer = 0
        self.state = ""

        self.p1_champion = None
        self.p2_champion = None

        self.elixir_rate = 1

    def add(self, side, position, name, cost, level, evo=False):
        e = cost
        if (side and e <= self.p1_elixir + 0.5) or (not side and e <= self.p2_elixir + 0.5): #if enough elixir
            did_preplace = False if (side and e <= self.p1_elixir) or (not side and e <= self.p2_elixir) else True
            
            if evo:
                card_type, card = card_factory.evolution_factory(side, position, name, level)
            else:
                card_type, card = card_factory.card_factory(side, position, name, level)
            
            if did_preplace:
                self.preplace = card
                if isinstance(card, list):
                    self.preplace_side = card[0].side
                else:
                    self.preplace_side = card.side

            if card_type == "troop":
                if isinstance(card, list):
                    if not did_preplace:
                        for each in card:
                            each.on_deploy(self)
                    self.troops.extend(card)
                else:
                    if not did_preplace:
                        card.on_deploy(self)
                    self.troops.append(card)
            elif card_type == "spell":
                if isinstance(card, list):
                    self.spells.extend(card)
                else:
                    self.spells.append(card)
            elif card_type == "building":
                if isinstance(card, list):
                    if not did_preplace:
                        for each in card:
                            each.on_deploy(self)
                    self.buildings.extend(card)
                else:
                    if not did_preplace:
                        card.on_deploy(self)
                    self.buildings.append(card)

            if did_preplace:
                if isinstance(card, list):
                    for each in card:
                        each.preplace = True
                        each.invulnerable = True
                        each.collideable = False
                        each.targetable = False
                else:
                    card.preplace = True
                    card.invulnerable = True
                    card.collideable = False
                    card.targetable = False
            
            if side:
                self.p1_elixir -= e
            else:
                self.p2_elixir -= e

            return True
        return False
    
    def tick(self):
        if self.timer >= 300:
            for tower in self.towers:
                tower.damage(10)
            self.active_attacks = []
            self.troops = []
            self.buildings = []
            self.p1_elixir = 0
            self.p2_elixir = 0
            return


        e_rate = self.elixir_rate/2.8
        if self.timer >= 240:
            self.state = "Overtime: 3x Elixir"
            e_rate = 3 * self.elixir_rate/2.8
        elif self.timer >= 120:
            self.state = "2x Elixir"
            e_rate = 2 * self.elixir_rate/2.8
        self.p1_elixir = min(10, self.p1_elixir + e_rate * TICK_TIME)
        self.p2_elixir = min(10, self.p2_elixir + e_rate * TICK_TIME)

        if self.preplace is not None and ((self.preplace_side and self.p1_elixir >= 0) or (not self.preplace_side and self.p2_elixir >= 0)):
            if isinstance(self.preplace, list):
                for each in self.preplace:
                    each.preplace = False
                    each.invulnerable = False
                    each.collideable = True
                    each.targetable = True
                    each.on_preplace()
                    if not isinstance(each, Spell):
                        each.on_deploy(self)
            else:
                self.preplace.preplace = False
                self.preplace.invulnerable = False
                self.preplace.collideable = True
                self.preplace.targetable = True
                self.preplace.on_preplace()
                if not isinstance(self.preplace, Spell):
                    self.preplace.on_deploy(self)
            self.preplace = None
            self.preplace_side = None

        for spell in self.spells:
            spell.tick(self)
        for building in self.buildings:
            building.tick(self)
        for tower in self.towers:
            tower.tick(self)
        for attack in self.active_attacks:
            attack.tick(self)
        for troop in self.troops:
            troop.tick(self)
        
        
    
    def cleanup(self):
        self.timer += TICK_TIME
        for troop in self.troops:
            troop.cleanup(self)
        for attack in self.active_attacks:
            attack.cleanup(self)
        for spell in self.spells:
            spell.cleanup(self)
        for building in self.buildings:
            building.cleanup(self)
        for tower in self.towers:
            winSide = tower.cleanup(self)
            if not winSide is None:
                return winSide
            
        p1_side = 0
        if self.timer >= 180: #overtime
            for tower in self.towers:
                p1_side += (1 if tower.side else -1)
            if p1_side > 0:
                return True
            elif p1_side < 0:
                return False
            if self.timer < 240:
                self.state = "Overtime: 2x Elixir"

        #do collision checks
        applyVelocity = {}

        # Handle troop-to-troop collisions
        for troop, c_troop in itertools.combinations(self.troops, 2):
            if (troop.ground == c_troop.ground):
                dist = vector.distance(c_troop.position, troop.position)
                if troop.collideable and c_troop.collideable and dist < (c_troop.collision_radius + troop.collision_radius):
                    if c_troop.invulnerable:
                        dist = vector.distance(troop.position, c_troop.position)
                        if dist < (c_troop.collision_radius + troop.collision_radius):
                            vec = troop.position.subtracted(c_troop.position)  # building to troop vector
                            if vec.magnitude() > 0:
                                vec.scale(((c_troop.collision_radius + troop.collision_radius) / vec.magnitude()) - 1)
                            
                            applyVelocity[troop] = applyVelocity.get(troop, vector.Vector(0, 0)).added(vec)
                    elif troop.invulnerable:
                        dist = vector.distance(c_troop.position, troop.position)
                        if dist < (troop.collision_radius + c_troop.collision_radius):
                            vec = c_troop.position.subtracted(troop.position)  # building to troop vector
                            if vec.magnitude() > 0:
                                vec.scale(((troop.collision_radius + c_troop.collision_radius) / vec.magnitude()) - 1)
                            
                            applyVelocity[c_troop] = applyVelocity.get(c_troop, vector.Vector(0, 0)).added(vec)
                    else:
                        vec = c_troop.position.subtracted(troop.position)  # troop to ctroop vector
                        if vec.magnitude() > 0:
                            vec.scale(((c_troop.collision_radius + troop.collision_radius) / vec.magnitude()) - 1)  # scale to avoid collision
                        
                        mass_ratio_troop = troop.mass / (c_troop.mass + troop.mass)
                        mass_ratio_ctroop = c_troop.mass / (c_troop.mass + troop.mass)
                        
                        applyVelocity[troop] = applyVelocity.get(troop, vector.Vector(0, 0)).added(vec.scaled(-mass_ratio_ctroop))
                        applyVelocity[c_troop] = applyVelocity.get(c_troop, vector.Vector(0, 0)).added(vec.scaled(mass_ratio_troop))

        # Handle troop-to-building and troop-to-tower collisions1
        for troop in self.troops:
            for building in self.buildings + self.towers:
                dist = vector.distance(troop.position, building.position)
                if troop.collideable and building.collideable and dist < (building.collision_radius + troop.collision_radius):
                    vec = troop.position.subtracted(building.position)  # building to troop vector
                    if vec.magnitude() > 0:
                        vec.scale(((building.collision_radius + troop.collision_radius) / vec.magnitude()) - 1)
                    
                    if vec.x < 0.01 and vec.x >= 0:
                        vec.x = 0.01
                    elif vec.x > -0.01 and vec.x < 0:
                        vec.x == -0.01 

                    applyVelocity[troop] = applyVelocity.get(troop, vector.Vector(0, 0)).added(vec)

        # Apply velocity adjustments
        for troop, vel in applyVelocity.items():
            troop.position.add(vel)

        for troop in self.troops:
            troop.handle_deaths(self.died)
        self.died = []