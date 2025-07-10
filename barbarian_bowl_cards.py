from abstract_classes import MeleeAttackEntity
from abstract_classes import RangedAttackEntity
from abstract_classes import Troop
from abstract_classes import Building
from abstract_classes import TILES_PER_MIN
from abstract_classes import TICK_TIME
import vector
import math

class BarbarianAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 0.7
    COLLISION_RADIUS = 0.5
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            position=position,
            target=target
            )
        
            
class Barbarian(Troop):
    def __init__(self, side, position, level, cloned=False):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 262 * pow(1.1, level - 1),         # Hit points (Example value)
            h_d= 75 * pow(1.1, level - 1),          # Hit damage (Example value)
            h_s=1.3,          # Hit speed (Seconds per hit)
            l_t=0.9,            # First hit cooldown
            h_r=0.7,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=4,            #mass
            c_r=0.5,        #collision radius
            p=position,               # Position (vector.Vector object)
            cloned=cloned
        )
        self.level = level
        self.ticks_per_frame = 6
        self.walk_cycle_frames = 6
        class_name = self.__class__.__name__.lower()
        self.sprite_path = f"sprites/{class_name}/{class_name}_0.png"
    def attack(self):
        return BarbarianAttackEntity(self.side, self.hit_damage, self.position, self.target)
    
class CannonAttackEntity(RangedAttackEntity):
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            velocity=1000*TILES_PER_MIN,
            position=position,
            target=target,
        )


class Cannon(Building):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,
            h_p=322 * pow(1.1, level - 3),
            h_d = 83 * pow(1.1, level - 3),
            h_s = 0.9,
            l_t = 0,
            h_r = 5.5,
            s_r = 5.5,
            g = True,
            t_g_o = True,
            t_o = False,
            l=30,
            d_t=1,
            c_r=0.6,
            d_s_c=0,
            d_s=None,
            p=position
        )
        self.next_spawn = None
        self.remaining_spawn_count = 0
        self.level = level
    
    def attack(self):
        return CannonAttackEntity(self.side, self.hit_damage, self.position, self.target)

class MegaMinionAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 1.6
    COLLISION_RADIUS = 0.6
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            position=position,
            target=target
            )
        
            
class MegaMinion(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 395 * pow(1.1, level - 3),         # Hit points (Example value)
            h_d= 147 * pow(1.1, level - 3),          # Hit damage (Example value)
            h_s=1.5,          # Hit speed (Seconds per hit)
            l_t=1.1,            # First hit cooldown
            h_r=1.6,            # Hit range
            s_r=5.5,            # Sight Range
            g=False,           # Ground troop
            t_g_o=False,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=6,            #mass
            c_r=0.6,        #collision radius
            p=position               # Position (vector.Vector object)
        ) 
        self.level = level
        self.walk_cycle_frames = 4
        class_name = self.__class__.__name__.lower()
        self.sprite_path = f"sprites/{class_name}/{class_name}_0.png"
    def attack(self):
        return MegaMinionAttackEntity(self.side, self.hit_damage, self.position, self.target)   
    
class BattleRamAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 0.5
    COLLISION_RADIUS = 0.75
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            position=position,
            target=target
            )
    
class BattleRam(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 430 * pow(1.1, level - 3),         # Hit points
            h_d= 135 * pow(1.1, level - 3),          # Hit damage (charge is 2x)
            h_s=0.4,          # Hit speed (Seconds per hit)
            l_t=0.35,            # First hit cooldown
            h_r=0.5,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=True,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=6,            #mass
            c_r=0.75,        #collision radius
            p=position               # Position (vector.Vector object)
        ) 
        self.level = level
        self.charge_speed = 120 * TILES_PER_MIN
        self.charge_damage = self.hit_damage * 2
        self.charge_charge_distance = 0
        self.charging = False
        self.should_delete = False

        self.sprite_path = "sprites/battleram/battleram.png"

    def kb(self, vec, t=None):
        if vec.magnitude() > 0:
            self.charging = False
            self.charge_charge_distance = 0
            self.move_speed = 60 * TILES_PER_MIN
        super().kb(vec, t)

    def stun(self):
        self.charging = False
        self.charge_charge_distance = 0
        self.stun_timer = 0.5
        self.move_speed = 60 * TILES_PER_MIN
        self.target = None

    def freeze(self, duration):
        self.stun_timer = duration
        self.charging = False
        self.charge_charge_distance = 0
        self.move_speed = 60 * TILES_PER_MIN
        self.attack_cooldown = self.hit_speed

    def die(self, arena):
        radians = math.radians(self.facing_dir)
        # Use cosine for x offset and sine for y offset
        dx = math.cos(radians) * 0.3
        dy = math.sin(radians) * 0.3

        # Spawn two troops offset in opposite directions perpendicular to the facing direction
        offset1 = vector.Vector(dx, dy)
        offset2 = vector.Vector(-dx, -dy)
        
        arena.troops.append(Barbarian(self.side, self.position.added(offset1), self.level, self.cloned))
        arena.troops.append(Barbarian(self.side, self.position.added(offset2), self.level, self.cloned))
        arena.troops.remove(self)
        self.cur_hp = -1

    def tick_func(self, arena):
        if self.stun_timer <= 0 and not self.charging and self.charge_charge_distance >= 3:
            self.charging = True
            self.move_speed = self.charge_speed
            self.charge_charge_distance = 0
        if self.stun_timer <= 0 and self.deploy_time <= 0 and not self.charging: #if not in range
            self.charge_charge_distance += self.move_speed

    def attack(self):
        self.should_delete = True
        if self.charging:
            return BattleRamAttackEntity(self.side, self.charge_damage, self.position, self.target)  
        else:
            return BattleRamAttackEntity(self.side, self.hit_damage, self.position, self.target)  

