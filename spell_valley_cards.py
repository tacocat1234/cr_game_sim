from abstract_classes import AttackEntity
from abstract_classes import Troop
from abstract_classes import Building
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
                if each.side != self.side: # if different side
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
                        if each.side != self.side and vector.distance(each.position, self.chain_center) < 4: # if different side
                            new = not any(each is h for h in self.has_hit)
                            if vector.distance(each.position, self.chain_center) < min_dist and new:
                                min = each
                                min_dist = vector.distance(each.position, self.chain_center)
                                
                    if not min is None:
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