import spooky_town_cards
from abstract_classes import AttackEntity
from abstract_classes import RangedAttackEntity
from abstract_classes import MeleeAttackEntity
from abstract_classes import TILES_PER_MIN
from abstract_classes import Tower
from abstract_classes import Troop
from abstract_classes import TICK_TIME
import vector
import math
import copy

class EvolutionFirecrackerBigSparkAttackEntity(AttackEntity):
    SPLASH_RADIUS = 2.5
    def __init__(self, side, level, position):
        super().__init__(s=side, 
                         d=20 * pow(1.1, level - 1), 
                         v=0, 
                         l=3, 
                         i_p=position)
        self.ctd = 6 * pow(1.1, level - 1)
        self.tick_timer = 0.25
        self.display_size = self.SPLASH_RADIUS


    def detect_hits(self, arena): #override
        out = []
        for each in arena.troops + arena.buildings + arena.towers:
            if not each.invulnerable and each.side != self.side and (vector.distance(each.position, self.position) <= self.SPLASH_RADIUS + each.collision_radius):
                    out.append(each)
        return out

    def tick(self, arena):
        if self.tick_timer <= 0:
            hits = self.detect_hits(arena)
            for each in hits:
                if isinstance(each, Tower):
                    each.damage(self.ctd)
                else:
                    each.damage(self.damage)
            self.tick_timer = 0.25
        else:
            self.tick_timer -= TICK_TIME


class EvolutionFirecrackerSmallSparkAttackEntity(AttackEntity):
    SPLASH_RADIUS = 1.2
    def __init__(self, side, level, position):
        super().__init__(s=side, 
                         d=20 * pow(1.1, level - 1), 
                         v=0, 
                         l=2.5, 
                         i_p=position)
        self.ctd = 6 * pow(1.1, level - 1)
        self.tick_timer = 0.25
        self.display_size = self.SPLASH_RADIUS


    def detect_hits(self, arena): #override
        out = []
        for each in arena.troops + arena.buildings + arena.towers:
            if not each.invulnerable and each.side != self.side and (vector.distance(each.position, self.position) <= self.SPLASH_RADIUS + each.collision_radius):
                    out.append(each)
        return out

    def tick(self, arena):
        if self.tick_timer <= 0:
            hits = self.detect_hits(arena)
            for each in hits:
                if isinstance(each, Tower):
                    each.damage(self.ctd)
                else:
                    each.damage(self.damage)
            self.tick_timer = 0.25
        else:
            self.tick_timer -= TICK_TIME

class EvolutionFirecrackerExplosionAttackEntity(RangedAttackEntity):
    def __init__(self, side, damage, position, target, level):
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

        self.level = level

        self.set_move_vec()
    
    def detect_hits(self, arena):
        out = []
        for each in arena.troops + arena.towers + arena.buildings:
            if not each.side == self.side and not each.invulnerable and not each in self.has_hit and (vector.distance(each.position, self.position) < each.collision_radius + (0.65 if self.duration > 0.445 else 0.4)):
                out.append(each)
                self.has_hit.append(each)
        return out
    
    def cleanup_func(self, arena):
        if self.duration <= TICK_TIME:
            arena.active_attacks.append(EvolutionFirecrackerSmallSparkAttackEntity(self.side, self.level, self.position))

class EvolutionFirecrackerAttackEntity(RangedAttackEntity):
    def __init__(self, side, damage, position, target, level):
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
        self.level = level

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
            attacks.append(EvolutionFirecrackerExplosionAttackEntity(self.side, self.damage, self.position, target_position, self.level))

        attacks.append(EvolutionFirecrackerBigSparkAttackEntity(self.side, self.level, self.position))

        return attacks
    
    def cleanup_func(self, arena):
        if vector.distance(self.position, self.target) <= 0.1:
            arena.active_attacks.extend(self.spawn_explosion_entities())
            arena.active_attacks.remove(self)

class EvolutionFirecracker(spooky_town_cards.Firecracker):
    def __init__(self, side, position, level):
        super().__init__(side, position, level)
        self.evo = True

    def attack(self):
        self.kb(vector.Vector(math.cos(math.radians(self.facing_dir + 180)),
                         math.sin(math.radians(self.facing_dir + 180))).scaled(1.5))
        return EvolutionFirecrackerAttackEntity(self.side, self.hit_damage, self.position, copy.deepcopy(self.target.position), self.level)
    
class EvolutionElectroDragonAttackEntity(AttackEntity):
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
                if self.chain_count < self.MAX_CHAIN_HITS: #if can still chain
                    min_dist = float("inf")
                    minimum = None
                    for each in arena.towers + arena.buildings + arena.troops: #find new hits
                        if (isinstance(each, Tower) or not each.invulnerable) and each.side != self.side and vector.distance(each.position, self.chain_center) < self.CHAIN_RADIUS: # if different side
                            new = not any(each is h for h in self.has_hit)
                            if vector.distance(each.position, self.chain_center) < min_dist and new:
                                minimum = each
                                min_dist = vector.distance(each.position, self.chain_center)
                                
                    if not minimum is None:
                        self.target = minimum
                        self.has_hit.append(minimum)
                        self.should_delete = False
        else:
            direction = self.target.position.subtracted(self.position)
            direction.normalize()

            movement = direction.scaled(self.velocity)
            self.position.add(movement)

    def cleanup(self, arena): #also delete self if single target here in derived classes
        if self.should_delete:
            arena.active_attacks.append(EvolutionElectroDragonInfiniteAttackEntity(self.side, self.damage, self.position))
            arena.active_attacks.remove(self)

