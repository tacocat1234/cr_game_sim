from abstract_classes import RangedAttackEntity
from abstract_classes import MeleeAttackEntity
from abstract_classes import AttackEntity
from abstract_classes import Troop
from abstract_classes import Tower
from abstract_classes import Spell
from royal_arena_cards import RoyalRecruit
from builders_workshop_cards import Bat
from abstract_classes import TILES_PER_MIN
from abstract_classes import TICK_TIME
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
    HIT_RANGE = 0.7
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
        arena.troops.append(Bat(self.side, self.position.added(vector.Vector(1.5, 0)), self.level))
        arena.troops.append(Bat(self.side, self.position.added(vector.Vector(-1.5, 0)), self.level))

    def die(self, arena):
        arena.troops.append(Bat(self.side, self.position, self.level))
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
        arena.troops.append(ElixirGolemite(self.side, self.position.added(vector.Vector(0.75, 0)), self.level))
        arena.troops.append(ElixirGolemite(self.side, self.position.added(vector.Vector(-0.75, 0)), self.level))
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
    def __init__(self, side, position, level):
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
            p=position               # Position (vector.Vector object)
        )
        self.level = level


    def attack(self):
        return ElixirGolemiteAttackEntity(self.side, self.hit_damage, self.position, self.target)
    
    def die(self, arena):
        if self.side:
            arena.p2_elixir += 0.5
        else:
            arena.p1_elixir += 0.5
        arena.troops.append(ElixirBlob(self.side, self.position.added(vector.Vector(0.75, 0)), self.level))
        arena.troops.append(ElixirBlob(self.side, self.position.added(vector.Vector(-0.75, 0)), self.level))
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
    def __init__(self, side, position, level):
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
            p=position               # Position (vector.Vector object)
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
    def __init__(self, side, damage, position, target, parent_pos):
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
        self.display_size = 0.75
        self.resize = True
        self.returning = False

        self.parent_pos = parent_pos

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
            h_p= 800 * pow(1.1, level - 6),         # Hit points (Example value)
            h_d= 106 * pow(1.1, level - 6),          # Hit damage (Example value)
            h_s=0.9,          # Hit speed (Seconds per hit)
            l_t=0.4,            # First hit cooldown
            h_r=4.5,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=False,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=4,            #mass
            c_r=0.6,        #collision radius
            p=position               # Position (vector.Vector object)
        )
        self.level = level

    def attack(self):
        self.stun_timer = 1.5
        return ExecutionerAttackEntity(self.side, self.hit_damage, self.position, copy.deepcopy(self.target.position), self.position)
    
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
        each.damage_amplificatgion = 1.2
        each.goblin_cursed_level = self.level
        each.cursed_timer = 0.1