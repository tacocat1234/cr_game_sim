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
        
class ElectroGiantAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 1.2
    COLLISION_RADIUS = 0.75
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            position=position,
            target=target
            )
        
class ElectroGiantReflectDisplay(MeleeAttackEntity):
    HIT_RANGE = 2
    COLLISION_RADIUS = 0.75
    def __init__(self, position):
        super().__init__(
            side=0,
            damage=0,
            position=position,
            target=None
            )
        self.display_size = self.HIT_RANGE + self.COLLISION_RADIUS
        
    def tick(self, arena):
        pass
    
    def cleanup(self, arena):
        pass
        
class ElectroGiantReflectAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 2
    COLLISION_RADIUS = 0.75
    def __init__(self, side, damage, ctd, position, parent):
        super().__init__(
            side=side,
            damage=damage,
            position=position,
            target=None
            )
        self.ctd = ctd
        self.display_size = self.HIT_RANGE + self.COLLISION_RADIUS
        self.duration = float('inf')
        self.parent = parent

    def apply_effect(self, target):
        target.attack_cooldown -= TICK_TIME
        target.stun()
        

    def detect_hits(self, arena):
        hits = []
        for each in arena.towers + arena.buildings + arena.troops:
                if each.side != self.side and not each.invulnerable and (each.attack_cooldown == each.hit_speed or each.attack_cooldown == 0) and each.target is self.parent: # if different side
                    if vector.distance(self.position, each.position) < self.HIT_RANGE + self.COLLISION_RADIUS + each.collision_radius:
                        hits.append(each)
        return hits

    def tick(self, arena):
        hits = self.detect_hits(arena)
        if len(hits) > 0:
            for each in hits:
                if (isinstance(each, Tower)):
                    each.damage(self.ctd)
                else:
                    each.damage(self.damage)
                self.apply_effect(each)

class ElectroGiant(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 2410 * pow(1.1, level - 6),         # Hit points (Example value)
            h_d= 102 * pow(1.1, level - 6),          # Hit damage (Example value)
            h_s=2.1,          # Hit speed (Seconds per hit)
            l_t=0.6,            # First hit cooldown
            h_r=1.2,            # Hit range
            s_r=7.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=False,       # Targets ground-only
            t_o=True,        # Not tower-only
            m_s=45*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=18,            #mass
            c_r=0.75,        #collision radius
            p=position               # Position (vector.Vector object)
        )
        self.level = level
        self.reflected_damage = 120 * pow(1.1, level - 6)
        self.reflected_ctd = 80 * pow(1.1, level - 6)

        self.reflect_entity = ElectroGiantReflectAttackEntity(self.side, self.reflected_damage, self.reflected_ctd, self.position, self)
        self.reflect_display = ElectroGiantReflectDisplay(self.position)

    def on_deploy(self, arena):
        arena.active_attacks.append(self.reflect_display)

    def tick_func(self, arena):
        if self.stun_timer <= 0:
            self.reflect_entity.tick(arena)

    def cleanup_func(self, arena):
        if self.stun_timer <= 0:
            self.reflect_entity.cleanup(arena)

    def die(self, arena):
        arena.active_attacks.remove(self.reflect_display)
        self.cur_hp = -1
        arena.troops.remove(self)

    def attack(self):
        return ElectroGiantAttackEntity(self.side, self.hit_damage, self.position, self.target)

class BowlerAttackEntity(RangedAttackEntity):
    SPLASH_RADIUS = 1.8
    def __init__(self, side, damage, position, target, parent_pos):
        super().__init__(
            side=side, 
            damage=damage, 
            velocity=170*TILES_PER_MIN, 
            position=position, 
            target=target
        )
        self.homing = False
        self.piercing = True
        self.set_move_vec()
        self.duration = 2.65
        self.display_size = 1
        self.resize = True

        self.parent_pos = parent_pos

    def detect_hits(self, arena):
        hits = []
        for each in arena.towers + arena.buildings + arena.troops:
            if each.side != self.side and (isinstance(each, Tower) or (each.ground and not each.invulnerable)) and each not in self.has_hit: # if different side
                if vector.distance(each.position, self.position) <= each.collision_radius + (-0.26 if self.duration > 2.45 else self.SPLASH_RADIUS):
                    hits.append(each)
                    self.has_hit.append(each)
        return hits

    def apply_effect(self, target):
        if isinstance(target, Troop):
            vec = target.position.subtracted(self.parent_pos)
            vec.normalize()
            vec.scale(1.8)
            target.kb(vec)


class Bowler(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 1300 * pow(1.1, level - 6),         # Hit points (Example value)
            h_d= 180 * pow(1.1, level - 6),          # Hit damage (Example value)
            h_s=2.5,          # Hit speed (Seconds per hit)
            l_t=2.0,            # First hit cooldown
            h_r=4,            # Hit range
            s_r=7.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=45*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=18,            #mass
            c_r=0.75,        #collision radius
            p=position               # Position (vector.Vector object)
        )
        self.level = level

    def attack(self):
        return BowlerAttackEntity(self.side, self.hit_damage, self.position, self.target.position, self.position)
    
class MagicArcherAttackEntity(RangedAttackEntity):
    SPLASH_RADIUS = 0.25
    EXTRA_SPLASH = 0.4
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side, 
            damage=damage, 
            velocity=1000*TILES_PER_MIN, 
            position=position, 
            target=target
        )
        self.homing = False
        self.piercing = True
        self.set_move_vec()
        self.duration = 0.67


    def detect_hits(self, arena):
        hits = []
        for each in arena.towers + arena.buildings + arena.troops:
            if each.side != self.side and not each.invulnerable and each not in self.has_hit: # if different side
                if vector.distance(each.position, self.position) <= each.collision_radius + self.SPLASH_RADIUS + (0 if self.duration < 0.6 else self.EXTRA_SPLASH):
                    hits.append(each)
                    self.has_hit.append(each)
        return hits


class MagicArcher(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 440 * pow(1.1, level - 9),         # Hit points (Example value)
            h_d= 111 * pow(1.1, level - 9),          # Hit damage (Example value)
            h_s=1.1,          # Hit speed (Seconds per hit)
            l_t=0.6,            # First hit cooldown
            h_r=7,            # Hit range
            s_r=7.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=False,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=3,            #mass
            c_r=0.6,        #collision radius
            p=position               # Position (vector.Vector object)
        )
        self.level = level

    def attack(self):
        return MagicArcherAttackEntity(self.side, self.hit_damage, self.position, self.target.position)