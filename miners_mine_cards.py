from abstract_classes import RangedAttackEntity
from abstract_classes import MeleeAttackEntity
from abstract_classes import AttackEntity
from abstract_classes import Troop
from abstract_classes import Spell
from abstract_classes import Tower
from abstract_classes import Building
from abstract_classes import TILES_PER_MIN
from abstract_classes import TICK_TIME
from goblin_stadium_cards import Goblin
import card_factory
import vector
import copy
import math

class ElixirCollector(Building):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,
            h_p=505 * pow(1.1, level - 3),
            h_d = 0,
            h_s = 9,
            l_t = 0,
            h_r = 0,
            s_r = 0,
            g = True,
            t_g_o = True,
            t_o = False,
            l=65,
            d_t=1,
            c_r=1,
            d_s_c=1,
            d_s=None,
            p=position
        )
        self.is_spawner = True
        self.level=level

    def die(self, arena):
        if self.side:
            arena.p1_elixir += 1
        else:
            arena.p2_elixir += 1
        super().die(arena)
        
    def tick(self, arena):
        if self.preplace:
            return
        if self.stun_timer <= 0:
            if self.attack_cooldown <= 0: #attack code
                if self.side:
                    arena.p1_elixir += 1
                else:
                    arena.p2_elixir += 1
                self.attack_cooldown = self.hit_speed

class Clone(Spell):
    def __init__(self, side, target, level):
        super().__init__(
            s=side,
            d=0,
            c_t_d=0,
            w=1, #waves
            t=0, #time between waves
            kb=0,
            r=3,
            v=0,
            tar=target
        )

    def detect_hits(self, arena):
        out = []
        for each in arena.troops + arena.buildings + arena.towers:
            if not each.invulnerable and each.side == self.side and (vector.distance(each.position, self.position) <= self.radius + each.collision_radius):
                out.append(each)
        return out
    
    def tick(self, arena):
        if self.preplace:
            return
        hits = self.detect_hits(arena)
        for each in hits:
            if (isinstance(each, Troop)) and not each.cloned and not each.invulnerable:
                
                c = card_factory.get_clone(each)
                
                if c is not None:
                    each.stun_timer = 0.5
                    each.kb(vector.Vector(0, 0.25 if self.side else -0.25))

                    c.cur_hp = 1
                    c.hit_points = 1
                    if c.has_shield:
                        c.shield_hp = 1
                        c.shield_max_hp = 1
                    c.cloned = True
                    c.deploy_time = 0.5

                    arena.troops.append(c)
                    c.kb(vector.Vector(0, -0.25 if self.side else 0.25))
        self.should_delete = True
        
class MotherWitchAttackEntity(RangedAttackEntity):
    def __init__(self, side, damage, position, target, level):
        super().__init__(
            side=side, 
            damage=damage, 
            velocity=800*TILES_PER_MIN, 
            position=position, 
            target=target
        )
        self.level = level

    def apply_effect(self, target):
        if isinstance(target, Troop):
            target.hog_cursed_level = self.level
            target.cursed_timer = 5

class MotherWitch(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 440 * pow(1.1, level - 9),         # Hit points (Example value)
            h_d= 110 * pow(1.1, level - 9),          # Hit damage (Example value)
            h_s=1,          # Hit speed (Seconds per hit)
            l_t=0.7,            # First hit cooldown
            h_r=5.5,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=False,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=6,            #mass
            c_r=0.5,        #collision radius
            p=position               # Position (vector.Vector object)
        )
        self.level = level
    def attack(self):
        return MotherWitchAttackEntity(self.side, self.hit_damage, self.position, self.target, self.level)
    
class CursedHogAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 0.75
    COLLISION_RADIUS = 0.6
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            position=position,
            target=target
            )
        
