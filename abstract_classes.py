import math
import random
import vector
import copy

TICK_TIME = 1/60 #tps
KB_TIME = 0.16
TILES_PER_MIN = 1/3600

def same_sign(x, y):
    return (x >= 0 and y >= 0) or (x < 0 and y < 0)

def on_bridge(x, tolerance=0):
    return (x > 4.5 - tolerance and x < 6.5 + tolerance) or (x > -6.5 - tolerance and x < -4.5 + tolerance)

def get_bridge(x):
    l = (x > 4.5 and x < 6.5)
    r = (x > -6.5 and x < -4.5)
    return -1 if l else (1 if r else 0)

def on_river(y):
    return y >= -1 and y <= 1

def get_true_target(position, target_position):
    if same_sign(position.y, target_position.y) and not on_river(target_position.y) and not on_river(position.y): #saem side
        return target_position
    elif on_bridge(target_position.x) and on_bridge(position.x) and on_river(target_position.y) and on_river(position.y): #both on bridge
        if same_sign(target_position.x, position.x): #same bridge
            return target_position
        else: #two opposite bridges
            return vector.Vector(4.5 if position.x > 0 else -4.5, -1 if position.y < 0 else 1)
    
    corners = [-6.5, -4.5, 4.5, 6.5]
    min_dist = float('inf')
    t_x = position.x
    t_y = 0

    corner = None
    to_corner = None
    if on_river(target_position.y) and on_bridge(target_position.x): #tar on bridge self not on bridge
        x = (6.5 if position.x > 5.5 else 4.5) if position.x > 0 else (-6.5 if position.x < -5.5 else -4.5)
        corner = vector.Vector(x, -1 if position.y < 0 else 1) #corner that might be touched
        to_corner = corner.subtracted(position)
    elif on_bridge(position.x) and on_river(position.y): #only you on bridge
        x = (6.5 if target_position.x > 5.5 else 4.5) if position.x > 0 else (-6.5 if target_position.x < -5.5 else -4.5)
        corner = vector.Vector(x, -1 if target_position.y < 0 else 1) #corner that might be touched
        to_corner = corner.subtracted(position)

    if to_corner is not None:
        delta_y = target_position.y - position.y
        corner_extended_x = to_corner.x * abs(delta_y/to_corner.y) if to_corner.y != 0 else to_corner.x#how much further to the right/left
        if (target_position.x == 5.5 or target_position.x == -5.5):
            return target_position
        elif (position.x > 0 and target_position.x > 5.5) or (position.x < 0 and target_position.x > -5.5): #if to the right
            if target_position.x > position.x + corner_extended_x: #if further than corner extension
                return corner #goes through the corner so instead go to corner first
            else:
                return target_position
        else:
            if target_position.x < position.x + corner_extended_x: #if further than corner extension
                return corner #goes through the corner so instead go to corner first
            else:
                return target_position
            
    to_target = target_position.subtracted(position)
    delta_y = target_position.y - position.y
    point_1 = to_target.scaled((1 - position.y)/delta_y) if delta_y != 0 else to_target #point at y = 1 (top of bridge)
    point_2 = to_target.scaled((-1 - position.y)/delta_y) if delta_y != 0 else to_target #point at y = -1 (bottom of bridge)

    if on_bridge(position.x + point_1.x) and on_bridge(position.x + point_2.x): #if both points lie on bridge, the straight line to target lies entirely on bridge so does not need to bend
        return target_position

    for i in range(4):
        dist = vector.distance( #distance between corners to target
            vector.Vector(corners[i], 1 if target_position.y > 0 else -1),
            target_position
        ) + vector.distance( #distance between corners to self
            vector.Vector(corners[i], 1 if position.y > 0 else -1),
            position
        )
        if dist < min_dist:
            min_dist = dist
            t_x = corners[i]

    t_y = 0.95 if position.y > 0 else -0.95
    t_x += 0.05 if t_x == 4.5 or t_x == -6.5 else -0.05

    return vector.Vector(t_x, t_y)

def true_distance(position1, position2): #only for towers
    if same_sign(position1.y, position2.y):
        return vector.distance(position1, position2)
    b1 = vector.Vector(5.5, 0)
    b2 = vector.Vector(-5.5, 0)
    d1 = vector.distance(position1, b1) + vector.distance(b1, position2) + 1.5
    d2 = vector.distance(position1, b2) + vector.distance(b2, position2) + 1.5
    return min(d1, d2)

class AttackEntity:
    def __init__(self, s, d, v, l, i_p):
        self.side = s
        self.damage = d
        self.velocity = v #vector.Vector object if not single target, i.e. firecracker, bomber, hunter, scalar otherwise, sparky, archers, etc.
        self.lifespan = l
        self.position = i_p
        
        self.duration = l
        self.has_hit = []
        self.sprite_path = ""
        self.display_size = 0.25
        self.resize = False
        self.reflectable = False
    
    def apply_effect(self, target):
        pass

    def tick_func(self, arena):
        pass

    def cleanup_func(self, arena):
        pass

    def tick(self, arena):
        self.tick_func(arena)
        if self.velocity != 0:
            self.position.add(self.velocity)
        hits = self.detect_hits(arena)
        for each in hits:
            new = not each in self.has_hit
            if (new):
                each.damage(self.damage)
                self.apply_effect(each)
                self.has_hit.append(each)
        
        
    def cleanup(self, arena): #also delete self if single target here in derived classes

        self.cleanup_func(arena)

        self.duration -= TICK_TIME
        if self.duration <= 0:
            arena.active_attacks.remove(self)
        
    def detect_hits(self, arena): # to be overriden in derived
        return []
    
    
