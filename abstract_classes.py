import math

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

class Arena:
    def __init__(self):
        self.troops = []
        self.active_attacks = []
        self.spells = []
        self.towers = [KingTower(True), PrincessTower(True), PrincessTower(True), KingTower(False), PrincessTower(False), PrincessTower(False) ]
    
    def tick(self):
        for troop in self.troops:
            troop.tick(self)
        for attack in self.active_attacks:
            attack.tick(self)
        for spell in self.spells:
            spell.tick(self)
        for troop in self.troops:
            troop.cleanup(self)
        for attack in self.active_attacks:
            attack.cleanup(self)
        for spell in self.spells:
            spell.cleanup(self)

class AttackEntity:
    def __init__(self, s, d, v, l, i_p):
        self.side = s
        self.damage = d
        self.velocity = v
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
                each.hp -= self.damage;
                self.has_hit.append(each)
        self.duration -= TICK_TIME
        
    def cleanup(self, arena): #also delete self if single target here in derived classes
        if self.duration <= 0:
            arena.active_attacks.remove(self)
        
    def detect_hits(self, arena): # to be overriden in derived
        return []

class Troop:
    def __init__(self, s, h_p, h_d, h_s, f_h, h_r, g, t_g_o, t_o, m_s, d_t, p):
        self.side = s
        self.hit_points = h_p
        self.hit_damage = h_d
        self.hit_speed = h_s
        self.hit_range = h_r
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
        
    def update_target(self, arena):
        if self.tower_only:
            min_dist = float('inf')
            for tower in arena.towers:
                if tower.side != self.side:
                    if distance(tower.position, self.position) < min_dist:
                        self.target = tower
                        min_dist = distance(tower.position, self.position)
        else:
            min_dist = float('inf')
            for each in arena.troops:
                if each.side != self.side and (not self.ground_only or (self.ground_only and each.ground)):
                    if distance(each.position, self.position) < min_dist:
                        self.target = each
                        min_dist = distance(each.position, self.position)
                    
    
    def move(self):
        direction_x = 0
        direction_y = 0
        if self.target is None:
                return False # No target to move towards (error?)
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
        
        if distance_to_target <= hit_range:
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
            self.attack_cooldown -= TICK_TIME
        
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
        self.spawn_timer = v == 0 ? 0 : distance(tar, king_pos) / v
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
                each.position.x += displacement.x * kb
                each.position.y += displacement.y * kb#end kb code
            self.waves -= 1 #decrease waves
            self.damage_cd = self.time_between #reset cooldown
        elif self.damage_cd > 0:
            self.damage_cd -= TICK_TIME #decrement cooldown
        else:
            self.should_delete = True #mark for deletion
            
    def cleanup(self, arena):
        if self.should_delete:
            arena.spells.remove(self) #delete
