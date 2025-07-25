from abstract_classes import AttackEntity
from abstract_classes import Troop
from abstract_classes import Spell
from abstract_classes import TILES_PER_MIN
from abstract_classes import TICK_TIME
import vector
import copy

class KnightAttackEntity(AttackEntity):
    KNIGHT_HIT_RANGE = 1.2
    KNIGHT_COLLISION_RADIUS = 0.5
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
        
        if (vector.distance(self.target.position, self.position) <= KnightAttackEntity.KNIGHT_HIT_RANGE + KnightAttackEntity.KNIGHT_COLLISION_RADIUS + self.target.collision_radius): #within hitrange of knight
            return [self.target]
        else:
            return [] #theoretically should never trigger, when attack, should always be in range unless very strange circumstances
        
    def tick(self, arena):
        hits = self.detect_hits(arena)
        if len(hits) > 0:
            hits[0].damage(self.damage)
            self.should_delete = True

    def cleanup(self, arena): #also delete self if single target here in derived classes
        self.duration -= TICK_TIME
        if self.duration <= 0:
            arena.active_attacks.remove(self)
        if self.should_delete:
            arena.active_attacks.remove(self)
        
            
class Knight(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 690 * pow(1.1, level - 1),         # Hit points (Example value)
            h_d= 79 * pow(1.1, level - 1),          # Hit damage (Example value)
            h_s=1.2,          # Hit speed (Seconds per hit)
            l_t=0.7,            # First hit cooldown
            h_r=1.2,            # Hit range
            s_r=5.5,            # Sight Range
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
    def attack(self):
        return KnightAttackEntity(self.side, self.hit_damage, self.position, self.target)

class MiniPekkaAttackEntity(AttackEntity):
    MP_HIT_RANGE = 1.2
    MP_COLLISION_RADIUS = 0.45
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
        
        if (vector.distance(self.target.position, self.position) <= MiniPekkaAttackEntity.MP_HIT_RANGE + MiniPekkaAttackEntity.MP_COLLISION_RADIUS + self.target.collision_radius): #within hitrange of knight
            return [self.target]
        else:
            return [] #theoretically should never trigger, when attack, should always be in range unless very strange circumstances
        
    def tick(self, arena):
        hits = self.detect_hits(arena)
        if len(hits) > 0:
            hits[0].damage(self.damage)
            self.should_delete = True

    def cleanup(self, arena): #also delete self if single target here in derived classes
        self.duration -= TICK_TIME
        if self.duration <= 0:
            arena.active_attacks.remove(self)
        if self.should_delete:
            arena.active_attacks.remove(self)
        
            
class MiniPekka(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 642 * pow(1.1, level - 1),         # Hit points (Example value)
            h_d= 356 * pow(1.1, level - 1),          # Hit damage (Example value)
            h_s=1.6,          # Hit speed (Seconds per hit)
            l_t=1.1,            # First hit cooldown
            h_r=0.8,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=90*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=4,            #mass
            c_r=0.45,        #collision radius
            p=position               # Position (vector.Vector object)
        ) 
        self.level = level
    def attack(self):
        return MiniPekkaAttackEntity(self.side, self.hit_damage, self.position, self.target)


class GiantAttackEntity(AttackEntity): #essentially same as Knight
    GIANT_HIT_RANGE = 1.2
    GIANT_COLLISION_RADIUS = 0.75
    def __init__(self, side, damage, position, target):
        super().__init__(
            s=side,
            d=damage,
            v=0,
            l=0.5,
            i_p=position,
            )
        self.target = target
        self.should_delete = False
    
    def detect_hits(self, arena):
        
        if (vector.distance(self.target.position, self.position) <= GiantAttackEntity.GIANT_HIT_RANGE + GiantAttackEntity.GIANT_COLLISION_RADIUS + self.target.collision_radius): #within hitrange of knight
            return [self.target]
        else:
            return [] #theoretically should never trigger, when attack, should always be in range unless very strange circumstances
        
    def tick(self, arena):
        hits = self.detect_hits(arena)
        if len(hits) > 0:
            hits[0].damage(self.damage)
            self.should_delete = True

    def cleanup(self, arena): #also delete self if single target here in derived classes
        self.duration -= TICK_TIME
        if self.duration <= 0:
            arena.active_attacks.remove(self)
        if self.should_delete:
            arena.active_attacks.remove(self)
        
class Giant(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,
            h_p = 1930 * pow(1.1, level - 3),
            h_d = 120 * pow(1.1, level - 3),
            h_s=1.5,
            l_t=1,
            h_r=1.2,
            s_r=7.5,
            g=True,
            t_g_o=True,
            t_o=True,
            m_s=45*TILES_PER_MIN,
            d_t=1,
            m=18,
            c_r=0.75,
            p=position
        ) 
        self.can_kb = False
        self.level = level
        self.walk_cycle_frames = 10
        class_name = self.__class__.__name__.lower()
        self.sprite_path = f"sprites/{class_name}/{class_name}_{self.walk_cycle_cur}.png"
    
    def attack(self):
        return GiantAttackEntity(self.side, self.hit_damage, self.position, self.target)
    

class MinionAttackEntity(AttackEntity):
    MINION_HIT_RANGE = 1.6
    MINION_COLLISION_RADIUS = 0.5
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
        
        if (vector.distance(self.target.position, self.position) <= MinionAttackEntity.MINION_HIT_RANGE + MinionAttackEntity.MINION_COLLISION_RADIUS + self.target.collision_radius): #within hitrange of knight
            return [self.target]
        else:
            return [] #theoretically should never trigger, when attack, should always be in range unless very strange circumstances
        
    def tick(self, arena):
        hits = self.detect_hits(arena)
        if len(hits) > 0:
            hits[0].damage(self.damage)
            self.should_delete = True

    def cleanup(self, arena): #also delete self if single target here in derived classes
        self.duration -= TICK_TIME
        if self.duration <= 0:
            arena.active_attacks.remove(self)
        if self.should_delete:
            arena.active_attacks.remove(self)
        
            
class Minion(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 90 * pow(1.1, level - 1),         # Hit points (Example value)
            h_d= 46 * pow(1.1, level - 1),          # Hit damage (Example value)
            h_s=1,          # Hit speed (Seconds per hit)
            l_t=0.5,            # First hit cooldown
            h_r=1.6,            # Hit range
            s_r=5.5,            # Sight Range
            g=False,           # Ground troop
            t_g_o=False,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=120*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=2,            #mass
            c_r=0.5,        #collision radius
            p=position               # Position (vector.Vector object)
        ) 
        self.level = level
        self.walk_cycle_frames = 4
        class_name = self.__class__.__name__.lower()
        self.sprite_path = f"sprites/{class_name}/{class_name}_0.png"
    def attack(self):
        return MinionAttackEntity(self.side, self.hit_damage, self.position, self.target)

class ArcherAttackEntity(AttackEntity):
    def __init__(self, side, damage, position, target):
        super().__init__(
            s=side,
            d=damage,
            v=600*TILES_PER_MIN,
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
            hits[0].damage(self.damage)
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
    
class Archer(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 119 * pow(1.1, level - 1),         # Hit points (Example value)
            h_d= 42 * pow(1.1, level - 1),          # Hit damage (Example value)
            h_s=0.9,          # Hit speed (Seconds per hit)
            l_t=0.4,            # First hit cooldown
            h_r=5,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=False,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=3,            #mass
            c_r=0.5,        #collision radius
            p=position               # Position (vector.Vector object)
        ) 
        self.level = level

        self.walk_cycle_frames = 7
        class_name = self.__class__.__name__.lower()
        self.sprite_path = f"sprites/{class_name}/{class_name}_{self.walk_cycle_cur}.png"
    
    def attack(self):
        return ArcherAttackEntity(self.side, self.hit_damage, self.position, self.target)
    

class MusketeerAttackEntity(AttackEntity):
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
            hits[0].damage(self.damage)
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
    
class Musketeer(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 340 * pow(1.1, level - 1),         # Hit points (Example value)
            h_d= 103 * pow(1.1, level - 1),          # Hit damage (Example value)
            h_s=1,          # Hit speed (Seconds per hit)
            l_t=0.2,            # First hit cooldown
            h_r=6,            # Hit range
            s_r=6,            # Sight Range
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
        return MusketeerAttackEntity(self.side, self.hit_damage, self.position, self.target)
    


class Fireball(Spell):
    def __init__(self, side, target, level):
        super().__init__(
            s=side,
            d=325 * pow(1.1, level - 1),
            c_t_d=98 * pow(1.1, level - 1),
            w=1,
            t=0,
            kb=1,
            r=2.5,
            v=600*TILES_PER_MIN,
            tar=target
        )

class Arrows(Spell):
    def __init__(self, side, target, level):
        super().__init__(
            s=side,
            d=48 * pow(1.1, level - 1),
            c_t_d=15 * pow(1.1, level - 1),
            w=3,
            t=0.2,
            kb=0,
            r=4,
            v=1100*TILES_PER_MIN,
            tar=target
        )