from abstract_classes import RangedAttackEntity
from abstract_classes import MeleeAttackEntity
from abstract_classes import AttackEntity
from abstract_classes import Troop
from abstract_classes import Tower
from abstract_classes import Spell
from abstract_classes import on_bridge
from abstract_classes import same_sign
from abstract_classes import TILES_PER_MIN
from abstract_classes import TICK_TIME
import vector
import copy
import math

class LogAttackEntity(AttackEntity):
    def __init__(self, side, damage, c_t_d, pos):
        super().__init__(
            s=side, 
            d=damage, 
            v=200 * TILES_PER_MIN, 
            l=3.03, 
            i_p=pos)
        self.has_hit = []
        self.crown_tower_damage = c_t_d
        
    def detect_hits(self, arena):
        hits = []
        for each in arena.troops + arena.buildings + arena.towers:
            if each.side != self.side and each.ground and not each.invulnerable and not each in self.has_hit:
                if each.position.x < self.position.x + 1.95 and each.position.x > self.position.x - 1.95 and each.position.y < self.position.y + 0.6 and each.position.y > self.position.y - 0.6:
                    hits.append(each)
        return hits
    
    def tick(self, arena):
        self.position.y += self.velocity if self.side else -self.velocity
        hits = self.detect_hits(arena)
        for each in hits:
            new = not each in self.has_hit
            if (new):
                if isinstance(each, Troop):
                    each.kb(vector.Vector(0, 0.7 if self.side else -0.7))
                    each.damage(self.damage)
                elif isinstance(each, Tower):
                    each.damage(self.crown_tower_damage)
                else:
                    each.damage(self.damage)
                self.has_hit.append(each)
    
class Log(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p = float('inf'),         # Hit points (Example value)
            h_d= 240 * pow(1.1, level - 9),          # Hit damage (Example value)
            h_s=0.1,          # Hit speed (Seconds per hit)
            l_t=0.1,            # First hit cooldown
            h_r=5.5,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=200*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=1,            #mass
            c_r=1.95,        #collision radius
            p=position               # Position (vector.Vector object)
        )
        self.level = level
        self.targetable = False
        self.invulnerable = True
        self.collideable = False
        self.timer = 3.03
        self.crown_tower_damage = 48 * pow(1.1, level - 9)

        self.collideable = False

        self.first = True

    def on_deploy(self, arena):
        self.targetable = False
        self.invulnerable = True
        self.collideable = False

    def move(self, arena):
        self.position.y += self.move_speed if self.side else -self.move_speed
    
    def tick(self, arena):
        self.timer -= TICK_TIME
        self.move(arena)
        if self.first:
            arena.active_attacks.append(self.attack())
            self.first = False
        if self.timer <= 0:
            self.should_delete = True

        

    def attack(self):
        return LogAttackEntity(self.side, self.hit_damage, self.crown_tower_damage, copy.deepcopy(self.position))
    
class ElectroWizardAttackEntity(RangedAttackEntity):
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            velocity=2000*TILES_PER_MIN,
            position=position,
            target=target,
        )

    def apply_effect(self, target):
        target.stun()

class ElectroWizardSpawnAttackEntity(AttackEntity):
    SPLASH_RADIUS = 2.5
    def __init__(self, side, damage, position, target_pos):
        super().__init__(
            s=side,
            d=damage,
            v=0,
            l=1/60 + 0.01,
            i_p=copy.deepcopy(position)
        )
        self.display_size = self.SPLASH_RADIUS

    def apply_effect(self, target):
        target.stun()
    
    def detect_hits(self, arena):
        hits = []
        for each in arena.towers + arena.buildings + arena.troops:
            if each.side != self.side: # if different side
                if vector.distance(self.position, each.position) < self.SPLASH_RADIUS + each.collision_radius:
                        hits.append(each)

        return hits

