from abstract_classes import Troop, Tower, Spell
from abstract_classes import RangedAttackEntity
from abstract_classes import MeleeAttackEntity, AttackEntity
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
        self.can_kb = False

    def attack(self):
        return SkeletonKingAttackEntity(self.side, self.hit_damage, self.position, self.target.position)
    
    def ability(self, arena):
        arena.spells.append(SkeletonKingAbility(self.side, self.position, self.level, min(self.amount, self.amount_max)))
        self.amount = 6

    def handle_deaths(self, list):
        for each in list:
            if self.amount < self.amount_max and not each.cloned:
                self.amount += 1
        
class GoldenKnightAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 1.2
    COLLISION_RADIUS = 0.8
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            position=position,
            target=target
            )

class GoldenKnight(Champion):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 1800 * pow(1.1, level - 11),         # Hit points (Example value)
            h_d= 160 * pow(1.1, level - 11),          # Hit damage (Example valufae)
            h_s=0.9,          # Hit speed (Seconds per hit)
            l_t=0.7,            # First hit cooldown
            h_r=1.2,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=10,            #mass
            c_r=0.8,        #collision radius
            p=position,               # Position (vector.Vector object)
            ability_cost = 1,
            ability_cast_time=0.766,
            ability_duration=float('inf'),
            ability_cooldown=11
        ) 
        self.level = level
        self.dash_damage = 310 * pow(1.1, level - 11)
        self.dashing = False
        self.dashed = []
        self.dash_center = None
        self.dash_count = 0
        self.max_dash_count = 10

    def update_target(self, arena):
        self.target = None 
        
        min_dist = float('inf')
        if not self.tower_only: #if not tower targeting
            for each in arena.troops: #for each troop
                if each.targetable and not each.invulnerable and each.side != self.side and (not self.ground_only or (self.ground_only and each.ground)) and each not in self.dashed: #targets air or is ground only and each is ground troup
                    dist = vector.distance(each.position, self.position)
                    if  dist < min_dist and dist < self.sight_range + self.collision_radius + each.collision_radius:
                        self.target = each
                        min_dist = vector.distance(each.position, self.position)
        for each in arena.buildings: #for each building, so if any building is closer then non tower targeting switches, or if tower targeting then finds closest building
            if each.side != self.side and each.targetable:
                dist = vector.distance(each.position, self.position)
                if  dist < min_dist and dist < self.sight_range + self.collision_radius + each.collision_radius and each not in self.dashed:
                    self.target = each
                    min_dist = vector.distance(each.position, self.position)
        
        for tower in arena.towers: #check for towers that it can currently hit
            if tower.side != self.side:
                dist = vector.distance(tower.position, self.position)
                if dist < min_dist:
                    self.target = None #ensures that it doesnt lock on to troops farther away than tower
                if dist < self.hit_range + self.collision_radius + tower.collision_radius and dist < min_dist and tower not in self.dashed: #iff can hit tower, then it locks on.
                    self.target = tower #ensures only locks when activel attacking tower, so giant at bridge doesnt immediatly lock onto tower and ruin everyones day
                    min_dist = dist

                if self.ability_active and dist < min_dist and dist < 5.5 + self.collision_radius + tower.collision_radius and tower not in self.dashed:
                    self.target = tower
                    min_dist = dist

    def level_up(self):
        self.dash_damage *= 1.1
        super().level_up()

    def attack(self):
        if not self.dashing:
            return GoldenKnightAttackEntity(self.side, self.hit_damage, self.position, self.target)
    
    def ability(self, arena):
        self.move_speed *= 2
        self.normal_move_speed *= 2
        self.dashed = []

    def ability_tick(self, arena):
        if self.target is not None and self.stun_timer <= 0:
            d = vector.distance(self.position, self.target.position)
            if self.dashing:
                if d < self.collision_radius + self.hit_range + self.target.collision_radius: #if hit
                    self.dashed.append(self.target) #register
                    arena.active_attacks.append(GoldenKnightAttackEntity(self.side, self.dash_damage, copy.deepcopy(self.position), self.target)) #attack
                    self.dash_count += 1
                    self.dash_center = copy.deepcopy(self.position)
                    self.update_target(arena) #find new

                    self.stun_timer = 0.2

                    if self.target is None or self.dash_count >= 10 or vector.distance(self.position, self.target.position) > 5.5 + self.target.collision_radius:
                        self.ability_duration_timer = 0 #done
                        self.dashing = False
                        self.collideable = True
                        self.invulnerable = False
                        self.dash_river = False
                elif vector.distance(self.position, self.dash_center) > 5.6:
                    self.ability_duration_timer = 0 #done
                    self.dashing = False
                    self.collideable = True
                    self.invulnerable = False
                    self.dash_river = False
            
            elif d < 5.5 + self.target.collision_radius + self.collision_radius:
                    self.update_target(arena)
                    self.dash_center = copy.deepcopy(self.position)
                    self.dashing = True
                    self.invulnerable = True
                    self.collideable = False
                    self.move_speed = 400 * TILES_PER_MIN * (1.35 if self.rage_timer > 0 else 1)
                    self.dash_river = True
                    self.hit_range = 0.2

        if self.dashing and (self.target is None or self.target.cur_hp <= 0):
            self.ability_duration_timer = 0 #done
            self.dashing = False
            self.invulnerable = False
            self.collideable = True
            self.dash_river = False

    def ability_end(self, arena):
        self.normal_move_speed /= 2
        self.move_speed = self.normal_move_speed
        self.dash_count = 0
        self.hit_range = 1.2
        self.dashed = []
        self.update_target(arena)

class MightyMinerAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 1.6
    COLLISION_RADIUS = 0.5
    def __init__(self, side, damage, position, target):
        super().__init__(
            side,
            damage,
            position,
            target
        )

class MightyMinerAbilityBombAttackEntity(AttackEntity):
    DAMAGE_RADIUS = 3
    def __init__(self, side, damage, position, target_pos):
        super().__init__(
            s=side,
            d=damage,
            v=0,
            l=0.25,
            i_p=copy.deepcopy(position)
        )
        self.display_size = MightyMinerAbilityBombAttackEntity.DAMAGE_RADIUS
        self.has_hit = []

    def detect_hits(self, arena):
        hits = []
        for each in arena.towers + arena.buildings + arena.troops:
            if each.side != self.side and (isinstance(each, Tower) or not each.invulnerable): # if different side
                if vector.distance(self.position, each.position) < MightyMinerAbilityBombAttackEntity.DAMAGE_RADIUS + each.collision_radius:
                    hits.append(each)
        return hits
            
    def tick(self, arena):
        hits = self.detect_hits(arena)
        for each in hits:
            new = not any(each is h for h in self.has_hit)
            if (new):
                each.damage(self.damage)
                if isinstance(each, Troop) and each.can_kb and not each.invulnerable:
                    vec = each.position.subtracted(self.position)
                    vec.normalize()
                    vec.scale(1.8)
                    each.kb(vec)
                    self.has_hit.append(each)


class MightyMinerAbilityBomb(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p=  float('inf'),         # Hit points (Example value)
            h_d= 334 * pow(1.1, level - 11),          # Hit damage (Example value)
            h_s=0,          # Hit speed (Seconds per hit)
            l_t=0,            # First hit cooldown
            h_r=0,            # Hit range
            s_r=0,            # Sight Range
            g=True,           # Ground troop
            t_g_o=False,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=0,          # Movement speed 
            d_t=1,            # Deploy time
            m=float('inf'),            #mass
            c_r=0.45,        #collision radius
            p=position               # Position (vector.Vector object)
        ) 
        self.level = level
        self.invulnerable=True
        self.moveable=False
        self.targetable=False
        self.target=None

    def tick(self, arena):
        if self.deploy_time <= 0:
            arena.active_attacks.append(self.attack())
            self.cur_hp = -1
    
    def attack(self):
        return MightyMinerAbilityBombAttackEntity(self.side, self.hit_damage, self.position, self.target)

