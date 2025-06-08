from abstract_classes import AttackEntity
from abstract_classes import RangedAttackEntity
from abstract_classes import MeleeAttackEntity
from abstract_classes import Troop
from abstract_classes import Spell
from abstract_classes import Building
from abstract_classes import Tower
from abstract_classes import TILES_PER_MIN
from abstract_classes import TICK_TIME
from bone_pit_cards import Skeleton
import vector
import math
import copy

class Earthquake(Spell):
    def __init__(self, side, target, level):
        super().__init__(
            s=side,
            d=39 * pow(1.1, level - 3),
            c_t_d=26 * pow(1.1, level - 3),
            w=3,
            t=1,
            kb=0,
            r=3.5,
            v=0,
            tar=target
        )
        self.pulse_time = 0.1
        self.pulse_timer = 0
        self.building_damage = 136 * pow(1.1, level - 3)

    def detect_hits(self, arena):
        out = []
        for each in arena.troops + arena.buildings + arena.towers:
            if each.side != self.side and each.ground and (isinstance(each, Tower) or not each.invulnerable) and (vector.distance(each.position, self.position) <= self.radius + each.collision_radius):
                out.append(each)
        return out

    def tick(self, arena):
        if self.preplace:
            return
        if self.waves > 0 and self.damage_cd <= 0:
            self.sprite_path = f"sprites/{self.class_name}/{self.class_name}_hit.png"
            hits = self.detect_hits(arena)
            for each in hits:
                if (isinstance(each, Tower)):
                    each.damage(self.crown_tower_damage)
                elif isinstance(each, Building):
                    each.damage(self.building_damage) #end damage, start kb
                else:
                    each.damage(self.damage)
            self.waves -= 1 #decrease waves
            self.damage_cd = self.time_between #reset cooldown
        elif self.damage_cd > 0:
            self.damage_cd -= TICK_TIME #decrement cooldown
        elif self.display_duration <= 0:
            self.should_delete = True #mark for deletion
        
        if self.pulse_timer <= 0:
            self.pulse_timer = self.pulse_time
            hits = self.detect_hits(arena)
            for each in hits:
                self.passive_effect(each)
        else:
            self.pulse_timer -= TICK_TIME

    def passive_effect(self, each):
        if isinstance(each, Troop):
            each.move_slow(0.5, 1, "earthquake")

class Graveyard(Spell):
    def __init__(self, side, target, level):
        super().__init__(
            s=side,
            d=0,
            c_t_d=0,
            w=13,
            t=0.5,
            kb=0,
            r=4,
            v=0,
            tar=target
        )
        self.initial_delay = 2.2
        self.display_duration = 9
        self.spawn_dir = 0
        self.level = level

    def tick(self, arena):
        if self.preplace:
            return
        
        if self.initial_delay <= 0:
            if self.damage_cd <= 0:
                angle = 10/13 * math.pi * self.spawn_dir
                pos = self.position.added(vector.Vector(math.cos(angle), math.sin(angle)).scaled(3.5))
                if pos.x > 9:
                    pos.x = 9
                if pos.x < -9:
                    pos.x = -9
                if pos.y > 16:
                    pos.y = 16
                if pos.y < -16:
                    pos .y = 16
                arena.troops.append(Skeleton(self.side, pos, self.level))
                self.damage_cd = self.time_between
                self.spawn_dir += 1
        
    def cleanup(self, arena):
        if self.preplace:
            return

        if self.display_duration <= 0:
            arena.spells.remove(self)    
    
        if self.initial_delay > 0:
            self.initial_delay -= TICK_TIME
        elif self.damage_cd > 0:
                self.damage_cd -= TICK_TIME
        self.display_duration -= TICK_TIME