class ElectroWizard(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 590 * pow(1.1, level - 9),         # Hit points (Example value)
            h_d= 91 * pow(1.1, level - 9),          # Hit damage (Example value)
            h_s=1.8,          # Hit speed (Seconds per hit)
            l_t=1.2,            # First hit cooldown
            h_r=5,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=False,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=90*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=5,            #mass
            c_r=0.5,        #collision radius
            p=position               # Position (vector.Vector object)
        ) 
        self.level = level
        self.secondary_target = None

        self.spawn_damage = 159 * pow(1.1, level - 9)

    def update_target(self, arena):
        self.target = None
        self.secondary_target = None
        min_dist = float('inf')
        second_min_dist = float('inf')

        for each in arena.troops + arena.buildings:
            if not each.invulnerable and each.targetable and each.side != self.side:
                dist = vector.distance(each.position, self.position)
                if dist < self.hit_range + each.collision_radius:
                    if dist < min_dist:
                        # Shift current closest to secondary
                        self.secondary_target = self.target
                        second_min_dist = min_dist

                        # Update closest
                        self.target = each
                        min_dist = dist
                    elif dist < second_min_dist:
                        self.secondary_target = each
                        second_min_dist = dist

    def tick(self, arena):
        self.tick_func(arena)
        
        if self.stun_timer <= 0 and self.deploy_time <= 0:
            if self.target is None or self.target.cur_hp <= 0 or vector.distance(self.target.position, self.position) > self.sight_range:
                self.update_target(arena)
            if self.secondary_target is None or self.secondary_target.cur_hp <= 0 or vector.distance(self.secondary_target.position, self.position) > self.sight_range:
                self.update_target(arena)

            self.move(arena)
            
            if (not self.target is None or not self.secondary_target is None) and self.attack_cooldown <= 0:
                atk = self.attack()
                arena.active_attacks.extend(atk)
                self.attack_cooldown = self.hit_speed
            
    def on_deploy(self, arena):
        arena.active_attacks.append(ElectroWizardSpawnAttackEntity(self.side, self.spawn_damage, self.position, self.target))

    def attack(self):
        attacks = []
        if self.target is not None and vector.distance(self.position, self.target.position) < self.hit_range + self.collision_radius + self.target.collision_radius:
            attacks.append(ElectroWizardAttackEntity(self.side, self.hit_damage, self.position, self.target))
        if self.secondary_target is not None and vector.distance(self.position, self.secondary_target.position) < self.hit_range + self.collision_radius + self.secondary_target.collision_radius:
            attacks.append(ElectroWizardAttackEntity(self.side, self.hit_damage, self.position, self.secondary_target))
        return attacks

class MinerAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 1.2
    COLLISION_RADIUS = 0.5
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            position=position,
            target=target
            )
        
            
