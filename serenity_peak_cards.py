from abstract_classes import RangedAttackEntity
from abstract_classes import MeleeAttackEntity
from abstract_classes import AttackEntity
from abstract_classes import Troop
from abstract_classes import Building
from abstract_classes import Tower
from abstract_classes import Spell
from royal_arena_cards import RoyalRecruit
from goblin_stadium_cards import Goblin
from builders_workshop_cards import Bat
from abstract_classes import TILES_PER_MIN
from abstract_classes import TICK_TIME
from abstract_classes import same_sign
from abstract_classes import on_bridge
import vector
import copy
import math


class RoyalDelivery(Spell):
    def __init__(self, side, target, level):
        super().__init__(
            s=side,
            d=171 * pow(1.1, level - 1),
            c_t_d=0,
            w=1,
            t=0,
            kb=0,
            r=3,
            v=0,
            tar=target
        )
        self.delay_time = 2.05
        self.level = level

    def tick(self, arena):
        if self.preplace:
            return
        if self.delay_time <= 0:
            self.sprite_path = f"sprites/{self.class_name}/{self.class_name}_hit.png"
            hits = self.detect_hits(arena)
            for each in hits:
                each.damage(self.damage)
            self.should_delete = True
    
    def cleanup(self, arena):
        if self.preplace:
            return
        
        self.delay_time -= TICK_TIME

        if self.should_delete:
            rr = RoyalRecruit(self.side, self.position, self.level)
            rr.deploy_time = 0.25
            arena.troops.append(rr)
            arena.spells.remove(self) #delete
        self.display_duration -= TICK_TIME

class Rage(Spell):
    def __init__(self, side, target, level):
        super().__init__(
            s=side,
            d=120 * pow(1.1, level - 6),
            c_t_d=36 * pow(1.1, level - 6),
            w=1,
            t=0,
            kb=0,
            r=3,
            v=0,
            tar=target
        )
        self.display_duration = 6
        self.pulse_time = 0.3
        self.pulse_timer = 0
    
    def passive_detect_hits(self, arena):
        out = []
        for each in arena.troops + arena.buildings + arena.towers:
            if each.side == self.side and (vector.distance(each.position, self.position) <= self.radius + each.collision_radius):
                out.append(each)
        return out 

    def passive_effect(self, each):
        each.rage()

class LumberjackAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 0.7
    COLLISION_RADIUS = 0.5
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            position=position,
            target=target
            )
        
class Lumberjack(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 1060 * pow(1.1, level - 9),         # Hit points (Example value)
            h_d= 200 * pow(1.1, level - 9),          # Hit damage (Example value)
            h_s=0.8,          # Hit speed (Seconds per hit)
            l_t=0.4,            # First hit cooldown
            h_r=0.7,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=False,        # not tower-only
            m_s=120*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=4,            #mass
            c_r=0.5,        #collision radius
            p=position               # Position (vector.Vector object)
        ) 
        self.level = level
    
    def attack(self):
        return LumberjackAttackEntity(self.side, self.hit_damage, self.position, self.target)

    def die(self, arena):
        arena.spells.append(Rage(self.side, self.position, self.level))
        super().die(arena)

class NightWitchAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 1.6
    COLLISION_RADIUS = 0.5
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            position=position,
            target=target
            )

class NightWitch(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 750 * pow(1.1, level - 9),         # Hit points (Example value)
            h_d= 260 * pow(1.1, level - 9),          # Hit damage (Example value)
            h_s=1.3,          # Hit speed (Seconds per hit)
            l_t=0.55,            # First hit cooldown
            h_r=1.6,            # Hit range
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
        self.spawn_time = 5
        self.spawn_timer = 1
    
    def tick(self, arena):
        if self.preplace:
            return

        if self.kb_timer > 0:
            self.kb_timer -= TICK_TIME #akward but better to keep it contained
            self.kb_tick()
        else:
            self.kb_vector = None
        
        self.spawn_timer -= TICK_TIME

        #update arena before
        if self.stun_timer <= 0:
            if self.deploy_time <= 0:
                if self.target is None or self.target.cur_hp <= 0:
                    self.update_target(arena)
                if self.move(arena) and self.attack_cooldown <= 0: #move, then if within range, attack
                    atk = self.attack()
                    if isinstance(atk, list) and len(atk) > 0:
                        arena.active_attacks.extend(atk)
                    elif not atk is None:
                        arena.active_attacks.append(self.attack())
                    self.attack_cooldown = self.hit_speed
                if self.spawn_timer <= 0:
                    self.spawn(arena)
                    self.spawn_timer = self.spawn_time

    def spawn(self, arena):
        arena.troops.append(Bat(self.side, self.position.added(vector.Vector(1.5, 0)), self.level, self.cloned))
        arena.troops.append(Bat(self.side, self.position.added(vector.Vector(-1.5, 0)), self.level, self.cloned))

    def die(self, arena):
        arena.troops.append(Bat(self.side, self.position, self.level, self.cloned))
        super().die(arena)

    def attack(self):
        return NightWitchAttackEntity(self.side, self.hit_damage, self.position, self.target)

class ElixirGolemAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 0.8
    COLLISION_RADIUS = 0.6
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            position=position,
            target=target
            )

