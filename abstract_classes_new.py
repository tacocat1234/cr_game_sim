import math
import random
from pygame.math import Vector2
from arena_new import Arena
import copy
from abc import ABC, abstractmethod
from enum import Enum

from __future__ import annotations
from typing import Optional

class Side(Enum):
    PLAYER1 = 0
    PLAYER2 = 1

def opposite_side(side: Side) -> Side:
    return Side.PLAYER2 if side == Side.PLAYER1 else Side.PLAYER1

class Effect(ABC):
    def __init__(
        self,
        duration: Optional[float] = None,
        source=None,
    ):
        self.duration = duration
        self.source = source
        self.target = None
        self.expired = False

    def on_apply(self, target) -> None: #on effect applied
        pass

    def on_remove(self, target) -> None: #on effect expiring/removed
        pass

    def on_tick(self, target, dt: float) -> None:
        pass

    def on_attack(self, target, attack) -> None:
        pass

    def on_process_attack(self, target, attack) -> None:
        pass

    def on_die(self, target) -> None:
        pass

    def update(self, dt: float) -> None:
        if self.duration is not None:
            self.duration -= dt
            if self.duration <= 0:
                self.expired = True

class EffectManager:
    def __init__(self, owner):
        self.owner = owner
        self.effects = []

    def apply(self, effect: Effect) -> None:
        effect.target = self.owner
        self.effects.append(effect)
        effect.on_apply(self.owner)

    def dispatch(self, event: str, *args, **kwargs) -> None: #braodcast event happening down to all effects in this manager, ex. self.effects.dispatch('on_tick', dt)
        # Snapshot so effects can safely remove themselves
        # or add other effects while an event is running.
        for effect in tuple(self.effects):
            if not effect.expired:
                getattr(effect, event)(self.owner, *args, **kwargs)

    def update(self, dt: float) -> None:
        for effect in tuple(self.effects):
            if effect.expired:
                continue

            effect.update(dt)

        self.remove_expired()

    def remove_expired(self) -> None:
        for effect in tuple(self.effects):
            if effect.expired:
                effect.on_remove(self.owner)
                self.effects.remove(effect)

    def has(self, effect_type: type) -> bool:
        return any(
            isinstance(effect, effect_type) and not effect.expired
            for effect in self.effects
        )

    def remove(self, effect: Effect) -> None:
        if effect in self.effects:
            effect.on_remove(self.owner)
            self.effects.remove(effect)

class Target(ABC):
    @abstractmethod
    def get_position(self) -> Vector2:
        pass

    @abstractmethod
    def is_valid_target(self, require_grounded: bool = False) -> bool:
        pass

class PositionTarget(Target):
    def __init__(self, position: Vector2):
        self._position = position

    def get_position(self) -> Vector2:
        return self._position

    def is_valid_target(self, require_grounded: bool =False) -> bool:
        return True #should always be valid, since entity can always walk to position

class EntityTarget(Target):
    def __init__(self, entity: Entity):
        self._entity = entity

    def get_position(self) -> Vector2:
        return self._entity.get_position()

    def is_valid_target(self, require_grounded: bool = False) -> bool:
        return self._entity.targetable and self._entity.is_alive() and (not require_grounded or self._entity.ground)

class Entity:
    TYPE = "other"
    SUBTYPE = "other"
    def __init__(self, arena: Arena, position: Vector2, target: Target):
        self._position = position #objects, so are private with accessors, as to prevnt modifying
        self._target = target
        self._arena = arena #also object, def don't want to mod

        self.targetable = False #defualt not targetable
        self.should_delete = False

        self.type = self.TYPE

    def get_arena(self) -> Arena:
        return self._arena

    def get_position(self) -> Vector2:
        return self._position

    def get_position_copy(self) -> Vector2:
        return self._position.copy()

    def get_target(self) -> Target:
        return self._target

    def get_target_copy(self) -> Target:
        return self._target.copy()

    def tick_func(self, dt: float) -> None: #for subclasses that want to run things in the tick step without needint to completely override tick behaviro
        pass

    def tick(self, dt: float) -> None:
        self.tick_func(dt)

    def cleanup_func(self, dt: float) -> None:
        pass

    def cleanup(self, dt: float) -> None:
        self.cleanup_func(dt)
        if self.should_delete:
            self._arena.remove_entity(self)