class RangedAttackEntity(AttackEntity):
    def __init__(self, side, damage, velocity, position, target):
        super().__init__(
            s=side,
            d=damage,
            v=velocity,
            l=float('inf'),
            i_p=copy.deepcopy(position)
        )
        self.homing = True
        self.target = target
        self.should_delete = False
        self.piercing = False
        self.initial_vec = None

    def set_initial_vec(self):
        self.initial_vec = vector.Vector(
            self.target.x - self.position.x, 
            self.target.y - self.position.y
        )

    def set_move_vec(self):
        if self.initial_vec is None:
            self.set_initial_vec()
        if not self.homing:
            self.move_vec = self.initial_vec.normalized().scaled(self.velocity)

    def detect_hits(self, arena):
        if (vector.distance(self.target.position, self.position) < self.target.collision_radius) and self.target not in self.has_hit:
            self.has_hit.append(self.target)
            return [self.target] # has hit
        else:
            return [] #hasnt hit 

    def tick(self, arena):
        self.tick_func(arena)
        hits = self.detect_hits(arena)
        if len(hits) > 0:
            for each in hits:
                each.damage(self.damage)
                self.apply_effect(each)
            if not self.piercing:
                self.should_delete = True
        else:
            direction = None
            if self.homing:
                direction = vector.Vector(
                    self.target.position.x - self.position.x, 
                    self.target.position.y - self.position.y
                )
                direction.normalize()
                direction.scale(self.velocity)
                self.position.add(direction)

            else:
                self.position.add(self.move_vec)
            
    def cleanup(self, arena):
        self.cleanup_func(arena)
        self.duration -= TICK_TIME
        if self.duration <= 0:
            try:
                arena.active_attacks.remove(self)
            except ValueError:
                print(self.__class__.__name__ + " not in active attacks")
        elif self.should_delete:
            try:
                arena.active_attacks.remove(self)
            except ValueError:
                print(self.__class__.__name__ + " not in active attacks")

class MeleeAttackEntity(AttackEntity):
    HIT_RANGE = 0
    COLLISION_RADIUS = 0
    def __init__(self, side, damage, position, target):
        super().__init__(
            s=side,
            d=damage,
            v=0,
            l=0.5,
            i_p=position
            )
        self.target = target
        self.should_delete = False
    
    def detect_hits(self, arena):
        if (vector.distance(self.target.position, self.position) <= self.HIT_RANGE + self.COLLISION_RADIUS + self.target.collision_radius): #within hitrange of knight
            return [self.target]
        else:
            return [] #theoretically should never trigger, when attack, should always be in range unless very strange circumstances
        
    def tick(self, arena):
        hits = self.detect_hits(arena)
        if len(hits) > 0:
            for each in hits:
                each.damage(self.damage)
            self.should_delete = True

    def cleanup(self, arena): #also delete self if single target here in derived classes
        self.duration -= TICK_TIME
        if self.duration <= 0:
            arena.active_attacks.remove(self)
        if self.should_delete and self in arena.active_attacks:
            arena.active_attacks.remove(self)


