import jungle_arena_cards
from abstract_classes import Troop
from abstract_classes import TICK_TIME
from abstract_classes import AttackEntity
from abstract_classes import RangedAttackEntity
from abstract_classes import TILES_PER_MIN
from goblin_stadium_cards import Goblin
import vector
import math
import copy

class EvolutionGoblinGiant(jungle_arena_cards.GoblinGiant):
    def __init__(self, side, position, level):
        super().__init__(side, position, level)
        self.evo = True
        self.spawn_timer = 1.8

    def tick_func(self, arena):
        if self.cur_hp < self.hit_points/2:
            if self.spawn_timer <= 0:
                self.spawn_timer = 1.8
                arena.troops.append(Goblin(self.side, self.position.added(vector.Vector(0, -self.collision_radius if self.side else self.collision_radius)), self.level))
            else:
                self.spawn_timer -= TICK_TIME

        v1 = vector.Vector(-0.2, 0.45).rotated(self.facing_dir)
        v2 = vector.Vector(-0.2, -0.45).rotated(self.facing_dir)
        self.backpack_goblins[0].position = self.position.added(v1)
        self.backpack_goblins[1].position = self.position.added(v2)

        if self.stun_timer <= 0:
            self.backpack_goblins[0].tick(arena)
            self.backpack_goblins[1].tick(arena)

class EvolutionDartGoblinPoisonAttackEntity(AttackEntity):
    SPLASH_RADIUS = 1.5
    def __init__(self, side, level, position):
        super().__init__(s=side, 
                         d=51 * pow(1.1, level - 11), 
                         v=0, 
                         l=4, 
                         i_p=position)
        self.small_damage = 51 * pow(1.1, level - 11) #1
        self.medium_damage = 115 * pow(1.1, level - 11) #4
        self.large_damage = 307 * pow(1.1, level - 11) #7
        self.stacks = 1
        self.tick_timer = 1.25
        self.display_size = self.SPLASH_RADIUS

    def increase_stack(self):
        self.stacks += 1
        self.duration = 4

    def detect_hits(self, arena): #override
        out = []
        for each in arena.troops + arena.buildings + arena.towers:
            if not each.invulnerable and each.side != self.side and (vector.distance(each.position, self.position) <= self.SPLASH_RADIUS + each.collision_radius):
                    out.append(each)
        return out

    def tick(self, arena):
        if self.stacks >= 7:
            self.damage = self.large_damage
        elif self.stacks >= 4:
            self.damage = self.medium_damage
        else:
            self.damage = self.medium_damage

        if self.tick_timer <= 0:
            hits = self.detect_hits(arena)
            for each in hits:
                each.damage(self.damage)
            self.tick_timer = 1
        else:
            self.tick_timer -= TICK_TIME

class EvolutionDartGoblinAttackEntity(RangedAttackEntity):
    def __init__(self, side, damage, position, target, parent):
        super().__init__(
            side=side, 
            damage=damage, 
            velocity=800*TILES_PER_MIN, 
            position=position, 
            target=target
        )
        self.parent = parent

    def tick(self, arena):
        self.tick_func(arena)
        hits = self.detect_hits(arena)
        if len(hits) > 0:
            for each in hits:
                each.damage(self.damage)
                if self.parent.target_poison is None:
                    obj = EvolutionDartGoblinPoisonAttackEntity(self.side, self.parent.level, self.target.position)
                    arena.active_attacks.append(obj)
                    self.parent.target_poison = obj
                else:
                    self.parent.target_poison.increase_stack()
            self.should_delete = True
        else:
            direction = None
            if self.homing:
                direction = vector.Vector(
                    self.target.position.x - self.position.x, 
                    self.target.position.y - self.position.y
                )
                direction.normalize()
                direction.scale(self.velocity)
                self.position.add(direction)

            else:
                self.position.add(self.move_vec)

    

class EvolutionDartGoblin(jungle_arena_cards.DartGoblin):
    def __init__(self, side, position, level):
        super().__init__(side, position, level)
        self.evo = True
        self.target_poison = None

    def tick_func(self, arena):
        if self.target is not None and self.target.cur_hp <= 0 or self.target is None:
            self.target_poison = None

    def attack(self):
        return EvolutionDartGoblinAttackEntity(self.side, self.hit_damage, self.position, self.target, self)
    
class EvolutionSkeletonBarrel(jungle_arena_cards.SkeletonBarrel):
    def __init__(self, side, position, level):
        super().__init__(side, position, level)
        self.evo = True
        self.cur_hp *= 1.25
        self.hit_points *= 1.25
        self.dropped_1 = False

    def tick_func(self, arena):
        if not self.dropped_1 and self.cur_hp <= 0.75 * self.hit_points:
            self.dropped_1 = True
            arena.troops.append(EvolutionSkeletonBarrelDeathBarrel(self.side, copy.deepcopy(self.position), self.level, self.cloned))

    def die(self, arena):
        delay = 0
        if not self.dropped_1:
            arena.troops.append(EvolutionSkeletonBarrelDeathBarrel(self.side, self.position, self.level, self.cloned))
            delay = 0.2

        second = EvolutionSkeletonBarrelDeathBarrel(self.side, self.position, self.level, self.cloned)
        second.deploy_time += delay
        arena.troops.append(second)
        self.cur_hp = -1
        arena.troops.remove(self)

    
class EvolutionSkeletonBarrelDeathBarrel(Troop):
    def __init__(self, side, position, level, cloned=False):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p=  float('inf'),         # Hit points (Example value)
            h_d= 243 * pow(1.1, level - 11),          # Hit damage (Example value)
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
            p=position,               # Position (vector.Vector object)
            cloned=cloned
        ) 
        self.level = level
        self.invulnerable=True
        self.targetable=False
        self.target=None
        self.collidable = False
        self.evo = True

    def on_deploy(self, arena):
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
            arena.troops.append(jungle_arena_cards.Skeleton(self.side, self.position.added(each), self.level, self.cloned))

        self.cur_hp = -1
        arena.troops.remove(self)

    def tick(self, arena):
        if self.deploy_time <= 0:
            arena.active_attacks.append(self.attack())
            self.should_delete = True
    
    def attack(self):
        return jungle_arena_cards.SkeletonBarrelDeathBarrelAttackEntity(self.side, self.hit_damage, self.position)