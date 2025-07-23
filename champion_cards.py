from abstract_classes import Troop, Tower, Spell
from abstract_classes import RangedAttackEntity
from abstract_classes import MeleeAttackEntity
from abstract_classes import TILES_PER_MIN
from abstract_classes import TICK_TIME
from bone_pit_cards import Skeleton
import copy
import math
import vector

class Champion(Troop):
    def __init__(self, s, h_p, h_d, h_s, l_t, h_r, s_r, g, t_g_o, t_o, m_s, d_t, m, c_r, p, ability_cost, ability_cast_time, ability_duration, ability_cooldown, cloned=False):
        super().__init__(s, h_p, h_d, h_s, l_t, h_r, s_r, g, t_g_o, t_o, m_s, d_t, m, c_r, p, cloned)
        self.ability_cost = ability_cost
        self.ability_cast_timer = ability_cast_time
        self.ability_cast_time = ability_cast_time
        self.ability_duration = ability_duration
        self.ability_duration_timer = ability_duration
        self.ability_cooldown = ability_cooldown
        self.ability_cooldown_timer = 0

        self.ability_active = False

        n = self.__class__.__name__.lower()
        self.ability_sprite_path = "sprites/" + n + "/" + n + "_ability.png"

    def on_deploy(self, arena):
        if self.side:
            arena.p1_champion = self
        else:
            arena.p2_champion = self

    def die(self, arena):
        if self.side:
            arena.p1_champion = None
        else:
            arena.p2_champion = None
        return super().die(arena)


    def tick(self, arena):
        if self.ability_active:
            if self.ability_cast_timer < 0: #if cast
                self.ability_cast_timer = 0 #remains on
                self.ability(arena) #trigger once

        
            if self.ability_cast_timer != 0:
                self.ability_cast_timer -= TICK_TIME #if not cast
            else: #if cast
                if self.ability_duration_timer > 0: #if duration active
                    self.ability_tick(arena)
                    self.ability_duration_timer -= TICK_TIME
                else:
                    self.ability_active = False
                    self.ability_end(arena)


        if self.ability_cooldown_timer > 0:
            self.ability_cooldown_timer -= TICK_TIME
            n = self.__class__.__name__.lower()
            self.ability_sprite_path = "sprites/" + n + "/" + n + "_ability_" + str(round((1 - self.ability_cooldown_timer/self.ability_cooldown) * 16)) + ".png"
        else:
            n = self.__class__.__name__.lower()
            self.ability_sprite_path = "sprites/" + n + "/" + n + "_ability.png"
        
        return super().tick(arena)

    def ability(self, arena):
        pass

    def ability_tick(self, arena):
        pass

    def ability_end(self, arena):
        pass

    def activate_ability(self, arena):
        works = False
        if self.side:
            if arena.p1_elixir >= self.ability_cost:
                arena.p1_elixir -= self.ability_cost
                works = True
            
        else:
            if arena.p2_elixir >= self.ability_cost:
                arena.p2_elixir -= self.ability_cost
                works = True
        
        if works:
            self.ability_active = True
            self.ability_duration_timer = self.ability_duration
            self.ability_cast_timer = self.ability_cast_time
            self.ability_cooldown_timer = self.ability_cooldown

class ArcherQueenAttackEntity(RangedAttackEntity):
    def __init__(self, side, damage, position, target):
        super().__init__(side, damage, 800 * TILES_PER_MIN, position, target)

class ArcherQueen(Champion):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 1000 * pow(1.1, level - 11),         # Hit points (Example value)
            h_d= 225 * pow(1.1, level - 11),          # Hit damage (Example value)
            h_s=1.2,          # Hit speed (Seconds per hit)
            l_t=0.9,            # First hit cooldown
            h_r=5,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=False,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=6,            #mass
            c_r=0.5,        #collision radius
            p=position,               # Position (vector.Vector object)
            ability_cost = 1,
            ability_cast_time=0.933,
            ability_duration=3,
            ability_cooldown=15
        ) 
        self.level = level

    def attack(self):
        return ArcherQueenAttackEntity(self.side, self.hit_damage, self.position, self.target)
    
    def ability(self, arena):
        self.targetable = False
        self.move_speed *= 0.75
        self.attack_cooldown /= 2.8
        self.hit_speed /= 2.8
        self.load_time /= 2.8
    
    def ability_end(self, arena):
        self.targetable = True
        self.hit_speed *= 2.8
        self.load_time *= 2.8
        self.move_speed *= 4/3

class SkeletonKingAbility(Spell):
    def __init__(self, side, target, level, amount):
        super().__init__(
            s=side,
            d=0,
            c_t_d=0,
            w=amount,
            t=0.25,
            kb=0,
            r=4,
            v=0,
            tar=target
        )
        self.initial_delay = 0.75
        self.display_duration = self.initial_delay + self.time_between * self.waves + 0.5
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
                    pos .y = -16
                arena.troops.append(Skeleton(self.side, pos, self.level, True))
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

class SkeletonKingAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 1.2
    COLLISION_RADIUS = 1.2
    SPLASH_RADIUS = 1.3
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            position=copy.deepcopy(target),
            target=copy.deepcopy(target) #not used
            )
        
    def detect_hits(self, arena):
        hits = []
        for each in arena.towers + arena.buildings + arena.troops:
            if each.side != self.side and (isinstance(each, Tower) or (each.ground and not each.invulnerable)): # if different side
                if vector.distance(each.position, self.position) <= each.collision_radius + self.SPLASH_RADIUS:
                    hits.append(each)
        return hits

class SkeletonKing(Champion):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 2300 * pow(1.1, level - 11),         # Hit points (Example value)
            h_d= 205 * pow(1.1, level - 11),          # Hit damage (Example value)
            h_s=1.6,          # Hit speed (Seconds per hit)
            l_t=1.3,            # First hit cooldown
            h_r=1.2,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=18,            #mass
            c_r=1.2,        #collision radius
            p=position,               # Position (vector.Vector object)
            ability_cost = 2,
            ability_cast_time=0.933,
            ability_duration=10,
            ability_cooldown=20
        ) 
        self.level = level
        self.amount = 6
        self.amount_max = 16

    def attack(self):
        return SkeletonKingAttackEntity(self.side, self.hit_damage, self.position, self.target.position)
    
    def ability(self, arena):
        arena.spells.append(SkeletonKingAbility(self.side, self.position, self.level, min(self.amount, self.amount_max)))
        self.amount = 6

    def handle_deaths(self, list):
        for each in list:
            if self.amount < self.amount_max and not each.cloned:
                self.amount += 1
        