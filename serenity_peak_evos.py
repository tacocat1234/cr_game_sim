import serenity_peak_cards
from  abstract_classes import TICK_TIME
from abstract_classes import TILES_PER_MIN
from abstract_classes import Troop
from abstract_classes import RangedAttackEntity
from goblin_stadium_cards import Goblin
import copy
import vector

class EvolutionLumberjackGhost(serenity_peak_cards.Lumberjack):
    def __init__(self, side, position, level):
        super().__init__(side, position, level)
        self.initial = copy.deepcopy(self.position)
        self.evo = True
        self.invulnerable = True
        self.targetable = False
        self.in_rage = True
        self.timer = 6

    def tick_func(self, arena):
        if self.in_rage and vector.distance(self.position, self.initial) > 3 + self.collision_radius:
            self.timer = min(2, self.timer)
            self.in_rage = False

    def cleanup_func(self, arena):
        if self.timer > 0:
            self.timer -= TICK_TIME
        else:
            self.should_delete = True

    def die(self, arena):
        self.cur_hp = -1
        arena.troops.remove(self)

class EvolutionLumberjack(serenity_peak_cards.Lumberjack):
    def __init__(self, side, position, level):
        super().__init__(side, position, level)
        self.evo = True

    def die(self, arena):
        arena.troops.append(EvolutionLumberjackGhost(self.side, copy.deepcopy(self.position), self.level))
        return super().die(arena)
    
class EvolutionExecutionerAttackEntity(serenity_peak_cards.ExecutionerAttackEntity):
    def __init__(self, side, damage, position, target, parent_pos):
        super().__init__(side, damage, position, target)
        self.normal_damage = damage
        self.axe_smash = True
        self.parent_pos = parent_pos

    def tick_func(self, arena):
        if self.duration <= 0.75 and not self.returning:
            self.returning = True
            self.has_hit = []

        if self.duration < 0.203 or self.duration > 1.297:
            self.axe_smash = True
            self.damage = 1.75 * self.normal_damage
        else:
            self.axe_smash = False
            self.damage = self.normal_damage
    
    def apply_effect(self, target):
        if not self.returning and self.axe_smash and isinstance(target, Troop) and target.can_kb and not target.invulnerable:
            vec = target.position.subtracted(self.parent_pos)
            vec.normalize()
            vec.scale(1.5)
            target.kb(vec)
    
class EvolutionExecutioner(serenity_peak_cards.Executioner):
    def __init__(self, side, position, level):
        super().__init__(side, position, level)
        self.evo = True

    def attack(self):
        self.stun_timer = 1.5
        return EvolutionExecutionerAttackEntity(self.side, self.hit_damage, self.position, copy.deepcopy(self.target.position), self.position)
    #subject to nerfs, not going to code

class EvolutionGoblinDrillMineTroop(serenity_peak_cards.GoblinDrillMineTroop):
    def __init__(self, side, position, level):
        super().__init__(side, position, level)
        self.evo = True

    def tick_func(self, arena):
        if self.invulnerable and vector.distance(self.position, self.target) < 0.25:
            gd = EvolutionGoblinDrill(self.side, self.position, self.level)
            arena.buildings.append(gd)
            gd.on_deploy(arena)
            arena.active_attacks.append(serenity_peak_cards.GoblinDrillSpawnAttackEntity(self.side, 51 * pow(1.1, self.level - 6), 16 * pow(1.1, self.level - 6), self.position))
            arena.troops.remove(self)
            self.cur_hp = -1 #just in case

class EvolutionGoblinDrill(serenity_peak_cards.GoblinDrill):
    def __init__(self, side, position, level):
        super().__init__(side, position, level)
        self.evo = True
        self.last_down = 1
        self.appear = False

    def tick_func(self, arena):
        if self.appear: #if should appear
            self.targetable = True
            self.invulnerable = False
            self.collision_radius = 0.5
            self.appear = False
            arena.active_attacks.append(serenity_peak_cards.GoblinDrillSpawnAttackEntity(self.side, 51 * pow(1.1, self.level - 6), 16 * pow(1.1, self.level - 6), self.position))
            return

        trigger = False
        if self.last_down == 1 and self.cur_hp <= 0.66 * self.hit_points:
            arena.troops.append(Goblin(self.side, copy.deepcopy(self.position), self.level)) #extra goblin on the first one
            self.last_down = 0.66
            trigger = True
        if self.last_down == 0.66 and self.cur_hp <= 0.33 * self.hit_points:
            self.last_down = 0.33
            trigger = True

        if trigger:
            arena.troops.append(Goblin(self.side, copy.deepcopy(self.position), self.level))
            self.targetable = False
            self.invulnerable = True
            self.collision_radius = 0
            self.appear = True
            self.stun_timer = 1 #time before reappearing
            if self.on_tower is not None:
                if self.position.y < self.on_tower.position.y:
                    self.position = vector.Vector(self.on_tower.position.x - self.on_tower.collision_radius, self.on_tower.position.y)
                elif self.position.x < self.on_tower.position.x:
                    self.position = vector.Vector(self.on_tower.position.x, self.on_tower.position.y + self.on_tower.collision_radius)
                elif self.position.y > self.on_tower.position.y:
                    self.position = vector.Vector(self.on_tower.position.x + self.on_tower.collision_radius, self.on_tower.position.y)
                else:
                    self.position = vector.Vector(self.on_tower.position.x, self.on_tower.position.y - self.on_tower.collision_radius)
    