from abstract_classes import RangedAttackEntity
from abstract_classes import MeleeAttackEntity
from abstract_classes import AttackEntity
from abstract_classes import Troop
from abstract_classes import Tower
from abstract_classes import Building
from abstract_classes import Spell
from abstract_classes import TILES_PER_MIN
from abstract_classes import TICK_TIME
from bone_pit_cards import Skeleton
from barbarian_bowl_cards import Barbarian
from goblin_stadium_cards import SpearGoblin
import vector
import copy
import math

class BeserkerAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 0.8
    COLLISION_RADIUS = 0.5
    def __init__(self, side, damage, position, target):
        super().__init__(
            side, 
            damage, 
            position, 
            target
        )

class Beserker(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 325 * pow(1.1, level - 1),         # Hit points (Example value)
            h_d= 40 * pow(1.1, level - 1),          # Hit damage (Example value)
            h_s=0.5,          # Hit speed (Seconds per hit)
            l_t=0.3,            # First hit cooldown
            h_r=0.8,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=120*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=2,            #mass
            c_r=0.5,        #collision radius
            p=position               # Position (vector.Vector object)
        )
        self.level = level
    def attack(self):
        return BeserkerAttackEntity(self.side, self.hit_damage, self.position, self.target)

class DartGoblinAttackEntity(RangedAttackEntity):
    def __init__(self, side, damage, velocity, position, target):
        super().__init__(
            side=side, 
            damage=damage, 
            velocity=800*TILES_PER_MIN, 
            position=position, 
            target=target
        )

class DartGoblin(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 123 * pow(1.1, level - 3),         # Hit points (Example value)
            h_d= 62 * pow(1.1, level - 3),          # Hit damage (Example value)
            h_s=0.7,          # Hit speed (Seconds per hit)
            l_t=0.35,            # First hit cooldown
            h_r=6.5,            # Hit range
            s_r=7.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=False,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=120*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=3,            #mass
            c_r=0.5,        #collision radius
            p=position               # Position (vector.Vector object)
        )
        self.level = level
    def attack(self):
        return DartGoblinAttackEntity(self.side, self.hit_damage, self.position, self.target)
    
class SkeletonBarrel(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 208 * pow(1.1, level - 1),         # Hit points
            h_d= 52 * pow(1.1, level - 1),          # Hit damage (charge is 2x)
            h_s=0.3,          # Hit speed (Seconds per hit)
            l_t=0.2,            # First hit cooldown
            h_r=0.35,            # Hit range
            s_r=7.7,            # Sight Range
            g=False,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=True,        # Not tower-only
            m_s=90*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=7,            #mass
            c_r=0.5,        #collision radius
            p=position               # Position (vector.Vector object)
        ) 
        self.level = level

        self.sprite_path = "sprites/skeletonbarrel/skeletonbarrel_full.png"
    
    def attack(self):
        self.should_delete = True
    
    def die(self, arena):
        arena.troops.append(SkeletonBarrelDeathBarrel(self.side, self.position, self.level))
        arena.troops.remove(self)
        self.cur_hp = -1

class SkeletonBarrelDeathBarrelAttackEntity(AttackEntity):
    DAMAGE_RADIUS = 2
    def __init__(self, side, damage, position):
        super().__init__(
            s=side,
            d=damage,
            v=0,
            l=0.25,
            i_p=copy.deepcopy(position)
        )
        self.display_size = SkeletonBarrelDeathBarrelAttackEntity.DAMAGE_RADIUS
        self.has_hit = []

    

    def detect_hits(self, arena):
        hits = []
        for each in arena.towers + arena.buildings + arena.troops:
            if each.side != self.side and (isinstance(each, Tower) or not each.invulnerable): # if different side
                if vector.distance(self.position, each.position) < SkeletonBarrelDeathBarrelAttackEntity.DAMAGE_RADIUS + each.collision_radius:
                    hits.append(each)
        return hits
            
    def tick(self, arena):
        hits = self.detect_hits(arena)
        for each in hits:
            new = not any(each is h for h in self.has_hit)
            if (new):
                each.damage(self.damage)
                if isinstance(each, Troop):
                    vec = each.position.subtracted(self.position)
                    vec.normalize() #scale 1, useless
                    each.kb(vec)
                self.has_hit.append(each)

