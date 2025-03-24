import math
import copy
import random
import vector

TICK_TIME = 1/60 #tps
TILES_PER_MIN = 1/3600

def same_sign(x, y):
    return (x >= 0 and y >= 0) or (x < 0 and y < 0)

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
        
    def tick(self, arena):
        self.position.add(self.velocity)
        hits = self.detect_hits(arena)
        for each in hits:
            new = True
            for h in self.has_hit:
                if each is h:
                    new = False
                    break
            if (new):
                each.hp -= self.damage
                self.has_hit.append(each)
        
        
    def cleanup(self, arena): #also delete self if single target here in derived classes
        self.duration -= TICK_TIME
        if self.duration <= 0:
            arena.active_attacks.remove(self)
        
    def detect_hits(self, arena): # to be overriden in derived
        return []


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

        self.facing_dir = 0
        self.ticks_per_frame = 12
        self.cur_ticks_per_frame = 0
        self.walk_cycle_frames = 1
        self.walk_cycle_cur = 0
        self.sprite_path = ""
        self.stun_timer = 0
        self.move_modifier = 1

        self.targetable = True
        self.invulnerable = False

    def stun(self):
        self.stun_timer = 0.5
        self.target = None
        
    def attack(self): #override
        return None #return the correct attackentity object
        
    def update_target(self, arena): #note: need to change code such that cannot lock onto tower when in sight range, only in attack range
        self.target = None #i.e. target may change (self.target = None) while towers are only targets, except when vector.distance to tower < attack range
        
        min_dist = float('inf')
        if not self.tower_only: #if not tower targeting
            for each in arena.troops: #for each troop
                if each.targetable and not each.invulnerable and each.side != self.side and (not self.ground_only or (self.ground_only and each.ground)): #targets air or is ground only and each is ground troup
                    dist = vector.distance(each.position, self.position)
                    if  dist < min_dist and dist < self.sight_range:
                        self.target = each
                        min_dist = vector.distance(each.position, self.position)
        for each in arena.buildings: #for each building, so if any building is closer then non tower targeting switches, or if tower targeting then finds closest building
            if each.side != self.side:
                dist = vector.distance(each.position, self.position)
                if  dist < min_dist and dist < self.sight_range:
                    self.target = each
                    min_dist = vector.distance(each.position, self.position)
        
        for tower in arena.towers: #check for towers that it can currently hit
            if tower.side != self.side:
                dist = vector.distance(tower.position, self.position)
                if not self.target is None and dist < vector.distance(self.target.position, self.position):
                    self.target = None
                if dist <= self.hit_range and dist < min_dist: #iff can hit tower, then it locks on.
                    self.target = tower #ensures only locks when activel attacking tower, so giant at bridge doesnt immediatly lock onto tower and ruin everyones day
                    min_dist = vector.distance(tower.position, self.position)
    
    def move(self, arena):
        direction_x = 0
        direction_y = 0
        if self.target is None: #head towards tower, since it sees nobody else
            min_dist = float('inf')
            tower_target = None
            for tower in arena.towers:
                if tower.side != self.side:
                    if vector.distance(tower.position, self.position) < min_dist:
                        tower_target = tower
                        min_dist = vector.distance(tower.position, self.position)

            if not tower_target is None and self.ground and not same_sign(tower_target.position.y, self.position.y): # if behind bridge and cant cross river
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
            

            if min_dist < self.hit_range + self.collision_radius + tower_target.collision_radius: #within hit range, locks on
                self.target = tower_target
                return True
            
            direction_x /= distance_to_target
            direction_y /= distance_to_target
            # Move in the direction of the target
            self.position.x += direction_x * self.move_speed
            self.position.y += direction_y * self.move_speed

            angle = math.degrees(math.atan2(direction_y, direction_x))  # Get angle in degrees
            self.facing_dir = angle

            return False

        if self.ground and not (same_sign(self.target.position.y, self.position.y) or math.isclose(self.position.y, 0, abs_tol=1e-2)):
            
            r_bridge = vector.distance(vector.Vector(5.5, 0), self.target.position)
            l_bridge = vector.distance(vector.Vector(-5.5, 0), self.target.position)
            
            tar_bridge = None
            
            if (r_bridge < l_bridge):
                tar_bridge = vector.Vector(5.5, 0)
            else:
                tar_bridge = vector.Vector(-5.5, 0)
            
            direction_x = tar_bridge.x - self.position.x
            direction_y = tar_bridge.y - self.position.y
            distance_to_target = math.sqrt(direction_x ** 2 + direction_y ** 2)
        else:
            direction_x = self.target.position.x - self.position.x
            direction_y = self.target.position.y - self.position.y
            distance_to_target = math.sqrt(direction_x ** 2 + direction_y ** 2)
        
        if vector.distance(self.target.position, self.position) < self.hit_range + self.collision_radius + self.target.collision_radius: #within hit range, then dont move just attack
            return True
        
        direction_x /= distance_to_target
        direction_y /= distance_to_target
        # Move in the direction of the target
        self.position.x += direction_x * self.move_speed
        self.position.y += direction_y * self.move_speed
        return False
            
        
    def tick(self, arena):
        #update arena before
        if self.stun_timer <= 0:
            if self.deploy_time <= 0:
                if self.target is None or self.target.cur_hp <= 0:
                    self.update_target(arena)
                if self.move(arena) and self.attack_cooldown <= 0: #move, then if within range, attack
                    atk = self.attack()
                    if isinstance(atk, list) and len(atk) > 0:
                        arena.active_attacks.extend(atk)
                    elif not atk is None:
                        arena.active_attacks.append(self.attack())
                    self.attack_cooldown = self.hit_speed
            
    
    def cleanup(self, arena): # each troop runs this after ALL ticks are finished
        if self.cur_hp <= 0:
            arena.troops.remove(self)
        
        if self.deploy_time > 0: #if deploying, timer
            self.deploy_time -= TICK_TIME
        elif self.stun_timer <= 0:
            if not self.target is None and not vector.distance(self.target.position, self.position) < self.hit_range + self.target.collision_radius + self.collision_radius and (self.attack_cooldown <= self.hit_speed - self.load_time):
                self.attack_cooldown = self.hit_speed - self.load_time #if not currently attacking but cooldown is less than first hit delay
            else: #otherwise
                self.attack_cooldown -= TICK_TIME #decrement time if either close enough to attack, cooldown greater than min cooldown, or both
            
            #new sprite updating code
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

        self.stun_timer = 0
        self.sprite_path = ""
        self.animation_cycle_frames = 1
        self.animation_cycle_cur = 1

    def stun(self):
        self.stun_timer = 0.5
        self.target = None

    def attack(self):
        return None

    def update_target(self, arena):
        self.target = None
        min_dist = float('inf')
        for each in arena.troops + arena.buildings:
            dist = vector.distance(each.position, self.position)
            if not each.invulnerable and each.targetable and each.side != self.side and dist < min_dist and dist < self.hit_range + each.collision_radius:
                self.target = each
                min_dist = vector.distance(each.position, self.position)
    
    def tick(self, arena):
        if self.stun_timer <= 0:
        #print(self.target) #temp
            if self.target is None or self.target.cur_hp <= 0:
                self.update_target(arena)
            if not self.target is None and self.attack_cooldown <= 0:
                atk = self.attack()
                if isinstance(atk, list) and len(atk) > 0:
                    arena.active_attacks.extend(atk)
                elif not atk is None:
                    arena.active_attacks.append(self.attack())
                self.attack_cooldown = self.hit_speed
            
            class_name = self.__class__.__name__.lower()
            if not self.animation_cycle_frames == 1: #more than one frame per thing
                self.sprite_path = f"sprites/{class_name}/{class_name}_{self.animation_cycle_cur}.png"
            else:
                self.sprite_path = f"sprites/{class_name}/{class_name}.png"
    
    def cleanup(self, arena):
        #print(self.cur_hp) #temp
        if self.cur_hp <= 0:
            arena.towers.remove(self)

        if self.stun_timer <= 0:
            if self.target is None or (vector.distance(self.target.position, self.position) > self.hit_range + self.target.collision_radius and (self.attack_cooldown <= self.hit_speed - self.load_time)):
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

        self.total_time = self.spawn_timer #number of ticks
        
        self.position = tar if v == 0 else self.king_pos

    def detect_hits(self, arena): #override
        out = []
        for each in arena.troops + arena.buildings + arena.towers:
            if (isinstance(each, Tower) or not each.invulnerable) and each.side != self.side and (vector.distance(each.position, self.position) <= self.radius + each.collision_radius):
                out.append(each)
        return out
        
    def tick(self, arena):
        if self.spawn_timer > 0:
            tower_to_target  = self.target_pos.subtracted(self.king_pos)
            self.position.add(tower_to_target.scaled(self.velocity / tower_to_target.magnitude()))
            self.spawn_timer -= 1 #spawn in
        elif self.waves > 0 and self.damage_cd <= 0:
            hits = self.detect_hits(arena)
            for each in hits:
                if (isinstance(each, Tower)):
                    each.cur_hp -= self.crown_tower_damage #crown tower damage
                else:
                    each.cur_hp -= self.damage; #end damage, start kb
                if (isinstance(each, Troop)):
                    displacement = each.position.subtracted(self.position)
                    displacement.normalize()
                    each.position.x += displacement.x * self.knock_back
                    each.position.y += displacement.y * self.knock_back#end kb code
            self.waves -= 1 #decrease waves
            self.damage_cd = self.time_between #reset cooldown
        elif self.damage_cd > 0:
            self.damage_cd -= TICK_TIME #decrement cooldown
        else:
            self.should_delete = True #mark for deletion
            
    def cleanup(self, arena):
        if self.should_delete:
            arena.spells.remove(self) #delete
        
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

        self.cur_hp = h_p
        self.target = None
        self.attack_cooldown = 0
        self.position = p

        self.stun_timer = 0

        self.targetable = True
        self.invulnerable = False

    def stun(self):
        self.stun_timer = 0.5
        self.target = None

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
    
    def tick(self, arena):
        #print(self.target) #temp
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
        #print(self.cur_hp) #temp
        self.cur_hp -= self.hit_points * TICK_TIME / self.lifespan
        if self.cur_hp <= 0:
            arena.buildings.remove(self)
            if not self.death_spawn is None:
                for i in range(self.death_spawn_count):
                    arena.troops.append(self.death_spawn(self.side, 
                        self.position.added(vector.Vector(random.uniform(-self.collision_radius, self.collision_radius), random.uniform(-self.collision_radius, self.collision_radius))), 
                        self.level))
        
        if self.stun_timer <= 0:
            if self.target is None or (vector.distance(self.target.position, self.position) > self.hit_range + self.target.collision_radius and (self.attack_cooldown <= self.hit_speed - self.load_time)):
                    self.attack_cooldown = self.hit_speed - self.load_time #if not currently attacking but cooldown is less than first hit delay
            else: #otherwise
                self.attack_cooldown -= TICK_TIME
        else:
            self.stun_timer -= TICK_TIME
