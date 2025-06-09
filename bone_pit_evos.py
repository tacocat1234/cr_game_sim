import bone_pit_cards
import random
import vector

class EvolutionSkeletonCounter:
    def __init__(self):
        self.count = 0

    def add(self):
        self.count += 1

    def sub(self):
        self.count -= 1

    def can_more(self):
        return self.count < 8

class EvolutionSkeleton(bone_pit_cards.Skeleton):
    def __init__(self, side, position, level, counter, cloned=False):
        super().__init__(side, position, level, cloned)
        self.count = counter

    def die(self, arena):
        self.count.sub()
        super().die(arena)
    
    def tick_func(self, arena):
        if self.attack_cooldown == self.hit_speed and self.count.can_more(): #after attack
            self.count.add()
            arena.troops.append(EvolutionSkeleton(self.side, self.target.position.added(vector.Vector(random.random() - 0.5, random.random() - 0.5)), self.level, self.count))