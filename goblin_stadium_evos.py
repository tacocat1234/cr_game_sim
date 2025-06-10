import goblin_stadium_cards
from abstract_classes import TICK_TIME
import vector
import copy

class EvolutionGoblinBrawler(goblin_stadium_cards.GoblinBrawler):
    def __init__(self, side, position, level):
        super().__init__(side, position, level)
        self.evo = True
        self.hit_points *= 1.1


class EvolutionGoblinCage(goblin_stadium_cards.GoblinCage):
    def __init__(self, side, position, level):
        super().__init__(side, position, level)
        self.evo = True
        self.hit_range = 3
        self.trapped = None
        self.hit_damage = 159 * pow(1.1, level - 3)
        self.hit_speed = 1.1

    def update_target(self, arena):
        min = float('inf')
        self.target = None
        for each in arena.troops:
            if each.side != self.side and each.ground and each.targetable and not each.invulnerable: # if different side
                d = vector.distance(self.position, each.position)
                if d < min and d < self.hit_range + each.collision_radius:
                    self.target = each

        if self.target is not None:
            self.target.collideable = False
            self.target.stun_timer = TICK_TIME * 2
            self.target.targetable = False

            self.target.kb(self.position.subtracted(self.target.position), 0.5)

    def tick_func(self, arena):
        if self.target is not None:
            self.target.stun_timer = TICK_TIME * 2

    def tick(self, arena):
        if self.preplace or self.deploy_time > 0 or self.stun_timer > 0:
            return
        self.tick_func(arena)
        if self.target is None or self.target.cur_hp <= 0:
            self.update_target(arena)
        if not self.target is None and self.attack_cooldown <= 0 and vector.distance(self.target.position, self.position) <= 0.2:
            self.target.position = copy.deepcopy(self.position)
            atk = self.attack()
            if not atk is None:
                arena.active_attacks.append(self.attack())
            self.attack_cooldown = self.hit_speed
    
    def attack(self):
        return goblin_stadium_cards.GoblinBrawlerAttackEntity(self.side, self.hit_damage, self.position, self.target)

    def die(self, arena):
        if self.target is not None:
            self.target.collideable = True
            self.target.targetable = True
        arena.troops.append(EvolutionGoblinBrawler(self.side, self.position, self.level))
        arena.buildings.remove(self)
        self.cur_hp = -1
    