from abstract_classes import MeleeAttackEntity
from abstract_classes import AttackEntity
from abstract_classes import Troop
from abstract_classes import Tower
from abstract_classes import Spell
from abstract_classes import Building
from abstract_classes import TILES_PER_MIN
from abstract_classes import TICK_TIME
import vector
import copy
import math

class GiantSnowball(Spell):
    def __init__(self, side, target, level):
        super().__init__(
            s=side,
            d=75 * pow(1.1, level - 1),
            c_t_d=23 * pow(1.1, level - 1),
            w=1,
            t=0,
            kb=1.8,
            r=2.5,
            v=800*TILES_PER_MIN,
            tar=target
        )

    def apply_effect(self, target):
        target.slow(2.5, "giantsnowball")

class IceSpiritAttackEntity(AttackEntity):
    DAMAGE_RADIUS = 1.5
    FREEZE_DURATION = 1.2
    def __init__(self, side, damage, position, target):
        super().__init__(
            s=side,
            d=damage,
            v=400*TILES_PER_MIN,
            l=float('inf'),
            i_p=copy.deepcopy(position)
        )
        self.target = target
        self.exploded = False
        self.has_hit = []

    def detect_hits(self, arena):
        hits = []
        if self.exploded:
            for each in arena.towers + arena.buildings + arena.troops:
                if (isinstance(each, Tower) or not each.invulnerable) and each.side != self.side: # if different side
                    if vector.distance(self.position, each.position) < IceSpiritAttackEntity.DAMAGE_RADIUS + each.collision_radius:
                        hits.append(each)
        return hits
            
    def tick(self, arena):
        if self.exploded:
            hits = self.detect_hits(arena)
            for each in hits:
                new = not any(each is h for h in self.has_hit)
                if (new):
                    each.damage(self.damage)
                    each.target = None
                    each.freeze(self.FREEZE_DURATION)
                    self.has_hit.append(each)
        else:
            direction = self.target.position.subtracted(self.position)
            direction.normalize()

            movement = direction.scaled(self.velocity)
            self.position.add(movement)
            
            if vector.distance(self.position, self.target.position) < self.target.collision_radius:
                self.display_size = IceSpiritAttackEntity.DAMAGE_RADIUS 
                self.duration =  0.25
                self.exploded = True
    
class IceSpirit(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 90 * pow(1.1, level - 1),         # Hit points (Example value)
            h_d= 43 * pow(1.1, level - 1),          # Hit damage (Example value)
            h_s=0.3,          # Hit speed (Seconds per hit)
            l_t=0.1,            # First hit cooldown
            h_r=2.5,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=False,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=120*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=1,            #mass
            c_r=0.4,        #collision radius
            p=position               # Position (vector.Vector object)
        ) 
        self.level = level
        self.should_delete = False
        self.walk_cycle_frames = 4
        class_name = self.__class__.__name__.lower()
        self.sprite_path = f"sprites/{class_name}/{class_name}_0.png"
    
    def attack(self):
        self.should_delete = True
        return IceSpiritAttackEntity(self.side, self.hit_damage, self.position, self.target)

class IceGolemAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 0.75
    COLLISION_RADIUS = 0.7
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            position=position,
            target=target
            )

class IceGolemDeathAttackEntity(AttackEntity):
    SPLASH_RADIUS = 2
    def __init__(self, side, damage, position, target_pos):
        super().__init__(
            s=side,
            d=damage,
            v=0,
            l=0.25,
            i_p=copy.deepcopy(position)
        )
        self.display_size = self.SPLASH_RADIUS

    def apply_effect(self, target):
        target.slow(2.5, "icegolemdeathattackentity")
    
    def detect_hits(self, arena):
        hits = []
        for each in arena.towers + arena.buildings + arena.troops:
            if each.side != self.side and (isinstance(each, Tower) or (each.ground and not each.invulnerable)): # if different side
                if vector.distance(self.position, each.position) < self.SPLASH_RADIUS + each.collision_radius:
                        hits.append(each)

        return hits