class FirecrackerExplosionAttackEntity(RangedAttackEntity):
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side, 
            damage=damage, 
            velocity=550*TILES_PER_MIN, 
            position=position, 
            target=target
        )
        self.duration = 0.545
        self.homing = False
        self.piercing = True

        self.set_move_vec()
    
    def detect_hits(self, arena):
        out = []
        for each in arena.troops + arena.towers + arena.buildings:
            if not each.side == self.side and not each.invulnerable and not each in self.has_hit and (vector.distance(each.position, self.position) < each.collision_radius + (0.65 if self.duration > 0.445 else 0.4)):
                out.append(each)
                self.has_hit.append(each)
        return out

class FirecrackerAttackEntity(RangedAttackEntity):
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side, 
            damage=damage, 
            velocity=400*TILES_PER_MIN, 
            position=position, 
            target=target
        )
        self.homing = False
        self.piercing = True
        self.display_size = 0.3
        self.resize = True

        to_tar = self.target.subtracted(self.position)

        self.facing_dir = math.atan2(to_tar.y, to_tar.x)

        self.set_move_vec()

    def detect_hits(self, arena):
        out = []
        for each in arena.troops + arena.towers + arena.buildings:
            if not each.side == self.side and not each.invulnerable and not each in self.has_hit and (vector.distance(each.position, self.position) < each.collision_radius + 0.4):
                out.append(each)
                self.has_hit.append(each)
        return out

    def spawn_explosion_entities(self):
        attacks = []
        num_attacks = 5
        spread_degrees = 60
        half_spread = spread_degrees / 2
        distance = 5

        for i in range(num_attacks):
            # Compute the angle offset: from -30° to +30°
            angle_offset = -half_spread + i * (spread_degrees / (num_attacks - 1))
            angle_rad = self.facing_dir + math.radians(angle_offset)

            # Compute the direction vector
            dir_x = math.cos(angle_rad)
            dir_y = math.sin(angle_rad)
            # Final target position
            target_position = self.position.added(vector.Vector(dir_x, dir_y).scaled(distance))
            attacks.append(FirecrackerExplosionAttackEntity(self.side, self.damage, self.position, target_position))

        return attacks
    
    def cleanup_func(self, arena):
        if vector.distance(self.position, self.target) <= 0.1:
            arena.active_attacks.extend(self.spawn_explosion_entities())
            arena.active_attacks.remove(self)
            

class Firecracker(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 119 * pow(1.1, level - 1),         # Hit points (Example value)
            h_d= 25 * pow(1.1, level - 1),          # Hit damage (Example value)
            h_s=3,          # Hit speed (Seconds per hit)
            l_t=2.4,            # First hit cooldown
            h_r=6,            # Hit range
            s_r=8.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=False,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=90*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=6,            #mass
            c_r=0.5,     #collision radius
            p=position               # Position (vector.Vector object)
        )
        self.level = level
    
    def attack(self):
        self.kb(vector.Vector(math.cos(math.radians(self.facing_dir + 180)),
                         math.sin(math.radians(self.facing_dir + 180))).scaled(1.5))
        return FirecrackerAttackEntity(self.side, self.hit_damage, self.position, copy.deepcopy(self.target.position))

class WallBreakerAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 0.5
    COLLISION_RADIUS = 0.4
    SPLASH_RADIUS = 1.5
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            position=position,
            target=target
            )
    
    def detect_hits(self, arena):
        hits = []
        for each in arena.towers + arena.buildings + arena.troops:
            if each.side != self.side and (isinstance(each, Tower) or (each.ground and not each.invulnerable)): # if different side
                if vector.distance(each.position, self.position) <= each.collision_radius + self.SPLASH_RADIUS:
                    hits.append(each)
        return hits
  
