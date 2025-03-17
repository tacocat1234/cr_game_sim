from abstract_classes import AttackEntity
from abstract_classes import Troop
from abstract_classes import Spell
from abstract_classes import Tower
from abstract_classes import TILES_PER_MIN
from abstract_classes import TICK_TIME
import vector
import copy

class Zap(Spell):
    def __init__(self, side, target, level):
        super().__init__(
            s=side,
            d=75 * pow(1.1, level - 1),
            c_t_d=23 * pow(1.1, level - 1),
            w=1, #waves
            t=0, #time between waves
            kb=0,
            r=2.5,
            v=0,
            tar=target
        )
    
    def tick(self, arena):
        if self.waves > 0:
            hits = self.detect_hits(arena)
            for each in hits:
                each.stun()
                if (isinstance(each, Tower)):
                    each.cur_hp -= self.crown_tower_damage #crown tower damage
                else:
                    each.cur_hp -= self.damage
            self.waves -= 1
        else:
            self.should_delete = True #mark for deletion