class Troop:
    def __init__(self, s, h_p, h_d, h_s, l_t, h_r, s_r, g, t_g_o, t_o, m_s, d_t, m, c_r, p, cloned=False):
        self.side = s
        self.hit_points = h_p
        self.hit_damage = h_d
        self.hit_speed = h_s
        self.load_time = l_t
        self.hit_range = h_r
        self.sight_range = s_r
        self.ground = g
        self.ground_only = t_g_o
        self.tower_only = t_o
        self.move_speed = m_s
        self.deploy_time = d_t
        self.mass = m
        self.collision_radius = c_r
        
        self.cur_hp = h_p
        self.position = p
        self.target = None
        self.attack_cooldown = h_s - l_t

        self.normal_load_time = l_t
        self.normal_hit_speed = h_s
        self.normal_move_speed = m_s

        self.facing_dir = 0
        self.ticks_per_frame = 6
        self.cur_ticks_per_frame = 0
        self.walk_cycle_frames = 1
        self.walk_cycle_cur = 0

        self.move_vector = vector.Vector(0, 0)
        
        class_name = self.__class__.__name__.lower()
        self.sprite_path = f"sprites/{class_name}/{class_name}.png"

        self.stun_timer = 0
        self.slow_timer = 0
        self.rage_timer = 0
        self.kb_timer = 0
        self.kb_max = 0

        self.kb_vector = None
        self.slow_sources = []

        self.targetable = True
        self.invulnerable = False
        self.moveable = True
        self.cross_river = False
        self.dash_river = False
        self.has_shield = False
        self.should_delete = False #only for kamikaze troops
        self.can_kb = True
        self.collideable = True

        self.preplace = False

        self.cursed_timer = 0
        self.goblin_cursed_level = None
        self.damage_amplification = 1
        self.hog_cursed_level = None
        self.target_lock = False

        if cloned:
            self.cur_hp = 1
            self.hit_points = 1
            if self.has_shield:
                self.shield_hp = 1
                self.shield_max_hp = 1
        self.cloned = cloned
        self.evo = False

    def rage(self):
        self.rage_timer = 2
        if self.rage_timer <= 0:
            self.hit_speed = 0.65 * self.hit_speed
            self.load_time = 0.65 * self.load_time
            self.move_speed = 1.35 * self.move_speed

    def slow(self, duration, source):
        if not self.invulnerable:
            if self.slow_timer < duration:
                self.slow_timer = duration
            self.hit_speed = 1.35 * self.hit_speed
            self.load_time = 1.35 * self.load_time
            if source not in self.slow_sources:
                self.move_speed = 0.65 * self.move_speed
                self.slow_sources.append(source)

    def move_slow(self, percent, duration, source):
        if self.slow_timer < duration:
            self.slow_timer = duration
        if source not in self.slow_sources:
            self.move_speed = (1 - percent) * self.move_speed
            self.slow_sources.append(source)

    def unslow(self):
        if self.rage_timer <= 0:
            self.hit_speed = self.normal_hit_speed
            self.load_time = self.normal_load_time
            self.move_speed = self.normal_move_speed
            self.slow_sources = []
        else: #is raged
            self.hit_speed = 0.65 * self.normal_hit_speed
            self.load_time = 0.65 * self.normal_load_time
            self.move_speed = 1.35 * self.move_speed
    
    def unrage(self):
        if self.slow_timer <= 0:
            self.hit_speed = self.normal_hit_speed
            self.load_time = self.normal_load_time
            self.move_speed = self.normal_move_speed
        else:
            self.hit_speed /= 0.65
            self.load_time /= 0.65
            self.move_speed /= 1.35

    def stun(self):
        if not self.invulnerable:
            self.stun_timer = 0.5
            self.target = None

    def freeze(self, duration):
        if not self.invulnerable:
            self.stun_timer = duration
            self.attack_cooldown = self.hit_speed

    def damage(self, amount):
        if not self.invulnerable:
            self.cur_hp -= amount*self.damage_amplification

    def heal(self, amount):
        self.cur_hp = min(self.cur_hp + amount, self.hit_points)

    def level_up(self):
        self.level += 1
        if self.has_shield:
            self.shield_hp *= 1.1
            self.shield_max_hp *= 1.1
        self.cur_hp *= 1.1
        self.hit_points *= 1.1
        self.hit_damage *= 1.1

    def on_deploy(self, arena):
        pass

    def on_preplace(self):
        pass
    
    def kb(self, vector, kb_time = None):
        if kb_time is None:
            self.kb_timer = KB_TIME
            self.kb_max = KB_TIME
        else:
            self.kb_timer = kb_time
            self.kb_max = kb_time

        if self.kb_vector is None:
            self.kb_vector = vector
        else:
            self.kb_vector.add(vector)

    def kb_tick(self):
        self.position.add(self.kb_vector.scaled(TICK_TIME/self.kb_max))

    def die(self, arena):
        if not self.should_delete and self.goblin_cursed_level is not None:
            from goblin_stadium_cards import Goblin
            arena.troops.append(Goblin(not self.side, copy.deepcopy(self.position), self.goblin_cursed_level, self.cloned))
        if not self.should_delete and self.hog_cursed_level is not None:
            from miners_mine_cards import CursedHog
            arena.troops.append(CursedHog(not self.side, copy.deepcopy(self.position), self.hog_cursed_level, self.cloned))
        self.cur_hp = -1
        arena.troops.remove(self)
        arena.died.append(self)

    def handle_deaths(self, list):
        pass

    def tick_func(self, arena):
        pass

    def cleanup_func(self, arena):
        pass

    def attack(self): #override
        return None #return the correct attackentity object
        
    def update_target(self, arena):
        self.target = None 
        
        min_dist = float('inf')
        if not self.tower_only: #if not tower targeting
            for each in arena.troops: #for each troop
                if each.targetable and each.side != self.side and (not self.ground_only or (self.ground_only and each.ground)): #targets air or is ground only and each is ground troup
                    dist = vector.distance(each.position, self.position)
                    if  dist < min_dist and dist < self.sight_range + self.collision_radius + each.collision_radius:
                        self.target = each
                        min_dist = vector.distance(each.position, self.position)
        for each in arena.buildings: #for each building, so if any building is closer then non tower targeting switches, or if tower targeting then finds closest building
            if each.side != self.side and each.targetable:
                dist = vector.distance(each.position, self.position)
                if  dist < min_dist and dist < self.sight_range + self.collision_radius + each.collision_radius:
                    self.target = each
                    min_dist = vector.distance(each.position, self.position)
        
        for tower in arena.towers: #check for towers that it can currently hit
            if tower.side != self.side:
                dist = vector.distance(tower.position, self.position)
                if dist < min_dist:
                    self.target = None #ensures that it doesnt lock on to troops farther away than tower
                if dist < self.hit_range + self.collision_radius + tower.collision_radius and dist < min_dist: #iff can hit tower, then it locks on.
                    self.target = tower #ensures only locks when activel attacking tower, so giant at bridge doesnt immediatly lock onto tower and ruin everyones day
                    min_dist = vector.distance(tower.position, self.position)
            
    def move(self, arena):
        move_vector = None
        #generate move vector
        approx_l_bridge = vector.distance(self.position, vector.Vector(-5.5, 0)) - 1.4
        approx_r_bridge = vector.distance(self.position, vector.Vector(5.5, 0)) - 1.4
        should_jump = min(approx_l_bridge, approx_r_bridge) > 2 and abs(self.position.y) < 3
        if self.ground and not ((self.cross_river or self.dash_river) and (should_jump or on_river(self.position.y))):
            move_target = None
            if self.target is None:
                min_dist = float('inf')
                tower_target = None
                for tower in arena.towers:
                    should_see = same_sign(tower.position.y, self.position.y) or same_sign(tower.position.x, self.position.x) or (tower.position.x == 0 or tower.position.x == 2 or tower.position.x == -2)
                    if tower.side != self.side and should_see:
                        if true_distance(tower.position, self.position) < min_dist:
                            tower_target = tower
                            min_dist = true_distance(tower.position, self.position)
                move_target = tower_target.position #set target
            else:
                move_target = self.target.position #set target
            true_target = get_true_target(self.position, move_target)
            move_vector = true_target.subtracted(self.position)
            move_vector.normalize()
            move_vector.scale(self.move_speed)
        else:
            m_s = self.move_speed 
            if (self.cross_river and not on_bridge(self.position.x) and on_river(self.position.y)):
                m_s = self.jump_speed
            if self.target is None: #if no target
                min_dist = float('inf')
                tower_target = None
                for tower in arena.towers:
                    if tower.side != self.side:
                        if vector.distance(tower.position, self.position) < min_dist:
                            tower_target = tower
                            min_dist = vector.distance(tower.position, self.position)
                to_tower = tower_target.position.subtracted(self.position) #target tower
                to_tower.normalize()
                move_vector = to_tower.scaled(m_s)
            else:
                to_target = self.target.position.subtracted(self.position)
                move_vector = to_target.normalized().scaled(m_s)
        
        #actual move
        self.move_vector = move_vector
        self.facing_dir = math.degrees(math.atan2(move_vector.y, move_vector.x))

        tar_d = vector.distance(self.position, self.target.position) if self.target else float('inf')
        attack_d = self.hit_range + self.collision_radius + self.target.collision_radius if self.target else -1
        if not self.target or tar_d > attack_d - 0.1: #if no target or far enough from target
            self.position.add(self.move_vector)
        else:
            self.move_vector = vector.Vector(0, 0)

        if tar_d < attack_d:
            v = self.target.position.subtracted(self.position)
            self.facing_dir = math.degrees(math.atan2(v.y, v.x))
        
        return tar_d < attack_d

    def old_move(self, arena):
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

            if not tower_target is None and ((self.ground and not self.dash_river) and not self.cross_river) and (not same_sign(tower_target.position.y, self.position.y) and (self.position.y < -1 or self.position.y > 1)): # if behind bridge and cant cross river

                tar_bridge = None
                
                x = self.position.x
                t_x = None
                
                if on_bridge(x):
                    t_x = x
                elif x >= 6.5:
                    t_x = 6.4
                elif x <= 4.5 and x >= 0:
                    t_x = 4.6
                elif x >= -4.5 and x < 0:
                    t_x = -4.6
                else:
                    t_x = -6.4
                
                
                tar_bridge = vector.Vector(t_x, 0.99 if self.position.y > 0 else -0.99)
            
                direction_x = tar_bridge.x - self.position.x #set movement
                direction_y = tar_bridge.y - self.position.y
                distance_to_target = math.sqrt(direction_x ** 2 + direction_y ** 2)
            elif self.cross_river and ((self.side and (self.position.y > - 2 and self.position.y < 1)) or (not self.side and (self.position.y < 2 and self.position.y > -1))):
                direction_x = 0
                direction_y = 1 if (self.side if self.target is None else self.target.position.y - self.position.y) > 0 else -1 #forwards 
                distance_to_target = 1
                m_s = self.jump_speed
            elif not tower_target is None:
                tar = None
                if (self.position.y < 1 and self.side) or (self.position.y > -1 and not self.side):
                    if self.position.x > 0 and tower_target.position.x < 0: #if on right and targeting left
                        tar = vector.Vector(4.5, 1.01 if self.side else -1.01)
                    if self.position.x < 0 and tower_target.position.x > 0: #if on left and targeting right
                        tar = vector.Vector(-4.5, 1.01 if self.side else -1.01)
                if tar is None:
                    direction_x = tower_target.position.x - self.position.x #set to directly move to tower
                    direction_y = tower_target.position.y - self.position.y
                    distance_to_target = math.sqrt(direction_x ** 2 + direction_y ** 2)
                else:
                    direction_x = tar.x - self.position.x
                    direction_y = tar.y - self.position.y
                    distance_to_target = math.sqrt(direction_x ** 2 + direction_y ** 2)

            # Normalize direction
            
            if tower_target is None:
                return #exit
            elif min_dist < self.hit_range + self.collision_radius + tower_target.collision_radius: #within hit range, locks on
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
        if ((self.ground and not self.dash_river) and not self.cross_river) and (not same_sign(self.target.position.y, self.position.y) and (self.position.y < -1 or self.position.y > 1)):
            #if not on bridge
            tar_bridge = None
            
            x = self.position.x
            t_x = None
            
            if vector.distance(self.position, vector.Vector(-5.5, 0)) + vector.distance(self.target.position, vector.Vector(-5.5, 0)) <= vector.distance(self.position, vector.Vector(5.5, 0)) + vector.distance(self.target.position, vector.Vector(5.5, 0)):
                if x <= -6.5: #left more optimal
                    t_x = -6.4
                elif x >= -4.5:
                    t_x = -4.4
                else:
                    t_x = x
            else: #right better
                if x >= 6.5:
                    t_x = 6.4
                elif x <= 4.5:
                    t_x = 4.4
                else:
                    t_x = x
            
            tar_bridge = vector.Vector(t_x, -0.99 if self.position.y < 0 else 0.99)
            direction_x = tar_bridge.x - self.position.x #set movement
            direction_y = tar_bridge.y - self.position.y
            distance_to_target = math.sqrt(direction_x ** 2 + direction_y ** 2)
        elif self.cross_river and (not on_bridge(self.position.x)) and ((self.target.position.y - self.position.y > 0 and (self.position.y > - 2 and self.position.y < 1)) or (not self.target.position.y - self.position.y > 0 and (self.position.y < 2 and self.position.y > -1))):
            direction_x = 0
            direction_y = 1 if (self.side if self.target is None else self.target.position.y - self.position.y) > 0 else -1 #forwards 
            distance_to_target = 1
            m_s = self.jump_speed
        elif self.ground and not self.dash_river: #if need bridge
            if (self.position.y < 1 and self.position.y > -1) and not (self.target.position.y <= 1 and self.target.position.y >= -1 and on_bridge(self.target.position.x)):
                bridge_side = 1 if self.position.y < self.target.position.y else -1 #move to other side of bridge while on bridge code
                bridge_min = -6.5 if self.position.x < 0 else 4.5
                bridge_max = -4.5 if self.position.x < 0 else 6.5

                to_tar = self.target.position.subtracted(self.position)
                to_corner1 = vector.Vector(bridge_min + 0.1, bridge_side).subtracted(self.position)
                to_corner2 = vector.Vector(bridge_max - 0.1, bridge_side).subtracted(self.position)

                ratio = float('inf') if to_tar.x == 0 else abs(to_tar.y/to_tar.x)

                t_x = self.target.position.x

                if to_corner1.x == 0 or (t_x < bridge_min and abs(to_corner1.y/to_corner1.x) > ratio):
                    tar_bridge = vector.Vector(bridge_min + 0.1, bridge_side)
                    direction_x = tar_bridge.x - self.position.x
                    direction_y = tar_bridge.y - self.position.y
                    distance_to_target = math.sqrt(direction_x ** 2 + direction_y ** 2)
                elif to_corner2.x == 0 or (t_x > bridge_max and abs(to_corner2.y/to_corner2.x) > ratio):
                    tar_bridge = vector.Vector(bridge_max - 0.1, bridge_side)
                    direction_x = tar_bridge.x - self.position.x
                    direction_y = tar_bridge.y - self.position.y
                    distance_to_target = math.sqrt(direction_x ** 2 + direction_y ** 2)
                else:
                    direction_x = self.target.position.x - self.position.x
                    direction_y = self.target.position.y - self.position.y
                    distance_to_target = math.sqrt(direction_x ** 2 + direction_y ** 2)
                
            else:
                direction_x = self.target.position.x - self.position.x
                direction_y = self.target.position.y - self.position.y
                distance_to_target = math.sqrt(direction_x ** 2 + direction_y ** 2)
        else:
            direction_x = self.target.position.x - self.position.x
            direction_y = self.target.position.y - self.position.y
            distance_to_target = math.sqrt(direction_x ** 2 + direction_y ** 2)

        d = vector.distance(self.target.position, self.position)
        if d >= self.hit_range + self.collision_radius + self.target.collision_radius - 0.1: #within hit range, then dont move just attack
            direction_x /= d
            direction_y /= d
            # Move in the direction of the target

            if d >= self.hit_range + self.collision_radius + self.target.collision_radius or isinstance(self.target, Troop):
                self.position.x += direction_x  * m_s
                self.position.y += direction_y * m_s
            angle = math.degrees(math.atan2(direction_y, direction_x))  # Get angle in degrees
            self.facing_dir = angle
            self.move_vector = vector.Vector(direction_x * m_s, direction_y * m_s)

        if vector.distance(self.target.position, self.position) < self.hit_range + self.collision_radius + self.target.collision_radius:
            self.move_vector = vector.Vector(0, 0)
            direction_x = self.target.position.x - self.position.x #set to directly move to tower
            direction_y = self.target.position.y - self.position.y
            self.facing_dir = math.degrees(math.atan2(direction_y, direction_x))  # Get angle in degrees
            return True
        return False
    
    def move_touchdown(self, arena):
        if self.target is None:
            self.move_vector = vector.Vector(0, (1 if self.side else -1) * self.move_speed)
            self.position.y += self.move_speed * (1 if self.side else -1)
        else:
            d = vector.distance(self.target.position, self.position)
            m_s = self.move_speed
            direction_x = self.target.position.x - self.position.x
            direction_y = self.target.position.y - self.position.y
            if d >= self.hit_range + self.collision_radius + self.target.collision_radius - 0.1: #within hit range, then dont move just attack
                direction_x /= d
                direction_y /= d
                # Move in the direction of the target

                if d >= self.hit_range + self.collision_radius + self.target.collision_radius or isinstance(self.target, Troop):
                    self.position.x += direction_x  * m_s
                    self.position.y += direction_y * m_s
                angle = math.degrees(math.atan2(direction_y, direction_x))  # Get angle in degrees
                self.facing_dir = angle
                self.move_vector = vector.Vector(direction_x * m_s, direction_y * m_s)

            if vector.distance(self.target.position, self.position) < self.hit_range + self.collision_radius + self.target.collision_radius:
                self.move_vector = vector.Vector(0, 0)
                direction_x = self.target.position.x - self.position.x #set to directly move to tower
                direction_y = self.target.position.y - self.position.y
                self.facing_dir = math.degrees(math.atan2(direction_y, direction_x))  # Get angle in degrees
                return True
        return False
        
    def tick(self, arena):
        if self.preplace or self.cur_hp <= 0:
            return
        #update arena before
        self.tick_func(arena)

        #handle kb
        if self.kb_timer > 0:
            self.kb_timer -= TICK_TIME #akward but better to keep it contained
            self.kb_tick()
        else:
            self.kb_vector = None

        if self.stun_timer <= 0:
            if self.deploy_time <= 0:
                if self.target is None or self.target.cur_hp <= 0 or not self.target.targetable or (self.ground_only and not self.target.ground):
                    self.update_target(arena)
                elif not self.target_lock and vector.distance(self.position, self.target.position) > self.hit_range + self.collision_radius + self.target.collision_radius: #add 0.2 so there is tiny buffer for ranged troops
                    self.update_target(arena)
                if (self.move(arena) if arena.type != "td" else self.move_touchdown(arena)) and self.attack_cooldown <= 0: #move, then if within range, attack
                    atk = self.attack()
                    if isinstance(atk, list) and len(atk) > 0:
                        arena.active_attacks.extend(atk)
                    elif not atk is None:
                        arena.active_attacks.append(atk)
                    self.attack_cooldown = self.hit_speed
                '''
                if arena.type != "td" and not (self.cross_river or not self.ground or self.dash_river) and self.position.y > -1 and self.position.y < 1 and not (on_bridge(self.position.x + 0.1) or on_bridge(self.position.x - 0.1)): #some leeway for bridge
                    if (self.position.x > 4 and self.position.x < 4.5):
                        self.position.x = 4.55
                    elif (self.position.x > 6.5 and self.position.x < 7):
                        self.position.x = 6.45
                    elif (self.position.x < -4 and self.position.x > -4.5):
                        self.position.x = -4.55
                    elif (self.position.x < -6.5 and self.position.x > -7):
                        self.position.x = -6.45
                    elif self.position.y < 0:
                        self.position.y = -1.05
                    else:
                        self.position.y = 1.05
                '''
    
    def cleanup(self, arena): # each troop runs this after ALL ticks are finished
        if self.preplace:
            return

        self.cleanup_func(arena)

        if self.cur_hp <= 0 or self.should_delete:
            self.die(arena)

        if self.rage_timer < 0:
            self.rage_timer = 0
            self.unrage()
        elif self.rage_timer > 0:
            self.rage_timer -= TICK_TIME
        
        if self.slow_timer < 0:
            self.slow_timer = 0
            self.unslow()
        elif self.slow_timer > 0:
            self.slow_timer -= TICK_TIME

        if self.cursed_timer <= 0:
            self.goblin_cursed_level = None
            self.hog_cursed_level = None
            self.damage_amplification = 1
        else:
            self.cursed_timer -= TICK_TIME
        

        if self.deploy_time > 0: #if deploying, timer
            self.deploy_time -= TICK_TIME
                
        elif self.stun_timer <= 0:
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