class AttackEntity(Entity): #very little should inheriet directly from this mos tattacks should inheriet from one of this cihld clases
    DISPLAY_SIZE = 0.25
    LIFESPAN = 0.1 
    SPLASH = False
    SPLASH_RADIUS = 0
    TYPE = "attack"
    def __init__(self, arena: Arena, owner: Entity, position: Vector2, target: Target, damage: float, crown_tower_damage: float = None):
        super().__init__(arena, position, target)

        self.owner = owner

        self.damage = damage
        self.crown_tower_damage = crown_tower_damage if crown_tower_damage is not None else damage

        self._damage_modfiers = dict() #map source (str) : ("additive"/"multiplicative", val)

        self.has_hit = []

    def add_modifier(self, source: str, modifier_type: str, value: float):
        self._damage_modfiers[source] = (modifier_type, value)

    def detect_hits(self, arena: Arena):
        pass

    def apply_effects(self, target: Entity):
        pass

    def true_damage(self) -> float:
        total_damage = self.damage
        multiplier = 1
        for _, (modifier_type, value) in self._damage_modfiers.items():
            if modifier_type == "additive":
                total_damage += value
            elif modifier_type == "multiplicative":
                multiplier *= value
        return total_damage * multiplier #assume add first always


class MeleeAttackEntity(AttackEntity):
    SUBTYPE = "melee"

class RangedAttackEntity(AttackEntity):
    SUBTYPE = "ranged"

class AOEAttackEntity(AttackEntity):
    SUBTYPE = "aoe"

