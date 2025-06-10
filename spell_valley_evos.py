import spell_valley_cards
from abstract_classes import AttackEntity
from abstract_classes import Troop
import vector

class EvolutionWizardSpecialAttackEntity(AttackEntity):
    SPLASH_RADIUS = 3
    def __init__(self, side, damage, position):
        super().__init__(
            s=side,
            d=damage,
            v=0,
            l=0.2,
            i_p=position
        )
        self.display_size = self.SPLASH_RADIUS

    def detect_hits(self, arena):
        hits = []
        for each in arena.towers + arena.buildings + arena.troops:
            if each.side != self.side and not each.invulnerable: # if different side
                if vector.distance(self.position, each.position) < self.SPLASH_RADIUS + each.collision_radius:
                    hits.append(each)
        return hits

    def apply_effect(self, target):
        if isinstance(target, Troop) and target.can_kb and not target.invulnerable:
            target.kb(target.position.subtracted(self.position).normalized().scaled(3))
    

class EvolutionWizard(spell_valley_cards.Wizard):
    def __init__(self, side, position, level):
        super().__init__(side, position, level)
        self.evo = True
        self.has_shield = True
        self.shield_max_hp = 281 * pow(1.1, level - 11)
        self.shield_hp = 281 * pow(1.1, level - 11)
        self.shield_damage = 200 * pow(1.1, level - 11)
        self.shield_exploded = False

    def tick_func(self, arena):
        if self.shield_exploded:
            arena.active_attacks.append(EvolutionWizardSpecialAttackEntity(self.side, self.shield_damage, self.position))
            self.shield_exploded = False

    def damage(self, amount):
        if self.shield_hp > 0:
            self.shield_hp -= amount * self.damage_amplification
            if self.shield_hp <= 0:
                self.shield_exploded = True
        else:
            self.cur_hp -= amount * self.damage_amplification