class CursedHog(Troop):
    def __init__(self, side, position, level, cloned=False):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 520 * pow(1.1, level - 9),         # Hit points (Example value)
            h_d= 44 * pow(1.1, level - 9),          # Hit damage (Example value)
            h_s=1.2,          # Hit speed (Seconds per hit)
            l_t=0.95,            # First hit cooldown
            h_r=0.75,            # Hit range
            s_r=9.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=True,        # tower-only
            m_s=120*TILES_PER_MIN,          # Movement speed 
            d_t=0.2,            # Deploy time
            m=2,            #mass
            c_r=0.6,        #collision radius
            p=position,               # Position (vector.Vector object)
            cloned=cloned
        ) 
        self.level = level
        self.walk_cycle_frames = 4
        class_name = self.__class__.__name__.lower()
        self.sprite_path = f"sprites/{class_name}/{class_name}_0.png"
        self.cross_river = True
        self.jump_speed = 160 * TILES_PER_MIN

    def attack(self):
        return CursedHogAttackEntity(self.side, self.hit_damage, self.position, self.target)
    
    def die(self, arena):
        if not self.should_delete and self.goblin_cursed_level is not None:
            arena.troops.append(Goblin(not self.side, self.position, self.goblin_cursed_level))
        self.cur_hp = -1
        arena.troops.remove(self)

class FishermanAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 1.2
    COLLISION_RADIUS = 0.5
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            position=position,
            target=target
            )

class FishermanSpecialAttackEntity(RangedAttackEntity):
    def __init__(self, side, damage, position, target, parent):
        super().__init__(
            side=side, 
            damage=damage, 
            velocity=800*TILES_PER_MIN, 
            position=position, 
            target=target
        )
        self.parent = parent
    
    def tick_func(self, arena):
        if self.target is None:
            self.parent.casting = False
            self.parent.reeling = False
            arena.active_attacks.remove(self)
    
    def apply_effect(self, target):
        target.slow(2.5, "fisherman")
        if target.cur_hp > 0:
            self.parent.casting = False
            self.parent.reeling = True
            self.parent.target_lock = True
            self.parent.target = target
            if self.parent.target is not None and isinstance(self.parent.target, Troop):
                self.parent.target_ms = self.parent.target.move_speed
        else:
            self.parent.casting = False
            self.parent.reeling = False
    
class Fisherman(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 720 * pow(1.1, level - 9),         # Hit points (Example value)
            h_d= 160 * pow(1.1, level - 9),          # Hit damage (Example value)
            h_s=1.3,          # Hit speed (Seconds per hit)
            l_t=1.2,            # First hit cooldown
            h_r=0.75,            # Hit range
            s_r=7.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=10,            #mass
            c_r=0.5,        #collision radius
            p=position               # Position (vector.Vector object)
        )
        self.dash_timer = 0
        self.casting = False
        self.reeling = False
        self.casted = False
        self.target_ms = None

        self.level = level
        self.ticks_per_frame = 6
        self.walk_cycle_frames = 6
        class_name = self.__class__.__name__.lower()
        self.sprite_path = f"sprites/{class_name}/{class_name}_dash.png"

    def tick_func(self, arena):
        if self.stun_timer <= 0 and self.deploy_time <= 0:
            if (self.target is None or self.target.cur_hp <= 0) and (self.reeling or self.casting):
                self.casted = False
                self.reeling = False
                self.casting = False
                self.stun_timer = 0
                self.move_speed = self.normal_move_speed
                self.collideable = True
                self.dash_river = False
                self.target_lock = False
                return

            if self.casting and not self.casted and self.target.cur_hp > 0: #if launching, launch reel
                arena.active_attacks.append(FishermanSpecialAttackEntity(self.side, self.hit_damage, self.position, self.target, self))
                self.target_lock = True
                self.casted = True            
            if self.target is not None: #if existing target
                d = vector.distance(self.position, self.target.position)
                if not self.reeling and not self.casting and d > 3.5 + self.target.collision_radius and d < 7 + self.target.collision_radius and self.dash_timer == 0:
                    self.casting = True #want to be casting
                    self.casted = False #but not yet cast
                    self.stun_timer = 1.3

            else: #if no existing target
                m_dist = float('inf')
                for tower in arena.towers:
                    dist = vector.distance(tower.position, self.position)
                    if tower.side != self.side and dist > 3.5 + tower.collision_radius and dist < 7 + tower.collision_radius:
                        if m_dist > dist:
                            m_dist = dist
                            self.target = tower
                if self.target is not None:
                    self.casting = True #want to be casting
                    self.casted = False #but not yet cast
                    self.stun_timer = 1.3

            if self.reeling: #reel connected
                if self.target is None:
                    self.reeling = False
                    self.move_speed = self.normal_move_speed
                    self.dash_river = False
                    self.target_lock = False
                    self.collideable = True
                elif isinstance(self.target, Troop): #if troop
                    if self.target is None or vector.distance(self.target.position, self.position) <= self.target.collision_radius + self.collision_radius + 0.1:
                        self.reeling = False #end reeling
                        self.casting = False
                        self.target.move_speed = self.target_ms
                        self.target.dash_river = False
                    else:
                        self.target.move_speed = 0 #immobilize
                        self.target.dash_river = True
                        self.target.position.add(self.position.subtracted(self.target.position).scaled(850*TILES_PER_MIN)) #reel to fisherman
                    
                else:
                    if self.target is None or vector.distance(self.target.position, self.position) <= self.target.collision_radius + self.collision_radius + self.hit_range:
                        self.reeling = False #end reeling
                        self.move_speed = self.normal_move_speed #return to normal movement
                        self.dash_river = False
                        self.target_lock = False
                        self.collideable = True
                    else:
                        self.move_speed = 450 * TILES_PER_MIN
                        self.dash_river = True
                        self.collideable = False
                    
    def attack(self):
        if self.dash_timer == 0: #if not dashings
            return FishermanAttackEntity(self.side, self.hit_damage, self.position, self.target)
        