class WallBreaker(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 207 * pow(1.1, level - 6),         # Hit points (Example value)
            h_d= 245 * pow(1.1, level - 6),          # Hit damage (Example value)
            h_s=1.2,          # Hit speed (Seconds per hit)
            l_t=1,            # First hit cooldown
            h_r=0.5,            # Hit range
            s_r=7,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=True,        # Not tower-only
            m_s=120*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=4,            #mass
            c_r=0.4,     #collision radius
            p=position               # Position (vector.Vector object)
        )
        self.level = level
    
    def attack(self):
        self.should_delete = True
        return WallBreakerAttackEntity(self.side, self.hit_damage, self.position, self.target)

class IceWizardSpawnAttackEntity(AttackEntity):
    SPLASH_RADIUS = 3
    def __init__(self, side, damage, position, target_pos):
        super().__init__(
            s=side,
            d=damage,
            v=0,
            l=1/60 + 0.01,
            i_p=copy.deepcopy(position)
        )
        self.display_size = self.SPLASH_RADIUS

    def apply_effect(self, target):
        target.slow(1, "icewizard")
    
    def detect_hits(self, arena):
        hits = []
        for each in arena.towers + arena.buildings + arena.troops:
            if each.side != self.side: # if different side
                if vector.distance(self.position, each.position) < self.SPLASH_RADIUS + each.collision_radius:
                        hits.append(each)

        return hits

class IceWizardAttackEntity(RangedAttackEntity):
    SPLASH_RADIUS = 1
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            velocity=700*TILES_PER_MIN,
            position=position,
            target=target,
        )
        self.exploded = False
        self.has_hit = []        
    
    def apply_effect(self, target):
        target.slow(2.5, "icewizard")

    def detect_hits(self, arena):
        hits = []
        if self.exploded:
            for each in arena.towers + arena.buildings + arena.troops:
                if each.side != self.side and (isinstance(each, Tower) or (not each.invulnerable)): # if different side
                    if vector.distance(self.position, each.position) < self.SPLASH_RADIUS + each.collision_radius:
                        hits.append(each)
        return hits
            
    def tick(self, arena):
        if self.exploded:
            hits = self.detect_hits(arena)
            for each in hits:
                new = not any(each is h for h in self.has_hit)
                if (new):
                    each.damage(self.damage)
                    self.apply_effect(each)
                    self.has_hit.append(each)
        else:
            direction = self.target.position.subtracted(self.position)
            direction.normalize()

            movement = direction.scaled(self.velocity)
            self.position.add(movement)
            
            if vector.distance(self.position, self.target.position) < 0.25:
                self.display_size = self.SPLASH_RADIUS
                self.duration =  0.1
                self.exploded = True

class IceWizard(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 569 * pow(1.1, level - 9),         # Hit points (Example value)
            h_d= 75 * pow(1.1, level - 9),          # Hit damage (Example value)
            h_s=1.7,          # Hit speed (Seconds per hit)
            l_t=1.2,            # First hit cooldown
            h_r=5.5,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=False,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=90*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=5,            #mass
            c_r=0.5,        #collision radius
            p=position               # Position (vector.Vector object)
        ) 
        self.level = level
        self.spawn_damage = 69 * pow(1.1, level - 9)
    
    def on_deploy(self, arena):
        arena.active_attacks.append(IceWizardSpawnAttackEntity(self.side, self.spawn_damage, self.position, self.target))

    def attack(self):
        return IceWizardAttackEntity(self.side, self.spawn_damage, self.position, self.target)

class RoyalGhostAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 1.2
    COLLISION_RADIUS = 0.6
    SPLASH_RADIUS = 1
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            position=target.position,
            target=target
            )
    
    def detect_hits(self, arena):
        hits = []
        for each in arena.towers + arena.buildings + arena.troops:
            if each.side != self.side and (isinstance(each, Tower) or (each.ground and not each.invulnerable)): # if different side
                if vector.distance(each.position, self.position) <= each.collision_radius + self.SPLASH_RADIUS:
                    hits.append(each)
        return hits
    
