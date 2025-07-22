from abstract_classes import Troop
from abstract_classes import RangedAttackEntity
from abstract_classes import MeleeAttackEntity
from abstract_classes import TILES_PER_MIN
from abstract_classes import TICK_TIME

class Champion(Troop):
    def __init__(self, s, h_p, h_d, h_s, l_t, h_r, s_r, g, t_g_o, t_o, m_s, d_t, m, c_r, p, ability_cost, ability_cast_time, ability_duration, ability_cooldown, cloned=False):
        super().__init__(s, h_p, h_d, h_s, l_t, h_r, s_r, g, t_g_o, t_o, m_s, d_t, m, c_r, p, cloned)
        self.ability_cost = ability_cost
        self.ability_cast_timer = ability_cast_time
        self.ability_cast_time = ability_cast_time
        self.ability_duration = ability_duration
        self.ability_duration_timer = ability_duration
        self.ability_cooldown = ability_cooldown
        self.ability_cooldown_timer = ability_cooldown

        self.ability_active = False


    def tick(self, arena):
        if self.ability_active:
            if self.ability_cast_timer < 0: #if cast
                self.ability_cast_timer = 0 #remains on
                self.ability(arena) #trigger once

        
            if self.ability_cast_timer != 0:
                self.ability_cast_timer -= TICK_TIME #if not cast
            else: #if cast
                if self.ability_duration_timer > 0: #if duration active
                    self.ability_tick(arena)
                    self.ability_duration_timer -= TICK_TIME
                else:
                    self.ability_active = False
                    self.ability_end(arena)


        if self.ability_cooldown_timer > 0:
            self.ability_cooldown_timer -= TICK_TIME
        
        return super().tick(arena)

    def ability(self, arena):
        pass

    def ability_tick(self, arena):
        pass

    def ability_end(self, arena):
        pass

    def activate_ability(self, arena):
        works = False
        if self.side:
            if arena.p1_elixir >= self.ability_cost:
                arena.p1_elixir -= self.ability_cost
                works = True
            
        else:
            if arena.p2_elixir >= self.ability_cost:
                arena.p2_elixir -= self.ability_cost
                works = True
        
        if works:
            self.ability_active = True
            self.ability_cast_timer = self.ability_cast_time
            self.ability_cooldown_timer = self.ability_cooldown

class ArcherQueenRangedAttackEntity(RangedAttackEntity):
    def __init__(self, side, damage, position, target):
        super().__init__(side, damage, 800 * TILES_PER_MIN, position, target)

class ArcherQueen(Champion):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 1000 * pow(1.1, level - 11),         # Hit points (Example value)
            h_d= 225 * pow(1.1, level - 11),          # Hit damage (Example value)
            h_s=1.2,          # Hit speed (Seconds per hit)
            l_t=0.9,            # First hit cooldown
            h_r=5,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=False,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            m=6,            #mass
            c_r=0.5,        #collision radius
            p=position,               # Position (vector.Vector object)
            ability_cost = 1,
            ability_cast_time=0.933,
            ability_duration=3,
            ability_cooldown=15
        ) 
        self.level = level

    def attack(self):
        return ArcherQueenRangedAttackEntity(self.side, self.hit_damage, self.position, self.target)
    
    def ability(self, arena):
        self.targetable = False
        self.move_speed *= 0.75
        self.hit_speed /= 2.8
        self.load_time /= 2.8
    
    def ability_end(self, arena):
        self.targetable = True
        self.hit_speed *= 2.8
        self.load_time *= 2.8
        self.move_speed *= 4/3