class Miner(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 1000 * pow(1.1, level - 9),         # Hit points (Example value)
            h_d= 160 * pow(1.1, level - 9),          # Hit damage (Example value)
            h_s=1.2,          # Hit speed (Seconds per hit)
            l_t=0.7,            # First hit cooldown
            h_r=1.2,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=650*TILES_PER_MIN,          # Movement speed 
            d_t=0,            # Deploy time
            m=6,            #mass
            c_r=0.5,        #collision radius
            p=vector.Vector(0, -13 if side else 13)               # Position (vector.Vector object)
        )
        self.target = position
        self.level = level
        self.invulnerable = True
        self.targetable = False
        self.collideable = False
        self.preplace = False
        self.normal_move_speed = 90*TILES_PER_MIN

    def tick_func(self, arena):
        if self.invulnerable and vector.distance(self.position, self.target) < 0.25:
            self.move_speed = 90 * TILES_PER_MIN
            self.invulnerable = False
            self.targetable = True
            self.collideable = True
            self.target = None
    
    def on_deploy(self, arena):
        self.invulnerable = True
        self.targetable = False
        self.collideable = False

    def move(self, arena):
        tar_pos = None if self.target is None else (self.target if isinstance(self.target, vector.Vector) else self.target.position)
        direction_x = 0
        direction_y = 0
        m_s = self.move_speed
        if self.target is None: #head towards tower, since it sees nobody else
            min_dist = float('inf')
            tower_target = None
            for tower in arena.towers:
                if tower.side != self.side:
                    if vector.distance(tower.position, self.position) < min_dist:
                        tower_target = tower
                        min_dist = vector.distance(tower.position, self.position)

            if not tower_target is None and self.ground and (not same_sign(tower_target.position.y, self.position.y) and ((self.position.y < -1 or self.position.y > 1) or not on_bridge(self.position.x))): # if behind bridge and cant cross river
                r_bridge = vector.distance(vector.Vector(5.5, 0), self.position)
                l_bridge = vector.distance(vector.Vector(-5.5, 0), self.position)
                
                tar_bridge = None
                
                
                if (r_bridge < l_bridge): #find closest bridge
                    tar_bridge = vector.Vector(5.5, 0)
                elif abs(r_bridge - l_bridge) > 0.1:
                    tar_bridge = vector.Vector(-5.5, 0)
                else: # if similar dist
                    if vector.distance(vector.Vector(5.5, 0), tower_target.position) < vector.distance(vector.Vector(-5.5, 0), tower_target.position):
                        tar_bridge = vector.Vector(5.5, 0) #go to side closer to tower
                    else:
                        tar_bridge = vector.Vector(-5.5, 0)
            
                direction_x = tar_bridge.x - self.position.x #set movement
                direction_y = tar_bridge.y - self.position.y
                distance_to_target = math.sqrt(direction_x ** 2 + direction_y ** 2)
            elif not tower_target is None:
                direction_x = tower_target.position.x - self.position.x #set to directly move to tower
                direction_y = tower_target.position.y - self.position.y
                distance_to_target = math.sqrt(direction_x ** 2 + direction_y ** 2)

            # Normalize direction
            
            if tower_target is None:
                return #exit
            elif self.move_speed != 650 * TILES_PER_MIN and min_dist < self.hit_range + self.collision_radius + tower_target.collision_radius: #within hit range, locks on
                self.target = tower_target
                self.move_vector = vector.Vector(0, 0)
                direction_x = tower_target.position.x - self.position.x #set to directly move to tower
                direction_y = tower_target.position.y - self.position.y
                self.facing_dir = math.degrees(math.atan2(direction_y, direction_x))  # Get angle in degrees
                return True
            
            direction_x /= distance_to_target
            direction_y /= distance_to_target
            # Move in the direction of the target
            self.position.x += direction_x * m_s
            self.position.y += direction_y * m_s

            angle = math.degrees(math.atan2(direction_y, direction_x))  # Get angle in degrees
            self.facing_dir = angle
            self.move_vector = vector.Vector(direction_x * m_s, direction_y * m_s)
            return False
        #and (not same side) while also (not at bridge) 
        if self.ground and (not same_sign(tar_pos.y, self.position.y) and ((self.position.y < -1 or self.position.y > 1) or not on_bridge(self.position.x))):
            
            r_bridge = vector.distance(vector.Vector(5.5, 0), tar_pos)
            l_bridge = vector.distance(vector.Vector(-5.5, 0), tar_pos)
            
            tar_bridge = None
            
            if (r_bridge < l_bridge):
                tar_bridge = vector.Vector(5.5, 0)
            else:
                tar_bridge = vector.Vector(-5.5, 0)
            
            direction_x = tar_bridge.x - self.position.x
            direction_y = tar_bridge.y - self.position.y
            distance_to_target = math.sqrt(direction_x ** 2 + direction_y ** 2)
        else:
            direction_x = tar_pos.x - self.position.x
            direction_y = tar_pos.y - self.position.y
            distance_to_target = math.sqrt(direction_x ** 2 + direction_y ** 2)
        
        if self.move_speed != 650 * TILES_PER_MIN and vector.distance(tar_pos, self.position) < self.hit_range + self.collision_radius + self.target.collision_radius: #within hit range, then dont move just attack
            self.move_vector = vector.Vector(0, 0)
            direction_x = tar_pos.x - self.position.x #set to directly move to tower
            direction_y = tar_pos.y - self.position.y
            self.facing_dir = math.degrees(math.atan2(direction_y, direction_x))  # Get angle in degrees
            return True
        
        direction_x /= distance_to_target
        direction_y /= distance_to_target
        # Move in the direction of the target

        self.position.x += direction_x  * m_s
        self.position.y += direction_y * m_s
        angle = math.degrees(math.atan2(direction_y, direction_x))  # Get angle in degrees
        self.facing_dir = angle
        self.move_vector = vector.Vector(direction_x * m_s, direction_y * m_s)
        return False

    def tick(self, arena):
        if self.preplace:
            return
        #update arena before
        tar_pos = None if self.target is None else (self.target if isinstance(self.target, vector.Vector) else self.target.position)

        self.tick_func(arena)
        if self.stun_timer <= 0:
            if self.deploy_time <= 0:
                if self.move_speed != 650 * TILES_PER_MIN:
                    if self.target is None or self.target.cur_hp <= 0 or not self.target.targetable:
                        self.update_target(arena)
                    elif vector.distance(self.position, tar_pos) > self.sight_range + self.collision_radius + self.target.collision_radius: #add 0.2 so there is tiny buffer for ranged troops
                        self.update_target(arena)
                if self.move(arena) and self.move_speed != 650 * TILES_PER_MIN and self.attack_cooldown <= 0: #move, then if within range, attack
                    atk = self.attack()
                    if isinstance(atk, list) and len(atk) > 0:
                        arena.active_attacks.extend(atk)
                    elif not atk is None:
                        arena.active_attacks.append(atk)
                    self.attack_cooldown = self.hit_speed


    def cleanup(self, arena): # each troop runs this after ALL ticks are finished
        if self.preplace:
            return
        self.cleanup_func(arena)

        if self.cur_hp <= 0 or self.should_delete:
            self.die(arena)
        
        if self.slow_timer < 0 :
            self.slow_timer = 0
            self.unslow()
        elif self.slow_timer > 0:
            self.slow_timer -= TICK_TIME

        if self.deploy_time > 0: #if deploying, timer
            self.deploy_time -= TICK_TIME
            if self.deploy_time <= 0:
                self.on_deploy(arena)
        elif self.stun_timer <= 0:
            if self.move_speed != 650 * TILES_PER_MIN:
                if not self.target is None and not vector.distance(self.target.position, self.position) < self.hit_range + self.target.collision_radius + self.collision_radius and (self.attack_cooldown <= self.hit_speed - self.load_time):
                    self.attack_cooldown = self.hit_speed - self.load_time #if not currently attacking but cooldown is less than first hit delay
                else: #otherwise
                    self.attack_cooldown -= TICK_TIME #decrement time if either close enough to attack, cooldown greater than min cooldown, or both
            
            class_name = self.__class__.__name__.lower()
            if not self.walk_cycle_frames == 1: #more than one frame per thing
                self.sprite_path = f"sprites/{class_name}/{class_name}_{self.walk_cycle_cur}.png"
            else:
                self.sprite_path = f"sprites/{class_name}/{class_name}.png"

            if self.cur_ticks_per_frame <= 0:
                self.cur_ticks_per_frame = self.ticks_per_frame
                self.walk_cycle_cur += 1
                if self.walk_cycle_cur >= self.walk_cycle_frames:
                    self.walk_cycle_cur = 0
            else:
                self.cur_ticks_per_frame -= 1
        else:
            self.stun_timer -= TICK_TIME

    def attack(self):
        return MinerAttackEntity(self.side, self.hit_damage * 0.25 if isinstance(self.target, Tower) else self.hit_damage, self.position, self.target)

