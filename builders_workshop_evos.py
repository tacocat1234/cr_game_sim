import builders_workshop_cards
from abstract_classes import TICK_TIME
from abstract_classes import TILES_PER_MIN
from abstract_classes import Tower
from abstract_classes import RangedAttackEntity
from goblin_stadium_cards import Goblin
import vector
import copy

class EvolutionBat(builders_workshop_cards.Bat):
    def __init__(self, side, position, level, cloned=False):
        super().__init__(side, position, level, cloned)
        self.evo = True
        self.healing_timer = 0
        self.healing = 38 * pow(1.1, level - 11)

    def tick_func(self, arena):
        if self.healing_timer < 0 and self.cur_hp < self.hit_points * 2:
            self.cur_hp += self.healing
            if self.cur_hp > self.hit_points * 2:
                self.cur_hp = self.hit_points * 2
            self.healing_timer = 0
        elif self.healing_timer > 0:
            self.healing_timer -= TICK_TIME
        

    def attack(self):
        if self.cur_hp < self.hit_points * 2:
            self.cur_hp += self.healing
            if self.cur_hp > self.hit_points * 2:
                self.cur_hp = self.hit_points * 2
            self.healing_timer = 0.5
        return super().attack()

class EvolutionZap(builders_workshop_cards.Zap):
    def __init__(self, side, target, level):
        super().__init__(side, target, level)
        self.evo = True
        self.waves = 2
        self.time_between = 1
        self.damage_cd = 0

    def tick_func(self, arena):
        self.radius = (self.time_between - self.damage_cd)/2 + 2.5

class EvolutionMortarAttackEntity(RangedAttackEntity):
    def __init__(self, side, damage, position, target, level):
        super().__init__(
            side=side,
            damage=damage,
            velocity=300*TILES_PER_MIN,
            position=position,
            target=target,
        )
        self.exploded = False
        self.has_hit = []    
        self.level = level    

    def detect_hits(self, arena):
        hits = []
        if self.exploded:
            for each in arena.towers + arena.buildings + arena.troops:
                if each.side != self.side and (isinstance(each, Tower) or (each.ground and not each.invulnerable)): # if different side
                    if vector.distance(self.position, each.position) < 2 + each.collision_radius:
                        hits.append(each)
        return hits
            
    def tick(self, arena):
        if self.exploded:
            hits = self.detect_hits(arena)
            for each in hits:
                new = not any(each is h for h in self.has_hit)
                if (new):
                    each.damage(self.damage)
                    self.has_hit.append(each)
        else:
            direction = self.target.subtracted(self.position)
            direction.normalize()

            movement = direction.scaled(self.velocity)
            self.position.add(movement)
            
            if vector.distance(self.position, self.target) < 0.25:
                self.display_size = 2
                self.duration =  0.1
                self.exploded = True
                arena.troops.append(Goblin(self.side, self.position, self.level))

class EvolutionMortar(builders_workshop_cards.Mortar):
    def __init__(self, side, position, level):
        super().__init__(side, position, level)
        self.evo = True
        self.hit_speed = 4
        self.load_time = 3
        self.cur_hp = self.cur_hp * 1.25

    def attack(self):
        return EvolutionMortarAttackEntity(self.side, self.hit_damage, self.position, copy.deepcopy(self.target.position), self.level)