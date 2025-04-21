from abstract_classes import RangedAttackEntity
from abstract_classes import MeleeAttackEntity
from abstract_classes import AttackEntity
from abstract_classes import Troop
from abstract_classes import Tower
from abstract_classes import TILES_PER_MIN
from abstract_classes import TICK_TIME
import vector
import copy
import math

class RoyalRecruitAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 1.6
    COLLISION_RADIUS = 0.5
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            position=position,
            target=target
            )

class RoyalRecruit(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 208 * pow(1.1, level - 1),         # Hit points (Example value)
            h_d= 52 * pow(1.1, level - 1),          # Hit damage (Example value)
            h_s=1.3,          # Hit speed (Seconds per hit)
            l_t=0.8,            # First hit cooldown
            h_r=1.6,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=1,            #mass
            c_r=0.5,        #collision radius
            p=position               # Position (vector.Vector object)
        )
        self.level = level
        self.has_shield = True
        self.shield_max_hp = 94 * pow(1.1, level - 1)
        self.shield_hp = self.shield_max_hp

        self.ticks_per_frame = 12
        self.walk_cycle_frames = 4
        class_name = self.__class__.__name__.lower()
        self.sprite_path = f"sprites/{class_name}/{class_name}_0.png"

    def damage(self, amount):
        if self.shield_hp > 0:
            self.shield_hp -= amount
        else:
            self.cur_hp -= amount

    def attack(self):
        return RoyalRecruitAttackEntity(self.side, self.hit_damage, self.position, self.target)

class RoyalGiantAttackEntity(RangedAttackEntity):
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            velocity=1000*TILES_PER_MIN,
            position=position,
            target=target,
        )

class RoyalGiant(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 1200 * pow(1.1, level - 1),         # Hit points (Example value)
            h_d= 120 * pow(1.1, level - 1),          # Hit damage (Example value)
            h_s=1.7,          # Hit speed (Seconds per hit)
            l_t=0.8,            # First hit cooldown
            h_r=6,            # Hit range
            s_r=7.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=True,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=18,            #mass
            c_r=0.75,        #collision radius
            p=position               # Position (vector.Vector object)
        ) 
        self.level = level
        self.can_kb = False
    
    def attack(self):
        return RoyalGiantAttackEntity(self.side, self.hit_damage, self.position, self.target)
                 
class RoyalHogAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 0.75
    COLLISION_RADIUS = 0.6
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            position=position,
            target=target
            )
        
class RoyalHog(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 395 * pow(1.1, level - 3),         # Hit points (Example value)
            h_d= 35 * pow(1.1, level - 3),          # Hit damage (Example value)
            h_s=1.2,          # Hit speed (Seconds per hit)
            l_t=0.8,            # First hit cooldown
            h_r=0.75,            # Hit range
            s_r=9.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=True,        # tower-only
            m_s=120*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=2,            #mass
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
        return RoyalHogAttackEntity(self.side, self.hit_damage, self.position, self.target)

class BalloonAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 0.1
    COLLISION_RADIUS = 0.5
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            position=position,
            target=target
            )

class Balloon(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,
            h_p = 1050 * pow(1.1, level - 6),
            h_d = 400 * pow(1.1, level - 6),
            h_s=2,
            l_t=1.8,
            h_r=0.1,
            s_r=7.7,
            g=False,
            t_g_o=True,
            t_o=True,
            m_s=60*TILES_PER_MIN,
            d_t=1,
            m=6,
            c_r=0.5,
            p=position
        ) 
        self.level = level
        self.walk_cycle_frames = 1
        class_name = self.__class__.__name__.lower()
        self.sprite_path = f"sprites/{class_name}/{class_name}.png"
    
    def attack(self):
        return BalloonAttackEntity(self.side, self.hit_damage, self.position, self.target)
    
    def die(self, arena):
        damage = 150 * pow(1.1, self.level - 6)
        self.cur_hp = -1
        arena.troops.append(BalloonDeathBomb(self.side, copy.deepcopy(self.position), self.level))
        arena.troops.remove(self)
    
class BalloonDeathBombAttackEntity(AttackEntity):
    DAMAGE_RADIUS = 3
    def __init__(self, side, damage, position):
        super().__init__(
            s=side,
            d=damage,
            v=0,
            l=0.25,
            i_p=copy.deepcopy(position)
        )
        self.display_size = BalloonDeathBombAttackEntity.DAMAGE_RADIUS
        self.has_hit = []

    def detect_hits(self, arena):
        hits = []
        for each in arena.towers + arena.buildings + arena.troops:
            if each.side != self.side and (isinstance(each, Tower) or not each.invulnerable): # if different side
                if vector.distance(self.position, each.position) < BalloonDeathBombAttackEntity.DAMAGE_RADIUS + each.collision_radius:
                    hits.append(each)
        return hits
            
    def tick(self, arena):
        hits = self.detect_hits(arena)
        for each in hits:
            new = not any(each is h for h in self.has_hit)
            if (new):
                each.damage(self.damage)
                self.has_hit.append(each)


