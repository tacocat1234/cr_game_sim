import abstract_classes

class KnightAttackEntity(AttackEntity):
    def __init__(self, side, damage, position):
        super().__init__(
            s=side,
            d=damage,
            v=0,
            l=float('inf'),
            i_p=position,
            )
        self.should_delete = False
    def detect_hits(self, arena):
        detected = None
        all_troops = arena.troops
        min_dist = float('inf')
        for each in all_troops:
            if each.side != self.side and each.ground:
                if distance(each.position, self.position) < min_dist:
                    detected = each
                    min_dist = distance(each.position, self.position)
        if not detected is None:
            return [detected]
        else:
            return []
        
    def tick(self, arena):
        hits = self.detect_hits(arena)
        if not hits:
            hits[0].hp -= self.damage
            self.should_delete = True

    def cleanup(self, arena): #also delete self if single target here in derived classes
        if self.should_delete:
            arena.active_attacks.remove(self)
        
            
class Knight(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s=side,              # Side (True for one player, False for the other)
            h_p= 690 * pow(1.1, level),         # Hit points (Example value)
            h_d= 79 * pow(1.1, level),          # Hit damage (Example value)
            h_s=1.2,          # Hit speed (Seconds per hit)
            f_h=0.5,            # First hit cooldown
            h_r=1.2,            # Hit range
            s_r=5.5,            # Sight Range
            g=True,           # Ground troop
            t_g_o=True,       # Targets ground-only
            t_o=False,        # Not tower-only
            m_s=60*TILES_PER_MIN,          # Movement speed 
            d_t=1,            # Deploy time
            p=position               # Position (Vector object)
        )
    def attack(self):
        return KnightAttackEntity(self.side, self.hit_damage, self.position)
        
class Giant(Troop):
    def __init__(self, side, position, level):
        super().__init__(
            s = side,
            h_p = 1930 * pow(1.1, level - 2),
            h_d = 120 * pow(1.1, level - 2),
            
        )