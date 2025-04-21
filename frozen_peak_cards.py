from abstract_classes import RangedAttackEntity
from abstract_classes import MeleeAttackEntity
from abstract_classes import AttackEntity
from abstract_classes import Troop
from abstract_classes import Tower
from abstract_classes import Spell
from abstract_classes import TILES_PER_MIN
from abstract_classes import TICK_TIME
import vector
import copy
import math

class GiantSnowball(Spell):
    def __init__(self, side, target, level):
        super().__init__(
            s=side,
            d=75 * pow(1.1, level - 1),
            c_t_d=23 * pow(1.1, level - 1),
            w=1,
            t=0,
            kb=1.8,
            r=2.5,
            v=800*TILES_PER_MIN,
            tar=target
        )

    def apply_effect(self, target):
        target.slow(2.5)

class IceSpiritAttackEntity(AttackEntity):
    DAMAGE_RADIUS = 1.5
    FREEZE_DURATION = 1.2
    def __init__(self, side, damage, position, target):
        super().__init__(
            s=side,
            d=damage,
            v=400*TILES_PER_MIN,
            l=float('inf'),
            i_p=copy.deepcopy(position)
        )
        self.target = target
        self.exploded = False
        self.has_hit = []

    def detect_hits(self, arena):
        hits = []
        if self.exploded:
            for each in arena.towers + arena.buildings + arena.troops:
                if (isinstance(each, Tower) or not each.invulnerable) and each.side != self.side: # if different side
                    if vector.distance(self.position, each.position) < IceSpiritAttackEntity.DAMAGE_RADIUS + each.collision_radius:
                        hits.append(each)
        return hits
            
    def tick(self, arena):
        if self.exploded:
            hits = self.detect_hits(arena)
            for each in hits:
                new = not any(each is h for h in self.has_hit)
                if (new):
                    each.damage(self.damage)
                    each.freeze(self.FREEZE_DURATION)
                    self.has_hit.append(each)
        else:
            direction = self.target.position.subtracted(self.position)
            direction.normalize()

            movement = direction.scaled(self.velocity)
            self.position.add(movement)
            
            if vector.distance(self.position, self.target.position) < self.target.collision_radius:
                self.display_size = IceSpiritAttackEntity.DAMAGE_RADIUS 
                self.duration =  0.25
                self.exploded = True
    
class IceSpirit(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 90 * pow(1.1, level - 1),         # Hit points (Example value)
            h_d= 43 * pow(1.1, level - 1),          # Hit damage (Example value)
            h_s=0.3,          # Hit speed (Seconds per hit)
            l_t=0.1,            # First hit cooldown
            h_r=2.5,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=False,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=120*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=1,            #mass
            c_r=0.4,        #collision radius
            p=position               # Position (vector.Vector object)
        ) 
        self.level = level
        self.should_delete = False
        self.walk_cycle_frames = 4
        class_name = self.__class__.__name__.lower()
        self.sprite_path = f"sprites/{class_name}/{class_name}_0.png"
    
    def attack(self):
        self.should_delete = True
        return IceSpiritAttackEntity(self.side, self.hit_damage, self.position, self.target)

class IceGolemAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 0.75
    COLLISION_RADIUS = 0.7
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            position=position,
            target=target
            )

class IceGolemDeathAttackEntity(AttackEntity):
    SPLASH_RADIUS = 2
    def __init__(self, side, damage, position, target_pos):
        super().__init__(
            s=side,
            d=damage,
            v=0,
            l=0.25,
            i_p=copy.deepcopy(position)
        )
        self.display_size = self.SPLASH_RADIUS

    def apply_effect(self, target):
        target.slow(1)
    
    def detect_hits(self, arena):
        hits = []
        for each in arena.towers + arena.buildings + arena.troops:
            if each.side != self.side and (isinstance(each, Tower) or (each.ground and not each.invulnerable)): # if different side
                if vector.distance(self.position, each.position) < self.SPLASH_RADIUS + each.collision_radius:
                        hits.append(each)
        return hits

class IceGolem(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 565 * pow(1.1, level - 3),         # Hit points (Example value)
            h_d= 40 * pow(1.1, level - 3),          # Hit damage (Example value)
            h_s=2.5,          # Hit speed (Seconds per hit)
            l_t=1.5,            # First hit cooldown
            h_r=0.75,            # Hit range
            s_r=7,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=True,        # Not tower-only
            m_s=45*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=6,            #mass
            c_r=0.7,        #collision radius
            p=position               # Position (vector.Vector object)
        )
        self.level = level
        self.ticks_per_frame = 6
        self.walk_cycle_frames = 6
        class_name = self.__class__.__name__.lower()
        self.sprite_path = f"sprites/{class_name}/{class_name}_0.png"
    def attack(self):
        return IceGolemAttackEntity(self.side, self.hit_damage, self.position, self.target)
    def die(self, arena):
        self.cur_hp = -1
        arena.active_attacks.append(IceGolemDeathAttackEntity(self.side, self.hit_damage, self.position, self.target))
        arena.troops.remove(self)

class Freeze(Spell):
    def __init__(self, side, target, level):
        super().__init__(
            s=side,
            d=72 * pow(1.1, level - 6),
            c_t_d=22 * pow(1.1, level - 6),
            w=1,
            t=0,
            kb=0,
            r=3,
            v=0,
            tar=target
        )
        self.display_duration = 4

    def apply_effect(self, target):
        target.freeze(4)