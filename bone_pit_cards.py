from abstract_classes import AttackEntity
from abstract_classes import MeleeAttackEntity
from abstract_classes import Troop
from abstract_classes import Building
from abstract_classes import Tower
from abstract_classes import TILES_PER_MIN
from abstract_classes import TICK_TIME
import vector
import copy
import random

class SkeletonAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 0.5
    COLLISION_RADIUS = 0.5
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            position=position,
            target=target
            )
        
            
class Skeleton(Troop):
    def __init__(self, side, position, level, cloned=False):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 32 * pow(1.1, level - 1),         # Hit points (Example value)
            h_d= 32 * pow(1.1, level - 1),          # Hit damage (Example value)
            h_s=1,          # Hit speed (Seconds per hit)
            l_t=0.5,            # First hit cooldown
            h_r=0.5,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=90*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=1,            #mass
            c_r=0.5,        #collision radius
            p=position,               # Position (vector.Vector object)
            cloned=cloned
        )
        self.level = level

        self.ticks_per_frame = 12
        self.walk_cycle_frames = 4
        class_name = self.__class__.__name__.lower()
        self.sprite_path = f"sprites/{class_name}/{class_name}_0.png"

    def attack(self):
        return SkeletonAttackEntity(self.side, self.hit_damage, self.position, self.target)
    
class BomberAttackEntity(AttackEntity):
    def __init__(self, side, damage, position, target_pos):
        super().__init__(
            s=side,
            d=damage,
            v=400*TILES_PER_MIN,
            l=float('inf'),
            i_p=copy.deepcopy(position)
        )
        self.target_pos = target_pos
        self.exploded = False
        self.has_hit = []

    def detect_hits(self, arena):
        hits = []
        if self.exploded:
            for each in arena.towers + arena.buildings + arena.troops:
                if each.side != self.side and (isinstance(each, Tower) or (each.ground and not each.invulnerable)): # if different side
                    if vector.distance(self.position, each.position) < 1.5 + each.collision_radius:
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
            direction = self.target_pos.subtracted(self.position)
            direction.normalize()

            movement = direction.scaled(self.velocity)
            self.position.add(movement)
            
            if vector.distance(self.position, self.target_pos) < 0.25:
                self.display_size = 1.5
                self.duration =  0.1
                self.exploded = True
    
class Bomber(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 130 * pow(1.1, level - 1),         # Hit points (Example value)
            h_d= 87 * pow(1.1, level - 1),          # Hit damage (Example value)
            h_s=1.8,          # Hit speed (Seconds per hit)
            l_t=1.6,            # First hit cooldown
            h_r=4.5,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=4,            #mass
            c_r=0.5,        #collision radius
            p=position               # Position (vector.Vector object)
        ) 
        self.level = level
        self.walk_cycle_frames = 4
        class_name = self.__class__.__name__.lower()
        self.sprite_path = f"sprites/{class_name}/{class_name}_0.png"
    
    def attack(self):
        return BomberAttackEntity(self.side, self.hit_damage, self.position, copy.deepcopy(self.target.position))
    

class Tombstone(Building):
    SPAWN_INTERVAL = 0.5
    def __init__(self, side, position, level):
        super().__init__(
            s=side,
            h_p=250 * pow(1.1, level - 3),
            h_d = 0,
            h_s = 3.5,
            l_t = 0,
            h_r = 0,
            s_r = 0,
            g = True,
            t_g_o = True,
            t_o = False,
            l=30,
            d_t=1,
            c_r=1,
            d_s_c=4,
            d_s=Skeleton,
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
        if self.preplace:
            return
        if self.stun_timer <= 0:
            if self.attack_cooldown <= 0: #attack code
                front = vector.Vector(0, 1.5) if self.side else vector.Vector(0, -1.5)
                arena.troops.append(Skeleton(self.side, self.position.added(front), self.level))
                self.next_spawn = 0.5
                self.remaining_spawn_count = 1
                self.attack_cooldown = self.hit_speed
        
        if self.remaining_spawn_count > 0 and self.next_spawn <= 0: #remaining skeleton
            front = vector.Vector(0, 1.5) if self.side else vector.Vector(0, -1.5)
            arena.troops.append(Skeleton(self.side, self.position.added(front), self.level))
            self.remaining_spawn_count -= 1 #one less spawn
            if self.remaining_spawn_count > 0: #if still spawns left
                self.next_spawn = 0.5 #reset timer
            elif not self.next_spawn is None:
                self.next_spawn = None #no more
                self.remaining_spawn_count = 0 #no more

class ValkyrieAttackEntity(AttackEntity):
    HIT_RANGE = 2.0
    COLLISION_RADIUS = 0.5
    def __init__(self, side, damage, position, target):
        super().__init__(
            s=side,
            d=damage,
            v=0,
            l=0.25,
            i_p=position
            )
        self.target = target
        self.has_hit = []
        self.display_size = ValkyrieAttackEntity.HIT_RANGE
    
    def detect_hits(self, arena):
        hits = []
        for each in arena.towers + arena.buildings + arena.troops:
            if each.side != self.side and (isinstance(each, Tower) or (each.ground and not each.invulnerable)): # if different side
                if vector.distance(self.position, each.position) < ValkyrieAttackEntity.HIT_RANGE + ValkyrieAttackEntity.COLLISION_RADIUS + each.collision_radius:
                    hits.append(each)
        return hits
        
    def tick(self, arena):
        hits = self.detect_hits(arena)
        for each in hits:
            new = True
            for h in self.has_hit:
                if each is h:
                    new = False
                    break
            if (new):
                each.damage(self.damage)
                self.has_hit.append(each)

    def cleanup(self, arena):
        self.duration -= TICK_TIME
        if self.duration <= 0:
            arena.active_attacks.remove(self)
        
            
class Valkyrie(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 900 * pow(1.1, level - 3),         # Hit points (Example value)
            h_d= 126 * pow(1.1, level - 3),          # Hit damage (Example value)
            h_s=1.5,          # Hit speed (Seconds per hit)
            l_t=1.4,            # First hit cooldown
            h_r=1.2,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=5,            #mass
            c_r=0.5,        #collision radius
            p=position               # Position (vector.Vector object)
        )
        self.level = level
    def attack(self):
        return ValkyrieAttackEntity(self.side, self.hit_damage, self.position, self.target)