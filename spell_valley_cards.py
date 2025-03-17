from abstract_classes import AttackEntity
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
                    each.cur_hp -= self.damage
                    self.has_hit.append(each)
        else:
            direction = self.target.position.subtracted(self.position)
            direction.normalize()

            movement = direction.scaled(self.velocity)
            self.position.add(movement)
            
            if vector.distance(self.position, self.target.position) < self.target.collision_radius:
                self.display_size = FireSpiritAttackEntity.DAMAGE_RADIUS 
                self.duration =  0.5
                self.exploded = True
    
class FireSpirit(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 90 * pow(1.1, level - 1),         # Hit points (Example value)
            h_d= 81 * pow(1.1, level - 1),          # Hit damage (Example value)
            h_s=0.3,          # Hit speed (Seconds per hit)
            l_t=0.1,            # First hit cooldown
            h_r=2,            # Hit range
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
    
    def attack(self):
        self.should_delete = True
        return FireSpiritAttackEntity(self.side, self.hit_damage, self.position, self.target)

    def cleanup(self, arena): # each troop runs this after ALL ticks are finished
        if self.cur_hp <= 0 or self.should_delete:
                self.cur_hp = -1
                arena.troops.remove(self)
            
        if self.deploy_time > 0: #if deploying, timer
                self.deploy_time -= TICK_TIME
        elif self.stun_timer <= 0:
            if not self.target is None and not vector.distance(self.target.position, self.position) < self.hit_range + self.target.collision_radius + self.collision_radius and (self.attack_cooldown <= self.hit_speed - self.load_time):
                self.attack_cooldown = self.hit_speed - self.load_time #if not currently attacking but cooldown is less than first hit delay
            else: #otherwise
                self.attack_cooldown -= TICK_TIME #decrement time if either close enough to attack, cooldown greater than min cooldown, or both
        else:
            self.stun_timer -= TICK_TIME

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
                hits[0].cur_hp -= self.damage
                self.should_delete = True
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
            h_r=2,            # Hit range
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
    
    def attack(self):
        self.should_delete = True
        return ElectroSpiritAttackEntity(self.side, self.hit_damage, self.position, self.target)

    def cleanup(self, arena): # each troop runs this after ALL ticks are finished
        if self.cur_hp <= 0 or self.should_delete:
                self.cur_hp = -1
                arena.troops.remove(self)
            
        if self.deploy_time > 0: #if deploying, timer
                self.deploy_time -= TICK_TIME
        elif self.stun_timer <= 0:
            if not self.target is None and not vector.distance(self.target.position, self.position) < self.hit_range + self.target.collision_radius + self.collision_radius and (self.attack_cooldown <= self.hit_speed - self.load_time):
                self.attack_cooldown = self.hit_speed - self.load_time #if not currently attacking but cooldown is less than first hit delay
            else: #otherwise
                self.attack_cooldown -= TICK_TIME #decrement time if either close enough to attack, cooldown greater than min cooldown, or both
        else:
            self.stun_timer -= TICK_TIME

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
                    each.cur_hp -= self.damage
                    self.has_hit.append(each)
        else:
            direction = self.target.position.subtracted(self.position)
            direction.normalize()

            movement = direction.scaled(self.velocity)
            self.position.add(movement)
            
            if vector.distance(self.position, self.target.position) < self.target.collision_radius:
                self.display_size = WizardAttackEntity.DAMAGE_RADIUS
                self.duration =  0.25
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
                    each.cur_hp -= self.damage
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
    
class InfernoTowerAttackEntity(AttackEntity):
    def __init__(self, side, damage, position, target):
        super().__init__(
            s=side,
            d=damage,
            v=2000*TILES_PER_MIN,
            l=float('inf'),
            i_p=copy.deepcopy(position)
        )
        self.target = target
        self.should_delete = False

    def detect_hits(self, arena):
        if (vector.distance(self.target.position, self.position) < self.target.collision_radius):
            return [self.target] # has hit
        else:
            return [] #hasnt hit yet
            
    def tick(self, arena):
        hits = self.detect_hits(arena)
        if len(hits) > 0:
            hits[0].cur_hp -= self.damage
            self.should_delete = True
        else:
            direction = vector.Vector(
                self.target.position.x - self.position.x, 
                self.target.position.y - self.position.y
            )
            direction.normalize()

            movement = direction.scaled(self.velocity)
            self.position.add(movement)

    def cleanup(self, arena):
        if self.should_delete:
            arena.active_attacks.remove(self)


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
        self.stage - 1
        self.stage_duration = 2

    def attack(self):
        return InfernoTowerAttackEntity(self.side, self.damage_stages[self.stage - 1], self.position, self.target)
    
    def tick(self, arena):
        #print(self.target) #temp
        if self.target is None or self.target.cur_hp <= 0:
            self.update_target(arena)
            self.stage = 1
            self.attack_cooldown = self.load_time - self.hit_speed
        if not self.target is None and self.attack_cooldown <= 0:
            atk = self.attack()
            if isinstance(atk, list) and len(atk) > 0:
                arena.active_attacks.extend(atk)
            elif not atk is None:
                arena.active_attacks.append(self.attack())
            self.attack_cooldown = self.hit_speed

    def cleanup(self, arena):
        #print(self.cur_hp) #temp
        self.cur_hp -= self.hit_points * TICK_TIME / self.lifespan
        if self.cur_hp <= 0:
            arena.buildings.remove(self)
        
        if self.stun_timer <= 0:
            self.attack_cooldown -= TICK_TIME
            if self.stage_duration <= 0:
                self.stage = self.stage + 1 if self.stage < 3 else self.stage
                self.stage_duration = 2
            else:
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
                    each.cur_hp -= self.damage
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
            if each.side != self.side and (isinstance(each, Tower) or (each.ground and not each.invulnerable)): # if different side
                if vector.distance(self.position, each.position) < BombTowerDeathBombAttackEntity.DAMAGE_RADIUS + each.collision_radius:
                    hits.append(each)
        return hits
            
    def tick(self, arena):
        hits = self.detect_hits(arena)
        for each in hits:
            new = not any(each is h for h in self.has_hit)
            if (new):
                each.cur_hp -= self.damage
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
        self.targetable=False
        self.target=None

    def tick(self, arena):
        if self.deploy_time <= 0:
            arena.active_attacks.append(self.attack())
            self.cur_hp = -1
    
    def attack(self):
        return BombTowerDeathBombAttackEntity(self.side, self.hit_damage, self.position, self.target)