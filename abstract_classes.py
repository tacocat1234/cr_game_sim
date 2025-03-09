import math
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
        
    def attack(self): #override
        return None #return the correct attackentity object
        
    def update_target(self, arena): #note: need to change code such that cannot lock onto tower when in sight range, only in attack range
        self.target = None #i.e. target may change (self.target = None) while towers are only targets, except when vector.distance to tower < attack range
        
        min_dist = float('inf')
        if not self.tower_only: #if not tower targeting
            for each in arena.troops: #for each troop
                if each.side != self.side and (not self.ground_only or (self.ground_only and each.ground)): #targets air or is ground only and each is ground troup
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

            if self.ground and not same_sign(tower_target.position.y, self.position.y): # if behind bridge and cant cross river
            
                r_bridge = vector.distance(vector.Vector(5.5, 0), tower_target.position)
                l_bridge = vector.distance(vector.Vector(-5.5, 0), tower_target.position)
                
                tar_bridge = None
                
                if (r_bridge < l_bridge): #find closest bridge
                    tar_bridge = vector.Vector(5.5, 0)
                else:
                    tar_bridge = vector.Vector(-5.5, 0)
            
                direction_x = tar_bridge.x - self.position.x #set movement
                direction_y = tar_bridge.y - self.position.y
                distance_to_target = math.sqrt(direction_x ** 2 + direction_y ** 2)
            else:
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
            return False

        if self.ground and not same_sign(self.target.position.y, self.position.y):
            
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
        if self.deploy_time <= 0:
            if self.target is None or self.target.cur_hp <= 0:
                self.update_target(arena)
            if self.move(arena) and self.attack_cooldown <= 0: #move, then if within range, attack
                atk = self.attack()
                if isinstance(atk, list):
                    arena.active_attacks.extend(atk)
                else:
                    arena.active_attacks.append(self.attack())
                self.attack_cooldown = self.hit_speed
    
    def cleanup(self, arena): # each troop runs this after ALL ticks are finished
        if self.cur_hp <= 0:
            arena.troops.remove(self)
        
        if self.deploy_time > 0: #if deploying, timer
            self.deploy_time -= TICK_TIME
        else:
            if not self.target is None and not vector.distance(self.target.position, self.position) < self.hit_range + self.target.collision_radius + self.collision_radius and (self.attack_cooldown <= self.hit_speed - self.load_time):
                self.attack_cooldown = self.hit_speed - self.load_time #if not currently attacking but cooldown is less than first hit delay
            else: #otherwise
                self.attack_cooldown -= TICK_TIME #decrement time if either close enough to attack, cooldown greater than min cooldown, or both
        
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

    def attack(self):
        return None

    def update_target(self, arena):
        self.target = None
        min_dist = float('inf')
        for each in arena.troops + arena.buildings:
            dist = vector.distance(each.position, self.position)
            if each.side != self.side and dist < min_dist and dist < self.hit_range + each.collision_radius:
                self.target = each
                min_dist = vector.distance(each.position, self.position)
    
    def tick(self, arena):
        #print(self.target) #temp
        if self.target is None or self.target.cur_hp <= 0:
            self.update_target(arena)
        if not self.target is None and self.attack_cooldown <= 0:
            arena.active_attacks.append(self.attack())
            self.attack_cooldown = self.hit_speed
    
    def cleanup(self, arena):
        #print(self.cur_hp) #temp
        if self.cur_hp <= 0:
            arena.towers.remove(self)
        if self.target is None or (vector.distance(self.target.position, self.position) > self.hit_range + self.target.collision_radius and (self.attack_cooldown <= self.hit_speed - self.load_time)):
                self.attack_cooldown = self.hit_speed - self.load_time #if not currently attacking but cooldown is less than first hit delay
        else: #otherwise
            self.attack_cooldown -= TICK_TIME



class Spell:
    def __init__(self, s, d, c_t_d, w, t, kb, r, v, tar):
        self.side = s
        self.damage = d
        self.crown_tower_damage = c_t_d,
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
        
        self.position = self.king_pos

    def detect_hits(self, arena): #override
        out = []
        for each in arena.troops + arena.buildings + arena.towers:
            if each.side != self.side and (vector.distance(each.position, self.position) <= self.radius + each.collision_radius):
                out.append(each)
        return out
        
    def tick(self, arena):
        if self.spawn_timer >= 0:
            self.position.add(self.target_pos.subtracted(self.king_pos).scaled(1 / self.total_time))
            self.spawn_timer -= 1 #spawn in
        elif self.waves > 0 and self.damage_cd <= 0:
            hits = self.detect_hits(arena)
            for each in hits:
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
        