class ElixirGolem(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 740 * pow(1.1, level - 3),         # Hit points (Example value)
            h_d= 120 * pow(1.1, level - 3),          # Hit damage (Example value)
            h_s=1.1,          # Hit speed (Seconds per hit)
            l_t=0.3,            # First hit cooldown
            h_r=0.8,            # Hit range
            s_r=7.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=True,        # Not tower-only
            m_s=45*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=15,            #mass
            c_r=0.6,        #collision radius
            p=position               # Position (vector.Vector object)
        )
        self.level = level
        self.can_kb = False


    def attack(self):
        return ElixirGolemAttackEntity(self.side, self.hit_damage, self.position, self.target)
    
    def die(self, arena):
        if self.side:
            arena.p2_elixir += 1
        else:
            arena.p1_elixir += 1
        arena.troops.append(ElixirGolemite(self.side, self.position.added(vector.Vector(0.75, 0)), self.level, self.cloned))
        arena.troops.append(ElixirGolemite(self.side, self.position.added(vector.Vector(-0.75, 0)), self.level, self.cloned))
        super().die(arena)

class ElixirGolemiteAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 0.8
    COLLISION_RADIUS = 0.5
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            position=position,
            target=target
            )

class ElixirGolemite(Troop):
    def __init__(self, side, position, level, cloned=False):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 360 * pow(1.1, level - 3),         # Hit points (Example value)
            h_d= 60 * pow(1.1, level - 3),          # Hit damage (Example value)
            h_s=1.1,          # Hit speed (Seconds per hit)
            l_t=0.3,            # First hit cooldown
            h_r=0.8,            # Hit range
            s_r=7.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=True,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=10,            #mass
            c_r=0.5,        #collision radius
            p=position,               # Position (vector.Vector object)
            cloned=cloned
        )
        self.level = level


    def attack(self):
        return ElixirGolemiteAttackEntity(self.side, self.hit_damage, self.position, self.target)
    
    def die(self, arena):
        if self.side:
            arena.p2_elixir += 0.5
        else:
            arena.p1_elixir += 0.5
        arena.troops.append(ElixirBlob(self.side, self.position.added(vector.Vector(0.75, 0)), self.level, self.cloned))
        arena.troops.append(ElixirBlob(self.side, self.position.added(vector.Vector(-0.75, 0)), self.level, self.cloned))
        super().die(arena)

class ElixirBlobAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 0.8
    COLLISION_RADIUS = 0.4
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            position=position,
            target=target
            )

class ElixirBlob(Troop):
    def __init__(self, side, position, level, cloned=False):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 170 * pow(1.1, level - 3),         # Hit points (Example value)
            h_d= 30 * pow(1.1, level - 3),          # Hit damage (Example value)
            h_s=1.1,          # Hit speed (Seconds per hit)
            l_t=0.3,            # First hit cooldown
            h_r=0.8,            # Hit range
            s_r=7.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=True,        # Not tower-only
            m_s=90*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=5,            #mass
            c_r=0.4,        #collision radius
            p=position,               # Position (vector.Vector object)
            cloned=cloned
        )
        self.level = level

    def attack(self):
        return ElixirBlobAttackEntity(self.side, self.hit_damage, self.position, self.target)
    
    def die(self, arena):
        if self.side:
            arena.p2_elixir += 0.5
        else:
            arena.p1_elixir += 0.5
        super().die(arena)