class IceGolem(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 565 * pow(1.1, level - 3),         # Hit points (Example value)
            h_d= 40 * pow(1.1, level - 3),          # Hit damage (Example value)
            h_s=2.5,          # Hit speed (Seconds per hit)
            l_t=1.5,            # First hit cooldown
            h_r=0.75,            # Hit range
            s_r=7,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=True,        # Not tower-only
            m_s=45*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=6,            #mass
            c_r=0.7,        #collision radius
            p=position               # Position (vector.Vector object)
        )
        self.level = level
        self.ticks_per_frame = 6
        self.walk_cycle_frames = 6
        class_name = self.__class__.__name__.lower()
        self.sprite_path = f"sprites/{class_name}/{class_name}_0.png"
    def attack(self):
        return IceGolemAttackEntity(self.side, self.hit_damage, self.position, self.target)
    def die(self, arena):
        arena.active_attacks.append(IceGolemDeathAttackEntity(self.side, self.hit_damage, self.position, self.target))
        super().die(arena)

class Freeze(Spell):
    def __init__(self, side, target, level):
        super().__init__(
            s=side,
            d=72 * pow(1.1, level - 6),
            c_t_d=22 * pow(1.1, level - 6),
            w=1,
            t=0,
            kb=0,
            r=3,
            v=0,
            tar=target
        )
        self.display_duration = 4

    def apply_effect(self, target):
        target.freeze(4)

class Lightning(Spell):
    def __init__(self, side, target, level):
        super().__init__(
            s=side,
            d=660 * pow(1.1, level - 6),
            c_t_d=198 * pow(1.1, level - 6),
            w=3,
            t=0.46,
            kb=0,
            r=3.5,
            v=0,
            tar=target
        )
        self.has_hit = []
    
    def detect_hits(self, arena): #override
        max = None
        for each in arena.troops + arena.buildings + arena.towers:
            if not each in self.has_hit:
                if not each.invulnerable and each.side != self.side and (vector.distance(each.position, self.position) <= self.radius + each.collision_radius):
                    if max is None or each.cur_hp > max.cur_hp:
                        max = each
        
        if max is not None:
            self.has_hit.append(max)
            return [max]
        else:
            return []

    def apply_effect(self, target):
        target.stun()

class BattleHealerSpawnHealAttackEntity(AttackEntity):
    TICK_PERIOD = 0.25
    RADIUS = 2.5
    def __init__(self, side, heal_amount, pos, parent):
        super().__init__(
            s=side,
            d=0,
            v=0,
            l=2.01,
            i_p=pos
            )
        self.heal_amount = heal_amount
        self.display_size = self.RADIUS
        self.wave_timer = 0
        self.parent = parent

    def cleanup_func(self, arena):
        if self.wave_timer <= 0:
            self.has_hit = []
            self.wave_timer = self.TICK_PERIOD
        else:
            self.wave_timer -= TICK_TIME

    def detect_hits(self, arena):
        hits = []
        for each in arena.troops:
            if each is not self.parent and each.side == self.side and not each in self.has_hit and vector.distance(self.position, each.position) < self.RADIUS:
                hits.append(each)
        return hits

    def apply_effect(self, target):
        target.heal(self.heal_amount)

class BattleHealerActiveHealAttackEntity(AttackEntity):
    TICK_PERIOD = 0.25
    RADIUS = 4
    def __init__(self, side, heal_amount, pos, parent):
        super().__init__(
            s=side,
            d=0,
            v=0,
            l=1.05,
            i_p=pos
            )
        self.heal_amount = heal_amount
        self.wave_timer = 0
        self.has_hit = []
        self.display_size = self.RADIUS
        self.parent = parent

    def cleanup_func(self, arena):
        if self.wave_timer <= 0:
            self.has_hit = []
            self.wave_timer = self.TICK_PERIOD
        else:
            self.wave_timer -= TICK_TIME

    def detect_hits(self, arena):
        hits = []
        for each in arena.troops:
            if each is not self.parent and each.side == self.side and not each in self.has_hit and vector.distance(self.position, each.position) < self.RADIUS:
                hits.append(each)
        return hits
    
    def apply_effect(self, target):
        target.heal(self.heal_amount)

class BattleHealerAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 1.6
    COLLISION_RADIUS = 0.5
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            position=position,
            target=target
            )

class BattleHealer(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 810 * pow(1.1, level - 3),         # Hit points (Example value)
            h_d= 70 * pow(1.1, level - 3),          # Hit damage (Example value)
            h_s=1.5,          # Hit speed (Seconds per hit)
            l_t=1.2,            # First hit cooldown
            h_r=0.75,            # Hit range
            s_r=7,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=6,            #mass
            c_r=0.5,        #collision radius
            p=position               # Position (vector.Vector object)
        )
        self.level = level
        self.ticks_per_frame = 6
        self.walk_cycle_frames = 6
        class_name = self.__class__.__name__.lower()

        self.cross_river = True
        self.jump_speed = 60*TILES_PER_MIN

        self.spawn_heal = 95 * pow(1.1, level - 3) / 4
        self.active_heal = 48 * pow(1.1, level - 3) / 4
        self.self_heal = 16 * pow(1.1, level - 3) # per second
        self.self_heal_timer = 0

        self.sprite_path = f"sprites/{class_name}/{class_name}_0.png"

    def level_up(self):
        self.self_heal *= 1.1
        self.active_heal *= 1.1
        super().level_up()

    def cleanup_func(self, arena):
        if self.self_heal_timer <= 0:
            self.heal(self.self_heal)
            self.self_heal_timer = 1
        else:
            self.self_heal_timer -= TICK_TIME

    def on_deploy(self, arena):
        arena.active_attacks.append(BattleHealerSpawnHealAttackEntity(self.side, self.spawn_heal, self.position, self))

    def attack(self):
        return [BattleHealerAttackEntity(self.side, self.hit_damage, self.position, self.target),
                BattleHealerActiveHealAttackEntity(self.side, self.active_heal, self.position, self)]

class GiantSkeletonAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 0.8
    COLLISION_RADIUS = 1
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            position=position,
            target=target
            )

class GiantSkeleton(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 2140 * pow(1.1, level - 6),         # Hit points (Example value)
            h_d= 167 * pow(1.1, level - 6),          # Hit damage (Example value)
            h_s=1.4,          # Hit speed (Seconds per hit)
            l_t=1.1,            # First hit cooldown
            h_r=0.8,            # Hit range
            s_r=5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=18,            #mass
            c_r=1,        #collision radius
            p=position               # Position (vector.Vector object)
        )
        self.level = level
        self.can_kb = False
        self.ticks_per_frame = 6
        self.walk_cycle_frames = 6
        class_name = self.__class__.__name__.lower()
        self.sprite_path = f"sprites/{class_name}/{class_name}_0.png"
    
    def attack(self):
        return GiantSkeletonAttackEntity(self.side, self.hit_damage, self.position, self.target)

    def die(self, arena):
        arena.troops.append(GiantSkeletonDeathBomb(self.side, self.position, self.level))
        super().die(arena)

class GiantSkeletonDeathBombAttackEntity(AttackEntity):
    DAMAGE_RADIUS = 3
    def __init__(self, side, damage, position):
        super().__init__(
            s=side,
            d=damage,
            v=0,
            l=0.25,
            i_p=copy.deepcopy(position)
        )
        self.display_size = GiantSkeletonDeathBombAttackEntity.DAMAGE_RADIUS
        self.has_hit = []

    def detect_hits(self, arena):
        hits = []
        for each in arena.towers + arena.buildings + arena.troops:
            if each.side != self.side and (isinstance(each, Tower) or not each.invulnerable): # if different side
                if vector.distance(self.position, each.position) < GiantSkeletonDeathBombAttackEntity.DAMAGE_RADIUS + each.collision_radius:
                    hits.append(each)
        return hits
            
    def tick(self, arena):
        hits = self.detect_hits(arena)
        for each in hits:
            new = not any(each is h for h in self.has_hit)
            if (new):
                if isinstance(each, Tower) or isinstance(each, Building):
                    each.damage(self.damage * 2)
                elif each.can_kb and not each.invulnerable:
                    each.damage(self.damage)
                    vec = each.position.subtracted(self.position)
                    vec.normalize()
                    vec.scale(1.8)
                    each.kb(vec)
                self.has_hit.append(each)