class MightyMiner(Champion):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 2250 * pow(1.1, level - 11),         # Hit points (Example value)
            h_d= 40 * pow(1.1, level - 11),          # Hit damage (Example value)
            h_s=0.4,          # Hit speed (Seconds per hit)
            l_t=0.7,            # First hit cooldown
            h_r=1.6,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=6,            #mass
            c_r=0.5,        #collision radius
            p=position,               # Position (vector.Vector object)
            ability_cost = 1,
            ability_cast_time=0.933,
            ability_duration=float('inf'),
            ability_cooldown=13
        ) 
        self.level = level
        self.stage = 1
        self.stage_duration = 2
        self.damage_stages = [40 * pow(1.1, level - 9), 200 * pow(1.1, level - 9), 400 * pow(1.1, level - 9)]
        self.target_x = None

    def level_up(self):
        super().level_up()
        for i in range(3):
            self.damage_stages[i] *= 1.1
    
    def tick_func(self, arena):
        if self.target is None or self.target.cur_hp <= 0 or vector.distance(self.position, self.target.position) > self.hit_range + self.collision_radius + self.target.collision_radius + 0.1 or not self.target.targetable:
            self.stage = 1
            self.stage_duration = 2
            self.attack_cooldown = self.load_time - self.hit_speed

    def freeze(self, duration):
        self.stage = 1
        self.stage_duration = 2
        self.attack_cooldown = self.load_time - self.hit_speed
        return super().freeze(duration)
    
    def kb(self, vector, kb_time=None):
        self.stage = 1
        self.stage_duration = 2
        self.attack_cooldown = self.load_time - self.hit_speed
        return super().kb(vector, kb_time) 

    def stun(self):
        self.stage = 1
        self.stage_duration = 2
        self.attack_cooldown = self.load_time - self.hit_speed
        super().stun()

    def cleanup_func(self, arena):
        if self.stun_timer <= 0:
            if self.stage_duration <= 0:
                self.stage = self.stage + 1 if self.stage < 3 else self.stage
                self.stage_duration = 2
            elif not (self.target is None or self.target.cur_hp <= 0 or vector.distance(self.position, self.target.position) > self.hit_range  + self.target.collision_radius + self.collision_radius or not self.target.targetable):
                self.stage_duration -= TICK_TIME

    def attack(self):
        return MightyMinerAttackEntity(self.side, self.damage_stages[self.stage - 1], self.position, self.target)
    
    def ability(self, arena):
        self.targetable = False
        self.invulnerable = True
        self.collideable = False
        self.target_x = -self.position.x
        self.stun_timer = float('inf') #completely disable
        arena.troops.append(MightyMinerAbilityBomb(self.side, copy.deepcopy(self.position), self.level))
    
    def ability_tick(self, arena):
        if self.target_x > 0 and self.position.x < self.target_x:
            self.position.x += 650 * TILES_PER_MIN
        elif self.target_x <= 0 and self.position.x > self.target_x:
            self.position.x -= 650 * TILES_PER_MIN
        else:
            self.stun_timer = 0
            self.ability_duration_timer = 0

    
    def ability_end(self, arena):
        self.move_speed = self.normal_move_speed
        self.targetable = True
        self.invulnerable = False
        self.collideable = True
        self.target_x = None

class BossBanditAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 0.8
    COLLISION_RADIUS = 0.6
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            position=position,
            target=target
            )

