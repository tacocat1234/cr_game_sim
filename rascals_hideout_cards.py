from abstract_classes import RangedAttackEntity
from abstract_classes import MeleeAttackEntity
from abstract_classes import AttackEntity
from abstract_classes import Troop
from abstract_classes import Tower
from abstract_classes import TILES_PER_MIN
from abstract_classes import TICK_TIME
import vector
import copy

class RascalBoyAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 0.8
    COLLISION_RADIUS = 0.75
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            position=position,
            target=target
            )
        
class RascalBoy(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 758 * pow(1.1, level - 1),         # Hit points (Example value)
            h_d= 52 * pow(1.1, level - 1),          # Hit damage (Example value)
            h_s=1.5,          # Hit speed (Seconds per hit)
            l_t=1.1,            # First hit cooldown
            h_r=0.8,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=False,        # not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=10,            #mass
            c_r=0.75,        #collision radius
            p=position               # Position (vector.Vector object)
        ) 
        self.level = level
    
    def attack(self):
        return RascalBoyAttackEntity(self.side, self.hit_damage, self.position, self.target)
    
class RascalGirlAttackEntity(RangedAttackEntity):
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side, 
            damage=damage, 
            velocity=800*TILES_PER_MIN, 
            position=position, 
            target=target
        )

class RascalGirl(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 102 * pow(1.1, level - 1),         # Hit points (Example value)
            h_d= 52 * pow(1.1, level - 1),          # Hit damage (Example value)
            h_s=1,          # Hit speed (Seconds per hit)
            l_t=0.5,            # First hit cooldown
            h_r=5,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=False,       # Targets ground-only
            t_o=False,        # not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=2,            #mass
            c_r=0.5,        #collision radius
            p=position               # Position (vector.Vector object)
        ) 
        self.level = level
    
    def attack(self):
        return RascalGirlAttackEntity(self.side, self.hit_damage, self.position, self.target)
    
class BanditAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 0.75
    COLLISION_RADIUS = 0.6
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            position=position,
            target=target
            )

class BanditDashAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 0.75
    COLLISION_RADIUS = 0.6
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            position=position,
            target=target
            )
    
class Bandit(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 750 * pow(1.1, level - 9),         # Hit points (Example value)
            h_d= 160 * pow(1.1, level - 9),          # Hit damage (Example value)
            h_s=1,          # Hit speed (Seconds per hit)
            l_t=0.5,            # First hit cooldown
            h_r=0.75,            # Hit range
            s_r=6,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=90*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=3,            #mass
            c_r=0.6,        #collision radius
            p=position               # Position (vector.Vector object)
        )
        self.dash_timer = 0
        self.should_dash = False

        self.can_kb = False
        self.level = level
        self.ticks_per_frame = 6
        self.walk_cycle_frames = 6
        class_name = self.__class__.__name__.lower()
        self.sprite_path = f"sprites/{class_name}/{class_name}_dash.png"

    def tick_func(self, arena):
        if self.stun_timer <= 0:
            if self.deploy_time <= 0:                    
                if self.should_dash:
                    self.update_target(arena) #give chance to target other troop instead
                    if self.target is None:
                        m = None
                        for tower in arena.towers:
                            dist = vector.distance(tower.position, self.position)
                            if m is None or dist < vector.distance(m.position, self.position):
                                m = tower
                        self.target = m
                    self.ground = False #allow cross river
                    self.should_dash = False
                    self.invulnerable = True
                    self.move_speed = 500*TILES_PER_MIN
                    self.dash_timer = 0.72
                elif self.target is not None:
                    d = vector.distance(self.position, self.target.position)
                    if d > 3.5 + self.target.collision_radius and d < 6 + self.target.collision_radius and self.dash_timer == 0:
                        self.should_dash = True
                else:
                    for tower in arena.towers:
                        dist = vector.distance(tower.position, self.position)
                        if tower.side != self.side and dist > 3.5 + tower.collision_radius and dist < 6 + tower.collision_radius:
                            self.stun_timer = 0.8
                            self.should_dash = True
                            break 
        
        if self.dash_timer < 0: #done dashing
            self.dash_timer = 0
            self.ground = True
            self.move_speed = 60*TILES_PER_MIN
            self.invulnerable = False
            self.attack_cooldown = self.hit_speed
            if self.target is not None:
                arena.active_attacks.append(BanditDashAttackEntity(self.side, self.hit_damage * 2, self.position, self.target))
        if self.dash_timer > 0:
            if not self.target is None and vector.distance(self.target.position, self.position) < self.hit_range:
                self.dash_timer = 0
            self.dash_timer -= TICK_TIME
    
    def attack(self):
        if self.dash_timer == 0: #if not dashings
            return BanditAttackEntity(self.side, self.hit_damage, self.position, self.target)