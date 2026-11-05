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

class Effect(ABC): #stun, freeze, rage, etc. or effects like being hog cursed or goblin cursed
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

    @abstractmethod
    def get_type(self) -> str:
        pass

class PositionTarget(Target):
    def __init__(self, position: Vector2):
        self._position = position

    def get_position(self) -> Vector2:
        return self._position

    def is_valid_target(self, require_grounded: bool =False) -> bool:
        return True #should always be valid, since entity can always walk to position
    
    def get_type(self) -> str:
        return "position"

class EntityTarget(Target):
    def __init__(self, entity: Entity):
        self._entity = entity

    def get_position(self) -> Vector2:
        return self._entity.get_position()

    def is_valid_target(self, require_grounded: bool = False) -> bool:
        return self._entity.targetable and self._entity.is_alive() and (not require_grounded or self._entity.ground)
    
    def get_type(self) -> str:
        return "entity"

class Entity:
    TYPE = None #not defined
    SUBTYPE = None #not defined
    BASE_PROPERTIES = {}
    def __init__(self, arena: Arena, position: Vector2, target: Target):
        self._position = position #objects, so are private with accessors, as to prevnt modifying
        self._target = target
        self._arena = arena #also object, def don't want to mod

        self._base_property_modifiers = {} # property (str) > {source (str) > (function: func, priority:int, timer:float)} 

        self.properties = {}

        self._property_modifiers = {}

        self.timers = {}

        self.should_delete = False

        self.type = self.TYPE

    def add_base_property_modifier(self, property_name: str, source: str, func, priority: int, timer: float = None) -> None:
        if property_name not in self._base_property_modifiers:
            self._base_property_modifiers[property_name] = {}
        elif self._base_property_modifiers[property_name].get(source) and self._base_property_modifiers[property_name][source][2] < timer: #if has source and new timer longer
            self._base_property_modifiers[property_name][source][2] = timer #update to the longer timer
            return
        
        self._base_property_modifiers[property_name][source] = (func, priority, timer) #set new

    def add_property_modifier(self, property_name: str, source: str, func, priority: int, timer: float = None) -> None:
        if property_name not in self._property_modifiers:
            self._property_modifiers[property_name] = {}
        elif self._property_modifiers[property_name].get(source) and self._property_modifiers[property_name][source][2] < timer: #if has source and new timer longer
            self._property_modifiers[property_name][source][2] = timer
            return
        
        self._property_modifiers[property_name][source] = (func, priority, timer)

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
    
    def get_base_property(self, property: str): #raw value
        return self.BASE_PROPERTIES.get(property, None)
    
    def get_property(self, property: str):
        return self.properties.get(property, None)
    
    def get_timer(self, timer: str) -> float:
        return self.timers.get(timer, 0)
    
    def get_true_base_property_value(self, property_name: str):
        base = self.BASE_PROPERTIES.get(property_name, None)
        if base is None:
            return None

        mods = self._base_property_modifiers.get(property_name, {}).items()
        mods = sorted(mods, key=lambda x: x[1][1]) #sort by priority        

        for _, (func, _, _) in mods:
            base = func(base) #apply that func

        return base
            

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

class AttackEntity(Entity): #very little should inheriet directly from this most attacks should inhereit from one of this child classes
    BASE_PROPERTIES = {
        "display_size" : 0.25,
        "lifespan" : 0.1,
        "splash" : False,
        "splash_radius" : 0,
        "damage" : 0,
        "crown_tower_damage" : 0,
        "reflectable" : False,
        "parryable" : False
    }
    TYPE = "attack"
    def __init__(self, arena: Arena, owner: Entity, position: Vector2, target: Target, damage: float, crown_tower_damage: float = None):
        super().__init__(arena, position, target)

        self.owner = owner

        self.timers = {
            "lifespan" : self.get_base_property("lifespan")
        }

        self.has_hit = []


    def detect_hits(self, arena: Arena):
        pass

    def apply_effects(self, target: Entity) -> None:
        pass

    def true_damage(self) -> float:
        return self.get_true_base_property_value("damage")
    
    def true_crown_tower_damage(self) -> float:
        return self.get_true_base_property_value("crown_tower_damage")


