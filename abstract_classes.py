import math
import random
import vector
import copy

TICK_TIME = 1/60 #tps
TILES_PER_MIN = 1/3600

def same_sign(x, y):
    return (x >= 0 and y >= 0) or (x < 0 and y < 0)

def on_bridge(x):
    return (x > 4.5 and x < 6.5) or (x > -6.5 and x < -4.5)

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
    
    def apply_effect(self, target):
        pass

    def cleanup_func(self, arena):
        pass

    def tick(self, arena):
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

    def detect_hits(self, arena):
        if (vector.distance(self.target.position, self.position) < self.target.collision_radius):
            return [self.target] # has hit
        else:
            return [] #hasnt hit yet
            
    def tick(self, arena):
        hits = self.detect_hits(arena)
        if len(hits) > 0:
            for each in hits:
                each.damage(self.damage)
                self.apply_effect(each)
            self.should_delete = True
        else:
            direction = None
            if self.homing:
                direction = vector.Vector(
                    self.target.position.x - self.position.x, 
                    self.target.position.y - self.position.y
                )
            else:
                direction = vector.Vector(
                    self.target.x - self.position.x, 
                    self.target.y - self.position.y
                )
            direction.normalize()

            movement = direction.scaled(self.velocity)
            self.position.add(movement)

    def cleanup(self, arena):
        self.duration -= TICK_TIME
        if self.duration <= 0:
            arena.active_attacks.remove(self)
        if self.should_delete:
            arena.active_attacks.remove(self)

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
        if self.should_delete:
            arena.active_attacks.remove(self)