class Unit(Entity):
    TYPE = "unit"
    HIT_POINTS = 0 #all these values will get overriden by subclasses with their values at tournament standard (level 11)
    HIT_DAMAGE = 0
    SHIELD_HIT_POINTS = 0
    HIT_SPEED = 0
    LOAD_TIME = 0
    HIT_RANGE = 0
    SIGHT_RANGE = 0
    GROUND = True
    GROUND_ONLY = True
    TOWER_ONLY = False
    MOVE_SPEED = 0
    DEPLOY_TIME = 1
    MASS = 0
    COLLISION_RADIUS = 0

    def __init__(self, 
            arena,
            position, 
            side,
            level
        ):
        super().__init__(arena, position, None) #unit is spawned with no target, that is determined by its own logic

        self.current_hp = self.get_max_hp()

        self.shield_current_hp = self.get_shield_max_hp()

        self.attack_cooldown = self.LOAD_TIME #attack cooldown before attacks, LOAD_TIME is the minimum time cooldown can be witout a target, can only finish the rest of the LOAD_TIME cooldown if the entity has a target

        self.side = side
        self.level = level

        self.targetable = True #can be targeted
        self.movable = True #can be moved
        self.damageable = True #can be damaged
        self.affectable = True #can be affected by effects (freeze, stun, rage, etc, log knockback)
        self.knockbackable = True #can be knocked back by non-log sources (log kb is controlled by affectable since it ignroes all other times of knocback immunity)

        self._speed_modifiers = dict() # source (str) : (move speed modifier (float), hit speed modifier (float), timer (float)) for troops
        # source (str) : (hit speed modifier (float), timer (float)) for nonmobile units

        self._damage_vulnerability_modifiers = dict() # source (str) : (additive/multiplicative, value, timer (float))
        self._stat_modifiers = dict() # source (str) : ()

        self._special_effects = dict() # modifier type (str), (modifier data (any), timer (float))), for goblin curse or hog curse or enchantment or etc

        self.stun_timer = 0 #timer for no_ai, used for stuns, freezes, other periods of no_ai
        self.no_ai = False #used for disabling AI, such as with goblin cage

    def get_level_modifier(self) -> float:
        return pow(1.1, self.level - 11)

    def get_max_hp(self) -> float:
        return self.HIT_POINTS * self.get_level_modifier() #scales by 1.1 per level, class constant is value at level 11

    def get_shield_max_hp(self) -> float:
        return self.SHIELD_HIT_POINTS * self.get_level_modifier()

    def get_attack_damage(self) -> float:
        return self.HIT_DAMAGE * self.get_level_modifier()

    def set_attributes(self, targetable=True, movable=True, damageable=True, affectable=True, knockbackable=True) -> None:
        self.targetable = targetable
        self.movable = movable
        self.damageable = damageable
        self.affectable = affectable
        self.knockbackable = knockbackable

    def has_shield(self) -> bool: #false if shield is broken or never had shield in first place
        return self.shield_current_hp > 0

    def is_alive(self) -> bool:
        return self.current_hp > 0
    
    def _scaled_damage(self, damage) -> float:
        total_damage = damage
        multiplier = 1
        for _, (modifier_type, value, _) in self._damage_vulnerability_modifiers.items():
            if modifier_type == "additive":
                total_damage += value
            elif modifier_type == "multiplicative":
                multiplier *= value
        return total_damage * multiplier #assume add first always

    def damage(self, amount: float) -> None:
        if self.has_shield():
            self.shield_current_hp -= self._scaled_damage(amount)
            if self.shield_current_hp < 0:
                self.shield_current_hp = 0
        else:
            self.current_hp -= self._scaled_damage(amount)
            if self.current_hp < 0:
                self.current_hp = 0

    def heal(self, amount: float) -> None:
        self.current_hp = min(self.get_max_hp(), self.current_hp + amount)

    def process_attack(self, attack: AttackEntity) -> None:
        if not self.invulnerable:
            self.damage(attack.true_damage())
        if self.affectable:
            attack.apply_effects(self)

    def get_attack_entity(self) -> AttackEntity: #returns standard attack entity for this unit, such as normal melee or normal ranged, excludign any additional attacks or effects that occur upon attack
        return None

    def attack_func(self) -> None: #runs when attacks, for overloading
        pass

    def _rune_giant_enchantment_callback(self, atk: AttackEntity) -> AttackEntity:
        cnt, bns = self._special_effects['runegiantenchantment'][0]
        if cnt == 2: #third attack, since zero one two
            self._special_effects['runegiantenchantment'][0][0] = 0
        else:
            self._special_effects['runegiantenchantment'][0][0] += 1
        atk.add_modifier('runegiantenchantment', 'additive', bns)

        return atk

    def attack(self): #method for unit to attack
        atk = self.get_attack_entity()

        if self.has_special_effect('runegiantenchantment'): # runegiantenchantment : ((bonus_counter, dmg_bonus), timer)
            atk = self._rune_giant_enchantment_callback(atk)
        
        self.arena.add_entity(atk)

        self.attack_func()
        
    def stun(self) -> None: #standard stun of 0.5 seconds
        if self.affectable:
            if self.stun_timer < 0.5:
                self.stun_timer = 0.5
            self.target = None

    def freeze(self, duration: float) -> None:
        if self.affectable:
            if self.stun_timer < duration:
                self.stun_timer = duration
            self.attack_cooldown = self.HIT_SPEED #freeze resets

    def _apply_speed_modifier(self, modifier_type: str, speed_modifier: float, hit_modifier: float, duration: float) -> None: #this is private that does not check for overwriting, will always overwrite
        self._speed_modifiers[modifier_type] = (hit_modifier, duration) #speed modifier is dropped for units that don't move since obviously they have no speed
    
    def rage(self, duration: float) -> None:
        if self.affectable:
            if self._is_speed_modifier_longer('rage', duration):
                self._apply_speed_modifier('rage', 1.3, 0.7, duration) #30% less time between attacks, +30% attack rate

    def ice_slow(self, duration: float) -> None: #standard ice slow effect of 30% slower movement and attakc
        if self.affectable:
            if self._is_speed_modifier_longer('ice_slow', duration):
                self._apply_speed_modifier('ice_slow', 1.3, 0.7, duration) #30% slower movement, 30% more time between attacks

    def modify_speed(self, slow_type: str, speed_modifier: float, hit_modifier: float, duration: float) -> None: #for ramrider, eq, poison
        if self.affectable:
            if self._is_speed_modifier_longer(slow_type, duration):
                self._apply_speed_modifier(slow_type, speed_modifier, hit_modifier, duration)

    def _net_speed_modifiers(self) -> tuple[float, float]:
        total_speed_modifier = 1.0
        total_hit_modifier = 1.0
        for speed_modifier, hit_modifier in self._speed_modifiers.values():
            total_speed_modifier *= speed_modifier
            total_hit_modifier *= hit_modifier
        return total_speed_modifier, total_hit_modifier

    def net_movemment_speed_modifiers(self) -> float:
        return self._net_speed_modifiers()[0]

    def net_hit_speed_modifiers(self) -> float:
        return self._net_speed_modifiers()[1]

    def special_effect(self, effect_type: str, duration: float) -> None:
        if self.affectable:
            if self._is_special_effect_longer(effect_type, duration):
                self._special_effects[effect_type] = (effect_type, duration)

    def has_special_effect(self, effect_type: str) -> bool:
        return effect_type in self._special_effects and self._special_effects[effect_type][1] > 0

    def _is_special_effect_longer(self, effect_type: str, duration: float) -> bool:
        return effect_type in self._special_effects and self._special_effects[effect_type][1] < duration

    def _is_speed_modifier_longer(self, modifier_type: str, duration: float) -> bool:
        return modifier_type in self._speed_modifiers and self._speed_modifiers[modifier_type][1] < duration

    def level_up(self, levels: int = 1) -> None:
        self.level += levels
        self.current_hp *= pow(1.1, levels) #ensure that actual health keeps up, so if max helath is increaed by 10%, it doesnt seem like the troop randomly lost 10% becuase actual health is still the previous value
        self.shield_current_hp *= pow(1.1, levels)
    
    def level_down(self, levels: int = 1) -> None:
        levels_capped = min(levels, self.level - 1) #decreaes by levels, unless levels would put level below 1, instead only decrase by enougth to set to 1
        self.level -= levels_capped
        self.current_hp /= pow(1.1, levels_capped)
        self.shield_current_hp /= pow(1.1, levels_capped)

    def die(self) -> None:
        self.current_hp = 0
        self.should_delete = True

