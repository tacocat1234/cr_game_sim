from abstract_classes import RangedAttackEntity
from abstract_classes import MeleeAttackEntity
from abstract_classes import Troop
from abstract_classes import Spell
from abstract_classes import Tower
from abstract_classes import Building
from abstract_classes import TILES_PER_MIN
from abstract_classes import TICK_TIME
import vector
import copy
import math

class Zap(Spell):
    def __init__(self, side, target, level):
        super().__init__(
            s=side,
            d=75 * pow(1.1, level - 1),
            c_t_d=23 * pow(1.1, level - 1),
            w=1, #waves
            t=0, #time between waves
            kb=0,
            r=2.5,
            v=0,
            tar=target
        )
    
    def apply_effect(self, target):
        target.stun()

class MortarAttackEntity(RangedAttackEntity):
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            velocity=300*TILES_PER_MIN,
            position=position,
            target=target,
        )
        self.exploded = False
        self.has_hit = []        

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

class Mortar(Building):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,
            h_p=535 * pow(1.1, level - 1),
            h_d=104 * pow(1.1, level - 1),
            h_s=5,
            l_t=4,
            h_r=11.5,
            s_r=11.5,
            g=True,
            t_g_o=True,
            t_o=False,
            l=30,
            d_t=3.5,
            c_r=0.6,
            d_s_c=0,
            d_s=None,
            p=position
        )
        self.level = level
        self.min_hit_range = 3.5

    def update_target(self, arena):
        self.target = None
        min_dist = float('inf')
        for each in arena.troops + arena.buildings + arena.towers:
            dist = vector.distance(each.position, self.position)
            if (isinstance(each, Tower) or ((not each.invulnerable and each.targetable) and (not self.ground_only or (self.ground_only and each.ground)))) and each.side != self.side and dist < min_dist and dist < self.hit_range + self.collision_radius  + each.collision_radius and dist > self.min_hit_range + self.collision_radius - each.collision_radius:
                self.target = each
                min_dist = vector.distance(each.position, self.position)

                angle = math.degrees(math.atan2(each.position.y - self.position.y, each.position.x - self.position.x))  # Get angle in degrees
                self.facing_dir = angle

    def tick_func(self, arena):
        if self.target is not None:
            dist = vector.distance(self.target.position, self.position)
            if dist < self.min_hit_range + self.collision_radius - self.target.collision_radius:
                self.update_target(arena)
    
    def attack(self):
        return MortarAttackEntity(self.side, self.hit_damage, self.position, copy.deepcopy(self.target.position))
    
class BatAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 1.2
    COLLISION_RADIUS = 0.5
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            position=position,
            target=target
            )

class Bat(Troop):
    def __init__(self, side, position, level, cloned=False):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 32 * pow(1.1, level - 1),         # Hit points (Example value)
            h_d= 32 * pow(1.1, level - 1),          # Hit damage (Example value)
            h_s=1.3,          # Hit speed (Seconds per hit)
            l_t=0.7,            # First hit cooldown
            h_r=1.2,            # Hit range
            s_r=5.5,            # Sight Range
            g=False,           # Ground troop
            t_g_o=False,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=120*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=1,            #mass
            c_r=0.5,        #collision radius
            p=position,               # Position (vector.Vector object)
            cloned=cloned
        ) 
        self.level = level
        self.walk_cycle_frames = 4
        class_name = self.__class__.__name__.lower()
        self.sprite_path = f"sprites/{class_name}/{class_name}_0.png"
    def attack(self):
        return BatAttackEntity(self.side, self.hit_damage, self.position, self.target)   
    
class Rocket(Spell):
    def __init__(self, side, target, level):
        super().__init__(
            s=side,
            d=700 * pow(1.1, level - 3),
            c_t_d=175 * pow(1.1, level - 3),
            w=1,
            t=0,
            kb=1.8,
            r=2,
            v=350*TILES_PER_MIN,
            tar=target
        )

class HogRiderAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 0.8
    COLLISION_RADIUS = 0.6
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            position=position,
            target=target
            )
        
class HogRider(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 800 * pow(1.1, level - 3),         # Hit points (Example value)
            h_d= 150 * pow(1.1, level - 3),          # Hit damage (Example value)
            h_s=1.6,          # Hit speed (Seconds per hit)
            l_t=1,            # First hit cooldown
            h_r=0.8,            # Hit range
            s_r=9.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=False,       # Targets ground-only
            t_o=True,        # tower-only
            m_s=120*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=4,            #mass
            c_r=0.6,        #collision radius
            p=position               # Position (vector.Vector object)
        ) 
        self.level = level
        self.walk_cycle_frames = 4
        class_name = self.__class__.__name__.lower()
        self.sprite_path = f"sprites/{class_name}/{class_name}_0.png"
        self.cross_river = True
        self.jump_speed = 160 * TILES_PER_MIN
    def attack(self):
        return HogRiderAttackEntity(self.side, self.hit_damage, self.position, self.target)
    
class FlyingMachineAttackEntity(RangedAttackEntity):
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            velocity=800*TILES_PER_MIN,
            position=position,
            target=target,
        )
    
class FlyingMachine(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 290 * pow(1.1, level - 3),         # Hit points (Example value)
            h_d= 81 * pow(1.1, level - 3),          # Hit damage (Example value)
            h_s=1.1,          # Hit speed (Seconds per hit)
            l_t=0.6,            # First hit cooldown
            h_r=6,            # Hit range
            s_r=6,            # Sight Range
            g=False,           # Ground troop
            t_g_o=False,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=90*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=3,            #mass
            c_r=0.5,        #collision radius
            p=position               # Position (vector.Vector object)
        ) 
        self.level = level
    
    def attack(self):
        return FlyingMachineAttackEntity(self.side, self.hit_damage, self.position, self.target)