class RoyalGhost(Troop):
    INVISIBLE_COOLDOWN = 1.8
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 1000 * pow(1.1, level - 9),         # Hit points (Example value)
            h_d= 216 * pow(1.1, level - 9),          # Hit damage (Example value)
            h_s=1.8,          # Hit speed (Seconds per hit)
            l_t=1.2,            # First hit cooldown
            h_r=1.2,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=90*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=3,            #mass
            c_r=0.6,        #collision radius
            p=position               # Position (vector.Vector object)
        ) 
        self.cross_river = True
        self.jump_speed = 90 * TILES_PER_MIN
        self.invisbility_timer = 0

        self.level = level

    def on_preplace(self):
        self.targetable = False
    
    def cleanup_func(self, arena):
        if self.invisbility_timer > 0 :
            self.invisbility_timer -= TICK_TIME
        else:
            self.targetable = False

    def attack(self):
        self.targetable = True
        self.invisbility_timer = RoyalGhost.INVISIBLE_COOLDOWN
        return RoyalGhostAttackEntity(self.side, self.hit_damage, self.position, self.target)
    
class ElectroDragonAttackEntity(AttackEntity):
    CHAIN_RADIUS = 4
    MAX_CHAIN_HITS = 3
    def __init__(self, side, damage, position, target):
        super().__init__(
            s=side,
            d=damage,
            v=2000*TILES_PER_MIN,
            l=float('inf'),
            i_p=copy.deepcopy(position)
        )
        self.target = target
        self.chain_count = 0
        self.chain_center = target.position
        self.has_hit = [target]
        self.should_delete = False

    def detect_hits(self, arena):
        if vector.distance(self.position, self.target.position) < self.target.collision_radius:
            self.chain_count += 1
            return [self.target]
        return []
            
    def tick(self, arena):
        hits = self.detect_hits(arena)
        if len(hits) > 0:
                hits[0].stun()
                hits[0].damage(self.damage)
                self.should_delete = True
                self.chain_center = self.target.position
                if self.chain_count < ElectroDragonAttackEntity.MAX_CHAIN_HITS: #if can still chain
                    min_dist = float("inf")
                    min = None
                    for each in arena.towers + arena.buildings + arena.troops: #find new hits
                        if (isinstance(each, Tower) or not each.invulnerable) and each.side != self.side and vector.distance(each.position, self.chain_center) < 4: # if different side
                            new = not any(each is h for h in self.has_hit)
                            if vector.distance(each.position, self.chain_center) < min_dist and new:
                                min = each
                                min_dist = vector.distance(each.position, self.chain_center)
                                
                    if not min is None:
                        self.target = min
                        self.has_hit.append(min)
                        self.should_delete = False
        else:
            direction = self.target.position.subtracted(self.position)
            direction.normalize()

            movement = direction.scaled(self.velocity)
            self.position.add(movement)

    def cleanup(self, arena): #also delete self if single target here in derived classes
        if self.should_delete:
            arena.active_attacks.remove(self)

class ElectroDragon(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 569 * pow(1.1, level - 9),         # Hit points (Example value)
            h_d= 75 * pow(1.1, level - 9),          # Hit damage (Example value)
            h_s=2.1,          # Hit speed (Seconds per hit)
            l_t=1.4,            # First hit cooldown
            h_r=3.5,            # Hit range
            s_r=5.5,            # Sight Range
            g=False,           # Ground troop
            t_g_o=False,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=7,            #mass
            c_r=0.6,        #collision radius
            p=position               # Position (vector.Vector object)
        ) 
        self.level = level
    
    def attack(self):
        return ElectroDragonAttackEntity(self.side, self.hit_damage, self.position, self.target)

class PhoenixAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 1.6
    COLLISION_RADIUS = 0.5
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            position=position,
            target=target
            )
        