class Troop(Unit):
    SUBTYPE = "troop"
    MOVE_SPEED = 0

    def damage(self, amount: float) -> None:
        multiplier = GoblinCurse.damage_amplification if self.has_special_effect('goblin_curse') else 1.0
        super().damage(amount * multiplier)

    def _apply_speed_modifier(self, modifier_type: str, speed_modifier: float, hit_modifier: float, duration: float) -> None: #this is private that does not check for overwriting, will always overwrite
        self._speed_modifiers[modifier_type] = (speed_modifier, hit_modifier, duration)

    def _is_speed_modifier_longer(self, modifier_type: str, duration: float) -> bool:
            return modifier_type in self._speed_modifiers and self._speed_modifiers[modifier_type][2] < duration

    def _goblin_curse_die_callback(self) -> None:
        self.arena.add_entity(Goblin(self.arena, self.position, opposite_side(self.side), self._special_effects['goblin_curse'][0])) #know must exist since callback only calls when exists

    def _hog_curse_die_callback(self) -> None:
        self.arena.add_entity(CursedHog(self.arena, self.position, opposite_side(self.side), self._special_effects['hog_curse'][0]))

    def die(self) -> None:
        if self.has_special_effect('goblin_curse'):
            self._goblin_curse_die_callback()
        if self.has_special_effect('hog_curse'):
            self._hog_curse_die_callback()
        super().die()