import simulation
from aiohttp import web
import asyncio
from abstract_classes import TICK_TIME
import json

async def run_sim_loop():
    while len(simulation.arenas) > 0: #conserve resources
        simulation.simulation_tick()
        await asyncio.sleep(TICK_TIME)

async def handle_action(request):
    data = await request.json()
    action = data.get("action")
    arena_id = None
    result = None

    if action == "join_random":
        result = simulation.join_random(
            player=data["player"],
            tower_troop=data["tower_troop"],
            level=data["level"]
        )
        arena_id = result
    elif action == "join_specific":
        result = simulation.join_specific(
            player=data["player"],
            arena_id=data["arena_id"],
            tower_troop=data["tower_troop"],
            level=data["level"],
            is_alias=data.get("is_alias", True)
        )
        arena_id = result
    elif action == "new_game":
        result = simulation.new_game(
            p1=data["p1"],
            p1_tower=data["p1_tower"],
            p1_level=data["p1_level"],
            random=data.get("random", True), #optional
            lobby_name=data.get("lobby_name") #optional
        )
        arena_id = result
        if len(simulation.arenas) == 1:
            asyncio.create_task(run_sim_loop()) #start
    elif action == "spawn_card":
        simulation.spawn_card(
           name=data["name"],
            pos=data["pos"],
            side=data["side"],
            level=data["level"],
            arena_id=data["arena_id"]
        )
        arena_id = data["arena_id"]
    elif action == "delete":
        a_id = data["arena_id"]
        if a_id in simulation.arenas:
            del simulation.arenas[a_id]
            del simulation.players[a_id]
            del simulation.status[a_id]
            simulation.aliases = {key:val for key, val in simulation.aliases.items() if val != a_id}
        return web.json_response({"confirm": True})
    else:
        return web.json_response({"err": "Invalid action", "confirm": False}, status=400) 

    if arena_id:
        return web.json_response({"confirm": True})
    else:
        return web.json_response({"err": "Arena creation/join failed", "confirm": False}, status=400)
    
async def get_info(request):
    data = await request.json()
    info = simulation.get_information(side=data.get("side", True), arena_id=data.get("arena_id"))
    return web.json_response(info)


    
app = web.Application()
app.router.add_post('/action', handle_action)
app.router.add_post('/wait', get_info)