class MeleeAttackEntity(AttackEntity):
    pass

class RangedAttackEntity(AttackEntity):
    pass

class AOEAttackEntity(AttackEntity):
    pass

class Unit(Entity):
    TYPE = "unit"
    BASE_PROPERTIES = { #overwritten by child classes with class specific constants at level 11
        "hit_points": 0,
        "hit_damage": 0,
        "shield_hit_points": 0,
        "hit_speed": 0,
        "load_time": 0,
        "hit_range": 0,
        "sight_range": 0,
        "ground": True,
        "ground_only": True,
        "tower_only": False,
        "move_speed": 0,
        "deploy_time": 1,
        "mass": 0,
        "collision_radius": 0,
        "targetable" : True, #can be targeted
        "movable" : True, #can be moved
        "damageable" : True, #can be damaged
        "affectable" : True, #can be affected by effects (freeze, stun, rage, etc, log knockback)
        "knockbackable" : True, #can be knocked back by non-log sources (log kb is controlled by affectable since it ignroes all other times of knocback immunity)
        "no_ai" : False,
        "damage_vulnerability" : 1
    }

    def __init__(self, 
            arena,
            position, 
            side,
            level
        ):
        super().__init__(arena, position, None) #unit is spawned with no target, that is determined by its own logic

        self.side = side #fundamental
        self.level = level

        self.current_hp = self.get_max_hp()

        self.shield_current_hp = self.get_shield_max_hp()

        self.attack_cooldown = self.get_base_property("hit_speed") #attack cooldown before attacks, LOAD_TIME is the minimum time cooldown can be witout a target, can only finish the rest of the LOAD_TIME cooldown if the entity has a target

        self.timers = {
            "deploy_timer": self.get_base_property("deploy_time"),
            "attack_cooldown": self.get_base_property("hit_speed"),
            "no_ai_timer": 0
        }

    def is_no_ai(self) -> bool:
        return self.get_property("no_ai") or self.get_timer("no_ai_timer") > 0

    def get_level_modifier(self) -> float:
        return pow(1.1, self.level - 11)

    def get_max_hp(self) -> float:
        return self.get_base_property("hit_points") * self.get_level_modifier() #scales by 1.1 per level, class constant is value at level 11

    def get_shield_max_hp(self) -> float:
        return self.get_base_property("shield_hit_points") * self.get_level_modifier()

    def get_attack_damage(self) -> float:
        return self.get_base_property("hit_damage") * self.get_level_modifier()

    def set_interaction_properties(self, targetable=True, movable=True, damageable=True, affectable=True, knockbackable=True) -> None: #basic 
        self.properties["targetable"] = targetable
        self.properties["movable"] = movable
        self.properties["damageable"] = damageable
        self.properties["affectable"] = affectable
        self.properties["knockbackable"] = knockbackable

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
        else:
            self.current_hp -= self._scaled_damage(amount)

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

    def attack(self): #method for unit to attack
        atk = self.get_attack_entity()
        
        self.arena.add_entity(atk)

        self.attack_func()

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
    TYPE = "troop"
    BASE_PROPERTIES = { #overwritten by child classes with class specific constants at level 11
        "hit_points": 0,
        "hit_damage": 0,
        "shield_hit_points": 0,
        "hit_speed": 0,
        "load_time": 0,
        "hit_range": 0,
        "sight_range": 0,
        "ground": True,
        "ground_only": True,
        "tower_only": False,
        "move_speed": 0,
        "deploy_time": 1,
        "mass": 0,
        "collision_radius": 0,
        "move_speed" : 0
    }