class EvolutionElectroDragonInfiniteAttackEntity(AttackEntity):
    CHAIN_RADIUS = 4
    def __init__(self, side, damage, position):
        super().__init__(
            s=side,
            d=damage,
            v=400*TILES_PER_MIN,
            l=float('inf'),
            i_p=copy.deepcopy(position)
        )
        self.target = None
        self.chain_center = None
        self.has_hit = None
        self.should_delete = False
        self.damage *= 0.66

    def find_initial(self, arena):
        minimum = None
        min_dist = float('inf')
        for each in arena.towers + arena.buildings + arena.troops: #find new hits
            if (isinstance(each, Tower) or not each.invulnerable) and each.side != self.side and vector.distance(each.position, self.position) < self.CHAIN_RADIUS: # if different side
                if vector.distance(each.position, self.position) < min_dist:
                    minimum = each
                    min_dist = vector.distance(each.position, self.position)

        self.target = minimum
        if self.target is not None:
            self.chain_center = self.target.position

    def detect_hits(self, arena):
        if vector.distance(self.position, self.target.position) < self.target.collision_radius:
            return [self.target]
        return []
            
    def tick(self, arena):
        if self.target is None: #if init
            self.find_initial(arena) #find init to chain to, set target
            if self.target is None: #
                self.should_delete = True #no in range, delete
                return #skip rest

        hits = self.detect_hits(arena)
        if len(hits) > 0:
                hits[0].damage(self.damage)
                self.should_delete = True
                self.chain_center = self.target.position
                min_dist = float("inf")
                minimum = None
                for each in arena.towers + arena.buildings + arena.troops: #find new hits
                    if (isinstance(each, Tower) or not each.invulnerable) and each.side != self.side and vector.distance(each.position, self.chain_center) < 4: # if different side
                        new = not each is self.has_hit
                        if new and vector.distance(each.position, self.chain_center) < min_dist:
                            minimum = each
                            min_dist = vector.distance(each.position, self.chain_center)
                            
                if not minimum is None:
                    self.target = minimum
                    self.has_hit = minimum
                    self.should_delete = False
        else:
            direction = self.target.position.subtracted(self.position)
            direction.normalize()

            movement = direction.scaled(self.velocity)
            self.position.add(movement)

    def cleanup(self, arena): #also delete self if single target here in derived classes
        if self.should_delete:
            arena.active_attacks.remove(self)


class EvolutionElectroDragon(spooky_town_cards.ElectroDragon):
    def __init__(self, side, position, level):
        super().__init__(side, position, level)
        self.evo = True

    def attack(self):
        return EvolutionElectroDragonAttackEntity(self.side, self.hit_damage, self.position, self.target)
    
class EvolutionWallBreakerRunnerAttackEntity(MeleeAttackEntity):
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
        self.display_size = self.SPLASH_RADIUS
    
    def detect_hits(self, arena):
        hits = []
        for each in arena.towers + arena.buildings + arena.troops:
            if each.side != self.side and (isinstance(each, Tower) or (each.ground and not each.invulnerable)): # if different side
                if vector.distance(each.position, self.position) <= each.collision_radius + self.SPLASH_RADIUS:
                    hits.append(each)
        return hits
  
class EvolutionWallBreakerRunner(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 103 * pow(1.1, level - 6),         # Hit points (Example value)
            h_d= 123 * pow(1.1, level - 6),          # Hit damage (Example value)
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
        self.evo = True
        self.invincibility_timer = 0.1 #avoid splash
        self.invulnerable = True

    def cleanup_func(self, arena):
        if self.invincibility_timer > 0:
            self.invincibility_timer -= TICK_TIME
        else:
            self.invulnerable = False
    
    def attack(self):
        self.should_delete = True
        return EvolutionWallBreakerRunnerAttackEntity(self.side, self.hit_damage, self.position, self.target)
    
class EvolutionWallBreakerDeathAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 0.5
    COLLISION_RADIUS = 0.4
    SPLASH_RADIUS = 1.5
    def __init__(self, side, damage, ctd, position, target):
        super().__init__(
            side=side,
            damage=damage,
            position=position,
            target=target
            )
        self.ctd = ctd
        self.display_size = self.SPLASH_RADIUS
    
    def detect_hits(self, arena):
        hits = []
        for each in arena.towers + arena.buildings + arena.troops:
            if each.side != self.side and (isinstance(each, Tower) or (each.ground and not each.invulnerable)): # if different side
                if vector.distance(each.position, self.position) <= each.collision_radius + self.SPLASH_RADIUS:
                    hits.append(each)
        return hits
    
    def tick(self, arena):
        hits = self.detect_hits(arena)
        if len(hits) > 0:
            for each in hits:
                if isinstance(each, Tower):
                    each.damage(self.ctd)
                else:
                    each.damage(self.damage)
            self.should_delete = True

class EvolutionWallBreaker(spooky_town_cards.WallBreaker):
    def __init__(self, side, position, level):
        super().__init__(side, position, level)
        self.evo = True
        self.death_ctd = 182 * pow(1.1, level - 6)

    def attack(self):
        self.should_delete = True

    def die(self, arena):
        arena.active_attacks.append(EvolutionWallBreakerDeathAttackEntity(self.side, self.hit_damage, self.death_ctd, self.position, self.target))
        arena.troops.append(EvolutionWallBreakerRunner(self.side, self.position, self.level))
        return super().die(arena)