import royal_arena_cards
from abstract_classes import AttackEntity
from abstract_classes import Troop
from abstract_classes import TILES_PER_MIN
import vector

class EvolutionRoyalGiantSpecialAttackEntity(AttackEntity):
    SPLASH_RADIUS = 2.5
    def __init__(self, side, damage, position):
        super().__init__(
            s=side,
            d=damage,
            v=0,
            l=0.2,
            i_p=position
        )
        self.display_size =self.SPLASH_RADIUS


    def detect_hits(self, arena):
        hits = []
        for each in arena.towers + arena.buildings + arena.troops:
            if each.side != self.side and not each.invulnerable and (not isinstance(each, Troop) or each.ground): # if different side
                if vector.distance(self.position, each.position) < self.SPLASH_RADIUS + each.collision_radius:
                    hits.append(each)
        return hits

    def apply_effect(self, target):
        if isinstance(target, Troop) and target.can_kb and not target.invulnerable:
            vec = target.position.subtracted(self.position)
            vec.normalize()
            target.kb(vec)

class EvolutionRoyalGiant(royal_arena_cards.RoyalGiant):
    def __init__(self, side, position, level):
        super().__init__(side, position, level)
        self.hit_points = self.hit_points * 1.1
        self.cur_hp = self.cur_hp * 1.1
        self.evo = True
        self.special_damage = 32 * pow(1.1, level - 11)

    def level_up(self):
        super().level_up()
        self.special_damage *= 1.1
    
    def attack(self):
        return [super().attack(), EvolutionRoyalGiantSpecialAttackEntity(self.side, self.special_damage, self.position)]
    
class EvolutionRoyalRecruit(royal_arena_cards.RoyalRecruit):
    def __init__(self, side, position, level):
        super().__init__(side, position, level)
        self.evo = True
        self.hit_points *= 1.11
        self.cur_hp *= 1.11
        self.hit_damage *= 1.12
        self.charge_speed = 120 * TILES_PER_MIN
        self.charge_damage = self.hit_damage * 2
        self.charge_charge_distance = 0
        self.charging = False

    def kb(self, vec, t=None):
        if vec.magnitude() > 0:
            self.charging = False
            self.charge_charge_distance = 0
            self.move_speed = 60 * TILES_PER_MIN
            super().kb(vec, t)
    
    def freeze(self, duration):
        self.stun_timer = duration
        self.charging = False
        self.charge_charge_distance = 0
        self.move_speed = 60 * TILES_PER_MIN
        self.attack_cooldown = self.hit_speed

    def tick_func(self, arnea):
        if self.shield_hp <= 0 and self.stun_timer <= 0 and not self.charging and self.charge_charge_distance >= 2:
            self.charging = True
            self.move_speed = self.charge_speed
            self.charge_charge_distance = 0
        if self.shield_hp <= 0 and self.stun_timer <= 0 and self.deploy_time <= 0 and not self.charging and not self.move_vector.magnitude() == 0: #if not in range
            self.charge_charge_distance += self.move_speed

    def attack(self):
        if self.charging:
            self.charging = False 
            self.charge_charge_distance = 0
            self.move_speed = 60 * TILES_PER_MIN
            return royal_arena_cards.RoyalRecruitAttackEntity(self.side, self.hit_damage * 2, self.position, self.target)
        else:
            return super().attack()
        
class EvolutionRoyalHogDropAttackEntity(AttackEntity):
    SPLASH_RADIUS = 1.4
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
            if each.side != self.side and not each.invulnerable and (not isinstance(each, Troop) or each.ground): # if different side
                if vector.distance(self.position, each.position) < self.SPLASH_RADIUS + each.collision_radius:
                    hits.append(each)
        return hits
        
class EvolutionRoyalHog(royal_arena_cards.RoyalHog):
    def __init__(self, side, position, level):
        super().__init__(side, position, level)
        self.evo = True
        self.drop_damage = 115 * pow(1.1, level - 11)
        self.ground = False
        self.dropped = False

    def level_up(self):
        self.drop_damage *= 1.1
        return super().level_up()

    def tick_func(self, arena):
        if self.dropped:
            self.dropped = False
            arena.active_attacks.append(EvolutionRoyalHogDropAttackEntity(self.side, self.drop_damage, self.position))
            self.ground = True #fall

    def attack(self):
        if not self.ground:
            self.dropped = True #drop
        return super().attack()

    def damage(self, amount):
        if not self.ground:
            self.dropped = True
        return super().damage(amount)

    