class Tower:
    def __init__(self, s, h_d, h_r, h_s, l_t, h_p, c_r, p):
        self.side = s
        self.hit_damage = h_d
        self.hit_range = h_r
        self.hit_speed = h_s
        self.load_time = l_t
        self.hit_points = h_p
        self.collision_radius = c_r

        self.cur_hp = h_p
        self.target = None
        self.attack_cooldown = 0
        self.position = p
        self.target = None

        self.normal_load_time = l_t
        self.normal_hit_speed = h_s

        self.slow_timer = 0
        self.rage_timer = 0
        self.stun_timer = 0
        self.sprite_path = ""
        self.animation_cycle_frames = 1
        self.animation_cycle_cur = 1
        self.targetable = True
        self.invulnerable = False
        self.ground = True
        self.type = None
        self.collideable = True
        self.can_kb = False
        self.activated = True

    def damage(self, amount):
        if not self.invulnerable:
            self.cur_hp -= amount
    
    def slow(self, duration, source):
        if self.slow_timer < duration:
            self.slow_timer = duration
        self.load_time = 1.35 * self.normal_load_time
        self.hit_speed = 1.35 * self.normal_hit_speed

    def unslow(self):
        self.hit_speed = self.normal_hit_speed
        self.load_time = self.normal_load_time

    def rage(self):
        self.rage_timer = 2
        if self.rage_timer <= 0:
            self.hit_speed = 0.65 * self.hit_speed
            self.load_time = 0.65 * self.load_time

    def unrage(self):
        if self.slow_timer <= 0:
            self.hit_speed = self.normal_hit_speed
            self.load_time = self.normal_load_time
        else:
            self.hit_speed /= 0.65
            self.load_time /= 0.65

    def stun(self):
        self.stun_timer = 0.5
        self.target = None

    def freeze(self, duration):
        self.stun_timer = duration
        self.attack_cooldown = self.hit_speed

    def tick_func(self, arena):
        pass
    
    def cleanup_func(self, arena):
        pass

    def attack(self):
        return None

    def update_target(self, arena):
        self.target = None
        min_dist = float('inf')
        for each in arena.troops + arena.buildings:
            dist = vector.distance(each.position, self.position)
            if each.targetable and each.side != self.side and dist < min_dist and dist < self.hit_range + self.collision_radius + each.collision_radius:
                self.target = each
                min_dist = vector.distance(each.position, self.position)
    
    def tick(self, arena):
        self.tick_func(arena)

        if self.stun_timer <= 0:
            if self.target is None or self.target.cur_hp <= 0 or (not self.target.targetable) or (vector.distance(self.target.position, self.position) > self.hit_range + self.target.collision_radius + self.collision_radius):
                self.update_target(arena)
            if not self.target is None and self.attack_cooldown <= 0:
                atk = self.attack()
                if isinstance(atk, list) and len(atk) > 0:
                    arena.active_attacks.extend(atk)
                elif not atk is None:
                    arena.active_attacks.append(atk)
                self.attack_cooldown = self.hit_speed
            
            class_name = self.__class__.__name__.lower()
            if not self.animation_cycle_frames == 1: #more than one frame per thing
                self.sprite_path = f"sprites/{class_name}/{class_name}_{self.animation_cycle_cur}.png"
            else:
                self.sprite_path = f"sprites/{class_name}/{class_name}.png"
    
    def cleanup(self, arena):
        self.cleanup_func(arena)
        if self.cur_hp <= 0:
            arena.towers.remove(self)

        if self.slow_timer < 0 :
            self.slow_timer = 0
            self.unslow()
        elif self.slow_timer > 0:
            self.slow_timer -= TICK_TIME
        
        if self.rage_timer < 0:
            self.rage_timer = 0
            self.unrage()
        elif self.rage_timer > 0:
            self.rage_timer -= TICK_TIME


        if self.stun_timer <= 0:
            if self.target is None or (vector.distance(self.target.position, self.position) > self.hit_range + self.collision_radius + self.target.collision_radius and (self.attack_cooldown <= self.hit_speed - self.load_time)):
                self.attack_cooldown = self.hit_speed - self.load_time #if not currently attacking but cooldown is less than first hit delay
            else: #otherwise
                self.attack_cooldown -= TICK_TIME
        else:
            self.stun_timer -= TICK_TIME