class SkeletonBarrelDeathBarrel(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p=  float('inf'),         # Hit points (Example value)
            h_d= 52 * pow(1.1, level - 1),          # Hit damage (Example value)
            h_s=0,          # Hit speed (Seconds per hit)
            l_t=0,            # First hit cooldown
            h_r=0,            # Hit range
            s_r=0,            # Sight Range
            g=True,           # Ground troop
            t_g_o=False,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=0,          # Movement speed 
            d_t=1.1,            # Deploy time
            m=float('inf'),            #mass
            c_r=0.5,        #collision radius
            p=position               # Position (vector.Vector object)
        ) 
        self.level = level
        self.invulnerable=True
        self.targetable=False
        self.target=None
        self.collidable = False

    def die(self, arena):
        flip = 1 if self.side else -1
        radius = 1.48
        angles = [(2 * math.pi * k / 7) + (math.pi / 2) for k in range(7)]
        positions = [vector.Vector(radius * math.cos(a), radius * math.sin(a) * flip) for a in angles]
        for each in positions:
            arena.troops.append(Skeleton(self.side, self.position.added(each), self.level))

        self.cur_hp = -1
        arena.troops.remove(self)

    def tick(self, arena):
        if self.deploy_time <= 0:
            arena.active_attacks.append(self.attack())
            self.should_delete = True
    
    def attack(self):
        return SkeletonBarrelDeathBarrelAttackEntity(self.side, self.hit_damage, self.position)

class BarbarianHut(Building):
    SPAWN_INTERVAL = 0.5
    def __init__(self, side, position, level):
        super().__init__(
            s=side,
            h_p=550 * pow(1.1, level - 3),
            h_d = 0,
            h_s = 14,
            l_t = 0,
            h_r = 0,
            s_r = 0,
            g = True,
            t_g_o = True,
            t_o = False,
            l=30,
            d_t=1,
            c_r=1,
            d_s_c=1,
            d_s=Barbarian,
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
                arena.troops.append(Barbarian(self.side, self.position.added(front), self.level))
                self.next_spawn = 0.5
                self.remaining_spawn_count = 2
                self.attack_cooldown = self.hit_speed
        
        if self.remaining_spawn_count > 0 and self.next_spawn <= 0: #remaining 2 gobs
            front = vector.Vector(0, 1.5) if self.side else vector.Vector(0, -1.5)
            arena.troops.append(Barbarian(self.side, self.position.added(front), self.level))
            self.remaining_spawn_count -= 1 #one less spawn
            if self.remaining_spawn_count > 0: #if still spawns left
                self.next_spawn = 0.5 #reset timer
            elif not self.next_spawn is None:
                self.next_spawn = None #no more
                self.remaining_spawn_count = 0 #no more

class Poison(Spell):
    def __init__(self, side, target, level):
        super().__init__(
            s=side,
            d=57 * pow(1.1, level - 6),
            c_t_d=18 * pow(1.1, level - 6),
            w=8,
            t=1,
            kb=0,
            r=3.5,
            v=0,
            tar=target
        )
        self.pulse_time = 0.25

    def passive_effect(self, each):
        if isinstance(each, Troop):
            each.move_slow(0.15, 0.25)

class GoblinGiantAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 1.2
    COLLISION_RADIUS = 0.75
    def __init__(self, side, damage, position, target):
        super().__init__(
            side, 
            damage, 
            position, 
            target
        )

class GoblinGiant(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 1967 * pow(1.1, level - 6),         # Hit points (Example value)
            h_d= 110 * pow(1.1, level - 6),          # Hit damage (Example value)
            h_s=1.5,          # Hit speed (Seconds per hit)
            l_t=0.7,            # First hit cooldown
            h_r=1.2,            # Hit range
            s_r=7.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=False,       # Targets ground-only
            t_o=True,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=18,            #mass
            c_r=0.75,        #collision radius
            p=position               # Position (vector.Vector object)
        )
        self.level = level
        self.ticks_per_frame = 6
        self.walk_cycle_frames = 6
        class_name = self.__class__.__name__.lower()
        self.can_kb = False

        self.sprite_path = f"sprites/{class_name}/{class_name}_0.png"

        v1 = vector.Vector(-0.2, 0.45).rotated(self.facing_dir)
        v2 = vector.Vector(-0.2, -0.45).rotated(self.facing_dir)

        self.backpack_goblins = [BackpackSpearGoblin(self.side, self.position.added(v1), self.level),
                                 BackpackSpearGoblin(self.side, self.position.added(v2), self.level)]
        

    def tick_func(self, arena):
        v1 = vector.Vector(-0.2, 0.45).rotated(self.facing_dir)
        v2 = vector.Vector(-0.2, -0.45).rotated(self.facing_dir)
        self.backpack_goblins[0].position = self.position.added(v1)
        self.backpack_goblins[1].position = self.position.added(v2)

        self.backpack_goblins[0].tick(arena)
        self.backpack_goblins[1].tick(arena)

    def cleanup_func(self, arena):
        self.backpack_goblins[0].cleanup(arena)
        self.backpack_goblins[1].cleanup(arena)

    def die(self, arena):
        v1 = vector.Vector(-0.2, 0.45).rotated(self.facing_dir)
        v2 = vector.Vector(-0.2, -0.45).rotated(self.facing_dir)
        self.cur_hp = -1
        arena.troops.append(SpearGoblin(self.side, self.position.added(v1), self.level))
        arena.troops.append(SpearGoblin(self.side, self.position.added(v2), self.level))
        arena.troops.remove(self)

    def attack(self):
        return GoblinGiantAttackEntity(self.side, self.hit_damage, self.position, self.target)
    
class BackpackSpearGoblinAttackEntity(RangedAttackEntity):
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side, 
            damage=damage, 
            velocity=500*TILES_PER_MIN, 
            position=position, 
            target=target
        )
    
