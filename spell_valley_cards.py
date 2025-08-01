from abstract_classes import AttackEntity, RangedAttackEntity
from abstract_classes import Troop
from abstract_classes import Building
from abstract_classes import Tower
from abstract_classes import TILES_PER_MIN
from abstract_classes import TICK_TIME
import vector
import copy


    
class FireSpiritAttackEntity(AttackEntity):
    DAMAGE_RADIUS = 2.3
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
                    if vector.distance(self.position, each.position) < FireSpiritAttackEntity.DAMAGE_RADIUS + each.collision_radius:
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
            
            if vector.distance(self.position, self.target.position) < self.target.collision_radius:
                self.display_size = FireSpiritAttackEntity.DAMAGE_RADIUS 
                self.duration = 0.25
                self.exploded = True
    
class FireSpirit(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 90 * pow(1.1, level - 1),         # Hit points (Example value)
            h_d= 81 * pow(1.1, level - 1),          # Hit damage (Example value)
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
        return FireSpiritAttackEntity(self.side, self.hit_damage, self.position, self.target)


class ElectroSpiritAttackEntity(AttackEntity):
    CHAIN_RADIUS = 4
    MAX_CHAIN_HITS = 9
    def __init__(self, side, damage, position, target):
        super().__init__(
            s=side,
            d=damage,
            v=2000*TILES_PER_MIN,
            l=float('inf'),
            i_p=copy.deepcopy(position)
        )
        self.target = target
        self.chain_count = 0
        self.chain_center = target.position
        self.has_hit = [target]
        self.should_delete = False

    def detect_hits(self, arena):
        if vector.distance(self.position, self.target.position) < self.target.collision_radius:
            self.chain_count += 1
            return [self.target]
        return []
            
    def tick(self, arena):
        hits = self.detect_hits(arena)
        if len(hits) > 0:
                hits[0].stun()
                hits[0].damage(self.damage)
                self.should_delete = True
                self.chain_center = self.target.position
                if self.chain_count < ElectroSpiritAttackEntity.MAX_CHAIN_HITS: #if can still chain
                    min_dist = float("inf")
                    min = None
                    for each in arena.towers + arena.buildings + arena.troops: #find new hits
                        if (isinstance(each, Tower) or not each.invulnerable) and each.side != self.side and vector.distance(each.position, self.chain_center) < 4: # if different side
                            new = not any(each is h for h in self.has_hit)
                            if vector.distance(each.position, self.chain_center) < min_dist and new:
                                min = each
                                min_dist = vector.distance(each.position, self.chain_center)
                                
                    if not min is None:
                        self.target = min
                        self.has_hit.append(min)
                        self.should_delete = False
        else:
            direction = self.target.position.subtracted(self.position)
            direction.normalize()

            movement = direction.scaled(self.velocity)
            self.position.add(movement)

    def cleanup(self, arena): #also delete self if single target here in derived classes
        if self.should_delete:
            arena.active_attacks.remove(self)
    
class ElectroSpirit(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 90 * pow(1.1, level - 1),         # Hit points (Example value)
            h_d= 39 * pow(1.1, level - 1),          # Hit damage (Example value)
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
        return ElectroSpiritAttackEntity(self.side, self.hit_damage, self.position, self.target)

class WizardAttackEntity(AttackEntity):
    DAMAGE_RADIUS = 1.5
    def __init__(self, side, damage, position, target):
        super().__init__(
            s=side,
            d=damage,
            v=600*TILES_PER_MIN,
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
                    if vector.distance(self.position, each.position) < WizardAttackEntity.DAMAGE_RADIUS + each.collision_radius:
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
            
            if vector.distance(self.position, self.target.position) < self.target.collision_radius:
                self.display_size = WizardAttackEntity.DAMAGE_RADIUS
                self.duration =  0.1
                self.exploded = True
    
class Wizard(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 340 * pow(1.1, level - 3),         # Hit points (Example value)
            h_d= 133 * pow(1.1, level - 3),          # Hit damage (Example value)
            h_s=1.4,          # Hit speed (Seconds per hit)
            l_t=1,            # First hit cooldown
            h_r=5.5,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=False,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=5,            #mass
            c_r=0.5,        #collision radius
            p=position               # Position (vector.Vector object)
        ) 
        self.level = level
    
    def attack(self):
        return WizardAttackEntity(self.side, self.hit_damage, self.position, self.target)
    
class SkeletonDragonAttackEntity(AttackEntity):
    DAMAGE_RADIUS = 0.8
    def __init__(self, side, damage, position, target):
        super().__init__(
            s=side,
            d=damage,
            v=500*TILES_PER_MIN,
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
                    if vector.distance(self.position, each.position) < SkeletonDragonAttackEntity.DAMAGE_RADIUS + each.collision_radius:
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
            
            if vector.distance(self.position, self.target.position) < self.target.collision_radius:
                self.display_size = SkeletonDragonAttackEntity.DAMAGE_RADIUS
                self.duration =  0.25
                self.exploded = True
    
class SkeletonDragon(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 220 * pow(1.1, level - 1),         # Hit points (Example value)
            h_d= 63 * pow(1.1, level - 1),          # Hit damage (Example value)
            h_s=1.9,          # Hit speed (Seconds per hit)
            l_t=1.5,            # First hit cooldown
            h_r=3.5,            # Hit range
            s_r=5.5,            # Sight Range
            g=False,           # Ground troop
            t_g_o=False,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=4,            #mass
            c_r=0.9,        #collision radius
            p=position               # Position (vector.Vector object)
        ) 
        self.level = level
    
    def attack(self):
        return SkeletonDragonAttackEntity(self.side, self.hit_damage, self.position, self.target)
    
class InfernoTowerAttackEntity(RangedAttackEntity):
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            velocity=0,
            position=position,
            target=target,
        )
        self.duration = 0.4 + TICK_TIME
        self.hit = False

    def detect_hits(self, arena):
        return [self.target]

    def tick(self, arena):
        self.tick_func(arena)
        if not self.hit:
            hits = self.detect_hits(arena)
            if len(hits) > 0:
                for each in hits:
                    self.hit = True
                    each.damage(self.damage)
                    self.apply_effect(each)
        if self.target is None or self.target.cur_hp <= 0:
            self.should_delete = True

class InfernoTower(Building):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,
            h_p= 825 * pow(1.1, level - 3),
            h_d = 20 * pow(1.1, level - 3),
            h_s = 0.4,
            l_t = 1.2,
            h_r = 5.5,
            s_r = 5.5,
            g = True,
            t_g_o = False,
            t_o = False,
            l=30,
            d_t=1,
            c_r=0.6,
            d_s_c=0,
            d_s=None,
            p=position
        )
        self.level = level
        self.stage = 1
        self.damage_stages = [20 * pow(1.1, level - 3), 75 * pow(1.1, level - 3), 400 * pow(1.1, level - 3)]

        self.stage_duration = 2
    
    def stun(self):
        self.stun_timer = 0.5
        self.target = None
        self.stage = 1
        self.stage_duration = 2

    def freeze(self, duration):
        self.stage = 1
        self.stage_duration = 2
        self.attack_cooldown = self.load_time - self.hit_speed
        return super().freeze(duration)

    def attack(self):
        return InfernoTowerAttackEntity(self.side, self.damage_stages[self.stage - 1], self.position, self.target)
    
    def tick(self, arena):
        if self.preplace or self.stun_timer > 0:
            return
        #print(self.target) #temp
        if self.target is None or self.target.cur_hp <= 0 or self.target.targetable == False:
            self.update_target(arena)
            self.stage = 1
            self.stage_duration = 2
            self.attack_cooldown = self.load_time - self.hit_speed
        if self.target is not None and self.target.invulnerable:
            self.stage = 1
            self.stage_duration = 2
            self.attack_cooldown = self.load_time - self.hit_speed
        if not self.target is None and self.attack_cooldown <= 0:
            atk = self.attack()
            if isinstance(atk, list) and len(atk) > 0:
                arena.active_attacks.extend(atk)
            elif not atk is None:
                arena.active_attacks.append(self.attack())
            self.attack_cooldown = self.hit_speed

    def cleanup_func(self, arena):
        if self.stun_timer <= 0:
            if self.stage_duration <= 0:
                self.stage = self.stage + 1 if self.stage < 3 else self.stage
                self.stage_duration = 2
            elif not (self.target is None or self.target.cur_hp <= 0):
                self.stage_duration -= TICK_TIME
        else:
            self.stun_timer -= TICK_TIME

class BombTowerAttackEntity(AttackEntity):
    DAMAGE_RADIUS = 1.5
    def __init__(self, side, damage, position, target_pos):
        super().__init__(
            s=side,
            d=damage,
            v=500*TILES_PER_MIN,
            l=float('inf'),
            i_p=copy.deepcopy(position)
        )
        self.target_pos = target_pos
        self.exploded = False
        self.has_hit = []

    def detect_hits(self, arena):
        hits = []
        if self.exploded:
            for each in arena.towers + arena.buildings + arena.troops:
                if each.side != self.side and (isinstance(each, Tower) or (each.ground and not each.invulnerable)): # if different side
                    if vector.distance(self.position, each.position) < BombTowerAttackEntity.DAMAGE_RADIUS + each.collision_radius:
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
            direction = self.target_pos.subtracted(self.position)
            direction.normalize()

            movement = direction.scaled(self.velocity)
            self.position.add(movement)
            
            if vector.distance(self.position, self.target_pos) < 0.25:
                self.display_size = BombTowerAttackEntity.DAMAGE_RADIUS
                self.duration =  0.25
                self.exploded = True

class BombTower(Building):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,
            h_p=640 * pow(1.1, level - 3),
            h_d=105 * pow(1.1, level - 3),
            h_s=1.6,
            l_t=1.6,
            h_r=6,
            s_r=6,
            g=True,
            t_g_o=True,
            t_o=False,
            l=30,
            d_t=1,
            c_r=0.6,
            d_s_c=1,
            d_s=BombTowerDeathBomb,
            p=position
        )
        self.level = level

    def attack(self):
        return BombTowerAttackEntity(self.side, self.hit_damage, self.position, self.target.position)
    
class BombTowerDeathBombAttackEntity(AttackEntity):
    DAMAGE_RADIUS = 3
    def __init__(self, side, damage, position, target_pos):
        super().__init__(
            s=side,
            d=damage,
            v=0,
            l=0.25,
            i_p=copy.deepcopy(position)
        )
        self.display_size = BombTowerDeathBombAttackEntity.DAMAGE_RADIUS
        self.has_hit = []

    def detect_hits(self, arena):
        hits = []
        for each in arena.towers + arena.buildings + arena.troops:
            if each.side != self.side and (isinstance(each, Tower) or not each.invulnerable): # if different side
                if vector.distance(self.position, each.position) < BombTowerDeathBombAttackEntity.DAMAGE_RADIUS + each.collision_radius:
                    hits.append(each)
        return hits
            
    def tick(self, arena):
        hits = self.detect_hits(arena)
        for each in hits:
            new = not any(each is h for h in self.has_hit)
            if (new):
                each.damage(self.damage)
                self.has_hit.append(each)


class BombTowerDeathBomb(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p=  float('inf'),         # Hit points (Example value)
            h_d= 105 * pow(1.1, level - 3),          # Hit damage (Example value)
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
        self.moveable=False
        self.targetable=False
        self.target=None

    def tick(self, arena):
        if self.deploy_time <= 0:
            arena.active_attacks.append(self.attack())
            self.cur_hp = -1
    
    def attack(self):
        return BombTowerDeathBombAttackEntity(self.side, self.hit_damage, self.position, self.target)