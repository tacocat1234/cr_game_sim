from abstract_classes import AttackEntity
from abstract_classes import Troop
from abstract_classes import TILES_PER_MIN
import vector

class KnightAttackEntity(AttackEntity):
    KNIGHT_HIT_RANGE = 1.2
    def __init__(self, side, damage, position, target):
        super().__init__(
            s=side,
            d=damage,
            v=0,
            l=float('inf'),
            i_p=position
            )
        self.target = target
        self.should_delete = False
    
    def detect_hits(self, arena):
        
        if (vector.distance(self.target.position, self.position) < KnightAttackEntity.KNIGHT_HIT_RANGE): #within hitrange of knight
            return [self.target]
        else:
            return [] #theoretically should never trigger, when attack, should always be in range unless very strange circumstances
        
    def tick(self, arena):
        hits = self.detect_hits(arena)
        if len(hits) > 0:
            hits[0].cur_hp -= self.damage
            self.should_delete = True

    def cleanup(self, arena): #also delete self if single target here in derived classes
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
            p=position               # Position (vector.Vector object)
        )
    def attack(self):
        return KnightAttackEntity(self.side, self.hit_damage, self.position, self.target)

class GiantAttackEntity(AttackEntity): #essentially same as Knight
    GIANT_HIT_RANGE = 1.2
    def __init__(self, side, damage, position, target):
        super().__init__(
            s=side,
            d=damage,
            v=0,
            l=float('inf'),
            i_p=position,
            )
        self.target = target
        self.should_delete = False
    
    def detect_hits(self, arena):
        
        if (vector.distance(self.target.position, self.position) < GiantAttackEntity.GIANT_HIT_RANGE): #within hitrange of knight
            return [self.target]
        else:
            return [] #theoretically should never trigger, when attack, should always be in range unless very strange circumstances
        
    def tick(self, arena):
        hits = self.detect_hits(arena)
        if len(hits) > 0:
            hits[0].cur_hp -= self.damage
            self.should_delete = True

    def cleanup(self, arena): #also delete self if single target here in derived classes
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
            p=position
        )
    
    def attack(self):
        return GiantAttackEntity(self.side, self.hit_damage, self.position, self.target)