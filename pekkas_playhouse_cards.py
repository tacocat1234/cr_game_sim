from abstract_classes import RangedAttackEntity
from abstract_classes import MeleeAttackEntity
from abstract_classes import Troop
from abstract_classes import Spell
from abstract_classes import Tower
from abstract_classes import Building
from abstract_classes import TILES_PER_MIN
from abstract_classes import TICK_TIME
from bone_pit_cards import Skeleton
from goblin_stadium_cards import Goblin
import vector
import copy
import math

class PekkaAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 1.2
    COLLISION_RADIUS = 0.75
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            position=position,
            target=target
            )

class Pekka(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 2350 * pow(1.1, level - 6),         # Hit points (Example value)
            h_d= 510 * pow(1.1, level - 6),          # Hit damage (Example value)
            h_s=1.8,          # Hit speed (Seconds per hit)
            l_t=1.3,            # First hit cooldown
            h_r=1.2,            # Hit range
            s_r=5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=45*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=18,            #mass
            c_r=0.75,        #collision radius
            p=position               # Position (vector.Vector object)
        ) 
        self.level = level
        self.can_kb = False
    def attack(self):
        return PekkaAttackEntity(self.side, self.hit_damage, self.position, self.target)

class BabyDragonAttackEntity(RangedAttackEntity):
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            velocity=500*TILES_PER_MIN,
            position=position,
            target=target,
        )
        self.exploded = False
        self.has_hit = []        

    def detect_hits(self, arena):
        hits = []
        if self.exploded:
            for each in arena.towers + arena.buildings + arena.troops:
                if each.side != self.side and not each.invulnerable: # if different side
                    if vector.distance(self.position, each.position) < 2 + each.collision_radius:
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
            direction = self.target.position.subtracted(self.position)
            direction.normalize()

            movement = direction.scaled(self.velocity)
            self.position.add(movement)
            
            if vector.distance(self.position, self.target.position) < 0.25:
                self.display_size = 2
                self.duration =  0.1
                self.exploded = True

class BabyDragon(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 720 * pow(1.1, level - 6),         # Hit points (Example value)
            h_d= 100 * pow(1.1, level - 6),          # Hit damage (Example value)
            h_s=1.5,          # Hit speed (Seconds per hit)
            l_t=1.2,            # First hit cooldown
            h_r=3.5,            # Hit range
            s_r=5.5,            # Sight Range
            g=False,           # Ground troop
            t_g_o=False,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=90*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=5,            #mass
            c_r=0.5,        #collision radius
            p=position               # Position (vector.Vector object)
        ) 
        self.level = level
    
    def attack(self):
        return BabyDragonAttackEntity(self.side, self.hit_damage, self.position, self.target)
    
class WitchAttackEntity(RangedAttackEntity):
    SPLASH_RADIUS = 1
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            velocity=600*TILES_PER_MIN,
            position=position,
            target=target,
        )
        self.exploded = False
        self.has_hit = []        

    def detect_hits(self, arena):
        hits = []
        if self.exploded:
            for each in arena.towers + arena.buildings + arena.troops:
                if each.side != self.side and (isinstance(each, Tower) or (not each.invulnerable)): # if different side
                    if vector.distance(self.position, each.position) < self.SPLASH_RADIUS + each.collision_radius:
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
            direction = self.target.position.subtracted(self.position)
            direction.normalize()

            movement = direction.scaled(self.velocity)
            self.position.add(movement)
            
            if vector.distance(self.position, self.target.position) < 0.25:
                self.display_size = self.SPLASH_RADIUS
                self.duration =  0.1
                self.exploded = True