class PrincessAttackEntity(RangedAttackEntity):
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            velocity=600*TILES_PER_MIN,
            position=position,
            target=target,
        )
        self.exploded = False
        self.has_hit = []        

    def detect_hits(self, arena):
        hits = []
        if self.exploded:
            for each in arena.towers + arena.buildings + arena.troops:
                if each.side != self.side: # if different side
                    if vector.distance(self.position, each.position) < 2 + each.collision_radius:
                        hits.append(each)
        return hits
            
    def tick(self, arena):
        if self.exploded:
            hits = self.detect_hits(arena)
            for each in hits:
                new = not any(each is h for h in self.has_hit)
                if (new):
                    each.damage(self.damage)
                    self.has_hit.append(each)
        else:
            direction = self.target.subtracted(self.position)
            direction.normalize()

            movement = direction.scaled(self.velocity)
            self.position.add(movement)
            
            if vector.distance(self.position, self.target) < 0.25:
                self.display_size = 2
                self.duration =  0.1
                self.exploded = True

class Princess(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 216 * pow(1.1, level - 9),         # Hit points (Example value)
            h_d= 140 * pow(1.1, level - 9),          # Hit damage (Example value)
            h_s=3,          # Hit speed (Seconds per hit)
            l_t=2.5,            # First hit cooldown
            h_r=9,            # Hit range
            s_r=9.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=False,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=3,            #mass
            c_r=0.5,     #collision radius
            p=position               # Position (vector.Vector object)
        )
        self.level = level
    def attack(self):
        return PrincessAttackEntity(self.side, self.hit_damage, self.position, self.target.position)

