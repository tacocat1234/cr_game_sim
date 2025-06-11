import barbarian_bowl_cards
from abstract_classes import AttackEntity
from abstract_classes import Troop
from abstract_classes import Tower
from abstract_classes import TICK_TIME
from abstract_classes import TILES_PER_MIN
import vector
import math

class EvolutionBarbarian(barbarian_bowl_cards.Barbarian):
    def __init__(self, side, position, level, cloned=False):
        super().__init__(side, position, level, cloned)
        self.evo = True
        self.normal_hit_damage = self.hit_damage
        self.hit_points = self.hit_points * 1.1
    
    def attack(self):
        self.rage()
        self.hit_damage = 1.35 * self.hit_damage
        self.rage_timer = 3
        return super().attack()
    
    def tick_func(self, arena):
        if self.rage_timer <= 0:
            self.hit_damage = self.normal_hit_damage

class EvolutionBattleRamSpecialAttackEntity(AttackEntity):
    SPLASH_RADIUS = 1.5
    def __init__(self, side, damage, position):
        super().__init__(
            s=side,
            d=damage,
            v=0,
            l=float('inf'),
            i_p=position
        )
        self.display_size = 0

    def detect_hits(self, arena):
        hits = []
        for each in arena.towers + arena.buildings + arena.troops:
            if each.side != self.side and (isinstance(each, Troop) and (each.ground and not each.invulnerable)): # if different side
                if vector.distance(self.position, each.position) < self.SPLASH_RADIUS + each.collision_radius:
                    hits.append(each)
        return hits

    def apply_effect(self, target):
        if target.can_kb and not target.invulnerable:
            vec = target.position.subtracted(self.position)
            vec.normalize()
            vec.scale(2)
            target.kb(vec)

class EvolutionBattleRam(barbarian_bowl_cards.BattleRam):
    def __init__(self, side, position, level):
        super().__init__(side, position, level)
        self.evo = True
        self.special_damage = 100 * pow(1.1, level - 3)
        self.special_attack = EvolutionBattleRamSpecialAttackEntity(self.side, self.special_damage, self.position)
        self.special_removed = True

    def tick_func(self, arena):
        if self.stun_timer <= 0 and not self.charging and self.charge_charge_distance >= 3:
            arena.active_attacks.append(self.special_attack)
            self.special_removed = False
            self.charging = True
            self.move_speed = self.charge_speed
            self.charge_charge_distance = 0
        if self.stun_timer <= 0 and self.deploy_time <= 0 and not self.charging: #if not in range
            self.charge_charge_distance += self.move_speed
        
        if not self.special_removed and not self.charging:
            arena.active_attacks.remove(self.special_attack)
            self.special_removed = True

    def die(self, arena):
        radians = math.radians(self.facing_dir)
        # Use cosine for x offset and sine for y offset
        dx = math.cos(radians) * 0.3
        dy = math.sin(radians) * 0.3

        # Spawn two troops offset in opposite directions perpendicular to the facing direction
        offset1 = vector.Vector(-dy, dx)
        offset2 = vector.Vector(dy, -dx)

        if self.charging:
            arena.active_attacks.remove(self.special_attack)

        arena.troops.append(EvolutionBarbarian(self.side, self.position.added(offset1), self.level, self.cloned))
        arena.troops.append(EvolutionBarbarian(self.side, self.position.added(offset2), self.level, self.cloned))
        arena.troops.remove(self)
        self.cur_hp = -1


    def attack(self):
        charge = self.charging
        c = vector.Vector(-2 * math.cos(math.radians(self.facing_dir)),
                  -2 * math.sin(math.radians(self.facing_dir)))
        self.kb(c)
        self.charging = charge
        if self.charging:
            self.move_speed = 120 * TILES_PER_MIN
            return barbarian_bowl_cards.BattleRamAttackEntity(self.side, self.charge_damage, self.position, self.target)  
        else:
            return barbarian_bowl_cards.BattleRamAttackEntity(self.side, self.hit_damage, self.position, self.target)