class Void(Spell):
    def __init__(self, side, target, level):
        super().__init__(
            s=side,
            d=0,
            c_t_d=0,
            w=3,
            t=1,
            kb=0,
            r=2.5,
            v=0,
            tar=target
        )
        self.level = level
        '''self.single = 200 * pow(1.1, level - 6)
        self.medium = 100 * pow(1.1, level - 6)
        self.large = 47 * pow(1.1, level - 6)

        self.single_ctd = 30 * pow(1.1, level - 6)
        self.medium_ctd = 16 * pow(1.1, level - 6)
        self.large_ctd = 11 * pow(1.1, level - 6)'''

        self.single = 190 * pow(1.1, level - 6)
        self.medium = 100 * pow(1.1, level - 6) #normally 100, slight buff
        self.large = 55 * pow(1.1, level - 6)

        self.single_ctd = 30 * pow(1.1, level - 6)
        self.medium_ctd = 16 * pow(1.1, level - 6)
        self.large_ctd = 11 * pow(1.1, level - 6)

    def tick(self, arena):
        if self.preplace:
            return
     
        elif self.waves > 0 and self.damage_cd <= 0:
            self.sprite_path = f"sprites/{self.class_name}/{self.class_name}_hit.png"
            hits = self.detect_hits(arena)
            ctd = self.single_ctd if len(hits) == 1 else (self.medium_ctd if len(hits) <= 4 else self.large_ctd)
            dmg = self.single if len(hits) == 1 else (self.medium if len(hits) <= 4 else self.large)
            for each in hits:
                if (isinstance(each, Tower)):
                    each.damage(ctd)
                else:
                    each.damage(dmg); #end damage, start kb
            self.waves -= 1 #decrease waves
            self.damage_cd = self.time_between #reset cooldown
        elif self.damage_cd > 0:
            self.damage_cd -= TICK_TIME #decrement cooldown
        elif self.display_duration <= 0:
            self.should_delete = True #mark for deletion

class Tornado(Spell):
    def __init__(self, side, target, level):
        super().__init__(
            s=side,
            d=53*pow(1.1, level - 6),
            c_t_d=9.5*pow(1.1, level - 6),
            w=1,
            t=0.5,
            kb=0,
            r=5.5,
            v=0,
            tar=target
        )
        self.display_duration = 1.051
        self.level = level
        self.pulse_time = 0.05
        self.pulse_timer = 0

    def passive_effect(self, target):
        if isinstance(target, Troop) and target.moveable:
            total_kb = -1/5 * target.mass + 6
            mag = total_kb/21
            target.kb(self.position.subtracted(target.position).scaled(mag), 0.05)

class CannonCartAttackEntity(RangedAttackEntity):
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side, 
            damage=damage, 
            velocity=1000*TILES_PER_MIN, 
            position=position, 
            target=target
        )

class CannonCart(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 558 * pow(1.1, level - 6),         # Hit points (Example value)
            h_d= 133 * pow(1.1, level - 6),          # Hit damage (Example value)
            h_s=1,          # Hit speed (Seconds per hit)
            l_t=0.4,            # First hit cooldown
            h_r=5.5,            # Hit range
            s_r=6,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=3,            #mass
            c_r=0.6,        #collision radius
            p=position               # Position (vector.Vector object)
        )
        self.level = level

    def die(self, arena):
        arena.buildings.append(CartCannon(self.side, self.position, self.level, self.cloned))
        self.cur_hp = -1 #bypass curse checks
        arena.troops.remove(self)
    
    def attack(self):
        return CannonCartAttackEntity(self.side, self.hit_damage, self.position, self.target)