class BackpackSpearGoblin(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 52 * pow(1.1, level - 1),         # Hit points (Example value)
            h_d= 32 * pow(1.1, level - 1),          # Hit damage (Example value)
            h_s=1.5,          # Hit speed (Seconds per hit)
            l_t=1,            # First hit cooldown
            h_r=5.5,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=False,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=120*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=1,            #mass
            c_r=0.5,        #collision radius
            p=position               # Position (vector.Vector object)
        ) 
        self.level = level
        self.walk_cycle_frames = 8
        class_name = self.__class__.__name__.lower()
        self.sprite_path = f"sprites/{class_name}/{class_name}_{self.walk_cycle_cur}.png"

    def move(self, arena):
        if self.target is not None:
            return vector.distance(self.target.position, self.position) < self.collision_radius + self.target.collision_radius + self.hit_range

    def attack(self):
        return BackpackSpearGoblinAttackEntity(self.side, self.hit_damage, self.position, self.target)
    
class BarbarianBarrelAttackEntity(AttackEntity):
    def __init__(self, side, damage, pos):
        super().__init__(
            s=side, 
            d=damage, 
            v=200 * TILES_PER_MIN, 
            l=1.35, 
            i_p=pos)
        self.has_hit = []
        
    def detect_hits(self, arena):
        hits = []
        for each in arena.troops + arena.buildings + arena.towers:
            if each.side != self.side and each.ground and not each.invulnerable and not each in self.has_hit:
                if each.position.x < self.position.x + 1.3 and each.position.x > self.position.x - 1.3 and each.position.y < self.position.y + 0.6 and each.position.y > self.position.y - 0.6:
                    hits.append(each)
        return hits
    
    def tick(self, arena):
        self.position.y += self.velocity if self.side else -self.velocity
        hits = self.detect_hits(arena)
        for each in hits:
            new = not each in self.has_hit
            if (new):
                each.damage(self.damage)
                self.apply_effect(each)
                self.has_hit.append(each)
    
class BarbarianBarrel(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p = float('inf'),         # Hit points (Example value)
            h_d= 151 * pow(1.1, level - 6),          # Hit damage (Example value)
            h_s=0.1,          # Hit speed (Seconds per hit)
            l_t=0.1,            # First hit cooldown
            h_r=5.5,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=200*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=1,            #mass
            c_r=1.3,        #collision radius
            p=position               # Position (vector.Vector object)
        )
        self.level = level
        self.targetable = False
        self.invulnerable = True
        self.timer = 1.35

        self.collideable = False

        self.first = True

    def move(self, arena):
        self.position.y += self.move_speed if self.side else -self.move_speed
    
    def tick(self, arena):
        self.timer -= TICK_TIME
        self.move(arena)
        if self.first:
            arena.active_attacks.append(self.attack())
            self.first = False
        if self.timer <= 0:
            self.should_delete = True
    
    def die(self, arena):
        self.cur_hp = -1
        arena.troops.append(Barbarian(self.side, self.position, self.level))
        arena.troops.remove(self)
        

    def attack(self):
        return BarbarianBarrelAttackEntity(self.side, self.hit_damage, copy.deepcopy(self.position))