class Spell:
    def __init__(self, s, d, c_t_d, w, t, kb, r, v, tar):
        self.side = s
        self.damage = d
        self.crown_tower_damage = c_t_d
        self.waves = w
        self.time_between = t
        self.knock_back = kb
        self.radius = r
        self.velocity = v
        self.target_pos = tar
        
        self.damage_cd = t
        self.king_pos = (vector.Vector(0, -12) if s else vector.Vector(0, 12))
        self.spawn_timer = 0 if v == 0 else vector.distance(tar, self.king_pos) / v #number of ticks
        self.should_delete = False
        self.display_duration = 0

        self.total_time = self.spawn_timer #number of ticks
        
        self.position = tar if v == 0 else self.king_pos
        
        self.class_name = self.__class__.__name__.lower()
        self.sprite_path = f"sprites/{self.class_name}/{self.class_name}_travel.png"
        self.pulse_timer = float('inf')
        self.pulse_time = float('inf')
        self.preplace = False
        self.evo = False
    

    def detect_hits(self, arena): #override
        out = []
        for each in arena.troops + arena.buildings + arena.towers:
            if (isinstance(each, Tower) or not each.invulnerable) and each.side != self.side and (vector.distance(each.position, self.position) <= self.radius + each.collision_radius):
                out.append(each)
        return out
    
    def passive_detect_hits(self, arena):
        return self.detect_hits(arena)
    
    def apply_effect(self, target):
        pass

    def on_preplace(self):
        pass

    def tick_func(self, arena):
        pass
        
    def tick(self, arena):
        if self.preplace:
            return
        self.tick_func(arena)
        if self.spawn_timer > 0:
            tower_to_target  = self.target_pos.subtracted(self.king_pos)
            self.position.add(tower_to_target.scaled(self.velocity / tower_to_target.magnitude()))
            self.spawn_timer -= 1 #spawn in
        elif self.waves > 0 and self.damage_cd <= 0:
            self.sprite_path = f"sprites/{self.class_name}/{self.class_name}_hit.png"
            hits = self.detect_hits(arena)
            for each in hits:
                is_tesla = (self.__class__.__name__ == "Earthquake" or self.__class__.__name__ == "Vines") and (each.__class__.__name__ == "Tesla" or each.__class__.__name__ == "EvolutionTesla")
                
                if not each.invulnerable or is_tesla:
                    if (isinstance(each, Tower)):
                        each.damage(self.crown_tower_damage)
                    else:
                        each.damage(self.damage); #end damage, start kb
                
                if isinstance(each, Troop) and (each.can_kb and each.moveable):
                    displacement = each.position.subtracted(self.position)
                    displacement.normalize()
                    displacement.scale(self.knock_back)
                    each.kb(displacement)
                self.apply_effect(each)
            self.waves -= 1 #decrease waves
            if self.waves > 0:
                self.damage_cd = self.time_between #reset cooldown
        elif self.damage_cd > 0:
            self.damage_cd -= TICK_TIME #decrement cooldown
        elif self.display_duration <= 0:
            self.should_delete = True #mark for deletion
        
        if self.pulse_timer <= 0:
            self.pulse_timer = self.pulse_time
            hits = self.passive_detect_hits(arena)
            for each in hits:
                self.passive_effect(each)
        else:
            self.pulse_timer -= TICK_TIME

    def passive_effect(self, each):
        pass
            
    def cleanup(self, arena):
        if self.preplace:
            return
        
        if self.should_delete:
            arena.spells.remove(self) #delete
        self.display_duration -= TICK_TIME
        