class SparkyAttackEntity(RangedAttackEntity):
    SPLASH_RADIUS = 1.8
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            velocity=1400*TILES_PER_MIN,
            position=position,
            target=target,
        )
        self.exploded = False
        self.display_size = 0.5
        self.resize = True

    def detect_hits(self, arena):
        hits = []
        if self.exploded:
            for each in arena.towers + arena.buildings + arena.troops:
                if each.side != self.side and (isinstance(each, Tower) or (not each.invulnerable)): # if different side
                    if vector.distance(self.position, each.position) < self.SPLASH_RADIUS + each.collision_radius:
                        hits.append(each)
        return hits
            
    def tick(self, arena):
        if self.exploded:
            hits = self.detect_hits(arena)
            for each in hits:
                new = not any(each is h for h in self.has_hit)
                if (new):
                    each.damage(self.damage)
                    self.has_hit.append(each)
        else:
            direction = self.target.position.subtracted(self.position)
            direction.normalize()

            movement = direction.scaled(self.velocity)
            self.position.add(movement)
            
            if vector.distance(self.position, self.target.position) < 0.25:
                self.display_size = self.SPLASH_RADIUS
                self.duration =  0.1
                self.exploded = True
    
class Sparky(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 1200 * pow(1.1, level - 9),         # Hit points (Example value)
            h_d= 1100 * pow(1.1, level - 9),          # Hit damage (Example value)
            h_s=4,          # Hit speed (Seconds per hit)
            l_t=3,            # First hit cooldown
            h_r=5,            # Hit range
            s_r=5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=18,            #mass
            c_r=1,     #collision radius
            p=position               # Position (vector.Vector object)
        )
        self.can_kb = False
        self.level = level
        self.attack_cooldown = self.hit_speed

    def slow(self, duration, source):
        if not self.invulnerable:
            self.attack_cooldown = self.hit_speed
            if self.slow_timer < duration:
                self.slow_timer = duration
            self.slow_timer = duration
            self.hit_speed = 1.35 * self.normal_hit_speed
            self.load_time = 1.35 * self.normal_load_time
    
    def stun(self):
        if not self.invulnerable:
            self.attack_cooldown = self.hit_speed
            self.stun_timer = 0.5
            self.target = None

    def kb(self, vector):
        if self.can_kb and not self.invulnerable:
            self.position.add(vector)
            self.attack_cooldown = self.hit_speed


    def attack(self):
        self.position.add(vector.Vector(math.cos(math.radians(self.facing_dir + 180)),
                         math.sin(math.radians(self.facing_dir + 180))).scaled(0.75))
        return SparkyAttackEntity(self.side, self.hit_damage, self.position, self.target)
    
class MegaKnightJumpAttackEntity(AttackEntity):
    SPLASH_RADIUS = 2.2
    def __init__(self, side, damage, position):
        super().__init__(
            s=side,
            d=damage,
            v=0,
            l=3/60 + 0.01,
            i_p=copy.deepcopy(position)
        )
        self.display_size = self.SPLASH_RADIUS

    def apply_effect(self, target):
        if not isinstance(target, Tower) and vector.distance(self.position, target.position) < 1:
            vec = target.position.subtracted(self.position)
            vec.normalize()
            target.kb(vec)
    
    def detect_hits(self, arena):
        hits = []
        for each in arena.towers + arena.buildings + arena.troops:
            if each.side != self.side and (isinstance(each, Tower) or each.ground): # if different side
                if vector.distance(self.position, each.position) < self.SPLASH_RADIUS + each.collision_radius:
                        hits.append(each)
        return hits
    
class MegaKnightAttackEntity(MeleeAttackEntity):
    SPLASH_RADIUS = 1.3
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            position=copy.deepcopy(target),
            target=copy.deepcopy(target) #not used
            )
        self.display_size = self.SPLASH_RADIUS
        
    def detect_hits(self, arena):
        hits = []
        for each in arena.towers + arena.buildings + arena.troops:
            if each.side != self.side and (isinstance(each, Tower) or (each.ground and not each.invulnerable)): # if different side
                if vector.distance(each.position, self.position) <= each.collision_radius + self.SPLASH_RADIUS:
                    hits.append(each)
        return hits
    
