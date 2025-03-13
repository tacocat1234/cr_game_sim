from abstract_classes import AttackEntity
from abstract_classes import Troop
from abstract_classes import Building
from abstract_classes import TILES_PER_MIN
from abstract_classes import TICK_TIME
import vector
import copy

class BarbarianAttackEntity(AttackEntity):
    HIT_RANGE = 0.7
    COLLISION_RADIUS = 0.5
    def __init__(self, side, damage, position, target):
        super().__init__(
            s=side,
            d=damage,
            v=0,
            l=0.5,
            i_p=position
            )
        self.target = target
        self.should_delete = False
    
    def detect_hits(self, arena):
        
        if (vector.distance(self.target.position, self.position) <= BarbarianAttackEntity.HIT_RANGE + BarbarianAttackEntity.COLLISION_RADIUS + self.target.collision_radius): #within hitrange of knight
            return [self.target]
        else:
            return [] #theoretically should never trigger, when attack, should always be in range unless very strange circumstances
        
    def tick(self, arena):
        hits = self.detect_hits(arena)
        if len(hits) > 0:
            hits[0].cur_hp -= self.damage
            self.should_delete = True

    def cleanup(self, arena): #also delete self if single target here in derived classes
        self.duration -= TICK_TIME
        if self.duration <= 0:
            arena.active_attacks.remove(self)
        if self.should_delete:
            arena.active_attacks.remove(self)
        
            
class Barbarian(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 262 * pow(1.1, level - 1),         # Hit points (Example value)
            h_d= 75 * pow(1.1, level - 1),          # Hit damage (Example value)
            h_s=1.3,          # Hit speed (Seconds per hit)
            l_t=0.9,            # First hit cooldown
            h_r=0.7,            # Hit range
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
    def attack(self):
        return BarbarianAttackEntity(self.side, self.hit_damage, self.position, self.target)
    
class CannonAttackEntity(AttackEntity):
    def __init__(self, side, damage, position, target):
        super().__init__(
            s=side,
            d=damage,
            v=1000*TILES_PER_MIN,
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


class Cannon(Building):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,
            h_p=322 * pow(1.1, level - 3),
            h_d = 83 * pow(1.1, level - 3),
            h_s = 0.9,
            l_t = 0,
            h_r = 5.5,
            s_r = 5.5,
            g = True,
            t_g_o = True,
            t_o = False,
            l=30,
            d_t=1,
            c_r=0.6,
            d_s_c=0,
            d_s=None,
            p=position
        )
        self.next_spawn = None
        self.remaining_spawn_count = 0
        self.level = level
    
    def attack(self):
        return CannonAttackEntity(self.side, self.hit_damage, self.position, self.target)

class MegaMinionAttackEntity(AttackEntity):
    HIT_RANGE = 1.6
    COLLISION_RADIUS = 0.6
    def __init__(self, side, damage, position, target):
        super().__init__(
            s=side,
            d=damage,
            v=0,
            l=0.5,
            i_p=position
            )
        self.target = target
        self.should_delete = False
    
    def detect_hits(self, arena):
        
        if (vector.distance(self.target.position, self.position) <= MegaMinionAttackEntity.HIT_RANGE + MegaMinionAttackEntity.COLLISION_RADIUS + self.target.collision_radius): #within hitrange of knight
            return [self.target]
        else:
            return [] #theoretically should never trigger, when attack, should always be in range unless very strange circumstances
        
    def tick(self, arena):
        hits = self.detect_hits(arena)
        if len(hits) > 0:
            hits[0].cur_hp -= self.damage
            self.should_delete = True

    def cleanup(self, arena): #also delete self if single target here in derived classes
        self.duration -= TICK_TIME
        if self.duration <= 0:
            arena.active_attacks.remove(self)
        if self.should_delete:
            arena.active_attacks.remove(self)
        
            
class MegaMinion(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 395 * pow(1.1, level - 3),         # Hit points (Example value)
            h_d= 147 * pow(1.1, level - 3),          # Hit damage (Example value)
            h_s=1.5,          # Hit speed (Seconds per hit)
            l_t=1.1,            # First hit cooldown
            h_r=1.6,            # Hit range
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
        return MegaMinionAttackEntity(self.side, self.hit_damage, self.position, self.target)   
    
class BattleRamAttackEntity(AttackEntity):
    HIT_RANGE = 0.5
    COLLISION_RADIUS = 0.75
    def __init__(self, side, damage, position, target):
        super().__init__(
            s=side,
            d=damage,
            v=0,
            l=0.5,
            i_p=position
            )
        self.target = target
        self.should_delete = False
    
    def detect_hits(self, arena):
        
        if (vector.distance(self.target.position, self.position) <= BattleRamAttackEntity.HIT_RANGE + BattleRamAttackEntity.COLLISION_RADIUS + self.target.collision_radius): #within hitrange of knight
            return [self.target]
        else:
            return [] #theoretically should never trigger, when attack, should always be in range unless very strange circumstances
        
    def tick(self, arena):
        hits = self.detect_hits(arena)
        if len(hits) > 0:
            hits[0].cur_hp -= self.damage
            self.should_delete = True

    def cleanup(self, arena): #also delete self if single target here in derived classes
        self.duration -= TICK_TIME
        if self.duration <= 0:
            arena.active_attacks.remove(self)
        if self.should_delete:
            arena.active_attacks.remove(self)
    
class BattleRam(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 430 * pow(1.1, level - 3),         # Hit points
            h_d= 135 * pow(1.1, level - 3),          # Hit damage (charge is 2x)
            h_s=0.4,          # Hit speed (Seconds per hit)
            l_t=0.05,            # First hit cooldown
            h_r=0.5,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=True,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=6,            #mass
            c_r=0.75,        #collision radius
            p=position               # Position (vector.Vector object)
        ) 
        self.level = level
        self.charge_speed = 120 * TILES_PER_MIN
        self.charge_damage = self.hit_damage * 2
        self.charge_charge_distance = 0
        self.charging = False
        self.should_delete = False

    def attack(self):
        self.should_delete = True
        if self.charging:
            return BattleRamAttackEntity(self.side, self.charge_damage, self.position, self.target)  
        else:
            return BattleRamAttackEntity(self.side, self.hit_damage, self.position, self.target)  
    
    def tick(self, arena):
        if not self.charging and self.charge_charge_distance >= 3:
            self.charging = True
            self.move_speed = self.charge_speed
            self.charge_charge_distance = 0

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
            if not self.charging:
                self.charge_charge_distance += self.move_speed
    
    def cleanup(self, arena): # each troop runs this after ALL ticks are finished
        if self.cur_hp <= 0 or self.should_delete:
            arena.troops.append(Barbarian(self.side, self.position.added(vector.Vector(0.3, 0)), self.level))
            arena.troops.append(Barbarian(self.side, self.position.added(vector.Vector(-0.3, 0)), self.level))
            arena.troops.remove(self)
        
        if self.deploy_time > 0: #if deploying, timer
            self.deploy_time -= TICK_TIME
        else:
            if not self.target is None and not vector.distance(self.target.position, self.position) < self.hit_range + self.target.collision_radius + self.collision_radius and (self.attack_cooldown <= self.hit_speed - self.load_time):
                self.attack_cooldown = self.hit_speed - self.load_time #if not currently attacking but cooldown is less than first hit delay
            else: #otherwise
                self.attack_cooldown -= TICK_TIME #decrement time if eithe