class Troop:
    def __init__(self, s, h_p, h_d, h_s, l_t, h_r, s_r, g, t_g_o, t_o, m_s, d_t, m, c_r, p):
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

        self.targetable = True
        self.invulnerable = False
        self.cross_river = False
        self.has_shield = False
        self.should_delete = False #only for kamikaze troops
        self.can_kb = True
        self.collideable = True

        self.preplace = False
        self.placed = True

    def slow(self, duration):
        if not self.invulnerable:
            self.slow_timer = duration
            self.hit_speed = 1.35 * self.normal_hit_speed
            self.load_time = 1.35 * self.normal_load_time
            self.move_speed = 0.65 * self.normal_move_speed

    def move_slow(self, percent, duration):
        self.slow_timer = duration
        self.move_speed = (1 - percent) * self.normal_move_speed

    def unslow(self):
        self.hit_speed = self.normal_hit_speed
        self.load_time = self.normal_load_time
        self.move_speed = self.normal_move_speed

    def stun(self):
        if not self.invulnerable:
            self.stun_timer = 0.5
            self.target = None

    def freeze(self, duration):
        if not self.invulnerable:
            self.stun_timer = duration
            self.attack_cooldown = self.hit_speed

    def damage(self, amount):
        self.cur_hp -= amount

    def heal(self, amount):
        self.cur_hp = min(self.cur_hp + amount, self.hit_points)

    def on_deploy(self, arena):
        pass
    
    def kb(self, vector):
        if self.can_kb and not self.invulnerable:
            self.position.add(vector)

    def die(self, arena):
        self.cur_hp = -1
        arena.troops.remove(self)

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
                if each.targetable and not each.invulnerable and each.side != self.side and (not self.ground_only or (self.ground_only and each.ground)): #targets air or is ground only and each is ground troup
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

            if not tower_target is None and (self.ground and not self.cross_river) and (not same_sign(tower_target.position.y, self.position.y) and ((self.position.y < -1 or self.position.y > 1) or not on_bridge(self.position.x))): # if behind bridge and cant cross river
                r_bridge = vector.distance(vector.Vector(5.6, 1 if self.position.y > 0 else -1), self.position)
                l_bridge = vector.distance(vector.Vector(-5.6, 1 if self.position.y > 0 else -1), self.position)

                tar_bridge = None
                
                
                if (r_bridge < l_bridge): #find closest bridge
                    tar_bridge = vector.Vector(5.6, 1 if self.position.y > 0 else -1)
                elif abs(r_bridge - l_bridge) > 0.1:
                    tar_bridge = vector.Vector(-5.6, 1 if self.position.y > 0 else -1)
                else: # if similar dist
                    if vector.distance(vector.Vector(5.6, 1 if self.position.y > 0 else -1), tower_target.position) < vector.distance(vector.Vector(-5.6, 1 if self.position.y > 0 else -1), tower_target.position):
                        tar_bridge = vector.Vector(5.6, 1 if self.position.y > 0 else -1) #go to side closer to tower
                    else:
                        tar_bridge = vector.Vector(-5.6, 1 if self.position.y > 0 else -1)
            
                direction_x = tar_bridge.x - self.position.x #set movement
                direction_y = tar_bridge.y - self.position.y
                distance_to_target = math.sqrt(direction_x ** 2 + direction_y ** 2)
            elif self.cross_river and ((self.side and (self.position.y > - 2 and self.position.y < 1)) or (not self.side and (self.position.y < 2 and self.position.y > -1))):
                direction_x = 0
                direction_y = 1 if (self.side if self.target is None else self.target.position.y - self.position.y) > 0 else -1 #forwards 
                distance_to_target = 1
                m_s = self.jump_speed
            elif not tower_target is None:
                direction_x = tower_target.position.x - self.position.x #set to directly move to tower
                direction_y = tower_target.position.y - self.position.y
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
        if (self.ground and not self.cross_river) and (not same_sign(self.target.position.y, self.position.y) and ((self.position.y < -1 or self.position.y > 1) or not on_bridge(self.position.x))):
            
            r_bridge = vector.distance(vector.Vector(5.6, 1 if self.position.y > 0 else -1), self.target.position)
            l_bridge = vector.distance(vector.Vector(-5.6, 1 if self.position.y > 0 else -1), self.target.position)
            
            tar_bridge = None
            
            if (r_bridge < l_bridge):
                tar_bridge = vector.Vector(5.6, 1 if self.position.y > 0 else -1)
            else:
                tar_bridge = vector.Vector(-5.6, 1 if self.position.y > 0 else -1)
            
            direction_x = tar_bridge.x - self.position.x
            direction_y = tar_bridge.y - self.position.y
            distance_to_target = math.sqrt(direction_x ** 2 + direction_y ** 2)
        elif self.cross_river and (not on_bridge(self.position.x)) and ((self.target.position.y - self.position.y > 0 and (self.position.y > - 2 and self.position.y < 1)) or (not self.target.position.y - self.position.y > 0 and (self.position.y < 2 and self.position.y > -1))):
            direction_x = 0
            direction_y = 1 if (self.side if self.target is None else self.target.position.y - self.position.y) > 0 else -1 #forwards 
            distance_to_target = 1
            m_s = self.jump_speed
        else:
            direction_x = self.target.position.x - self.position.x
            direction_y = self.target.position.y - self.position.y
            distance_to_target = math.sqrt(direction_x ** 2 + direction_y ** 2)
        
        if vector.distance(self.target.position, self.position) < self.hit_range + self.collision_radius + self.target.collision_radius: #within hit range, then dont move just attack
            self.move_vector = vector.Vector(0, 0)
            direction_x = self.target.position.x - self.position.x #set to directly move to tower
            direction_y = self.target.position.y - self.position.y
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
        self.tick_func(arena)
        if self.stun_timer <= 0:
            if self.deploy_time <= 0:
                if self.target is None or self.target.cur_hp <= 0 or not self.target.targetable:
                    self.update_target(arena)
                elif vector.distance(self.position, self.target.position) > self.sight_range + self.collision_radius + self.target.collision_radius: #add 0.2 so there is tiny buffer for ranged troops
                    self.update_target(arena)
                if self.move(arena) and self.attack_cooldown <= 0: #move, then if within range, attack
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

        if self.placed:
            self.on_deploy(arena)
            self.placed = False

        if self.cur_hp <= 0 or self.should_delete:
            self.die(arena)
        
        if self.slow_timer < 0 :
            self.slow_timer = 0
            self.unslow()
        elif self.slow_timer > 0:
            self.slow_timer -= TICK_TIME

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
        self.stun_timer = 0
        self.sprite_path = ""
        self.animation_cycle_frames = 1
        self.animation_cycle_cur = 1
        self.targetable = True
        self.invulnerable = False
        self.ground = True
        self.type = None

    def damage(self, amount):
        self.cur_hp -= amount
    
    def slow(self, duration):
        self.slow_timer = duration
        self.load_time = 1.35 * self.normal_load_time
        self.hit_speed = 1.35 * self.normal_hit_speed

    def unslow(self):
        self.hit_speed = self.normal_hit_speed
        self.load_time = self.normal_load_time

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
            if not each.invulnerable and each.targetable and each.side != self.side and dist < min_dist and dist < self.hit_range + self.collision_radius + each.collision_radius:
                self.target = each
                min_dist = vector.distance(each.position, self.position)
    
    def tick(self, arena):
        self.tick_func(arena)

        if self.stun_timer <= 0:
            if self.target is None or self.target.cur_hp <= 0 or vector.distance(self.target.position, self.position) > self.hit_range + self.target.collision_radius + self.collision_radius + 4:
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

    def detect_hits(self, arena): #override
        out = []
        for each in arena.troops + arena.buildings + arena.towers:
            if (isinstance(each, Tower) or not each.invulnerable) and each.side != self.side and (vector.distance(each.position, self.position) <= self.radius + each.collision_radius):
                out.append(each)
        return out
    
    def apply_effect(self, target):
        pass
        
    def tick(self, arena):
        if self.preplace:
            return
        if self.spawn_timer > 0:
            tower_to_target  = self.target_pos.subtracted(self.king_pos)
            self.position.add(tower_to_target.scaled(self.velocity / tower_to_target.magnitude()))
            self.spawn_timer -= 1 #spawn in
        elif self.waves > 0 and self.damage_cd <= 0:
            self.sprite_path = f"sprites/{self.class_name}/{self.class_name}_hit.png"
            hits = self.detect_hits(arena)
            for each in hits:
                if (isinstance(each, Tower)):
                    each.damage(self.crown_tower_damage)
                else:
                    each.damage(self.damage); #end damage, start kb
                if (isinstance(each, Troop)):
                    displacement = each.position.subtracted(self.position)
                    displacement.normalize()
                    displacement.scale(self.knock_back)
                    each.kb(displacement)
                self.apply_effect(each)
            self.waves -= 1 #decrease waves
            self.damage_cd = self.time_between #reset cooldown
        elif self.damage_cd > 0:
            self.damage_cd -= TICK_TIME #decrement cooldown
        elif self.display_duration <= 0:
            self.should_delete = True #mark for deletion
        
        if self.pulse_timer <= 0:
            self.pulse_timer = self.pulse_time
            hits = self.detect_hits(arena)
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
    def __init__(self, s, h_p, h_d, h_s, l_t, h_r, s_r, g, t_g_o, t_o, l, d_t, c_r, d_s_c, d_s: type, p):
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

        self.facing_dir = 0
        class_name = self.__class__.__name__.lower()
        self.sprite_path_front = f"sprites/{class_name}/{class_name}" # + "_base.png" or + "_top.png"

        self.is_spawner = False
        self.targetable = True
        self.invulnerable = False
        self.preplace = False

    def slow(self, duration):
        self.slow_timer = duration
        self.hit_speed = 1.35 * self.normal_hit_speed
        self.load_time = 1.35 * self.normal_load_time

    def unslow(self):
        self.hit_speed = self.normal_hit_speed
        self.load_time = self.normal_load_time

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

    def update_target(self, arena):
        self.target = None
        min_dist = float('inf')
        for each in arena.troops + arena.buildings + arena.towers:
            dist = vector.distance(each.position, self.position)
            if (isinstance(each, Tower) or ((not each.invulnerable and each.targetable) and (not self.ground_only or (self.ground_only and each.ground)))) and each.side != self.side and dist < min_dist and dist < self.hit_range + self.collision_radius + each.collision_radius:
                self.target = each
                min_dist = vector.distance(each.position, self.position)

                angle = math.degrees(math.atan2(each.position.y - self.position.y, each.position.x - self.position.x))  # Get angle in degrees
                self.facing_dir = angle
    
    def tick(self, arena):
        if self.preplace:
            return
        self.tick_func(arena)
        if self.target is None or self.target.cur_hp <= 0:
            self.update_target(arena)
        if not self.target is None and self.attack_cooldown <= 0:
            atk = self.attack()
            if isinstance(atk, list) and len(atk) > 0:
                arena.active_attacks.extend(atk)
            elif not atk is None:
                arena.active_attacks.append(self.attack())
            self.attack_cooldown = self.hit_speed
    
    def cleanup(self, arena):
        if self.preplace:
            return
        
        self.cleanup_func(arena)

        self.cur_hp -= self.hit_points * TICK_TIME / self.lifespan
        if self.cur_hp <= 0:
            arena.buildings.remove(self)
            if not self.death_spawn is None:
                for i in range(self.death_spawn_count):
                    arena.troops.append(self.death_spawn(self.side, 
                        self.position.added(vector.Vector(random.uniform(-self.collision_radius, self.collision_radius), random.uniform(-self.collision_radius, self.collision_radius))), 
                        self.level))
        
        if self.slow_timer < 0 :
            self.slow_timer = 0
            self.unslow()
        elif self.slow_timer > 0:
            self.slow_timer -= TICK_TIME
        
        if self.stun_timer <= 0:
            if not self.is_spawner and (self.target is None or (vector.distance(self.target.position, self.position) > self.hit_range + self.target.collision_radius and (self.attack_cooldown <= self.hit_speed - self.load_time))):
                    self.attack_cooldown = self.hit_speed - self.load_time #if not currently attacking but cooldown is less than first hit delay
            else: #otherwise
                self.attack_cooldown -= TICK_TIME
        else:
            self.stun_timer -= TICK_TIME
