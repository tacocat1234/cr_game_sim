from abstract_classes import AttackEntity
from abstract_classes import Troop
from abstract_classes import Building
from abstract_classes import TILES_PER_MIN
from abstract_classes import TICK_TIME
import vector
import copy
import random

class SpearGoblinAttackEntity(AttackEntity):
    def __init__(self, side, damage, position, target):
        super().__init__(
            s=side,
            d=damage,
            v=500*TILES_PER_MIN,
            l=float('inf'),
            i_p=copy.deepcopy(position)
        )
        self.target = target
        self.should_delete = False

    def detect_hits(self, arena):
        if (vector.distance(self.target.position, self.position) < self.target.collision_radius):
            return [self.target] # has hit
        else:
            return [] #hasnt hit yet
            
    def tick(self, arena):
        hits = self.detect_hits(arena)
        if len(hits) > 0:
            hits[0].damage(self.damage)
            self.should_delete = True
        else:
            direction = vector.Vector(
                self.target.position.x - self.position.x, 
                self.target.position.y - self.position.y
            )
            direction.normalize()

            movement = direction.scaled(self.velocity)
            self.position.add(movement)

    def cleanup(self, arena):
        if self.should_delete:
            arena.active_attacks.remove(self)
    
class SpearGoblin(Troop):
    def __init__(self, side, position, level, cloned=False):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 52 * pow(1.1, level - 1),         # Hit points (Example value)
            h_d= 32 * pow(1.1, level - 1),          # Hit damage (Example value)
            h_s=1.7,          # Hit speed (Seconds per hit)
            l_t=1.2,            # First hit cooldown
            h_r=5.5,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
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
        self.walk_cycle_frames = 8
        class_name = self.__class__.__name__.lower()
        self.sprite_path = f"sprites/{class_name}/{class_name}_{self.walk_cycle_cur}.png"
    
    def attack(self):
        return SpearGoblinAttackEntity(self.side, self.hit_damage, self.position, self.target)

class GoblinAttackEntity(AttackEntity):
    HIT_RANGE = 0.5
    COLLISION_RADIUS = 0.5
    def __init__(self, side, damage, position, target):
        super().__init__(
            s=side,
            d=damage,
            v=0,
            l=0.5,
            i_p=position
            )
        self.target = target
        self.should_delete = False
    
    def detect_hits(self, arena):
        
        if (vector.distance(self.target.position, self.position) <= GoblinAttackEntity.HIT_RANGE + GoblinAttackEntity.COLLISION_RADIUS + self.target.collision_radius): #within hitrange of knight
            return [self.target]
        else:
            return [] #theoretically should never trigger, when attack, should always be in range unless very strange circumstances
        
    def tick(self, arena):
        hits = self.detect_hits(arena)
        if len(hits) > 0:
            hits[0].damage(self.damage)
            self.should_delete = True

    def cleanup(self, arena): #also delete self if single target here in derived classes
        self.duration -= TICK_TIME
        if self.duration <= 0:
            arena.active_attacks.remove(self)
        if self.should_delete:
            arena.active_attacks.remove(self)
        
            
class Goblin(Troop):
    def __init__(self, side, position, level, cloned=False):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 79 * pow(1.1, level - 1),         # Hit points (Example value)
            h_d= 47 * pow(1.1, level - 1),          # Hit damage (Example value)
            h_s=1.1,          # Hit speed (Seconds per hit)
            l_t=0.7,            # First hit cooldown
            h_r=0.5,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=120*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=2,            #mass
            c_r=0.5,        #collision radius
            p=position,               # Position (vector.Vector object)
            cloned=cloned
        )
        self.level = level
    def attack(self):
        return GoblinAttackEntity(self.side, self.hit_damage, self.position, self.target)

class GoblinBrawlerAttackEntity(AttackEntity):
    HIT_RANGE = 0.8
    COLLISION_RADIUS = 0.5
    def __init__(self, side, damage, position, target):
        super().__init__(
            s=side,
            d=damage,
            v=0,
            l=0.5,
            i_p=position
            )
        self.target = target
        self.should_delete = False
    
    def detect_hits(self, arena):
        
        if (vector.distance(self.target.position, self.position) <= GoblinBrawlerAttackEntity.HIT_RANGE + GoblinBrawlerAttackEntity.COLLISION_RADIUS + self.target.collision_radius): #within hitrange of knight
            return [self.target]
        else:
            return [] #theoretically should never trigger, when attack, should always be in range unless very strange circumstances
        
    def tick(self, arena):
        hits = self.detect_hits(arena)
        if len(hits) > 0:
            hits[0].damage(self.damage)
            self.should_delete = True

    def cleanup(self, arena): #also delete self if single target here in derived classes
        self.duration -= TICK_TIME
        if self.duration <= 0:
            arena.active_attacks.remove(self)
        if self.should_delete:
            arena.active_attacks.remove(self)
        
            
