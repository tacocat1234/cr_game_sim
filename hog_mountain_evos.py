import hog_mountain_cards
from abstract_classes import RangedAttackEntity
from abstract_classes import AttackEntity
from abstract_classes import TILES_PER_MIN
from abstract_classes import TICK_TIME
from spell_valley_cards import FireSpirit
import vector
import copy

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
        super().__init__(s, d, 0, 1, i_p)

        self.display_size = 0
        self.size = 0
        self.maximum_range = 6
        self.pulse_time = self.lifespan  # seconds
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
                f_s = FireSpirit(self.side, self.position.added(vector.Vector((-1.5 if self.spawn_side else 1.5) if self.hot_spawn else 0, 0 if self.hot_spawn else (0.6 if self.side else -0.6))), self.level, self.cloned)
                f_s.deploy_time = 0
                arena.troops.append(f_s)
                if self.hot_spawn:
                    self.spawn_side = not self.spawn_side
                    self.hot_spawn = False

    def attack(self):
        self.hot_spawn = True
        self.spawn_timer = 0
        return super().attack()
    
from serenity_peak_cards import Rage
    
class EvolutionEliteBarbarianSpearRage(Rage):
    SPLASH_RADIUS = 1
    LIFESPAN = 2
    def __init__(self, side, target):
        super().__init__(side, target, 0)
        self.damage = 0
        self.radius = EvolutionEliteBarbarianSpearRage.SPLASH_RADIUS
        self.display_duration = EvolutionEliteBarbarianSpearRage.LIFESPAN
    
class EvolutionEliteBarbarianSpear(RangedAttackEntity):
    def __init__(self, side, damage, position, target):
        super().__init__(side, damage, 700 * TILES_PER_MIN, position, target)
        self.drop_rage_timer = 0.0625
        self.drop_rage_timer_max = 0.125

    def drop_rage(self, arena):
        arena.spells.append(EvolutionEliteBarbarianSpearRage(self.side, copy.deepcopy(self.position)))

    def on_hit(self, arena):
        self.drop_rage(arena)
        super().on_hit(arena)

    def tick_func(self, arena):
        if self.drop_rage_timer <= 0:
            self.drop_rage(arena)

        super().tick_func(arena)

    def cleanup_func(self, arena):
        if self.drop_rage_timer <= 0:
            self.drop_rage_timer = self.drop_rage_timer_max
        else:
            self.drop_rage_timer -= TICK_TIME
        super().cleanup_func(arena)
    
class EvolutionEliteBarbarian(hog_mountain_cards.EliteBarbarian):
    SPEAR_MIN_RANGE = 3.0
    SPEAR_MAX_RANGE = 4.5
    def __init__(self, side, position, level):
        super().__init__(side, position, level)
        self.spear_dmg = 220 * pow(1.1, self.level - 11)
        self.spear_cooldown = 0
        self.spear_max_cooldown = 5
        self.evo = True

    def throw_spear(self, arena, target):
        arena.active_attacks.append(EvolutionEliteBarbarianSpear(self.side, self.spear_dmg, self.position, target))

    def find_target_in_range(self, arena):
        if self.target is not None:
            d = vector.distance(self.target.position, self.position)
            if d > EvolutionEliteBarbarian.SPEAR_MIN_RANGE and d < EvolutionEliteBarbarian.SPEAR_MAX_RANGE:
                return self.target
        else:
            for tower in arena.towers:
                if tower.side != self.side:
                    d = vector.distance(tower.position, self.position)
                    if d > EvolutionEliteBarbarian.SPEAR_MIN_RANGE and d < EvolutionEliteBarbarian.SPEAR_MAX_RANGE: #terminate first since only one tower wille ver be in range
                        return tower
        return None

    def tick_func(self, arena):
        t = self.find_target_in_range(arena)
        if t and self.spear_cooldown <= 0:
            self.throw_spear(arena, t)
            self.spear_cooldown = 5
        else:
            self.spear_cooldown -= TICK_TIME
            
        super().tick_func(arena)

from training_camp_cards import Minion
class EvolutionMinionHordeMinion(Minion):
    IMMUNITY_DURATION = 3.0
    MOVE_SPEED_DECREASE = 0.67
    HIT_SPEED_DECREASE = 0.67
    def __init__(self, side, position, level):
        super().__init__(side, position, level)
        self.evo = True
        self.immunity_active = False
        self.immunity_remaining = EvolutionMinionHordeMinion.IMMUNITY_DURATION

    def activate_immunity(self):
        self.hit_speed /= EvolutionMinionHordeMinion.HIT_SPEED_DECREASE
        self.load_time /= EvolutionMinionHordeMinion.HIT_SPEED_DECREASE
        self.move_speed *= EvolutionMinionHordeMinion.MOVE_SPEED_DECREASE
        self.invulnerable = True
        self.unaffectable = True
        self.targetable = False
        self.display_transparent = True
        self.immunity_active = True

    def remove_immunity(self):
        self.hit_speed = self.normal_hit_speed
        self.move_speed = self.normal_move_speed
        self.invulnerable = False
        self.unaffectable = False
        self.targetable = True
        self.display_transparent = False
        self.immunity_active = False

    def damage(self, amount):
        super().damage(amount)
        if not self.immunity_active and self.immunity_remaining > 0:
            self.activate_immunity()

    def cleanup_func(self, arena):
        if self.immunity_active and self.immunity_remaining > 0:
            self.immunity_remaining -= TICK_TIME
        elif self.immunity_active:
            self.remove_immunity()
            
        
        super().cleanup_func(arena)