class BossBandit(Champion):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 2721 * pow(1.1, level - 11),         # Hit points (Example value)
            h_d= 268 * pow(1.1, level - 11),          # Hit damage (Example value)
            h_s=1.2,          # Hit speed (Seconds per hit)
            l_t=0.8,            # First hit cooldown
            h_r=0.8,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=90*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=6,            #mass
            c_r=0.6,        #collision radius
            p=position,               # Position (vector.Vector object)
            ability_cost = 1,
            ability_cast_time=0.933,
            ability_duration=1,
            ability_cooldown=3
        ) 
        self.level = level
        self.ability_count = 2
        self.dashing = False
        self.should_dash = False
        self.dash_center = None
    
    def attack(self):
        if not self.dashing:
            return BossBanditAttackEntity(self.side, self.hit_damage, self.position, self.target)
        
    def activate_ability(self, arena):
        if self.ability_count > 0:
            self.ability_count -= 1
            return super().activate_ability(arena)
        
    def update_dash_target(self, arena):
        self.update_target(arena)
        if self.target is None and self.stun_timer <= 0:
            t_t = None
            m_dist = float('inf')
            for each in arena.towers:
                if each.side != self.side:
                    d = vector.distance(each.position, self.position)
                    if d < 6 + each.collision_radius + self.collision_radius and d > 3.5 + each.collision_radius + self.collision_radius and d < m_dist:
                        t_t = each
                        m_dist = d

            if t_t is not None:
                self.target = t_t
        
    def tick_func(self, arena):
        if self.ability_count <= 0:
            self.ability_sprite_path = "sprites/bossbandit/bossbandit_ability_0.png"
        if self.target is None and self.stun_timer <= 0:
            t_t = None
            m_dist = float('inf')
            for each in arena.towers:
                if each.side != self.side:
                    d = vector.distance(each.position, self.position)
                    if d < 6 + each.collision_radius + self.collision_radius and d > 3.5 + each.collision_radius + self.collision_radius and d < m_dist:
                        t_t = each
                        m_dist = d

            if t_t is not None:
                self.target = t_t

        if (self.target is not None and self.stun_timer <= 0):
            if self.should_dash:
                self.update_dash_target(arena)
                self.should_dash = False

                if self.target is not None:
                    self.invulnerable = True
                    self.collideable = False
                    self.dash_river = True
                    self.dashing = True
                else:
                    self.move_speed = self.normal_move_speed
                    return

            d = vector.distance(self.position, self.target.position)
            if not self.dashing:
                if d < 6 + self.target.collision_radius + self.collision_radius and d > 3.5 + self.target.collision_radius + self.collision_radius:
                    self.dash_center = copy.deepcopy(self.position)
                    self.should_dash = True
                    self.move_speed = 500 * (1.35 if self.rage_timer > 0 else 1) * TILES_PER_MIN                    
                    self.stun_timer = 0.8 #charge time

            if self.dashing:
                if d < self.collision_radius + self.hit_range + self.target.collision_radius: #if hit
                    arena.active_attacks.append(BossBanditAttackEntity(self.side, self.hit_damage * 2, copy.deepcopy(self.position), self.target)) #attack
                    self.dashing = False
                    self.collideable = True
                    self.invulnerable = False
                    self.dash_river = False
                    self.move_speed = self.normal_move_speed
                elif vector.distance(self.position, self.dash_center) > 6.1:
                    self.dashing = False
                    self.collideable = True
                    self.invulnerable = False
                    self.dash_river = False
                    self.move_speed = self.normal_move_speed
            
        if self.dashing and (self.target is None or self.target.cur_hp <= 0):
            self.dashing = False
            self.invulnerable = False
            self.collideable = True
            self.dash_river = False
            self.move_speed = self.normal_move_speed

    def ability(self, arena):
        self.targetable = False
        self.invulnerable = True
        self.stun_timer = 1 #completely disable

    def ability_tick(self, arena):
        if self.stun_timer <= 1/3:
            self.position.y += (-1 if self.side else 1) * 1080*TILES_PER_MIN

    def ability_end(self, arena):
        self.stun_timer = 0
        self.targetable = True
        self.invulnerable = False