class CartCannonAttackEntity(RangedAttackEntity):
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            velocity=1000*TILES_PER_MIN,
            position=position,
            target=target,
        )


class CartCannon(Building):
    def __init__(self, side, position, level, cloned):
        super().__init__(
            s=side,
            h_p=513 * pow(1.1, level - 6),
            h_d = 133 * pow(1.1, level - 6),
            h_s = 0.9,
            l_t = 0,
            h_r = 5.51,
            s_r = 5.51,
            g = True,
            t_g_o = True,
            t_o = False,
            l=30,
            d_t=0.4,
            c_r=0.6,
            d_s_c=0,
            d_s=None,
            p=position,
            cloned=cloned
        )
        self.next_spawn = None
        self.remaining_spawn_count = 0
        self.level = level
    
    def attack(self):
        return CartCannonAttackEntity(self.side, self.hit_damage, self.position, self.target)
    
class GoblinMachineAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 1.2
    COLLISION_RADIUS = 0.6
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            position=position,
            target=target
            )


class GoblinMachineTargetIndicator(AttackEntity):
    def __init__(self, side, position):
        super().__init__(self, side, 0, float('inf'), position)
        self.display_size = 1.5

class GoblinMachineRocket(RangedAttackEntity):
    SPLASH_RADIUS = 1.5
    def __init__(self, side, damage, ctd, position, target):
        super().__init__(
            side=side, 
            damage=damage, 
            velocity=300*TILES_PER_MIN, 
            position=position, 
            target=target
        )
        self.homing = False
        self.set_move_vec()
        self.ctd = ctd
        self.exploded = False
        self.has_hit = []
        
    def tick(self, arena):
        self.tick_func(arena)
        if self.exploded:
            hits = self.detect_hits(arena)
            if len(hits) > 0:
                for each in hits:
                    self.has_hit.append(each)
                    if (isinstance(each, Tower)):
                        each.damage(self.ctd)
                    else:
                        each.damage(self.damage)
                    self.apply_effect(each)
        else:
            self.position.add(self.move_vec)
            if vector.distance(self.position, self.target) < 0.1:
                self.exploded = True
                self.display_size = 1.5
                self.duration = 0.1
        
    
    def detect_hits(self, arena):
        hits = []
        for each in arena.towers + arena.buildings + arena.troops:
            if each.side != self.side: # if different side
                if vector.distance(self.position, each.position) < self.SPLASH_RADIUS + each.collision_radius and each not in self.has_hit:
                    hits.append(each)

        return hits
    
