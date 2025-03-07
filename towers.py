import vector
import math
from abstract_classes import AttackEntity
from abstract_classes import Tower
from abstract_classes import TILES_PER_MIN
from abstract_classes import TICK_TIME

class PrincessTowerAttackEntity(AttackEntity):
    PRINCESS_PROJECTILE_CONTACT_RANGE = 0.5 #kinda random, maybe factcheck with wiki later?
    def __init__(self, side, damage, position, target):
        super().__init__(
            s=side,
            d=damage,
            v=600*TILES_PER_MIN,
            l=float('inf'),
            i_p=position
        )
        self.target = target
        self.should_delete = False

    def detect_hits(self, arena):
        if (vector.Vector.distance(self.target.position, self.position) < PrincessTowerAttackEntity.PRINCESS_PROJECTILE_CONTACT_RANGE):
            return [self.target] # has hit
        else:
            return [] #hasnt hit yet
            
    def tick(self, arena):
        hits = self.detect_hits(arena)
        if len(hits) > 0:
            hits[0].cur_hp -= self.damage
            self.should_delete = True
        else:
            direction = vector.Vector(
                self.target.position.x - self.position.x, 
                self.target.position.y - self.position.y
            )
            magnitude = math.sqrt((direction.x ** 2 + direction.y ** 2))

            if magnitude > 0:
                direction.scale(1 / magnitude)  # Convert to unit vector.Vector

            movement = direction.scaled(self.velocity)
            self.position.add(movement)

    def cleanup(self, arena):
        if self.should_delete:
            arena.active_attacks.remove(self)




class PrincessTower(Tower):
    def __init__(self, side, level, l_or_r):
        x = 5.5 if l_or_r else -5.5 #right is true left is false
        y = -10 if side else 10 #your side is true opp side is false
        super().__init__(
            s=side,
            h_d=50 * pow(1.1, level - 1),
            h_r=7.5,
            h_s=0.8,
            l_t=0.81, #.01 extra so it stays below 0
            h_p=1400 * pow(1.1, level - 1),
            p=vector.Vector(x, y)
        )
    def attack(self):
        return PrincessTowerAttackEntity(self.side, self.hit_damage, self.position)

class KingTowerAttackEntity(AttackEntity):
    KING_PROJECTILE_CONTACT_RANGE = 0.5 #kinda random, maybe factcheck with wiki later?
    MAX_TOWERS = 3
    def __init__(self, side, damage, position, target):
        super().__init__(
            s=side,
            d=damage,
            v=1000*TILES_PER_MIN,
            l=float('inf'),
            i_p=position
        )
        self.target = target
        self.should_delete = False

    def detect_hits(self, arena):
        if (vector.Vector.distance(self.target.position, self.position) < KingTowerAttackEntity.KING_PROJECTILE_CONTACT_RANGE):
            return [self.target] # has hit
        else:
            return [] #hasnt hit yet
            
    def tick(self, arena):
        hits = self.detect_hits(arena)
        if len(hits) > 0:
            hits[0].cur_hp -= self.damage
            self.should_delete = True
        else:
            direction = vector.Vector(
                self.target.position.x - self.position.x, 
                self.target.position.y - self.position.y
            )
            magnitude = math.sqrt((direction.x ** 2 + direction.y ** 2))

            if magnitude > 0:
                direction.scale(1 / magnitude)  # Convert to unit vector.Vector

            movement = direction.scaled(self.velocity)
            self.position.add(movement)

    def cleanup(self, arena):
        if self.should_delete:
            arena.active_attacks.remove(self)


class KingTower(Tower):
    def __init__(self, side, level):
        super().__init__(
            s=side,
            h_d=50 * pow(1.1, level - 1),
            h_r=7,
            h_s=1,
            l_t=0.5,
            h_p=2400 * pow(1.1, level - 1),
            p=vector.Vector(0, -13 if side else 13)
        )
        self.activated = False
        self.activation_timer = 4
    
    def attack(self):
        return KingTowerAttackEntity(self.side, self.hit_damage, self.position)

    def tick(self, arena):
        if self.target is None or self.target.cur_hp <= 0:
            self.update_target(arena)
        if self.activation_timer <= 0 and not self.target is None and self.attack_cooldown <= 0:
            self.attack()
            self.attack_cooldown = self.hit_speed
    

    def cleanup(self, arena):
        if self.cur_hp <= 0:
            arena.towers.remove(self)
        
        if vector.Vector.distance(self.target.position, self.position) > self.hit_range and (self.attack_cooldown <= self.hit_speed - self.load_time):
                self.attack_cooldown = self.hit_speed - self.load_time #if not currently attacking but cooldown is less than first hit delay
        else: #otherwise
            self.attack_cooldown -= TICK_TIME

        if not self.activated:
            if self.cur_hp < self.hit_points: # if been hit
                activated = True #activate

            alive_towers = 0
            for each in arena.towers: #count # towers
                if each.side == self.side:
                    alive_towers += 1

            if alive_towers < KingTower.MAX_TOWERS: #if any towers gone
                activated = True #activate
        elif self.activation_timer > 0:
            self.activation_timer -= TICK_TIME