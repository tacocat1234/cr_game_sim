import pekkas_playhouse_cards
from abstract_classes import MeleeAttackEntity
from abstract_classes import Troop
from abstract_classes import TICK_TIME
import vector


class EvolutionGoblinBarrel(pekkas_playhouse_cards.GoblinBarrel):
    def __init__(self, side, target, level, fake=False):
        super().__init__(side, target, level, fake)
        self.evo = True
        self.new_deploy = True

    def tick_func(self, arena):
        if self.new_deploy and not self.fake:
            tar = vector.Vector(-self.target_pos.x, self.target_pos.y)
            arena.spells.append(EvolutionGoblinBarrel(self.side, tar, self.level, True))
            self.new_deploy = False

    

class EvolutionPekkaAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 1.2
    COLLISION_RADIUS = 0.75
    def __init__(self, side, damage, position, target, parent):
        super().__init__(
            side=side,
            damage=damage,
            position=position,
            target=target
            )
        self.parent = parent
        
        self.small_heal = 142 * pow(1.1, parent.level - 11)
        self.medium_heal = 282 * pow(1.1, parent.level - 11)
        self.large_heal = 565 * pow(1.1, parent.level - 11)

        self.small_threshold = 990 * pow(1.1, parent.level - 11)
        self.medium_threshold = 1990 * pow(1.1, parent.level - 11)

    def tick(self, arena):
        hits = self.detect_hits(arena)
        if len(hits) > 0:
            for each in hits:
                each.damage(self.damage)
                if each.cur_hp <= 0 and isinstance(each, Troop):
                    amount = self.small_heal if each.hit_points <= self.small_threshold else (self.medium_heal if each.hit_points <= self.medium_threshold else self.large_heal)
                    self.parent.overheal(amount)

            self.should_delete = True
    

class EvolutionPekka(pekkas_playhouse_cards.Pekka):
    def __init__(self, side, position, level):
        super().__init__(side, position, level)
        self.evo = True

    def overheal(self, amount):
        self.cur_hp += amount
        if self.cur_hp > self.hit_points * 1.5:
            self.cur_hp = self.hit_points * 1.5

    def attack(self):
        return EvolutionPekkaAttackEntity(self.side, self.hit_damage, self.position, self.target, self)

class EvolutionWitch(pekkas_playhouse_cards.Witch):
    def __init__(self, side, position, level):
        super().__init__(side, position, level)
        self.evo = True
        self.heal_amount = 36 * pow(1.1, level - 6)

        self.heal_timers = []

    def level_up(self):
        self.heal_amount *= 1.1
        return super().level_up()
    
    def tick_func(self, arena):
        for i in reversed(range(len(self.heal_timers))):
            self.heal_timers[i] -= TICK_TIME
            if self.heal_timers[i] <= 0:
                self.overheal(self.heal_amount)
                self.heal_timers.pop(i)
    
    def overheal(self, amount):
        self.cur_hp += amount
        if self.cur_hp > self.hit_points * 1.24:
            self.cur_hp = self.hit_points * 1.24

    def handle_deaths(self, list):
        for each in list:
            n = each.__class__.__name__.lower()
            if not each.cloned and (each.side == self.side) and (n == "guard" or n == "skeleton" or n == "evolutionskeleton"):
                self.heal_timers.append(1)