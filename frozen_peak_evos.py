import frozen_peak_cards
from abstract_classes import AttackEntity
from abstract_classes import Troop
from abstract_classes import TILES_PER_MIN
from abstract_classes import TICK_TIME
from abstract_classes import Tower
import copy
import vector

class EvolutionIceSpiritSpecialAttackEntity(AttackEntity):
    DAMAGE_RADIUS = 2
    FREEZE_DURATION = 1.2
    def __init__(self, side, damage, position, remaining = 1):
        super().__init__(
            s=side,
            d=damage,
            v=0,
            l=float('inf'),
            i_p=position
        )
        self.timer = 3
        self.exploded = False
        self.has_hit = []
        self.left = remaining
        self.dropped = False

    def detect_hits(self, arena):
        hits = []
        if self.exploded:
            for each in arena.towers + arena.buildings + arena.troops:
                if (isinstance(each, Tower) or not each.invulnerable) and each.side != self.side: # if different side
                    if vector.distance(self.position, each.position) < EvolutionIceSpiritAttackEntity.DAMAGE_RADIUS + each.collision_radius:
                        hits.append(each)
        return hits
            
    def tick(self, arena):
        if self.exploded:
            hits = self.detect_hits(arena)
            for each in hits:
                new = not any(each is h for h in self.has_hit)
                if (new):
                    each.damage(self.damage)
                    each.freeze(self.FREEZE_DURATION)
                    self.has_hit.append(each)

            if self.left > 0 and not self.dropped:
                self.dropped = True
                arena.active_attacks.append(EvolutionIceSpiritSpecialAttackEntity(self.side, self.damage, self.position, 0))

    def cleanup_func(self, arena):
        if self.timer > 0:
            self.timer -= TICK_TIME
        elif self.duration > 0.25:
            self.display_size = EvolutionIceSpiritSpecialAttackEntity.DAMAGE_RADIUS 
            self.duration =  0.25
            self.exploded = True

class EvolutionIceSpiritAttackEntity(AttackEntity):
    DAMAGE_RADIUS = 1.5
    FREEZE_DURATION = 1.2
    def __init__(self, side, damage, position, target):
        super().__init__(
            s=side,
            d=damage,
            v=400*TILES_PER_MIN,
            l=float('inf'),
            i_p=copy.deepcopy(position)
        )
        self.target = target
        self.exploded = False
        self.has_hit = []

        self.dropped = False

    def detect_hits(self, arena):
        hits = []
        if self.exploded:
            for each in arena.towers + arena.buildings + arena.troops:
                if (isinstance(each, Tower) or not each.invulnerable) and each.side != self.side: # if different side
                    if vector.distance(self.position, each.position) < EvolutionIceSpiritAttackEntity.DAMAGE_RADIUS + each.collision_radius:
                        hits.append(each)
        return hits
            
    def tick(self, arena):
        if self.exploded:
            hits = self.detect_hits(arena)
            for each in hits:
                new = not any(each is h for h in self.has_hit)
                if (new):
                    each.damage(self.damage)
                    each.freeze(self.FREEZE_DURATION)
                    self.has_hit.append(each)

            if not self.dropped:
                self.dropped = True
                arena.active_attacks.append(EvolutionIceSpiritSpecialAttackEntity(self.side, self.damage, self.target.position))

        else:
            direction = self.target.position.subtracted(self.position)
            direction.normalize()

            movement = direction.scaled(self.velocity)
            self.position.add(movement)
            
            if vector.distance(self.position, self.target.position) < self.target.collision_radius:
                self.display_size = EvolutionIceSpiritAttackEntity.DAMAGE_RADIUS 
                self.duration =  0.25
                self.exploded = True

class EvolutionIceSpirit(frozen_peak_cards.IceSpirit):
    def __init__(self, side, position, level):
        super().__init__(side, position, level)
        self.evo = True

    def attack(self):
        self.should_delete = True
        return EvolutionIceSpiritAttackEntity(self.side, self.hit_damage, self.position, self.target)
    
class EvolutionGiantSnowball(frozen_peak_cards.GiantSnowball):
    def __init__(self, side, target, level):
        super().__init__(side, target, level)
        self.evo = True
        self.picked_up = []
        self.roll_timer = 0.67
        self.has_hit = []

    def detect_hits(self, arena): #override
        out = []
        for each in arena.troops + arena.buildings + arena.towers:
            if (isinstance(each, Tower) or not each.invulnerable) and each.side != self.side and (vector.distance(each.position, self.position) <= self.radius + each.collision_radius):
                if not each in self.has_hit:
                    out.append(each)
                    self.has_hit.append(each)
        return out

    def tick(self, arena):
        if self.preplace:
            return
        self.tick_func(arena)

        if self.spawn_timer > 0:
            tower_to_target  = self.target_pos.subtracted(self.king_pos)
            self.position.add(tower_to_target.scaled(self.velocity / tower_to_target.magnitude()))
            self.spawn_timer -= 1 #spawn in
            if self.spawn_timer <= 0:
                self.roll_timer = 0.67
            self.sprite_path = f"sprites/{self.class_name}/{self.class_name}_hit.png"
        else:
            hits = self.detect_hits(arena)
            for each in hits:
                if (isinstance(each, Tower)):
                    each.damage(self.crown_tower_damage)
                else:
                    each.damage(self.damage); #end damage, start kb
                each.slow(4, "giantsnowball")
                if isinstance(each, Troop) and not each.invulnerable:
                    self.picked_up.append(each)
                    each.targetable = False
                    each.stun()
                    each.stun_timer = 0
                    arena.troops.remove(each)

            if self.roll_timer > 0:
                v = vector.Vector(0, self.velocity/2 if self.side else -self.velocity/2)
                self.position.add(v)
                self.roll_timer -= TICK_TIME
            else:
                i = len(self.picked_up)
                for each in self.picked_up:
                    each.targetable = True
                    each.position = self.position.added(vector.Vector(0, i * 1/100 if self.side else -i * 1/100))
                    i -= 1
                arena.troops.extend(self.picked_up)
                self.should_delete = True