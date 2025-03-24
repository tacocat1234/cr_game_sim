import socket
import json
import arena
import card_factory
import vector
import towers
import threading

HOST_IP = "127.0.0.1"
PORT = 5555
BUFFER_SIZE = 4096

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST_IP, PORT))




print(f"Server started on {HOST_IP}:{PORT}")

id_map = {} # int : arena.Arena() obj
player_map = {} # int : [uuid, uuid]
arena_states = {} # int : string

# from client JSON format {
# "id" : uuid, #player id
# "action" : string, # "create", "join", "created", "joined", "exit"
# "arena_id" : int (uuid),
# "side" : bool
# "level" : int
# "place" : troopobj, buildingobj, spellobj, None # thing to add
#}

#delete arena.Arena() obj when both players bound to that arena action == exit


# to client JSON format {
# "arena_state" : string # "queuing" (1p), "active" (2p), "p1_win", "p2_win"
# "troop_x" : list,
# "troop_y" : list,
# ... #other coordinate lists
# err = None
#}

lock = threading.Lock()

def handle_clients():
    while True:
        try:
            data, addr = server_socket.recvfrom(BUFFER_SIZE)
            player_data = json.loads(data.decode())

            err = None
            player_id = player_data["id"]  # Unique player ID
            action = player_data["action"]
            arena_id = player_data["arena_id"]

            if not (action == "join" or action == "create"):
                place_x = player_data["x"]
                place_y = player_data["y"]
                place_level = player_data["level"]
                place_str = player_data["place"]
            else:
                place_x = 0
                place_y = 0
                place_level = 0
                place_str = ""

            place_pos = vector.Vector(place_x, place_y)
            verification = None

            with lock:
                match action:
                    case "create":
                        if arena_id not in id_map:
                            id_map[arena_id] = arena.Arena()
                            id_map[arena_id].towers.extend([towers.KingTower(True, player_data["king_level"]), 
                                towers.PrincessTower(True, player_data["princess_level"], True), 
                                towers.PrincessTower(True, player_data["princess_level"], False), 
                                ])
                        if arena_id not in player_map:
                            player_map[arena_id] = [player_id]
                            arena_states[arena_id] = "queuing"  # One player waiting
                    case "join":
                        if arena_id in player_map and len(player_map[arena_id]) == 1:
                            player_map[arena_id].append(player_id)
                            id_map[arena_id].towers.extend([towers.KingTower(True, player_data["king_level"]), #send this data (king_level, princesselevel) only when action is create or join
                                towers.PrincessTower(True, player_data["princess_level"], True), 
                                towers.PrincessTower(True, player_data["princess_level"], False), 
                                ])
                            arena_states[arena_id] = "active"  # Two players, match active
                        else:
                            err = "Invalid arena id"
                    case "created" | "joined":
                        side = player_data["side"]
                        if place_str:
                            place_type = card_factory.get_type(place_str)
                            place_obj = card_factory.card_factory(side, place_pos, place_str, place_level) 
                            if place_type == "troop":
                                if isinstance(place_obj, list):
                                    id_map[arena_id].troops.extend(place_obj)
                                else:
                                    id_map[arena_id].troops.append(place_obj)
                            elif place_type == "spell":
                                if isinstance(place_obj, list):
                                    id_map[arena_id].spells.extend(place_obj)
                                else:
                                    id_map[arena_id].spells.append(place_obj)
                            elif place_type == "building":
                                if isinstance(place_obj, list):
                                    id_map[arena_id].buildings.extend(place_obj)
                                else:
                                    id_map[arena_id].buildings.append(place_obj)
                            verification = True
                    case "wait":
                        pass
                    case "exit":
                        if arena_id in player_map and player_id in player_map[arena_id]:
                            player_map[arena_id].remove(player_id)
                            if not player_map[arena_id]:  # Remove arena if no players left
                                del player_map[arena_id]
                                del id_map[arena_id]
                                del arena_states[arena_id]
                    case _:
                        err = "Invalid Action."

                # Prepare game state update
                if arena_id in id_map:
                    troop_x = [t.position.x for t in id_map[arena_id].troops]
                    troop_y = [t.position.y for t in id_map[arena_id].troops]
                    troop_l = [t.level for t in id_map[arena_id].troops]
                    troop_hp_ratio = [t.cur_hp / t.hit_points for t in id_map[arena_id].troops]
                    troop_sprite = [t.sprite_path for t in id_map[arena_id].troops]
                    troop_dir = [t.facing_dir for t in id_map[arena_id].troops]
                    troop_side = [t.side for t in id_map[arena_id].troops]

                    spell_x = [s.position.x for s in id_map[arena_id].spells]
                    spell_y = [s.position.y for s in id_map[arena_id].spells]
                    spell_sprite = [s.sprite_path for s in id_map[arena_id].spells]

                    building_x = [b.position.x for b in id_map[arena_id].buildings]
                    building_y = [b.position.y for b in id_map[arena_id].buildings]
                    building_l = [b.level for b in id_map[arena_id].buildings]
                    building_hp = [b.cur_hp / b.hit_points for b in id_map[arena_id].buildings]
                    building_sprite = [b.sprite_path for b in id_map[arena_id].buildings]
                    building_side = [b.side for b in id_map[arena_id].buildings]

                    attack_x = [a.position.x for a in id_map[arena_id].active_attacks]
                    attack_y = [a.position.y for a in id_map[arena_id].active_attacks]
                    attack_r = [a.display_size for a in id_map[arena_id].active_attacks]

                    tower_x = [t.position.x for t in id_map[arena_id].towers]
                    tower_y = [t.position.y for t in id_map[arena_id].towers]
                    tower_l = [t.level for t in id_map[arena_id].towers]
                    tower_hp = [t.cur_hp / t.hit_points for t in id_map[arena_id].towers]
                    tower_sprite = [t.sprite_path for t in id_map[arena_id].towers]
                else:
                    troop_x = troop_y = troop_l = troop_hp_ratio = troop_sprite = troop_dir = []
                    spell_x = spell_y = spell_sprite = []
                    building_x = building_y = building_l = building_hp = building_sprite = []
                    attack_x = attack_y = []
                    tower_x = tower_y = tower_l = tower_hp = tower_sprite = []

                # Send response
                response_data = {
                    "arena_state": arena_states.get(arena_id, "unknown"),
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
                    "building_side" : building_side,
                    "attack_x": attack_x,
                    "attack_y": attack_y,
                    "attack_r" : attack_r,
                    "tower_x": tower_x,
                    "tower_y": tower_y,
                    "tower_l": tower_l,
                    "tower_hp": tower_hp, # actually ratio of cur hp to max hp
                    "tower_sprite": tower_sprite,
                    "ack": verification,
                    "err": err
                }

            server_socket.sendto(json.dumps(response_data).encode(), addr)


        except Exception as e:
            print(f"Error: {e}")

def update_arenas():
    while True:
        with lock:
            for id, a in list(id_map.items()):
                a.tick()
                fin = a.cleanup()
                if fin is not None:
                    arena_states[id] = "p1_win" if fin else "p2_win"

client_thread = threading.Thread(target=handle_clients, daemon=True)
client_thread.start()

# Create and start the arena update thread
arena_thread = threading.Thread(target=update_arenas, daemon=True)
arena_thread.start()

# Keep the main thread running to prevent the program from exiting
client_thread.join()
arena_thread.join()