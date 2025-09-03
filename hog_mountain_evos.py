import hog_mountain_cards
from abstract_classes import RangedAttackEntity
from abstract_classes import AttackEntity
from abstract_classes import TILES_PER_MIN
from abstract_classes import TICK_TIME
from spell_valley_cards import FireSpirit
import vector

class Net(RangedAttackEntity):
    def __init__(self, side, position, target):
        super().__init__(side, 0, 1000 * TILES_PER_MIN, position, target)
        self.display_size = self.target.collision_radius + 0.1
        self.target_ground = False
        self.duration = 4
        self.piercing = True

    def apply_effect(self, target):
        self.position = self.target.position
        self.velocity = 0
        self.target_ground = target.ground
        target.ground = True
        target.stun_timer = 4

    def tick_func(self, arena):
        if self.target.cur_hp <= 0 or self.target is None:
            self.should_delete = True
        if self.duration <= TICK_TIME:
            self.target.ground = self.target_ground

class EvolutionHunter(hog_mountain_cards.Hunter):
    def __init__(self, side, position, level):
        super().__init__(side, position, level)
        self.evo = True
        self.net_target = None
        self.target_flying = False
        self.net_cooldown = 0

    def update_net_target(self, arena):
        self.net_target = None 
        
        min_dist = float('inf')
        if not self.tower_only: #if not tower targeting
            for each in arena.troops: #for each troop
                if each.targetable and not each.invulnerable and each.side != self.side and (not self.ground_only or (self.ground_only and each.ground)): #targets air or is ground only and each is ground troup
                    dist = vector.distance(each.position, self.position)
                    if  dist < min_dist and dist < self.sight_range + self.collision_radius + each.collision_radius:
                        self.net_target = each
                        min_dist = vector.distance(each.position, self.position)

    def tick_func(self, arena):
        if self.net_target is None or self.net_target.cur_hp <= 0:
            self.update_net_target(arena)
        if self.net_target is not None and self.net_cooldown <= 0 and vector.distance(self.position, self.net_target.position) <= 4:
            arena.active_attacks.append(Net(self.side, self.position, self.net_target))
            self.net_cooldown = 4
        else:
            self.net_cooldown -= TICK_TIME

class EvolutionTeslaPulseAttackEntity(AttackEntity):
    def __init__(self, s, d, i_p):
        super().__init__(s, d, 0, 1.5, i_p)
        self.display_size = 0
        self.has_hit = []

    def tick_func(self, arena):
        self.display_size += 4/60

    def detect_hits(self, arena):
        hits = []
        for each in arena.towers + arena.buildings + arena.troops:
            if not each.invulnerable and each.side != self.side: # if different side
                d = vector.distance(self.position, each.position)
                if d <= self.display_size + each.collision_radius + 0.5 and d >= self.display_size - each.collision_radius - 0.5:
                    hits.append(each)
        return hits
    
    def apply_effect(self, target):
        target.stun()

class EvolutionTesla(hog_mountain_cards.Tesla):
    def __init__(self, side, position, level):
        super().__init__(side, position, level)
        self.evo = True
        self.pulse_damage = 58 * pow(1.1, level - 1)

    def change_state(self, arena):
        if not self.targetable:
            arena.active_attacks.append(EvolutionTeslaPulseAttackEntity(self.side, self.pulse_damage, self.position))
        return super().change_state(arena)

class EvolutionFurnace(hog_mountain_cards.Furnace):
    def __init__(self, side, position, level):
        super().__init__(side, position, level)
        self.evo = True
        self.spawn_side = False
        self.hot_spawn = False

    def tick_func(self, arena):
        if self.stun_timer <= 0:
            if self.spawn_timer > 0:
                if not self.hot_spawn:
                    self.spawn_timer -= TICK_TIME
            else:
                if self.hot_spawn:
                    self.spawn_timer = 1.8
                else:
                    self.spawn_timer = 7
                f_s = FireSpirit(self.side, self.position.added(vector.Vector((-1.5 if self.spawn_side else 1.5) if self.hot_spawn else 0, 0 if self.hot_spawn else (0.6 if self.side else -0.6))), self.level)
                f_s.deploy_time = 0
                arena.troops.append(f_s)
                if self.hot_spawn:
                    self.spawn_side = not self.spawn_side
                    self.hot_spawn = False

    def attack(self):
        self.hot_spawn = True
        self.spawn_timer = 0
        return super().attack()