class ExecutionerAttackEntity(RangedAttackEntity):
    SPLASH_RADIUS = 1
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side, 
            damage=damage, 
            velocity=1200*TILES_PER_MIN, 
            position=position, 
            target=target
        )
        self.homing = False
        self.piercing = True
        self.set_initial_vec()
        self.set_move_vec()
        self.duration = 1.5
        self.display_size = 1
        self.resize = True
        self.returning = False

    def tick_func(self, arena):
        if self.duration <= 0.75 and not self.returning:
            self.returning = True
            self.has_hit = []
    
    def cleanup_func(self, arena):
        self.velocity -= 2/270
        self.set_move_vec()

    def detect_hits(self, arena):
        hits = []
        for each in arena.towers + arena.buildings + arena.troops:
            if each.side != self.side and not each.invulnerable and each not in self.has_hit: # if different side
                if vector.distance(each.position, self.position) <= each.collision_radius + (0.6 if self.duration > 1.2 else self.SPLASH_RADIUS):
                    hits.append(each)
                    self.has_hit.append(each)
        return hits


class Executioner(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 800 * pow(1.1, level -6),         # Hit points (Example value)
            h_d= 106 * pow(1.1, level - 6),          # Hit damage (Example value)
            h_s=0.9,          # Hit speed (Seconds per hit)
            l_t=0.4,            # First hit cooldown
            h_r=4.5,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=False,       # Targets ground-only
            t_o=False,        # Not tower-only``
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=4,            #mass
            c_r=0.6,        #collision radius
            p=position               # Position (vector.Vector object)
        )
        self.level = level

    def attack(self):
        self.stun_timer = 1.5
        return ExecutionerAttackEntity(self.side, self.hit_damage, self.position, copy.deepcopy(self.target.position))
    
class GoblinCurse(Spell):
    def __init__(self, side, target, level):
        super().__init__(
            s=side,
            d=19 * pow(1.1, level - 6),
            c_t_d=4 * pow(1.1, level - 6),
            w=6,
            t=1,
            kb=0,
            r=3,
            v=0,
            tar=target
        )
        self.pulse_time = 0.1
        self.pulse_timer = 0
        self.level = level

    def passive_effect(self, each):
        if isinstance(each, Troop):
            each.damage_amplificatgion = 1.2
            each.goblin_cursed_level = self.level
            if each.cursed_timer <= 0.1:
                each.cursed_timer = 0.1

class GoblinDrillSpawnAttackEntity(AttackEntity):
    SPLASH_RADIUS = 2
    def __init__(self, side, damage, ctd, position):
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
            vec.scale(1)
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

