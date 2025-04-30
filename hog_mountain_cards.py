from abstract_classes import RangedAttackEntity
from abstract_classes import MeleeAttackEntity
from abstract_classes import AttackEntity
from abstract_classes import Troop
from abstract_classes import Tower
from abstract_classes import Building
from abstract_classes import Spell
from spell_valley_cards import FireSpirit
from abstract_classes import TILES_PER_MIN
from abstract_classes import TICK_TIME
import vector
import copy
import math
import random

class EliteBarbarianAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 1.2
    COLLISION_RADIUS = 0.5
    def __init__(self, side, damage, position, target):
        super().__init__(
            side, 
            damage, 
            position, 
            target
        )

class EliteBarbarian(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 524 * pow(1.1, level - 1),         # Hit points (Example value)
            h_d= 150 * pow(1.1, level - 1),          # Hit damage (Example value)
            h_s=1.4,          # Hit speed (Seconds per hit)
            l_t=0.9,            # First hit cooldown
            h_r=1.2,            # Hit range
            s_r=6,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=90*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=4,            #mass
            c_r=0.5,        #collision radius
            p=position               # Position (vector.Vector object)
        )
        self.level = level
    def attack(self):
        return EliteBarbarianAttackEntity(self.side, self.hit_damage, self.position, self.target)

class Furnace(Building):
    SPAWN_INTERVAL = 0.5
    def __init__(self, side, position, level):
        super().__init__(
            s=side,
            h_p=400 * pow(1.1, level - 3),
            h_d = 0,
            h_s = 5,
            l_t = 0,
            h_r = 0,
            s_r = 0,
            g = True,
            t_g_o = True,
            t_o = False,
            l=28,
            d_t=1,
            c_r=1,
            d_s_c=1,
            d_s=FireSpirit,
            p=position
        )
        self.next_spawn = None
        self.remaining_spawn_count = 0
        self.is_spawner = True
        self.level = level
    
    def cleanup_func(self, arena):
        if self.stun_timer <= 0:
            if not self.next_spawn is None and self.next_spawn > 0:
                self.next_spawn -= TICK_TIME
        
    def tick(self, arena):
        if self.stun_timer <= 0:
            if self.attack_cooldown <= 0: #attack code
                front = vector.Vector(0, 1.5) if self.side else vector.Vector(0, -1.5)
                arena.troops.append(FireSpirit(self.side, self.position.added(front), self.level))
                self.attack_cooldown = self.hit_speed

class ZappyAttackEntity(RangedAttackEntity):
    def __init__(self, side, damage, velocity, position, target):
        super().__init__(
            side=side, 
            damage=damage, 
            velocity=2000*TILES_PER_MIN, 
            position=position, 
            target=target
        )

    def apply_effect(self, target):
        target.stun()

class Zappy(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 250 * pow(1.1, level - 3),         # Hit points (Example value)
            h_d= 55 * pow(1.1, level - 3),          # Hit damage (Example value)
            h_s=2.1,          # Hit speed (Seconds per hit)
            l_t=1,            # First hit cooldown
            h_r=4.5,            # Hit range
            s_r=5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=False,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=4,            #mass
            c_r=0.6,     #collision radius
            p=position               # Position (vector.Vector object)
        )
        self.level = level
    def attack(self):
        return ZappyAttackEntity(self.side, self.hit_damage, self.position, self.target)
    
class XBowAttackEntity(RangedAttackEntity):
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side, 
            damage=damage, 
            velocity=1400*TILES_PER_MIN, 
            position=position, 
            target=target
        )

class XBow(Building):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,
            h_p=1000 * pow(1.1, level - 6),
            h_d=26 * pow(1.1, level - 6),
            h_s=0.3,
            l_t=0,
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
    
    def attack(self):
        return XBowAttackEntity(self.side, self.hit_damage, self.position, copy.deepcopy(self.target.position))


class HunterAttackEntity(RangedAttackEntity):
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side, 
            damage=damage, 
            velocity=0, 
            position=position, 
            target=target
        )
        self.random_delay = random.uniform(0, 0.2)
        self.homing = False
        self.duration = 0.709 + self.random_delay


    def cleanup(self, arena):
        self.random_delay -= TICK_TIME
        if self.velocity == 0 and self.random_delay <= 0:
            self.velocity = 550*TILES_PER_MIN
        self.duration -= TICK_TIME
        if self.duration <= 0 or self.should_delete:
            arena.active_attacks.remove(self)

    def detect_hits(self, arena):
        for each in arena.troops + arena.towers + arena.buildings:
            if not each.side == self.side and (vector.distance(each.position, self.position) < each.collision_radius + (0.95 if self.duration - self.random_delay < 0.2 else 0.35)):
                return [each] # has hit
        return [] #hasnt hit yet

class Hunter(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 524 * pow(1.1, level - 6),         # Hit points (Example value)
            h_d= 53 * pow(1.1, level - 6),          # Hit damage (Example value)
            h_s=2.2,          # Hit speed (Seconds per hit)
            l_t=1.4,            # First hit cooldown
            h_r=4,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=False,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=5,            #mass
            c_r=0.6,     #collision radius
            p=position               # Position (vector.Vector object)
        )
        self.level = level
        self.attack_cooldown = 0.3
    
    def attack(self):
        attacks = []
        num_attacks = 10
        spread_degrees = 60
        half_spread = spread_degrees / 2
        distance = 6.5

        # Convert facing direction to radians
        facing_rad = math.radians(self.facing_dir)

        for i in range(num_attacks):
            # Compute the angle offset: from -30° to +30°
            angle_offset = -half_spread + i * (spread_degrees / (num_attacks - 1))
            angle_rad = facing_rad + math.radians(angle_offset)

            # Compute the direction vector
            dir_x = math.cos(angle_rad)
            dir_y = math.sin(angle_rad)
            # Final target position
            target_position = self.position.added(vector.Vector(dir_x, dir_y).scaled(distance))
            attacks.append(HunterAttackEntity(self.side, self.hit_damage, self.position, target_position))

        return attacks