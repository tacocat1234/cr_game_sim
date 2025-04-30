import vector
import math
import copy
from abstract_classes import AttackEntity
from abstract_classes import RangedAttackEntity
from abstract_classes import Tower
from abstract_classes import TILES_PER_MIN
from abstract_classes import TICK_TIME

class PrincessTowerAttackEntity(AttackEntity):
    def __init__(self, side, damage, position, target):
        super().__init__(
            s=side,
            d=damage,
            v=600*TILES_PER_MIN,
            l=float('inf'),
            i_p=copy.deepcopy(position)
        )
        self.target = target
        self.should_delete = False

    def detect_hits(self, arena):
        if (vector.distance(self.target.position, self.position) < self.target.collision_radius):
            return [self.target] # has hit
        else:
            return [] #hasnt hit yet
            
    def tick(self, arena):
        hits = self.detect_hits(arena)
        if len(hits) > 0:
            hits[0].damage(self.damage)
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
        y = -9.5 if side else 9.5 #your side is true opp side is false
        super().__init__(
            s=side,
            h_d=50 * pow(1.08, level - 1),
            h_r=7.5,
            h_s=0.8,
            l_t=0.867, #.0166... extra so it stays below 0
            h_p=1400 * pow(1.1, level - 1),
            c_r=1,
            p=vector.Vector(x, y)
        )

        self.level = level

    def attack(self):
        return PrincessTowerAttackEntity(self.side, self.hit_damage, self.position, self.target)

class KingTowerAttackEntity(AttackEntity):
    def __init__(self, side, damage, position, target):
        super().__init__(
            s=side,
            d=damage,
            v=1000*TILES_PER_MIN,
            l=float('inf'),
            i_p=copy.deepcopy(position)
        )
        self.target = target
        self.should_delete = False

    def detect_hits(self, arena):
        if (vector.distance(self.target.position, self.position) < self.target.collision_radius):
            return [self.target] # has hit
        else:
            return [] #hasnt hit yet
            
    def tick(self, arena):
        hits = self.detect_hits(arena)
        if len(hits) > 0:
            hits[0].damage(self.damage)
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
    MAX_TOWERS = 3
    def __init__(self, side, level):
        super().__init__(
            s=side,
            h_d=50 * pow(1.08, level - 1),
            h_r=7,
            h_s=1,
            l_t=0.5,
            h_p=2400 * pow(1.1, level - 1),
            c_r=1.4,
            p=vector.Vector(0, -13 if side else 13)
        )
        self.activated = False
        self.activation_timer = 4

        self.level = level
    
    def attack(self):
        return KingTowerAttackEntity(self.side, self.hit_damage, self.position, self.target)

    def tick(self, arena):
        if self.stun_timer <= 0:
            if self.target is None or self.target.cur_hp <= 0:
                self.update_target(arena)
            if self.activation_timer <= 0 and not self.target is None and self.attack_cooldown <= 0:
                arena.active_attacks.append(self.attack())
                self.attack_cooldown = self.hit_speed

            class_name = self.__class__.__name__.lower()
            if not self.animation_cycle_frames == 1: #more than one frame per thing
                self.sprite_path = f"sprites/{class_name}/{class_name}_{self.animation_cycle_cur}.png"
            else:
                self.sprite_path = f"sprites/{class_name}/{class_name}.png"


    def cleanup(self, arena):
        if self.cur_hp <= 0:
            arena.towers.remove(self)
            return not self.side
        

        if self.stun_timer <= 0:
            if self.target is None or (vector.distance(self.target.position, self.position) > self.hit_range + self.collision_radius and (self.attack_cooldown <= self.hit_speed - self.load_time)):
                    self.attack_cooldown = self.hit_speed - self.load_time #if not currently attacking but cooldown is less than first hit delay
            else: #otherwise
                self.attack_cooldown -= TICK_TIME

            if not self.activated:
                if self.cur_hp < self.hit_points: # if been hit
                    self.activated = True #activate

                alive_towers = 0
                for each in arena.towers: #count # towers
                    if each.side == self.side:
                        alive_towers += 1

                if alive_towers < KingTower.MAX_TOWERS: #if any towers gone
                    self.activated = True #activate
            elif self.activation_timer > 0:
                self.activation_timer -= TICK_TIME
        else:
            self.stun_timer -= TICK_TIME

class CannoneerAttackEntity(RangedAttackEntity):
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            velocity=1000*TILES_PER_MIN,
            position=position,
            target=target,
        )
        self.display_size = 0.35
        self.resize = True

class Cannoneer(Tower):
    def __init__(self, side, level, l_or_r):
        x = 5.5 if l_or_r else -5.5 #right is true left is false
        y = -9.5 if side else 9.5 #your side is true opp side is false
        super().__init__(
            s=side,
            h_d=241 * pow(1.08, level - 6),
            h_r=7.5,
            h_s=2.4,
            l_t=1.6, #.01 extra so it stays below 0
            h_p=1940 * pow(1.1, level - 6),
            c_r=1,
            p=vector.Vector(x, y)
        )

        self.level = level
    def attack(self):
        return CannoneerAttackEntity(self.side, self.hit_damage, self.position, self.target)