class EvolutionCannonSpecialAttackEntity(AttackEntity):
    SPLASH_RADIUS = 2
    def __init__(self, side, damage, ctd, position, delay):
        super().__init__(
            s=side,
            d=damage,
            v=0,
            l=0.5 + delay,
            i_p=position
        )
        self.ctd = ctd
        self.display_size = 0.25
        self.resize = True
        self.position = self.position.added(vector.Vector(0, delay * 30))
        self.delay = delay
        self.delay_left = delay

    def tick(self, arena):
        if self.delay_left > 0:
            self.delay_left -= TICK_TIME
            self.position.subtract(vector.Vector(0, 1/2))
            return
        
        self.resize = False
        self.display_size = self.SPLASH_RADIUS
        self.tick_func(arena)

        hits = self.detect_hits(arena)
        for each in hits:
            new = not each in self.has_hit
            if (new):
                if isinstance(each, Tower):
                    each.damage(self.ctd)
                else:
                    each.damage(self.damage)
                    self.apply_effect(each)
                self.has_hit.append(each)

    def detect_hits(self, arena):
        hits = []
        for each in arena.towers + arena.buildings + arena.troops:
            if each.side != self.side and not each.invulnerable: # if different side
                if vector.distance(self.position, each.position) < self.SPLASH_RADIUS + each.collision_radius:
                    hits.append(each)
        return hits

    def apply_effect(self, target):
        if isinstance(target, Troop) and target.can_kb and not target.invulnerable:
            vec = target.position.subtracted(self.position)
            vec.normalize()
            vec.scale(2)
            target.kb(vec)

class EvolutionCannon(barbarian_bowl_cards.Cannon):
    def __init__(self, side, position, level):
        super().__init__(side, position, level)
        self.evo = True
        self.strike_damage = 138 * pow(1.1, level - 1)
        self.strike_ctd = 35 * pow(1.1, level - 1)

    def on_deploy(self, arena):
        arena.active_attacks.append(EvolutionCannonSpecialAttackEntity(self.side, self.strike_damage, self.strike_ctd, vector.Vector(2.5, self.position.y + 1.5 if self.side else -1.5), 4/6))
        arena.active_attacks.append(EvolutionCannonSpecialAttackEntity(self.side, self.strike_damage, self.strike_ctd, vector.Vector(-2.5, self.position.y + 1.5 if self.side else -1.5), 4/6))
        arena.active_attacks.append(EvolutionCannonSpecialAttackEntity(self.side, self.strike_damage, self.strike_ctd, vector.Vector(7.5, self.position.y + 1.5 if self.side else -1.5), 1))
        arena.active_attacks.append(EvolutionCannonSpecialAttackEntity(self.side, self.strike_damage, self.strike_ctd, vector.Vector(-7.5, self.position.y + 1.5 if self.side else -1.5), 1))
        arena.active_attacks.append(EvolutionCannonSpecialAttackEntity(self.side, self.strike_damage, self.strike_ctd, vector.Vector(0, self.position.y + 8.5 if self.side else -8.5), 4/6))
        arena.active_attacks.append(EvolutionCannonSpecialAttackEntity(self.side, self.strike_damage, self.strike_ctd, vector.Vector(4.5, self.position.y + 8.5 if self.side else -8.5), 5/6))
        arena.active_attacks.append(EvolutionCannonSpecialAttackEntity(self.side, self.strike_damage, self.strike_ctd, vector.Vector(-4.5, self.position.y + 8.5 if self.side else -8.5), 5/6))
        arena.active_attacks.append(EvolutionCannonSpecialAttackEntity(self.side, self.strike_damage, self.strike_ctd, vector.Vector(8.5, self.position.y + 8.5 if self.side else -8.5), 1))
        arena.active_attacks.append(EvolutionCannonSpecialAttackEntity(self.side, self.strike_damage, self.strike_ctd, vector.Vector(-8.5, self.position.y + 8.5 if self.side else -8.5), 1))