class GiantSkeletonDeathBomb(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p=  float('inf'),         # Hit points (Example value)
            h_d= 334 * pow(1.1, level - 6),          # Hit damage (Example value)
            h_s=0,          # Hit speed (Seconds per hit)
            l_t=0,            # First hit cooldown
            h_r=0,            # Hit range
            s_r=0,            # Sight Range
            g=True,           # Ground troop
            t_g_o=False,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=0,          # Movement speed 
            d_t=3,            # Deploy time
            m=float('inf'),            #mass
            c_r=0.45,        #collision radius
            p=position               # Position (vector.Vector object)
        ) 
        self.level = level
        self.invulnerable=True
        self.moveable = False
        self.targetable=False
        self.target=None

    def tick(self, arena):
        if self.deploy_time <= 0:
            arena.active_attacks.append(self.attack())
            self.cur_hp = -1
    
    def attack(self):
        return GiantSkeletonDeathBombAttackEntity(self.side, self.hit_damage, self.position)
    
class VinesDisplayEntity(AttackEntity):
    def __init__(self, side, target):
        super().__init__(side, 0, 0, 0.47*5, target.position)
        self.display_size = target.collision_radius + 0.2
    
class Vines(Spell):
    def __init__(self, side, target, level):
        super().__init__(
            s=side,
            d=41 * pow(1.1, level - 6),
            c_t_d=9 * pow(1.1, level - 6),
            w=5,
            t=0.47,
            kb=0,
            r=2.5,
            v=0,
            tar=target
        )
        self.has_hit = []
        self.did_ground = []
        self.display_duration = 0.47*5+0.1

    def apply_effect(self, each):
        self.did_ground.append(each.ground)
        each.ground = True
        each.stun() #stun effects
        each.stun_timer = self.waves * self.time_between #real timer

    def tick(self, arena):
        if len(self.has_hit) == 0:
            self.detect_initial_hits(arena)
            for each in self.has_hit:
                arena.active_attacks.append(VinesDisplayEntity(self.side, each))
                self.apply_effect(each) #stun all hits
            self.damage_cd = 0
        elif self.waves > 0 and self.damage_cd <= 0:
            for each in self.has_hit:
                if not each.invulnerable or (each.__class__.__name__ == "Tesla" or each.__class__.__name__ == "EvolutionTesla"):
                    if (isinstance(each, Tower)):
                        each.damage(self.crown_tower_damage)
                    else:
                        each.damage(self.damage); #end damage, start kb
            self.waves -= 1 #decrease waves
            if self.waves > 0:
                self.damage_cd = self.time_between #reset cooldown

    def cleanup(self, arena):
        if self.preplace:
            return
        self.damage_cd -= TICK_TIME
        if self.should_delete or self.display_duration <= 0:
            i = 0
            for each in self.has_hit:
                each.ground = self.did_ground[i]
                i += 1
            arena.spells.remove(self) #delete
        self.display_duration -= TICK_TIME

    def detect_initial_hits(self, arena): #override
        out = []
        for _ in range(3):
            max = None
            for each in arena.troops + arena.buildings + arena.towers:
                if not each in self.has_hit:
                    if not each.invulnerable and each.side != self.side and (vector.distance(each.position, self.position) <= self.radius + each.collision_radius):
                        if max is None or each.cur_hp > max.cur_hp:
                            max = each

            if max is not None:
                self.has_hit.append(max)
                out.append(max)
        return out
    
    