class GoblinDrillMineTroop(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 1,         # Hit points (Example value)
            h_d= 0,          # Hit damage (Example value)
            h_s=0,          # Hit speed (Seconds per hit)
            l_t=0,            # First hit cooldown
            h_r=0,            # Hit range
            s_r=0,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=300*TILES_PER_MIN,          # Movement speed 
            d_t=0,            # Deploy time
            m=0,            #mass
            c_r=0.5,        #collision radius
            p=vector.Vector(0, -13 if side else 13)               # Position (vector.Vector object)
        )
        self.target = position
        self.level = level
        self.invulnerable = True
        self.moveable = False
        self.targetable = False
        self.collideable = False
        self.preplace = False

    def tick_func(self, arena):
        if self.invulnerable and vector.distance(self.position, self.target) < 0.25:
            gd = GoblinDrill(self.side, self.position, self.level)
            arena.buildings.append(gd)
            gd.on_deploy(arena)
            arena.active_attacks.append(GoblinDrillSpawnAttackEntity(self.side, 51 * pow(1.1, self.level - 6), 16 * pow(1.1, self.level - 6), self.position))
            arena.troops.remove(self)
            self.cur_hp = -1 #just in case

    def on_preplace(self):
        self.invulnerable = True
        self.targetable = False
        self.collideable = False

    def move(self, arena):
        if not same_sign(self.target.y, self.position.y) and ((self.position.y < -1 or self.position.y > 1)):
            tar_bridge = None
            
            x = self.position.x
            t_x = None
            
            if self.target.x < 0:
                if x <= -6.5: #left more optimal
                    t_x = -6.4
                elif x >= -4.5:
                    t_x = -4.4
                else:
                    t_x = x
            else: #right better
                if x >= 6.5:
                    t_x = 6.4
                elif x <= 4.5:
                    t_x = 4.4
                else:
                    t_x = x
            
            tar_bridge = vector.Vector(t_x, -1 if self.position.y < 0 else 1)
        
            direction_x = tar_bridge.x - self.position.x #set movement
            direction_y = tar_bridge.y - self.position.y
            distance_to_target = math.sqrt(direction_x ** 2 + direction_y ** 2)
        else:
            if self.position.y < 1 and self.position.y > -1 and on_bridge(self.position.x) and not (self.target.y < 1 and self.target.y > -1 and on_bridge(self.target.x)):
                bridge_side = 1 if self.position.y < self.target.y else -1
                bridge_min = -6 if self.position.x < 0 else 5
                bridge_max = -5 if self.position.x < 0 else 6

                to_tar = self.target.subtracted(self.position)
                to_corner1 = vector.Vector(bridge_min + 0.1, bridge_side).subtracted(self.position)
                to_corner2 = vector.Vector(bridge_max - 0.1, bridge_side).subtracted(self.position)

                ratio = float('inf') if to_tar.x == 0 else abs(to_tar.y/to_tar.x)

                t_x = self.target.x

                if to_corner1.x == 0 or (t_x < bridge_min and abs(to_corner1.y/to_corner1.x) > ratio):
                    tar_bridge = vector.Vector(bridge_min + 0.1, bridge_side)
                    direction_x = tar_bridge.x - self.position.x
                    direction_y = tar_bridge.y - self.position.y
                    distance_to_target = math.sqrt(direction_x ** 2 + direction_y ** 2)
                elif to_corner2.x == 0 or (t_x > bridge_max and abs(to_corner2.y/to_corner2.x) > ratio):
                    tar_bridge = to_corner2 = vector.Vector(bridge_max - 0.1, bridge_side).subtracted(self.position)
                    direction_x = tar_bridge.x - self.position.x
                    direction_y = tar_bridge.y - self.position.y
                    distance_to_target = math.sqrt(direction_x ** 2 + direction_y ** 2)
                else:
                    direction_x = self.target.x - self.position.x
                    direction_y = self.target.y - self.position.y
                    distance_to_target = math.sqrt(direction_x ** 2 + direction_y ** 2)
                
            else:
                direction_x = self.target.x - self.position.x
                direction_y = self.target.y - self.position.y
                distance_to_target = math.sqrt(direction_x ** 2 + direction_y ** 2)
        
        direction_x /= distance_to_target
        direction_y /= distance_to_target
        # Move in the direction of the target
        m_s = self.move_speed
        self.position.x += direction_x  * m_s
        self.position.y += direction_y * m_s
        angle = math.degrees(math.atan2(direction_y, direction_x))  # Get angle in degrees
        self.facing_dir = angle
        self.move_vector = vector.Vector(direction_x * m_s, direction_y * m_s)

    def tick(self, arena):
        if self.preplace:
            return
        self.tick_func(arena)
        self.move(arena)

    def cleanup(self, arena):
        pass
        
class GoblinDrill(Building):
    SPAWN_INTERVAL = 0.5
    def __init__(self, side, position, level):
        super().__init__(
            s=side,
            h_p=820 * pow(1.1, level - 6),
            h_d = 0,
            h_s = 3,
            l_t = 0,
            h_r = 0,
            s_r = 0,
            g = True,
            t_g_o = True,
            t_o = False,
            l=9,
            d_t=1,
            c_r=0.5,
            d_s_c=2,
            d_s=Goblin,
            p=position
        )
        self.next_spawn = None
        self.remaining_spawn_count = 0
        self.is_spawner = True
        self.level = level
        self.attack_cooldown = 1
        self.on_tower = None

    def snap_around_tower(self, tower):

        if abs(self.position.y - tower.position.y) >= abs(self.position.x - tower.position.x):
            if self.position.y <= tower.position.y:
                self.position.y = math.floor(tower.position.y - tower.collision_radius)
            else:
                self.position.y = math.ceil(tower.position.y + tower.collision_radius)
        else:
            if self.position.x <= tower.position.x:
                self.position.x = math.floor(tower.position.x - tower.collision_radius)
            else:
                self.position.x = math.ceil(tower.position.x + tower.collision_radius)

    def on_deploy(self, arena):
        for each in arena.towers:
            if each.side != self.side and vector.distance(each.position, self.position) <= each.collision_radius + self.collision_radius:
                self.on_tower = each
                self.snap_around_tower(each)
                return

    
    def cleanup_func(self, arena):
        if self.stun_timer <= 0:
            if not self.next_spawn is None and self.next_spawn > 0:
                self.next_spawn -= TICK_TIME
        
    def tick(self, arena):
        if self.preplace or self.stun_timer > 0:
            return
        self.tick_func(arena)
        
        if self.attack_cooldown <= 0: #attack code
            front = vector.Vector(0, 1.5) if self.side else vector.Vector(0, -1.5)
            newFire = Goblin(self.side, self.position.added(front), self.level)
            newFire.deploy_time = 0
            arena.troops.append(newFire)
            self.attack_cooldown = self.hit_speed