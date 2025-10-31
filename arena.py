from abstract_classes import TICK_TIME
from abstract_classes import Troop
from abstract_classes import Spell
from abstract_classes import ElixirLossTracker
import card_factory
import vector
import itertools
import random

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
        self.timer = 0
        self.state = ""
        self.elixir_trackers = []
        self.type = "normal"

        self.p1_champion = None
        self.p2_champion = None

        self.elixir_rate = 1

        # queue of [cards, card_type, delay_remaining]
        self.pending_preplacements = []

    def add(self, side, position, name, cost, level, evo=False, zero_delay=False):
        e = cost
        if (side and e <= self.p1_elixir + 0.2) or (not side and e <= self.p2_elixir + 0.2):  # some leneincy
            e_rate = self.elixir_rate / 2.8
            if self.timer >= 240:
                e_rate = 3 * self.elixir_rate / 2.8
            elif self.timer >= 120:
                e_rate = 2 * self.elixir_rate / 2.8

            delay = 0 
            if side:
                if not e <= self.p1_elixir:
                    delay = (e - self.p1_elixir)/e_rate
            else:
                if not e <= self.p2_elixir:
                    delay = (e - self.p2_elixir)/e_rate

            if evo:
                card_type, card = card_factory.evolution_factory(side, position, name, level)
            else:
                if name == "spiritempress":
                    if side and self.p1_elixir > 6 or not side and self.p2_elixir > 6:
                        card_type, card = card_factory.card_factory(side, position, name, level)
                    else:
                        card_type, card = card_factory.card_factory(side, position, "spiritempressground", level)
                else:
                    card_type, card = card_factory.card_factory(side, position, name, level)

            e_t = ElixirLossTracker(position.x, position.y + (1 if side else -1), e, side, self)
            e_t.timer += delay
            self.elixir_trackers.append(e_t)

            # normalize to list
            cards = card if isinstance(card, list) else [card]

            # troops/buildings get ghosted for 1s
            if card_type in ["troop", "building"]:
                if name not in ["log", "barbarianbarrel", "goblindrill"]:
                    for c in cards:
                        c.preplace = True
                        c.invulnerable = True
                        c.collideable = False
                        c.targetable = False
                        if card_type == "troop":
                            self.troops.append(c)
                        else:
                            self.buildings.append(c)

                        if name in card_factory.champions:
                            if side:
                                self.p1_champion = c
                            else:
                                self.p2_champion = c
    
                    # deduct elixir immediately
                    if side:
                        self.p1_elixir -= e
                    else:
                        self.p2_elixir -= e

                    # push into pending queue with 1s delay
                    self.pending_preplacements.append([cards, card_type, delay if zero_delay else 1.0 + delay])  # delay in seconds
                else:
                    if side:
                        self.p1_elixir -= e
                    else:
                        self.p2_elixir -= e

                    if delay > 0:
                        for c in cards:
                            c.preplace = True
                            c.invulnerable = True
                            c.collideable = False
                            c.targetable = False
                            if card_type == "troop":
                                self.troops.append(c)
                            else:
                                self.buildings.append(c)

                        # push into pending queue with 1s delay
                        self.pending_preplacements.append([cards, card_type, delay])
                    else:
                        self.troops.extend(cards)
                    return True
            else:
                # spells deploy instantly
                if side:
                    self.p1_elixir -= e
                else:
                    self.p2_elixir -= e

                if delay > 0:
                    for c in cards:
                        c.preplace = True
                        self.spells.append(c)

                    # push into pending queue with 1s delay
                    self.pending_preplacements.append([cards, card_type, delay])
                else:
                    self.spells.extend(cards)

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

        # elixir regen
        e_rate = self.elixir_rate / 2.8
        if self.timer >= 240:
            self.state = "Overtime: 3x Elixir"
            e_rate = 3 * self.elixir_rate / 2.8
        elif self.timer >= 120:
            self.state = "2x Elixir"
            e_rate = 2 * self.elixir_rate / 2.8
        self.p1_elixir = min(10, self.p1_elixir + e_rate * TICK_TIME)
        self.p2_elixir = min(10, self.p2_elixir + e_rate * TICK_TIME)

        # handle delayed deployments
        still_pending = []
        for cards, card_type, delay in self.pending_preplacements:
            delay -= TICK_TIME
            if delay <= 0:
                for c in cards:
                    c.preplace = False
                    
                    if not isinstance(c, Spell):
                        c.invulnerable = False
                        c.collideable = True
                        c.targetable = True
                        c.on_preplace()
                        c.on_deploy(self)
                        
            else:
                still_pending.append([cards, card_type, delay])
        self.pending_preplacements = still_pending

        # tick all entities
        for attack in self.active_attacks:
            attack.tick(self)
        for spell in self.spells:
            spell.tick(self)
        for building in self.buildings:
            building.tick(self)
        for tower in self.towers:
            tower.tick(self)
        for troop in self.troops:
            troop.tick(self)

        for tracker in self.elixir_trackers:
            tracker.tick()

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
        if self.timer >= 180:  # overtime
            for tower in self.towers:
                p1_side += (1 if tower.side else -1)
            if p1_side > 0: #p1 side
                return True
            elif p1_side < 0:
                return False
            if self.timer < 240:
                self.state = "Overtime: 2x Elixir"

        # do collision checks
        applyVelocity = {}

        # troop-to-troop collisions
        for troop, c_troop in itertools.combinations(self.troops, 2):
            if (troop.ground == c_troop.ground):
                dist = vector.distance(c_troop.position, troop.position)
                if troop.collideable and c_troop.collideable and dist < (c_troop.collision_radius + troop.collision_radius):
                    if c_troop.invulnerable:
                        dist = vector.distance(troop.position, c_troop.position)
                        if dist < (c_troop.collision_radius + troop.collision_radius):
                            vec = troop.position.subtracted(c_troop.position)
                            if vec.magnitude() > 0:
                                vec.scale(((c_troop.collision_radius + troop.collision_radius) / vec.magnitude()) - 1)
                            applyVelocity[troop] = applyVelocity.get(troop, vector.Vector(0, 0)).added(vec)
                    elif troop.invulnerable:
                        dist = vector.distance(c_troop.position, troop.position)
                        if dist < (troop.collision_radius + c_troop.collision_radius):
                            vec = c_troop.position.subtracted(troop.position)
                            if vec.magnitude() > 0:
                                vec.scale(((troop.collision_radius + c_troop.collision_radius) / vec.magnitude()) - 1)
                            applyVelocity[c_troop] = applyVelocity.get(c_troop, vector.Vector(0, 0)).added(vec)
                    else:
                        vec = c_troop.position.subtracted(troop.position)
                        if vec.magnitude() > 0:
                            vec.scale(((c_troop.collision_radius + troop.collision_radius) / vec.magnitude()) - 1)
                        mass_ratio_troop = troop.mass / (c_troop.mass + troop.mass)
                        mass_ratio_ctroop = c_troop.mass / (c_troop.mass + troop.mass)
                        applyVelocity[troop] = applyVelocity.get(troop, vector.Vector(0, 0)).added(vec.scaled(-mass_ratio_ctroop))
                        applyVelocity[c_troop] = applyVelocity.get(c_troop, vector.Vector(0, 0)).added(vec.scaled(mass_ratio_troop))

        # troop-to-building/tower collisions
        for troop in self.troops:
            for building in self.buildings + self.towers:
                dist = vector.distance(troop.position, building.position)
                if troop.collideable and building.collideable and dist < (building.collision_radius + troop.collision_radius):
                    vec = troop.position.subtracted(building.position)
                    if vec.magnitude() > 0:
                        vec.scale(((building.collision_radius + troop.collision_radius) / vec.magnitude()) - 1)

                    if vec.x < 0.01 and vec.x >= 0:
                        vec.x = 0.01
                    elif vec.x > -0.01 and vec.x < 0:
                        vec.x == -0.01

                    applyVelocity[troop] = applyVelocity.get(troop, vector.Vector(0, 0)).added(vec)

        # apply velocities
        for troop, vel in applyVelocity.items():
            troop.position.add(vel)

        for troop in self.troops:
            if troop.position.x > 9:
                troop.position.x = 9
                troop.position.y += random.random()/100 - 0.005
            if troop.position.x < -9:
                troop.position.x = -9
                troop.position.y += random.random()/100 - 0.005
            if troop.position.y > 16:
                troop.position.y = 16
            if troop.position.y < -16:
                troop.position.y = -16
            troop.handle_deaths(self.died)
        self.died = []