class BalloonDeathBomb(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p=  float('inf'),         # Hit points (Example value)
            h_d= 150 * pow(1.1, level - 6),          # Hit damage (Example value)
            h_s=0,          # Hit speed (Seconds per hit)
            l_t=0,            # First hit cooldown
            h_r=0,            # Hit range
            s_r=0,            # Sight Range
            g=True,           # Ground troop
            t_g_o=False,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=0,          # Movement speed 
            d_t=3,            # Deploy time
            m=float('inf'),            #mass
            c_r=0.45,        #collision radius
            p=position               # Position (vector.Vector object)
        ) 
        self.level = level
        self.invulnerable=True
        self.targetable=False
        self.target=None

    def tick(self, arena):
        if self.deploy_time <= 0:
            arena.active_attacks.append(self.attack())
            self.cur_hp = -1
    
    def attack(self):
        return BalloonDeathBombAttackEntity(self.side, self.hit_damage, self.position)
    
class PrinceAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 1.6
    COLLISION_RADIUS = 0.6
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            position=position,
            target=target
            )
    
class Prince(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 1200 * pow(1.1, level - 6),         # Hit points
            h_d= 245 * pow(1.1, level - 6),          # Hit damage (charge is 2x)
            h_s=1.4,          # Hit speed (Seconds per hit)
            l_t=0.9,            # First hit cooldown
            h_r=1.6,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=6,            #mass
            c_r=0.6,        #collision radius
            p=position               # Position (vector.Vector object)
        ) 
        self.level = level
        self.charge_speed = 120 * TILES_PER_MIN
        self.charge_damage = self.hit_damage * 2
        self.charge_charge_distance = 0
        self.charging = False
        self.cross_river = True
        self.jump_speed = 160 * TILES_PER_MIN
        self.can_kb = False

        class_name = self.__class__.__name__.lower()
        self.sprite_path = f"sprites/{class_name}/{class_name}_0.png"

    def stun(self):
        self.charging = False
        self.charge_charge_distance = 0
        self.stun_timer = 0.5
        self.move_speed = 60 * TILES_PER_MIN
        self.target = None

    def tick_func(self, arnea):
        if self.stun_timer <= 0 and not self.charging and self.charge_charge_distance >= 3:
            self.charging = True
            self.move_speed = self.charge_speed
            self.charge_charge_distance = 0
        if self.stun_timer <= 0 and self.deploy_time <= 0 and not self.charging and self.move_vector.magnitude() == 0: #if not in range
            self.charge_charge_distance += self.move_speed

    def attack(self):
        if self.charging:
            self.charging = False 
            self.charge_charge_distance = 0
            self.move_speed = 60 * TILES_PER_MIN
            return PrinceAttackEntity(self.side, self.charge_damage, self.position, self.target) 
        else:
            return PrinceAttackEntity(self.side, self.hit_damage, self.position, self.target)
        
class DarkPrinceAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 1.2
    COLLISION_RADIUS = 0.6
    SPLASH_RADIUS = 1.1
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            position=copy.deepcopy(target),
            target=copy.deepcopy(target) #not used
            )
        
    def detect_hits(self, arena):
        hits = []
        for each in arena.towers + arena.buildings + arena.troops:
            if each.side != self.side and (isinstance(each, Tower) or (each.ground and not each.invulnerable)): # if different side
                if vector.distance(each.position, self.position) <= each.collision_radius + self.SPLASH_RADIUS:
                    hits.append(each)
        return hits
                
            

class DarkPrince(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 750 * pow(1.1, level - 6),         # Hit points
            h_d= 155 * pow(1.1, level - 6),          # Hit damage (charge is 2x)
            h_s=1.3,          # Hit speed (Seconds per hit)
            l_t=0.9,            # First hit cooldown
            h_r=1.2,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=6,            #mass
            c_r=0.6,        #collision radius
            p=position               # Position (vector.Vector object)
        ) 
        self.level = level
        self.charge_speed = 120 * TILES_PER_MIN
        self.charge_damage = self.hit_damage * 2
        self.charge_charge_distance = 0
        self.charging = False
        self.cross_river = True
        self.jump_speed = 160 * TILES_PER_MIN
        self.can_kb = False

        self.has_shield = True
        self.shield_max_hp = 150 * pow(1.1, level - 6)
        self.shield_hp = self.shield_max_hp
        class_name = self.__class__.__name__.lower()
        self.sprite_path = f"sprites/{class_name}/{class_name}_0.png"

    def damage(self, amount):
        if self.shield_hp > 0:
            self.shield_hp -= amount
        else:
            self.cur_hp -= amount

    def stun(self):
        self.charging = False
        self.charge_charge_distance = 0
        self.stun_timer = 0.5
        self.move_speed = 60 * TILES_PER_MIN
        self.target = None

    def tick_func(self, arnea):
        if self.stun_timer <= 0 and not self.charging and self.charge_charge_distance >= 3:
            self.charging = True
            self.move_speed = self.charge_speed
            self.charge_charge_distance = 0
        if self.stun_timer <= 0 and self.deploy_time <= 0 and not self.charging and self.move_vector.magnitude() == 0: #if not in range
            self.charge_charge_distance += self.move_speed

    def attack(self):
        if self.charging:
            self.charging = False 
            self.charge_charge_distance = 0
            self.move_speed = 60 * TILES_PER_MIN
            return DarkPrinceAttackEntity(self.side, self.charge_damage, self.position, self.target.position) 
        else:
            return DarkPrinceAttackEntity(self.side, self.hit_damage, self.position, self.target.position)