from abstract_classes import Troop
from abstract_classes import MeleeAttackEntity
from abstract_classes import RangedAttackEntity
from abstract_classes import Spell
import vector

from training_camp_cards import MiniPekka

class SuperMiniPekkaAttackEntity(MeleeAttackEntity):
    def __init__(self, side, damage, position, target):
        super().__init__(side, damage, position, target)

class SuperMiniPekkaPancake(Troop):
    def __init__(self, position):
        super().__init__(s = 0, h_p = 1, h_d = 0, h_s = 0, l_t = 0, h_r = 0, s_r= 0 , g = True, t_g_o = True, t_o = True, m_s = 0, d_t = 0, m = float('inf'), c_r = 0.3, p=position)
        self.invulnerable = True
        self.targetable = False
        self.collideable = False
        self.can_kb = False

    def tick(self, arena):
        for each in arena.troops:
            if self.side == each.side and vector.distance(each.position, self.position) < self.collision_radius + each.collision_radius + 0.1:
                self.should_delete = True

class SuperMiniPekka(MiniPekka):
    def __init__(self, side, position, level):
        super().__init__(side, position, level)
        self.hit_damage = float('inf')

    def attack(self):
        return SuperMiniPekkaAttackEntity(self.side, self.hit_damage, self.position, self.target)