class GoblinMachine(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 1908 * pow(1.1, level - 9),         # Hit points (Example value)
            h_d= 175 * pow(1.1, level - 9),          # Hit damage (Example value)
            h_s=1.2,          # Hit speed (Seconds per hit)
            l_t=0.7,            # First hit cooldown
            h_r=1.2,            # Hit range
            s_r=6,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=3,            #mass
            c_r=0.6,        #collision radius
            p=position               # Position (vector.Vector object)
        )
        self.level = level
        self.rocket_damage = 324 * pow(1.1, level - 9)
        self.rocket_ctd = 146 * pow(1.1, level - 9)
        self.rocket_hit_speed = 3.5
        self.rocket_load_time = 1.5
        self.rocket_cooldown = 1.5
        self.rocket_min = 2.5
        self.rocket_max = 5
        self.extra = 0
        self.rocket = None
        self.rocket_target = None
        self.rocket_indicator = GoblinMachineTargetIndicator(self.side, vector.Vector(0, 0))

    def level_up(self):
        self.rocket_damage *= 1.1
        self.rocket_ctd *= 1.1
        return super().level_up()

    def attack(self):
        return GoblinMachineAttackEntity(self.side, self.hit_damage, self.position, self.target)

    def tick_func(self, arena):
        if self.rocket_cooldown <= self.rocket_load_time and self.rocket_target is None:
            self.rocket_cooldown = self.rocket_load_time
        elif self.stun_timer <= 0:
            if self.rocket_cooldown <= 0:
                self.rocket = GoblinMachineRocket(self.side, self.rocket_damage, self.rocket_ctd, self.position, self.rocket_target)
                arena.active_attacks.append(self.rocket)
                self.rocket_cooldown = self.rocket_hit_speed
            else:
                self.rocket_cooldown -= TICK_TIME
        
        if self.rocket_target is None:
            self.update_rocket_target(arena)
            if self.rocket_target is not None:
                self.rocket_indicator.position = self.rocket_target
                arena.active_attacks.append(self.rocket_indicator)
        elif vector.distance(self.position, self.rocket_target) + self.collision_radius - self.extra < self.rocket_min:
            arena.active_attacks.remove(self.rocket_indicator)
            self.rocket_target = None

        if self.rocket is not None and self.rocket.exploded:
            self.update_rocket_target(arena)
            if self.rocket_target is None:
                if self.rocket_indicator in arena.active_attacks:
                    arena.active_attacks.remove(self.rocket_indicator)
            else:
                self.rocket_indicator.position = self.rocket_target
            self.rocket = None #release the rocket

    def die(self, arena):
        self.rocket_indicator.should_delete = True
        if self.rocket_indicator in arena.active_attacks:
            arena.active_attacks.remove(self.rocket_indicator)
        super().die(arena)
    
    def update_rocket_target(self, arena):
        self.rocket_target = None 
        self.extra = 0
        
        min_dist = self.rocket_max
        for each in arena.troops: #for each troop
            if each.targetable and each.side != self.side: #targets air or is ground only and each is ground troup
                dist = vector.distance(each.position, self.position)
                if dist > self.rocket_min and dist < min_dist and dist < self.rocket_max + self.collision_radius:
                    self.rocket_target = each.position
                    min_dist = vector.distance(each.position, self.position)
        for each in arena.buildings: #for each building, so if any building is closer then non tower targeting switches, or if tower targeting then finds closest building
            if each.side != self.side and each.targetable:
                dist = vector.distance(each.position, self.position)
                if dist < min_dist and dist < self.rocket_max + self.collision_radius:
                    self.rocket_target = each.position
                    min_dist = vector.distance(each.position, self.position)
        
        for tower in arena.towers: #check for towers that it can currently hit
            if tower.side != self.side:
                dist = vector.distance(tower.position, self.position)
                if dist - tower.collision_radius > self.rocket_min and dist < self.rocket_max + self.collision_radius + tower.collision_radius and dist < min_dist: #iff can hit tower, then it locks on.
                    self.extra = tower.collision_radius
                    self.rocket_target = tower.position #ensures only locks when activel attacking tower, so giant at bridge doesnt immediatly lock onto tower and ruin everyones day
                    min_dist = vector.distance(tower.position, self.position)

        self.rocket_target = copy.deepcopy(self.rocket_target)

class SpiritEmpressGroundAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 0.8
    COLLISION_RADIUS = 0.6
    def __init__(side, damage, position, target):
        super().__init__(side, damage, position, target)

class SpiritEmpressAttackEntity(RangedAttackEntity):
    def __init__(side, damage, position, target):
        super().__init__(
            side=side, 
            damage=damage, 
            velocity=800*TILES_PER_MIN, 
            position=position, 
            target=target
        )

class SpiritEmpressGround(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 919 * pow(1.1, level - 9),         # Hit points (Example value)
            h_d= 276 * pow(1.1, level - 9),          # Hit damage (Example value)
            h_s=1.1,          # Hit speed (Seconds per hit)
            l_t=0.8,            # First hit cooldown
            h_r=0.8,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=3,            #mass
            c_r=0.6,        #collision radius
            p=position               # Position (vector.Vector object)
        )
        self.level = level
    
    def attack(self):
        return SpiritEmpressGroundAttackEntity(self.hit_damage, self.position, self.target)

class SpiritEmpress(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 1068 * pow(1.1, level - 9),         # Hit points (Example value)
            h_d= 249 * pow(1.1, level - 9),          # Hit damage (Example value)
            h_s=1.4,          # Hit speed (Seconds per hit)
            l_t=1,            # First hit cooldown
            h_r=5,            # Hit range
            s_r=5.5,            # Sight Range
            g=False,           # Ground troop
            t_g_o=False,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=6,            #mass
            c_r=0.6,        #collision radius
            p=position               # Position (vector.Vector object)
        )
        self.level = level

    def attack(self):
        return SpiritEmpressAttackEntity(self.hit_damage, self.position, self.target)