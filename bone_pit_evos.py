from abstract_classes import TICK_TIME
from abstract_classes import TILES_PER_MIN
from abstract_classes import AttackEntity
from abstract_classes import Tower
from abstract_classes import Troop
import bone_pit_cards
import random
import vector
import copy

class EvolutionSkeletonCounter:
    def __init__(self):
        self.count = 0

    def add(self):
        self.count += 1

    def sub(self):
        self.count -= 1

    def can_more(self):
        return self.count < 8

class EvolutionSkeleton(bone_pit_cards.Skeleton):
    def __init__(self, side, position, level, counter, cloned=False):
        super().__init__(side, position, level, cloned)
        self.count = counter
        self.evo = True

    def die(self, arena):
        self.count.sub()
        super().die(arena)

    def attack(self): #temp
        return super().attack()
    
    def tick_func(self, arena):
        if self.attack_cooldown >= self.hit_speed - TICK_TIME and self.count.can_more(): #after attack
            self.count.add()
            arena.troops.append(EvolutionSkeleton(self.side, self.target.position.added(vector.Vector(random.random() - 0.5, random.random() - 0.5)), self.level, self.count))

class EvolutionBomberAttackEntity(AttackEntity):
    def __init__(self, side, damage, position, target_pos, dir, remaining=2):
        super().__init__(
            s=side,
            d=damage,
            v=400*TILES_PER_MIN,
            l=float('inf'),
            i_p=copy.deepcopy(position)
        )
        self.target_pos = target_pos
        self.exploded = False
        self.dir = dir
        self.remaining = remaining
        self.has_hit = []

    def detect_hits(self, arena):
        hits = []
        if self.exploded:
            for each in arena.towers + arena.buildings + arena.troops:
                if each.side != self.side and (isinstance(each, Tower) or (each.ground and not each.invulnerable)): # if different side
                    if vector.distance(self.position, each.position) < 1.5 + each.collision_radius:
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
            direction = self.target_pos.subtracted(self.position)
            direction.normalize()

            movement = direction.scaled(self.velocity)
            self.position.add(movement)
            
            if vector.distance(self.position, self.target_pos) < 0.25:
                self.display_size = 1.5
                self.duration =  0.1
                self.exploded = True
                if self.remaining > 0:
                    arena.active_attacks.append(EvolutionBomberAttackEntity(self.side, self.damage, self.position, self.position.added(self.dir), self.dir, self.remaining - 1))

class EvolutionBomber(bone_pit_cards.Bomber):
    def __init__(self, side, position, level):
        super().__init__(side, position, level)
        self.evo = True
    
    def attack(self):
        dir = self.target.position.subtracted(self.position)
        dir.normalize()
        dir.scale(2.5)
        return EvolutionBomberAttackEntity(self.side, self.hit_damage, self.position, copy.deepcopy(self.target.position), dir)

class EvolutionValkyrieSpecialAttackEntity(AttackEntity):
    SPLASH_RADIUS = 5.5
    COLLISION_RADIUS = 0.5
    def __init__(self, side, damage, ctd, position):
        super().__init__(
            s=side,
            d=damage,
            v=0,
            l=0.5,
            i_p=position
        )
        self.ctd = ctd
        self.display_size = self.SPLASH_RADIUS

    def detect_hits(self, arena):
        hits = []
        for each in arena.towers + arena.buildings + arena.troops:
            if each.side != self.side and not each.invulnerable: # if different side
                if vector.distance(self.position, each.position) < self.SPLASH_RADIUS + each.collision_radius:
                    hits.append(each)
        return hits
    
    def tick(self, arena):
        self.tick_func(arena)
        hits = self.detect_hits(arena)
        for each in hits:
            new = not each in self.has_hit
            if (new):
                if isinstance(each, Tower):
                    each.damage(self.ctd)
                else:
                    each.damage(self.damage)
                    self.apply_effect(each)
                self.has_hit.append(each)

    def apply_effect(self, target):
        if isinstance(target, Troop) and not target.invulnerable:
            mag = (-1/5 * target.mass + 5.7)/2
            to_self = self.position.subtracted(target.position)
            mag = min(mag, to_self.magnitude() - self.COLLISION_RADIUS - target.collision_radius)

            target.kb(to_self.normalized().scaled(mag), 0.5)
    

class EvolutionValkyrie(bone_pit_cards.Valkyrie):
    def __init__(self, side, position, level):
        super().__init__(side, position, level)
        self.evo = True
        self.special_damage = 53 * pow(1.1, level - 6)
        self.special_ctd = 23 * pow(1.1, level - 6)

    def attack(self):
        return [super().attack(), EvolutionValkyrieSpecialAttackEntity(self.side, self.special_damage, self.special_ctd, self.position)]