class PhoenixDeathAttackEntity(AttackEntity):
    SPLASH_RADIUS = 2.5
    def __init__(self, side, damage, ctd, position, target_pos):
        super().__init__(
            s=side,
            d=damage,
            v=0,
            l=1/60 + 0.01,
            i_p=copy.deepcopy(position)
        )
        self.display_size = self.SPLASH_RADIUS
        self.ctd = ctd

    def apply_effect(self, target):
        if isinstance(target, Troop) and target.can_kb and not target.invulnerable:
            vec = target.position.subtracted(self.position)
            vec.normalize()
            vec.scale(2)
            target.kb(vec)
    
    def detect_hits(self, arena):
        hits = []
        for each in arena.towers + arena.buildings + arena.troops:
            if each.side != self.side: # if different side
                if vector.distance(self.position, each.position) < self.SPLASH_RADIUS + each.collision_radius:
                        hits.append(each)

        return hits
    
    def tick(self, arena):
        hits = self.detect_hits(arena)
        for each in hits:
            new = not each in self.has_hit
            if (new):
                if (isinstance(each, Tower)):
                    each.damage(self.ctd)
                else:
                    each.damage(self.damage)
                self.apply_effect(each)
                self.has_hit.append(each)
        
class Phoenix(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 870 * pow(1.1, level - 9),         # Hit points (Example value)
            h_d= 180 * pow(1.1, level - 9),          # Hit damage (Example value)
            h_s=1,          # Hit speed (Seconds per hit)
            l_t=0.5,            # First hit cooldown
            h_r=1.6,            # Hit range
            s_r=5.5,            # Sight Range
            g=False,           # Ground troop
            t_g_o=False,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=2,            #mass
            c_r=0.6,        #collision radius
            p=position               # Position (vector.Vector object)
        ) 
        self.level = level
        self.death_damage = 135 * pow(1.1, level - 9)
        self.crown_tower_death_damage = 41 * pow(1.1, level - 9)
    
    def attack(self):
        return PhoenixAttackEntity(self.side, self.hit_damage, self.target.position, self.target)
    
    def die(self, arena):
        arena.active_attacks.append(PhoenixDeathAttackEntity(self.side, self.death_damage, self.crown_tower_death_damage, self.position, self.target))
        arena.troops.append(PhoenixEgg(self.side, self.position, self.level, self.cloned))
        super().die(arena)
    
class PhoenixEgg(Troop):
    def __init__(self, side, position, level, cloned):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 199 * pow(1.1, level - 9),         # Hit points (Example value)
            h_d= 0,          # Hit damage (Example value)
            h_s=3.3,          # Hit speed (Seconds per hit)
            l_t=0,            # First hit cooldown
            h_r=0,            # Hit range
            s_r=0,            # Sight Range
            g=True,           # Ground troop
            t_g_o=False,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=0,          # Movement speed 
            d_t=1,            # Deploy time
            m=99999,            #mass
            c_r=0.6,        #collision radius
            p=position,               # Position (vector.Vector object)
            cloned=cloned
        ) 
        self.level = level
        self.can_kb = False
    
    def tick(self, arena):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= TICK_TIME
        else:
            self.should_delete = True
            arena.troops.append(RebornPhoenix(self.side, self.position, self.level, self.cloned))

class RebornPhoenix(Troop):
    def __init__(self, side, position, level, cloned=False):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 696 * pow(1.1, level - 9),         # Hit points (Example value)
            h_d= 144 * pow(1.1, level - 9),          # Hit damage (Example value)
            h_s=1,          # Hit speed (Seconds per hit)
            l_t=0.5,            # First hit cooldown
            h_r=1.6,            # Hit range
            s_r=5.5,            # Sight Range
            g=False,           # Ground troop
            t_g_o=False,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=0.733,            # Deploy time
            m=2,            #mass
            c_r=0.6,        #collision radius
            p=position,               # Position (vector.Vector object)
            cloned=cloned
        ) 
        self.level = level
    
    def attack(self):
        return PhoenixAttackEntity(self.side, self.hit_damage, self.target.position, self.target)