class MegaKnight(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 3300 * pow(1.1, level - 9),         # Hit points (Example value)
            h_d= 222 * pow(1.1, level - 9),          # Hit damage (Example value)
            h_s=1.7,          # Hit speed (Seconds per hit)
            l_t=1.2,            # First hit cooldown
            h_r=0.7,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=18,            #mass
            c_r=0.75,        #collision radius
            p=position               # Position (vector.Vector object)
        )
        self.spawn_damage = 355 * pow(1.1, level - 9)
        self.jump_cooldown = 0
        self.jump_timer = 0
        self.should_jump = False

        self.can_kb = False
        self.level = level
        self.ticks_per_frame = 6
        self.walk_cycle_frames = 6
        class_name = self.__class__.__name__.lower()
        self.sprite_path = f"sprites/{class_name}/{class_name}_jump.png"

    def tick_func(self, arena):
        if self.stun_timer <= 0:
            if self.deploy_time <= 0:
                if self.jump_cooldown > 0:
                    self.jump_cooldown -= TICK_TIME
                
                if self.jump_timer == 0 and self.jump_cooldown <= 0:
                    
                    if self.should_jump:
                        if self.target is None: #if target toewr
                            self.update_target(arena) #give chance to target other troop instead
                        self.should_jump = False
                        self.collideable = False
                        self.move_speed = 250*TILES_PER_MIN
                        self.jump_timer = 0.8
                    elif self.target is not None:
                        d = vector.distance(self.position, self.target.position)
                        if d > 3.5 + self.target.collision_radius and d < 5 + self.target.collision_radius and self.jump_timer == 0 and self.jump_cooldown <= 0:
                            self.stun_timer = 0.3
                            self.should_jump = True
                    else:
                        for tower in arena.towers:
                            dist = vector.distance(tower.position, self.position)
                            if tower.side != self.side and dist > 3.5 + tower.collision_radius and dist < 5 + tower.collision_radius:
                                self.stun_timer = 0.3
                                self.should_jump = True
                                break 
        
        if self.jump_timer < 0: #done jumping
            self.jump_timer = 0
            self.stun_timer = 0.3
            self.jump_cooldown = 0.9
            self.move_speed = 60*TILES_PER_MIN
            self.collision_radius = 0.75
            self.collideable = True
            self.attack_cooldown = self.hit_speed
            arena.active_attacks.append(MegaKnightJumpAttackEntity(self.side, self.hit_damage * 2, self.position))
        if self.jump_timer >  0:
            self.jump_timer -= TICK_TIME
            x = self.jump_timer
            self.collision_radius = -1.8*x*(x-0.8) + 0.75
        
    
    def on_deploy(self, arena):
        self.jump_cooldown = 0.9
        arena.active_attacks.append(MegaKnightJumpAttackEntity(self.side, self.spawn_damage, self.position))
    
    def attack(self):
        if self.jump_timer == 0: #if not jumpings
            return MegaKnightAttackEntity(self.side, self.hit_damage, self.position, self.target.position)

class InfernoDragonAttackEntity(RangedAttackEntity):
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            velocity=2000*TILES_PER_MIN,
            position=position,
            target=target,
        )

class InfernoDragon(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 1070 * pow(1.1, level - 9),         # Hit points (Example value)
            h_d= 30 * pow(1.1, level - 9),          # Hit damage (Example value)
            h_s=0.4,          # Hit speed (Seconds per hit)
            l_t=1.2,            # First hit cooldown
            h_r=3.5,            # Hit range
            s_r=5.5,            # Sight Range
            g=False,           # Ground troop
            t_g_o=False,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=5,            #mass
            c_r=0.5,        #collision radius
            p=position               # Position (vector.Vector object)
        ) 
        self.level = level
        self.stage = 1
        self.stage_duration = 2
        self.damage_stages = [30 * pow(1.1, level - 9), 100 * pow(1.1, level - 9), 350 * pow(1.1, level - 9)]
    
    def tick_func(self, arena):
        if self.target is None or self.target.cur_hp <= 0:
            self.update_target(arena)
            self.stage = 1
            self.attack_cooldown = self.load_time - self.hit_speed

    def cleanup_func(self, arena):
        if self.stun_timer <= 0:
            if self.stage_duration <= 0:
                self.stage = self.stage + 1 if self.stage < 3 else self.stage
                self.stage_duration = 2
            else:
                self.stage_duration -= TICK_TIME

    def attack(self):
        return InfernoDragonAttackEntity(self.side, self.damage_stages[self.stage - 1], self.position, self.target)
    
    
class RamRiderAttackEntity(MeleeAttackEntity):
    HIT_RANGE = 0.8
    COLLISION_RADIUS = 0.6
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            position=position,
            target=target
            )
    
