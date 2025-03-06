import math
import arena

TICK_TIME = 1/60 #tps
TILES_PER_MIN = 1/3600

def same_sign(x, y):
    return (x >= 0 and y >= 0) or (x < 0 and y < 0)

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def add(self, other):
        self.x += other.x
        self.y += other.y
        
    def subtract(self, other):
        self.x -= other.x
        self.y -= other.y
        
    def scale(self, scalar):
        self.x *= scalar
        self.y *= scalar

def distance(vec1, vec2):
    return math.sqrt((vec2.x - vec1.x) ** 2 + (vec2.y - vec1.y) ** 2)


class Troop:
    def __init__(self, s, h_p, h_d, h_s, f_h, h_r, s_r, g, t_g_o, t_o, m_s, d_t, p):
        self.side = s
        self.hit_points = h_p
        self.hit_damage = h_d
        self.hit_speed = h_s
        self.hit_range = h_r
        self.sight_range = s_r
        self.ground = g
        self.ground_only = t_g_o
        self.tower_only = t_o
        self.move_speed = m_s
        self.deploy_time = d_t
        
        self.cur_hp = h_p
        self.position = p
        self.target = None
        self.attack_cooldown = f_h
        
    def attack(self): #override
        return None #return the correct attackentity object
        
    def update_target(self, arena): #note: need to change code such that cannot lock onto tower when in sight range, only in attack range
        self.target = None #i.e. target may change (self.target = None) while towers are only targets, except when distance to tower < attack range
        
        if not self.tower_only:
            min_dist = float('inf')
            for each in arena.troops:
                if each.side != self.side and (not self.ground_only or (self.ground_only and each.ground)):
                    dist = distance(each.position, self.position)
                    if  dist < min_dist and dist < self.sight_range:
                        self.target = each
                        min_dist = distance(each.position, self.position)
        else:
            min_dist = float('inf')
            for each in arena.buildings:
                if each.side != self.side:
                    dist = distance(each.position, self.position)
                    if  dist < min_dist and dist < self.sight_range:
                        self.target = each
                        min_dist = distance(each.position, self.position)
        
        for tower in arena.towers: #check if any tower is closer/within range
            if tower.side != self.side:
                dist = distance(tower.position, self.position)
                if dist <= self.hit_range and dist < min_dist: #if in hit range and closer, target becoems tower
                    self.target = tower
                    min_dist = distance(tower.position, self.position)
    
    def move(self):
        direction_x = 0
        direction_y = 0
        if self.target is None: #target tower, sees nobody else
            min_dist = float('inf')
            tower_target = None
            for tower in arena.towers:
                if tower.side != self.side:
                    if distance(tower.position, self.position) < min_dist:
                        tower_target = tower
                        min_dist = distance(tower.position, self.position)

            if self.ground and not same_sign(tower_target.position.y, self.position.y): # if behind bridge and cant cross
            
                r_bridge = distance(Vector(5.5, 0), self.target.position)
                l_bridge = distance(Vector(-5.5, 0), self.target.position)
                
                tar_bridge = None
                
                if (r_bridge < l_bridge): #find closest bridge
                    tar_bridge = Vector(5.5, 0)
                else:
                    tar_bridge = Vector(-5.5, 0)
            
                direction_x = tar_bridge.position.x - self.position.x #set movement
                direction_y = tar_bridge.position.y - self.position.y
                distance_to_target = math.sqrt(direction_x ** 2 + direction_y ** 2)
            else:
                direction_x = tower_target.position.x - self.position.x #set to directly move to tower
                direction_y = tower_target.position.y - self.position.y
                distance_to_target = math.sqrt(direction_x ** 2 + direction_y ** 2)

            if min_dist <= self.hit_range:
                return True

        if self.ground and not same_sign(self.target.position.y, self.position.y):
            
            r_bridge = distance(Vector(5.5, 0), self.target.position)
            l_bridge = distance(Vector(-5.5, 0), self.target.position)
            
            tar_bridge = None
            
            if (r_bridge < l_bridge):
                tar_bridge = Vector(5.5, 0)
            else:
                tar_bridge = Vector(-5.5, 0)
            
            direction_x = tar_bridge.position.x - self.position.x
            direction_y = tar_bridge.position.y - self.position.y
            distance_to_target = math.sqrt(direction_x ** 2 + direction_y ** 2)
        else:
            direction_x = self.target.position.x - self.position.x
            direction_y = self.target.position.y - self.position.y
            distance_to_target = math.sqrt(direction_x ** 2 + direction_y ** 2)
        
        if distance_to_target <= self.hit_range:
            return True
        # Normalize direction
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
            if self.move() and self.attack_cooldown <= 0: #move, then if within range, attack
                arena.active_attacks.append(self.attack())
                self.attack_cooldown = self.hit_speed
    def cleanup(self, arena): # each troop runs this after ALL ticks are finished
        if self.cur_hp <= 0:
            arena.troops.remove(self)
        
        if self.deploy_time > 0: #if deploying, timer
            self.deploy_time -= TICK_TIME
        else:
            if not distance(self.target.position, self.position) < self.hit_range and (self.attack_cooldown <= self.hit_speed - self.load_time):
                self.attack_cooldown = self.hit_speed - self.load_time #if not currently attacking but cooldown is less than first hit delay
            else: #otherwise
                self.attack_cooldown -= TICK_TIME #decrement time if either close enough to attack, cooldown greater than min cooldown, or both
        
class Spell:
    def __init__(self, s, d, w, t, kb, v, tar):
        self.side = s
        self.damage = d
        self.waves = w
        self.time_between = t
        self.knock_back = kb
        self.velocity = v
        self.target_pos = tar
        
        self.damage_cd = t
        king_pos = (Vector(0, -12) if s else Vector(0, 12))
        self.spawn_timer = 0 if v == 0 else distance(tar, king_pos) / v
        self.should_delete = False
        
    def detect_hits(self, arena): #override
        return []
        
    def tick(self, arena):
        if self.spawn_timer >= 0:
            self.spawn_timer -= TICK_TIME #spawn in
        elif self.waves > 0 and self.damage_cd <= 0:
            hits = self.detect_hits(arena)
            for each in hits:
                each.hp -= self.damage; #end damage, start kb
                displacement = Vector(each.position.x - self.target_pos.x, each.position.y - self.target_pos.y)
                distance_to_target = math.sqrt(displacement.x ** 2 + displacement.y ** 2)
                if distance_to_target != 0:
                    displacement.x /= distance_to_target
                    displacement.y /= distance_to_target
                each.position.x += displacement.x * self.kb
                each.position.y += displacement.y * self.kb#end kb code
            self.waves -= 1 #decrease waves
            self.damage_cd = self.time_between #reset cooldown
        elif self.damage_cd > 0:
            self.damage_cd -= TICK_TIME #decrement cooldown
        else:
            self.should_delete = True #mark for deletion
            
    def cleanup(self, arena):
        if self.should_delete:
            arena.spells.remove(self) #delete
