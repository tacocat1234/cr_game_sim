from abstract_classes import Troop
from abstract_classes import MeleeAttackEntity
from abstract_classes import RangedAttackEntity
from abstract_classes import AttackEntity
from abstract_classes import Spell
from abstract_classes import Tower
from abstract_classes import TILES_PER_MIN
from goblin_stadium_cards import Goblin
import vector
import copy

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
                arena.active_attacks.append(SuperMiniPekkaPancakeHealEntity(self.side, 100*pow(1.1, self.level - 11), self.positon, self.position))
                self.should_delete = True

class SuperMiniPekkaPancakeHealEntity(AttackEntity):
    DAMAGE_RADIUS = 1.5
    FREEZE_DURATION = 1.2
    def __init__(self, side, damage, position, target):
        super().__init__(
            s=side,
            d=damage,
            v=0,
            l=float('inf'),
            i_p=copy.deepcopy(position)
        )
        self.target = target
        self.has_hit = []
        self.display_size = SuperMiniPekkaPancakeHealEntity.DAMAGE_RADIUS 
        self.duration =  0.25
        self.exploded = True

    def detect_hits(self, arena):
        hits = []
        if self.exploded:
            for each in arena.towers + arena.buildings + arena.troops:
                if (isinstance(each, Tower) or not each.invulnerable) and each.side == self.side: # if different side
                    if vector.distance(self.position, each.position) < SuperMiniPekkaPancakeHealEntity.DAMAGE_RADIUS + each.collision_radius:
                        hits.append(each)
        return hits
            
    def tick(self, arena):
        hits = self.detect_hits(arena)
        for each in hits:
            new = not any(each is h for h in self.has_hit)
            if (new):
                each.heal(self.damage)
                self.has_hit.append(each)
                

class SuperMiniPekka(MiniPekka):
    def __init__(self, side, position, level):
        super().__init__(side, position, level)
        self.hit_damage = float('inf')
        self.drop_pancake = False

    def tick_func(self, arena):
        if self.drop_pancake:
            arena.troops.append(SuperMiniPekkaPancake(copy.deepcopy(self.position)))
            self.drop_pancake = False        

    def attack(self):
        return SuperMiniPekkaAttackEntity(self.side, self.hit_damage, self.position, self.target)
    
class PartyRocket(Spell):
    def __init__(self, side, target, level):
        super().__init__(
            s=side,
            d=0,
            c_t_d=0,
            w=1,
            t=0,
            kb=1.8,
            r=2,
            v=350*TILES_PER_MIN,
            tar=target
        )
        self.level = level

    def apply_effect(self, target):
        target = Goblin(self.side, self.position, self.level)