class Building:
    def __init__(self, s, h_p, h_d, h_s, l_t, h_r, s_r, g, t_g_o, t_o, l, d_t, c_r, d_s_c, d_s: type, p, cloned=False):
        self.side = s
        self.hit_points = h_p
        self.hit_damage = h_d
        
        self.hit_speed = h_s
        self.load_time = l_t
        self.hit_range = h_r
        self.sight_range = s_r

        self.ground = g
        self.ground_only = t_g_o
        self.tower_only = t_o
        
        self.lifespan = l
        self.deploy_time = d_t
        self.collision_radius = c_r
        self.death_spawn_count = d_s_c
        self.death_spawn = d_s

        self.normal_hit_speed = h_s
        self.normal_load_time = l_t
        self.cur_hp = h_p
        self.target = None
        self.attack_cooldown = 0
        self.position = p

        self.stun_timer = 0
        self.slow_timer = 0
        self.rage_timer = 0

        self.facing_dir = 0
        class_name = self.__class__.__name__.lower()
        self.sprite_path_front = f"sprites/{class_name}/{class_name}" # + "_base.png" or + "_top.png"

        self.is_spawner = False
        self.targetable = True
        self.invulnerable = False
        self.preplace = False
        self.collideable = True
        self.evo = False

        if cloned:
            self.cur_hp = 1
            self.hit_points = 1
        self.cloned = cloned

    def slow(self, duration, source):
        if self.slow_timer < duration:
            self.slow_timer = duration
        self.slow_timer = duration
        self.hit_speed = 1.35 * self.normal_hit_speed
        self.load_time = 1.35 * self.normal_load_time

    def unslow(self):
        self.hit_speed = self.normal_hit_speed
        self.load_time = self.normal_load_time
    
    def rage(self):
        self.rage_timer = 2
        if self.rage_timer <= 0:
            self.hit_speed = 0.65 * self.hit_speed
            self.load_time = 0.65 * self.load_time

    def unrage(self):
        if self.slow_timer <= 0:
            self.hit_speed = self.normal_hit_speed
            self.load_time = self.normal_load_time
        else:
            self.hit_speed /= 0.65
            self.load_time /= 0.65

    def damage(self, amount):
        self.cur_hp -= amount

    def stun(self):
        self.stun_timer = 0.5
        self.target = None

    def freeze(self, duration):
        if not self.invulnerable:
            self.stun_timer = duration
            self.attack_cooldown = self.hit_speed

    def tick_func(self, arena):
        pass
    
    def cleanup_func(self, arena):
        pass

    def attack(self):
        return None
    
    def on_deploy(self, arena):
        pass
    
    def on_preplace(self):
        pass

    def update_target(self, arena):
        self.target = None
        min_dist = float('inf')
        for each in arena.troops + arena.buildings + arena.towers:
            dist = vector.distance(each.position, self.position)
            if (isinstance(each, Tower) or (each.targetable and (not self.ground_only or (self.ground_only and each.ground)))) and each.side != self.side and dist < min_dist and dist < self.hit_range + self.collision_radius + each.collision_radius:
                self.target = each
                min_dist = vector.distance(each.position, self.position)

                angle = math.degrees(math.atan2(each.position.y - self.position.y, each.position.x - self.position.x))  # Get angle in degrees
                self.facing_dir = angle
    
    def tick(self, arena):
        if self.preplace or self.deploy_time > 0 or self.stun_timer > 0:
            return
        self.tick_func(arena)
        if self.target is None or self.target.cur_hp <= 0 or not self.target.targetable or (self.ground_only and not self.target.ground) or vector.distance(self.target.position, self.position) > self.hit_range + self.collision_radius + self.target.collision_radius:
            self.update_target(arena)
        if (not self.target is None) and self.attack_cooldown <= 0:
            atk = self.attack()
            if isinstance(atk, list) and len(atk) > 0:
                arena.active_attacks.extend(atk)
            elif not atk is None:
                arena.active_attacks.append(self.attack())
            self.attack_cooldown = self.hit_speed

    def die(self, arena):
        arena.buildings.remove(self)
        self.cur_hp = -1
        if not self.death_spawn is None:
            for i in range(self.death_spawn_count):
                arena.troops.append(self.death_spawn(self.side, 
                    self.position.added(vector.Vector(random.uniform(-self.collision_radius, self.collision_radius), random.uniform(-self.collision_radius, self.collision_radius))), 
                    self.level))
    
    def cleanup(self, arena):
        if self.preplace:
            return

        if self.deploy_time > 0:
            self.deploy_time -= TICK_TIME
            return
        
        self.cleanup_func(arena)

        self.cur_hp -= self.hit_points * TICK_TIME / self.lifespan
        if self.cur_hp <= 0:
            self.die(arena)
        
        if self.slow_timer < 0 :
            self.slow_timer = 0
            self.unslow()
        elif self.slow_timer > 0:
            self.slow_timer -= TICK_TIME
        
        if self.rage_timer < 0:
            self.rage_timer = 0
            self.unrage()
        elif self.rage_timer > 0:
            self.rage_timer -= TICK_TIME    
            
        if self.stun_timer <= 0:
            if not self.is_spawner and (self.target is None or (vector.distance(self.target.position, self.position) > self.hit_range + self.target.collision_radius + self.collision_radius and (self.attack_cooldown <= self.hit_speed - self.load_time))):
                self.attack_cooldown = self.hit_speed - self.load_time #if not currently attacking but cooldown is less than first hit delay
            else: #otherwise
                self.attack_cooldown -= TICK_TIME
        else:
            self.stun_timer -= TICK_TIME

class ElixirLossTracker:
    def __init__(self, x, y, amount, side, container):
        self.x = x
        self.y = y
        self.amount = amount
        self.timer = 1
        self.side = side
        self.container = container

    def tick(self):
        self.timer -= TICK_TIME
        if self.timer <= 0:
            self.container.elixir_trackers.remove(self)