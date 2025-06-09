from abstract_classes import RangedAttackEntity
from abstract_classes import TICK_TIME
from abstract_classes import TILES_PER_MIN
import training_camp_cards
import vector

class EvolutionKnight(training_camp_cards.Knight):
    def __init__(self, side, position, level):
        super().__init__(side, position, level)
        self.evo = True
    
    def damage(self, amount):
        if self.move_vector.y > 0:
            super().damage(amount * 0.4)
        else:
            super().damage(amount)

class EvolutionArcher(training_camp_cards.Archer):
    def __init__(self, side, position, level):
        super().__init__(side, position, level)
        self.hit_range = 6
        self.sight_range = 6
        self.evo = True
    
    def attack(self):
        if self.target is not None and vector.distance(self.target.position, self.position) >= 4.5:
            return training_camp_cards.ArcherAttackEntity(self.side, self.hit_damage * 2, self.position, self.target)
        else:
            return super().attack()
        
class EvolutionMusketeerSnipeAttackEntity(RangedAttackEntity):
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side, 
            damage=damage, 
            velocity=2650*TILES_PER_MIN, 
            position=position, 
            target=target
        )
        
class EvolutionMusketeer(training_camp_cards.Musketeer):
    def __init__(self, side, position, level):
        super().__init__(side, position, level)
        self.sniper_shots = 3
        self.sniper_cooldown = 0
        self.evo = True
        self.sniper_target = None

    def can_snipe(self, each):
        return each.targetable and each.position.x >= self.position.x - 1 and each.position.x <= self.position.x + 1 and ((self.side and each.position.y > self.position.y) or (not self.side and each.position.y < self.position.y))

    def tick_func(self, arena):
        if self.sniper_shots > 0 and self.target is None and self.sniper_cooldown <= 0:
            if self.sniper_target is None:
                min_dist = float('inf')
                for each in arena.troops + arena.buildings:
                    if each.side != self.side and self.can_snipe(each):
                        d = vector.distance(self.position, each.position)
                        if d < min_dist:
                            min_dist = d
                            self.sniper_target = each
            
            if self.sniper_target is not None:
                self.sniper_shots -= 1
                arena.active_attacks.append(EvolutionMusketeerSnipeAttackEntity(self.side, self.hit_damage * 1.8, self.position, self.sniper_target))
                self.sniper_cooldown = 1
        
        if self.sniper_target is None or self.sniper_target.cur_hp <= 0 or not self.sniper_target.targetable:
            self.sniper_target = None

        if self.sniper_cooldown > 0:
            self.sniper_cooldown -= TICK_TIME