class RamRider(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 1461 * pow(1.1, level - 9),         # Hit points
            h_d= 220 * pow(1.1, level - 9),          # Hit damage (charge is 2x)
            h_s=1.8,          # Hit speed (Seconds per hit)
            l_t=1.2,            # First hit cooldown
            h_r=0.8,            # Hit range
            s_r=7.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=True,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=4,            #mass
            c_r=0.6,        #collision radius
            p=position               # Position (vector.Vector object)
        ) 
        self.level = level
        self.charge_speed = 120 * TILES_PER_MIN
        self.charge_damage = self.hit_damage * 2
        self.charge_charge_distance = 0
        self.charging = False
        self.cross_river = True
        self.jump_speed = 160 * TILES_PER_MIN

        class_name = self.__class__.__name__.lower()
        self.sprite_path = f"sprites/{class_name}/{class_name}_0.png"

        self.rider = RamRiderRider(self.side, self.position, self.level)

    def kb(self, vec):
        if vec.magnitude() > 0:
            self.charging = False
            self.charge_charge_distance = 0
            self.move_speed = 60 * TILES_PER_MIN
            self.position.add(vec)
    
    def freeze(self, duration):
        self.stun_timer = duration
        self.charging = False
        self.charge_charge_distance = 0
        self.move_speed = 60 * TILES_PER_MIN
        self.attack_cooldown = self.hit_speed
    
    def stun(self):
        self.charging = False
        self.charge_charge_distance = 0
        self.stun_timer = 0.5
        self.move_speed = 60 * TILES_PER_MIN
        self.target = None

    def tick_func(self, arena):
        if self.stun_timer <= 0:
            self.rider.tick(arena)
        if self.stun_timer <= 0 and not self.charging and self.charge_charge_distance >= 3:
            self.charging = True
            self.move_speed = self.charge_speed
            self.charge_charge_distance = 0
        if self.stun_timer <= 0 and self.deploy_time <= 0 and not self.charging and not self.move_vector.magnitude() == 0: #if not in range
            self.charge_charge_distance += self.move_speed

    def cleanup_func(self, arena):
        if self.stun_timer <= 0:
            self.rider.cleanup(arena)

    def attack(self):
        if self.charging:
            self.charging = False 
            self.charge_charge_distance = 0
            self.move_speed = 60 * TILES_PER_MIN
            return RamRiderAttackEntity(self.side, self.charge_damage, self.position, self.target) 
        else:
            return RamRiderAttackEntity(self.side, self.hit_damage, self.position, self.target)

class RamRiderRiderAttackEntity(RangedAttackEntity):
    def __init__(self, side, damage, position, target):
        super().__init__(
            side=side,
            damage=damage,
            velocity=600*TILES_PER_MIN,
            position=position,
            target=target,
        )

    def apply_effect(self, target):
        target.move_slow(0.7, 2, "ramriderrider")

class RamRiderRider(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 1,         # Hit points (Example value)
            h_d= 86 * pow(1.1, level - 9),          # Hit damage (Example value)
            h_s=1.1,          # Hit speed (Seconds per hit)
            l_t=0.7,            # First hit cooldown
            h_r=5.5,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=False,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=0,          # Movement speed 
            d_t=0,            # Deploy time
            m=0,            #mass
            c_r=0,        #collision radius
            p=position               # Position (vector.Vector object)
        ) 
        self.level = level
        self.snared = []
        self.snared_snare_time = []

    def update_target(self, arena):
        self.target = None 

        abs_closest = None
        
        min_dist = float('inf')
        for each in arena.troops: #for each troop
            if each.targetable and not each.invulnerable and each.side != self.side: #targets air or is ground only and each is ground troup
                dist = vector.distance(each.position, self.position)
                if dist < min_dist and dist < self.sight_range + self.collision_radius + each.collision_radius:
                    if each in self.snared:
                        abs_closest = each
                    else:
                        self.target = each
                    min_dist = vector.distance(each.position, self.position)
        
        if self.target is None:
            self.target = abs_closest
    
    def cleanup_func(self, arena):
        self.update_target(arena)
        for i in range(len(self.snared) - 1, -1, -1):
            if self.snared_snare_time[i] <= 0:
                del self.snared[i]
                del self.snared_snare_time[i]
            else:
                self.snared_snare_time[i] -= TICK_TIME

    def attack(self):
        if isinstance(self.target, Troop):
            self.snared.append(self.target)
            self.snared_snare_time.append(2.1)
            return RamRiderRiderAttackEntity(self.side, self.hit_damage, self.position, self.target)