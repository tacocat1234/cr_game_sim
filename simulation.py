import arena
from card_factory import card_factory
from card_factory import tower_factory
import uuid
import random

arenas = {} #map of id to arena
players = {} # map of id to [p1, p2]
status = {} # map of id to str
aliases = {} # map of alias to id

def join_random(player, tower_troop, level):
    waiting_games = [a_id for a_id, stat in status.items() if stat == "waiting_random"]
    if not waiting_games:
        return None  # No waiting games to join
    chosen_id = random.choice(waiting_games)
    players[chosen_id].append(player)
    status[chosen_id] = "active"
    arenas[chosen_id].towers.extend(tower_factory(False, tower_troop, level))
    return chosen_id

def join_specific(player, arena_id, tower_troop, level, is_alias=True):
    a_id = aliases.get(arena_id) if is_alias else arena_id
    if a_id not in players or status[a_id] != "waiting_specific":
        return None  # Invalid ID
    players[a_id].append(player)
    status[a_id] = "active"
    arenas[a_id].towers.extend(tower_factory(False, tower_troop, level))
    return a_id

def new_game(p1, p1_tower, p1_level, p2=None, p2_tower = None, p2_level = None, random=True, lobby_name=None):
    a_id = str(uuid.uuid1())
    if random:
        status[a_id] = "waiting_random"
    else:
        if not lobby_name in aliases:
            aliases[lobby_name] = a_id
        else:
            return None #alias already in use
        status[a_id] = "waiting_specific"
    
    arenas[a_id] = arena.Arena()
    arenas[a_id].towers.extend(tower_factory(True, p1_tower, p1_level))
    players[a_id] = [p1]
    if p2 is not None:
        players[a_id].append(p2)
        status[a_id] = "active"
        arenas[a_id].towers.extend(tower_factory(False, p2_tower, p2_level))
    return a_id


def simulation_tick():
    for key, each in arenas.items():
        if status[key] == "active":
            each.tick()
    for key, each in arenas.items():
        if status[key] == "active":
            win = each.cleanup()
            if win is not None:
                status[key] = "p1_win" if win else "p2_win"

def spawn_card(name, pos, side, level, arena_id):
    place_type, place_obj = card_factory(side, pos, name, level)
    if place_type == "troop":
        if isinstance(place_obj, list):
            arenas[arena_id].troops.extend(place_obj)
        else:
            arenas[arena_id].troops.append(place_obj)
    elif place_type == "spell":
        if isinstance(place_obj, list):
            arenas[arena_id].spells.extend(place_obj)
        else:
            arenas[arena_id].spells.append(place_obj)
    elif place_type == "building":
        if isinstance(place_obj, list):
            arenas[arena_id].buildings.extend(place_obj)
        else:
            arenas[arena_id].buildings.append(place_obj)

def get_information(side, arena_id):
    if arena_id not in arenas:
        err = "Invalid arena ID"
        response_data = {"err" : err}
    else:
        a = arenas[arena_id]
        err = None
        troop_x = [t.position.x for t in a.troops]
        troop_y = [(t.position.y if side else -t.position.y) for t in a.troops]
        troop_l = [t.level for t in a.troops]
        troop_hp_ratio = [t.cur_hp / t.hit_points for t in a.troops]
        troop_sprite = [t.sprite_path for t in a.troops]
        troop_dir = [(t.facing_dir if side else -t.facing_dir) for t in a.troops]
        troop_side = [t.side for t in a.troops]

        spell_x = [s.position.x for s in a.spells]
        spell_y = [(s.position.y if side else -s.position.y) for s in a.spells]
        spell_sprite = [s.sprite_path for s in a.spells]

        building_x = [b.position.x for b in a.buildings]
        building_y = [(b.position.y if side else -b.position.y) for b in a.buildings]
        building_l = [b.level for b in a.buildings]
        building_hp = [b.cur_hp / b.hit_points for b in a.buildings]
        building_sprite = [b.sprite_path_front for b in a.buildings]
        building_dir = [(b.facing_dir if side else - b.facing_dir) for b in a.buildings]
        building_side = [b.side for b in a.buildings]

        attack_x = [a.position.x for a in a.active_attacks]
        attack_y = [(a.position.y if side else -a.position.y) for a in a.active_attacks]
        attack_r = [a.display_size for a in a.active_attacks]

        tower_x = [t.position.x for t in a.towers]
        tower_y = [(t.position.y if side else -t.position.y) for t in a.towers]
        tower_l = [t.level for t in a.towers]
        tower_hp = [t.cur_hp / t.hit_points for t in a.towers]
        tower_sprite = [t.sprite_path for t in a.towers]

        response_data = {
                    "arena_state": status.get(arena_id, "unknown"),
                    "troop_x": troop_x,
                    "troop_y": troop_y,
                    "troop_l": troop_l,
                    "troop_hp": troop_hp_ratio,  # actually ratio of cur hp to max hp
                    "troop_sprite": troop_sprite,
                    "troop_dir": troop_dir,
                    "troop_side": troop_side,
                    "spell_x": spell_x,
                    "spell_y": spell_y,
                    "spell_sprite": spell_sprite,
                    "building_x": building_x,
                    "building_y": building_y,
                    "building_l": building_l,
                    "building_hp": building_hp,
                    "building_sprite": building_sprite,
                    "building_dir" : building_dir,
                    "building_side" : building_side,
                    "attack_x": attack_x,
                    "attack_y": attack_y,
                    "attack_r" : attack_r,
                    "tower_x": tower_x,
                    "tower_y": tower_y,
                    "tower_l": tower_l,
                    "tower_hp": tower_hp, # actually ratio of cur hp to max hp
                    "tower_sprite": tower_sprite,
                    "err": err
                }
    return response_data
    