class GoblinBrawler(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 485 * pow(1.1, level - 3),         # Hit points (Example value)
            h_d= 159 * pow(1.1, level - 3),          # Hit damage (Example value)
            h_s=1.1,          # Hit speed (Seconds per hit)
            l_t=0.9,            # First hit cooldown
            h_r=0.8,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=90*TILES_PER_MIN,          # Movement speed 
            d_t=0.4,            # Deploy time
            m=2,            #mass
            c_r=0.5,        #collision radius
            p=position               # Position (vector.Vector object)
        )
        self.level = level
    def attack(self):
        return GoblinBrawlerAttackEntity(self.side, self.hit_damage, self.position, self.target)

class GoblinCage(Building):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,
            h_p=400 * pow(1.1, level - 3),
            h_d = 0,
            h_s = float("inf"),
            l_t = 0,
            h_r = 0,
            s_r = 0,
            g = True,
            t_g_o = True,
            t_o = False,
            l=20,
            d_t=1,
            c_r=1,
            d_s_c=1,
            d_s=GoblinBrawler,
            p=position
        )
        self.level = level

class OldGoblinHut(Building):
    SPAWN_INTERVAL = 0.5
    def __init__(self, side, position, level):
        super().__init__(
            s=side,
            h_p=400 * pow(1.1, level - 3),
            h_d = 0,
            h_s = 10,
            l_t = 0,
            h_r = 0,
            s_r = 0,
            g = True,
            t_g_o = True,
            t_o = False,
            l=29,
            d_t=1,
            c_r=1,
            d_s_c=1,
            d_s=SpearGoblin,
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
        if self.preplace or self.deploy_time > 0:
            return
        if self.stun_timer <= 0:
            if self.attack_cooldown <= 0: #if wave time
                front = vector.Vector(random.random()/4 - 0.125, 1.5) if self.side else vector.Vector(random.random()/4 - 0.125, -1.5)
                newGob = SpearGoblin(self.side, self.position.added(front), self.level)
                newGob.deploy_time = 0
                arena.troops.append(newGob)
                self.next_spawn = 0.5
                self.remaining_spawn_count = 2
                self.attack_cooldown = self.hit_speed
        
        if self.remaining_spawn_count > 0 and self.next_spawn <= 0: #remaining 2 gobs
            front = vector.Vector(random.random()/4 - 0.125, 1.5) if self.side else vector.Vector(random.random()/4 - 0.125, -1.5)
            newGob = SpearGoblin(self.side, self.position.added(front), self.level)
            newGob.deploy_time = 0
            arena.troops.append(newGob)
            self.remaining_spawn_count -= 1 #one less spawn
            if self.remaining_spawn_count > 0: #if still spawns left
                self.next_spawn = 0.5 #reset timer
            elif not self.next_spawn is None:
                self.next_spawn = None #no more
                self.remaining_spawn_count = 0 #no more

class GoblinHut(Building):
    SPAWN_INTERVAL = 0.5
    def __init__(self, side, position, level):
        super().__init__(
            s=side,
            h_p=617 * pow(1.1, level - 3),
            h_d = 0,
            h_s = 1.8,
            l_t = 0,
            h_r = 7,
            s_r = 7,
            g = True,
            t_g_o = False,
            t_o = False,
            l=30,
            d_t=1,
            c_r=1,
            d_s_c=1,
            d_s=SpearGoblin,
            p=position
        )
        self.level = level
    
    def tick(self, arena):
        if self.preplace or self.deploy_time > 0:
            return
        
        if self.target is None or self.target.cur_hp <= 0 or not self.target.targetable:
            self.update_target(arena)
        
        if self.stun_timer <= 0 and self.target is not None and self.attack_cooldown <= 0:
            front = vector.Vector(random.random()/4 - 0.125, 1.5) if self.side else vector.Vector(random.random()/4 - 0.125, -1.5)
            newGob = SpearGoblin(self.side, self.position.added(front), self.level)
            newGob.deploy_time = 0
            arena.troops.append(newGob)
            self.attack_cooldown = self.hit_speed
