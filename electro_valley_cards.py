from abstract_classes import RangedAttackEntity
from abstract_classes import MeleeAttackEntity
from abstract_classes import AttackEntity
from abstract_classes import Troop
from abstract_classes import Tower
from abstract_classes import TILES_PER_MIN
from abstract_classes import TICK_TIME
import vector
import copy
import math

class LogAttackEntity(AttackEntity):
    def __init__(self, side, damage, c_t_d, pos):
        super().__init__(
            s=side, 
            d=damage, 
            v=200 * TILES_PER_MIN, 
            l=3.03, 
            i_p=pos)
        self.has_hit = []
        self.crown_tower_damage = c_t_d
        
    def detect_hits(self, arena):
        hits = []
        for each in arena.troops + arena.buildings + arena.towers:
            if each.side != self.side and each.ground and not each.invulnerable and not each in self.has_hit:
                if each.position.x < self.position.x + 1.95 and each.position.x > self.position.x - 1.95 and each.position.y < self.position.y + 0.6 and each.position.y > self.position.y - 0.6:
                    hits.append(each)
        return hits
    
    def tick(self, arena):
        self.position.y += self.velocity if self.side else -self.velocity
        hits = self.detect_hits(arena)
        for each in hits:
            new = not each in self.has_hit
            if (new):
                if isinstance(each, Troop):
                    each.kb(vector.Vector(0, 0.7 if self.side else -0.7))
                    each.damage(self.damage)
                elif isinstance(each, Tower):
                    each.damage(self.crown_tower_damage)
                else:
                    each.damage(self.damage)
                self.has_hit.append(each)
    
class Log(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p = float('inf'),         # Hit points (Example value)
            h_d= 240 * pow(1.1, level - 9),          # Hit damage (Example value)
            h_s=0.1,          # Hit speed (Seconds per hit)
            l_t=0.1,            # First hit cooldown
            h_r=5.5,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=200*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=1,            #mass
            c_r=1.95,        #collision radius
            p=position               # Position (vector.Vector object)
        )
        self.level = level
        self.targetable = False
        self.invulnerable = True
        self.timer = 3.03
        self.crown_tower_damage = h_d= 48 * pow(1.1, level - 9)

        self.collideable = False

        self.first = True

    def move(self, arena):
        self.position.y += self.move_speed if self.side else -self.move_speed
    
    def tick(self, arena):
        self.timer -= TICK_TIME
        self.move(arena)
        if self.first:
            arena.active_attacks.append(self.attack())
            self.first = False
        if self.timer <= 0:
            self.should_delete = True

        

    def attack(self):
        return LogAttackEntity(self.side, self.hit_damage, self.crown_tower_damage, copy.deepcopy(self.position))