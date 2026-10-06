import electro_valley_cards
from abstract_classes import TICK_TIME
from abstract_classes import AttackEntity
from abstract_classes import MeleeAttackEntity
from abstract_classes import Tower
from abstract_classes import Troop
import vector
import copy

class EvolutionPrincessSlowAreaAttackEntity(AttackEntity):
    SPLASH_RADIUS = 3
    def __init__(self, side, damage, position, target_pos):
        super().__init__(
            s=side,
            d=damage,
            v=0,
            l=5.5,
            i_p=copy.deepcopy(position)
        )
        self.display_size = self.SPLASH_RADIUS

    def apply_effect(self, target):
        target.slow(5.5, "evolutionprincessslow")
    
    def detect_hits(self, arena):
        hits = []
        for each in arena.towers + arena.buildings + arena.troops:
            if each.side != self.side and (isinstance(each, Tower) or (each.ground and not each.invulnerable)): # if different side
                if vector.distance(self.position, each.position) < self.SPLASH_RADIUS + each.collision_radius:
                        hits.append(each)

        return hits


class EvolutionPrincessDeathAttackEntity(AttackEntity):
    SPLASH_RADIUS = 3
    def __init__(self, side, damage, position, target_pos):
        super().__init__(
            s=side,
            d=damage,
            v=0,
            l=3.5,
            i_p=copy.deepcopy(position)
        )
        self.display_size = self.SPLASH_RADIUS

    def apply_effect(self, target):
        target.slow(3.5, "evolutionprincessslow")
    
    def detect_hits(self, arena):
        hits = []
        for each in arena.towers + arena.buildings + arena.troops:
            if each.side != self.side and (isinstance(each, Tower) or (each.ground and not each.invulnerable)): # if different side
                if vector.distance(self.position, each.position) < self.SPLASH_RADIUS + each.collision_radius:
                        hits.append(each)

        return hits
    
class EvolutionPrincessAttackEntity(electro_valley_cards.PrincessAttackEntity):
    def __init__(self, side, damage, position, target):
        super().__init__(side, damage, position, target)

    def explode(self, arena):
        arena.active_attacks.append(EvolutionPrincessSlowAreaAttackEntity(self.side, 0, self.position, self.position))
        return super().explode(arena)

class EvolutionPrincess(electro_valley_cards.Princess):
    def __init__(self, side, position, level):
        super().__init__(side, position, level)
        self.evo = True
        self.slow_counter = 1
        self.hits_for_slow = 2

    def attack(self):
        self.slow_counter -= 1
        if self.slow_counter == 0:
            self.slow_counter = self.hits_for_slow
            return EvolutionPrincessAttackEntity(self.side, self.hit_damage, self.position, self.target.position)
        else:
            return electro_valley_cards.PrincessAttackEntity(self.side, self.hit_damage, self.position,self.target.position)
        
    def die(self, arena):
        arena.active_attacks.append(EvolutionPrincessDeathAttackEntity(self.side, self.hit_damage, self.position, self.target))
        super().die(arena)
    

class EvolutionMegaKnightAttackEntity(MeleeAttackEntity):
    SPLASH_RADIUS = 1.3
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            position=copy.deepcopy(target),
            target=copy.deepcopy(target) #not used
            )
        self.display_size = self.SPLASH_RADIUS
        self.launch_target = None
        self.tar_normal = 0
        
    def detect_hits(self, arena):
        hits = []
        for each in arena.towers + arena.buildings + arena.troops:
            if each.side != self.side and (isinstance(each, Tower) or (each.ground and not each.invulnerable)): # if different side
                if vector.distance(each.position, self.position) <= each.collision_radius + self.SPLASH_RADIUS:
                    hits.append(each)
        return hits
    
    def tick(self, arena):
        if self.launch_target is None:
            hits = self.detect_hits(arena)
            if len(hits) > 0:
                for each in hits:
                    each.damage(self.damage)
                self.launch_target = hits[0]
                self.apply_effect(hits[0])
                if isinstance(self.launch_target, Troop):
                    self.duration = 0.5
                    self.launch_target.collideable = False
                else:
                    self.should_delete = True
                self.tar_normal = self.launch_target.collision_radius

        else:
            if self.duration <= TICK_TIME:
                self.launch_target.collideable = True
                self.launch_target.collision_radius = self.tar_normal
            elif self.launch_target:
                self.launch_target.collision_radius = (-15*(self.duration)*(self.duration - 0.5) + 1) * self.tar_normal

    
    def apply_effect(self, target):
        if isinstance(target, Troop):
            mag = 4 if target.mass <= 4 else -1/7 * (target.mass - 4) + 4
            target.kb(vector.Vector(0, mag if self.side else -mag), 0.5)

class EvolutionMegaKnight(electro_valley_cards.MegaKnight):
    def __init__(self, side, position, level):
        super().__init__(side, position, level)
        self.evo = True
        self.launch_counter = 1
        self.hits_for_launch = 2

    def attack(self):
        self.launch_counter -= 1
        if self.launch_counter == 0:
            self.launch_counter = self.hits_for_launch
            return EvolutionMegaKnightAttackEntity(self.side, self.hit_damage, self.position, self.target.position)
        else:
            return electro_valley_cards.MegaKnightAttackEntity(self.side, self.hit_damage, self.position,self.target.position)

class EvolutionInfernoDragon(electro_valley_cards.InfernoDragon):
    def __init__(self, side, position, level):
        super().__init__(side, position, level)
        self.evo = True
        self.decharge_timer = 0
    
    def tick_func(self, arena):
        if self.target is None or self.target.cur_hp <= 0 or vector.distance(self.position, self.target.position) > self.hit_range + self.collision_radius + self.target.collision_radius or not self.target.targetable:
            if self.decharge_timer > 0: #If out of range but has decharge
                self.decharge_timer -= TICK_TIME # decremenet
            else:
                self.stage = 1 #reset
                self.stage_duration = 2
                self.attack_cooldown = self.load_time - self.hit_speed

        else: #if infernoing
            self.decharge_timer = 9