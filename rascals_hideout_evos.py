import rascals_hideout_cards
from abstract_classes import MeleeAttackEntity
from abstract_classes import AttackEntity
from abstract_classes import Tower
from abstract_classes import TICK_TIME
import vector


class EvolutionElectroGiantDamperAttackEntity(AttackEntity):
    def __init__(self, s, d, i_p):
        super().__init__(s, d, 0, 0.5, i_p)

        self.display_size = 0
        self.size = 0
        self.maximum_range = 6
        self.pulse_time = self.lifespan # seconds
        self.elapsed_time = 0
        self.band_width = 1.0

        self.has_hit = []

    def tick_func(self, arena):
        self.size = min(self.maximum_range, self.maximum_range * self.elapsed_time / self.pulse_time)
        self.display_size = self.size
        super().tick_func(arena)

    def cleanup_func(self, arena):
        self.elapsed_time += TICK_TIME
        super().cleanup_func(arena)

    def detect_hits(self, arena):
        hits = []

        for each in arena.towers + arena.buildings + arena.troops:
            if not each.invulnerable and each.side != self.side:
                d = vector.distance(self.position, each.position)

                if (
                    d <= self.size + each.collision_radius + self.band_width/2 and d >= self.size - each.collision_radius - self.band_width/2
                ):
                    hits.append(each)

        return hits

    def apply_effect(self, target):
        if not isinstance(target, Tower):
            target.level_down()


class EvolutionElectroGiant(rascals_hideout_cards.ElectroGiant):
    def __init__(self, side, position, level):
        super().__init__(side, position, level)
        self.evo = True
        self.damper_timer = 3.5
        self.damper_max_timer = 6

    def tick_func(self, arena):
        if self.damper_timer <= 0:
            arena.active_attacks.append(EvolutionElectroGiantDamperAttackEntity(self.side, 0, self.position))

        super().tick_func(arena)

    def cleanup_func(self, arena):
        if self.damper_timer <= 0:
            self.damper_timer = self.damper_max_timer
        else:
            self.damper_timer -= TICK_TIME
        super().cleanup_func(arena) 