class Witch(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 524 * pow(1.1, level - 6),         # Hit points (Example value)
            h_d= 84 * pow(1.1, level - 6),          # Hit damage (Example value)
            h_s=1.1,          # Hit speed (Seconds per hit)
            l_t=0.4,            # First hit cooldown
            h_r=5.5,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=False,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=8,            #mass
            c_r=0.5,        #collision radius
            p=position               # Position (vector.Vector object)
        ) 
        self.level = level
        self.spawn_time = 7
        self.spawn_timer = 1
    
    def tick(self, arena):
        if self.preplace:
            return
        self.tick_func(arena)

        if self.kb_timer > 0:
            self.kb_timer -= TICK_TIME #akward but better to keep it contained
            self.kb_tick()
        else:
            self.kb_vector = None
        
        self.spawn_timer -= TICK_TIME

        #update arena before
        if self.stun_timer <= 0:
            if self.deploy_time <= 0:
                if self.target is None or self.target.targetable == False or self.target.cur_hp <= 0:
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
        s1 = Skeleton(self.side, self.position.added(vector.Vector(2, 0)), self.level, self.cloned)
        s1.deploy_time = 0
        arena.troops.append(s1)

        s2 = Skeleton(self.side, self.position.added(vector.Vector(-2, 0)), self.level, self.cloned)
        s2.deploy_time = 0
        arena.troops.append(s2)

        s3 = Skeleton(self.side, self.position.added(vector.Vector(0, 2)), self.level, self.cloned)
        s3.deploy_time = 0
        arena.troops.append(s3)

        s4 = Skeleton(self.side, self.position.added(vector.Vector(0, -2)), self.level, self.cloned)
        s4.deploy_time = 0
        arena.troops.append(s4)


    def attack(self):
        return WitchAttackEntity(self.side, self.hit_damage, self.position, self.target)

class GuardAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 1.6
    COLLISION_RADIUS = 0.5
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            position=position,
            target=target
            )

class Guard(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 51 * pow(1.1, level - 6),         # Hit points (Example value)
            h_d= 76 * pow(1.1, level - 6),          # Hit damage (Example value)
            h_s=1,          # Hit speed (Seconds per hit)
            l_t=0.6,            # First hit cooldown
            h_r=1.6,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=90*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=1,            #mass
            c_r=0.5,        #collision radius
            p=position               # Position (vector.Vector object)
        )
        self.level = level
        self.has_shield = True
        self.shield_max_hp = 150 * pow(1.1, level - 6)
        self.shield_hp = self.shield_max_hp

        self.ticks_per_frame = 12
        self.walk_cycle_frames = 4
        class_name = self.__class__.__name__.lower()
        self.sprite_path = f"sprites/{class_name}/{class_name}_0.png"

    def level_up(self):
        self.shield_max_hp *= 1.1
        self.shield_hp *= 1.1
        return super().level_up()

    def damage(self, amount):
        if self.shield_hp > 0:
            self.shield_hp -= amount * self.damage_amplification
        else:
            self.cur_hp -= amount * self.damage_amplification

    def attack(self):
        return GuardAttackEntity(self.side, self.hit_damage, self.position, self.target)
    
class FakeGoblinAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 0.5
    COLLISION_RADIUS = 0.5
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            position=position,
            target=target
            )
    
class FakeGoblin(Troop):
    def __init__(self, side, position, level, cloned=False):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 31.6 * pow(1.1, level - 1),         # Hit points (Example value)
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
        return FakeGoblinAttackEntity(self.side, self.hit_damage, self.position, self.target)
    
class GoblinBarrel(Spell):
    def __init__(self, side, target, level, fake=False):
        super().__init__(
            s=side,
            d=0,
            c_t_d=0,
            w=1,
            t=0,
            kb=0,
            r=1.5,
            v=400*TILES_PER_MIN,
            tar=target
        )
        self.level = level
        self.fake = fake

    def tick_func(self, arena):
        pass
    
    def tick(self, arena):
        if self.preplace:
            return
        self.tick_func(arena)

        if self.spawn_timer > 0:
            tower_to_target  = self.target_pos.subtracted(self.king_pos)
            self.position.add(tower_to_target.scaled(self.velocity / tower_to_target.magnitude()))
            self.spawn_timer -= 1 #spawn in
        elif self.waves > 0:
            summon_type = FakeGoblin if self.fake else Goblin
            flip = 1 if self.side else -1
            pos1 = vector.Vector(0, 1/2 * flip)
            pos2 = vector.Vector(-math.sqrt(3)/4, -1/4 * flip)
            pos3 = vector.Vector(math.sqrt(3)/4, -1/4 * flip)
            arena.troops.extend([summon_type(self.side, self.position.added(pos1), self.level), 
                    summon_type(self.side, self.position.added(pos2), self.level),
                    summon_type(self.side, self.position.added(pos3), self.level)])
            self.damage_cd = self.time_between #reset cooldown
            self.waves = 0
        else:
            self.should_delete = True #mark for deletion