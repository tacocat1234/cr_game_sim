const server_address = ""; 

arenaId = "";
side = null;

// Start a new game
function new_game(id, tower, level, random = true, lobby_name = null) {
    const body = {
        action: "new_game",
        p1: id,
        p1_tower: tower,
        p1_level: level,
        random: random
    };
    if (lobby_name) body.lobby_name = lobby_name;

    side = True

    return fetch(server_address + "/action", { //get_info
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
    }).then(res => res.json())
    .then(data => {
        console.log("Game info:", data);
        arenaId = data.arena_id; // store this for later
    })
    .catch(console.error);
    
}

function join_random(id, tower, level) {
    const body = {
        action: "join_random",
        player: id,
        tower_troop: tower,
        level: level
    };

    side = false;

    return fetch(server_address + "/action", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
    })
    .then(res => res.json())
    .then(data => {
        console.log("Joined random game:", data);
        arenaId = data.arena_id;
    })
    .catch(console.error);
}

function join_specific(id, lobby_name, tower, level, is_alias = true) {
    const body = {
        action: "join_specific",
        player: id,
        arena_id: lobby_name,
        tower_troop: tower,
        level: level,
        is_alias: is_alias
    };

    side = false;

    return fetch(server_address + "/action", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
    })
    .then(res => res.json())
    .then(data => {
        console.log("Joined specific game:", data);
        arenaId = data.arena_id;
    })
    .catch(console.error);
}

function spawn_card(name, pos, level) {
    if (!arenaId || side === null) {
        console.error("Missing arenaId or side");
        return;
    }

    const body = {
        action: "spawn_card",
        name: name,
        pos: pos,// { x: number, y: number }
        side: side,
        level: level,
        arena_id: arenaId
    };

    return fetch(server_address + "/action", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
    })
    .then(res => res.json())
    .then(data => {
    })
    .catch(console.error);
}

function delete_arena() {
    if (!arenaId || side === null) {
        console.error("Missing arenaId or side");
        return;
    }

    const body = {
        action: "delete",
        arena_id: arenaId
    };

    return fetch(server_address + "/action", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
    })
    .then(res => res.json())
    .then(data => {
    })
    .catch(console.error);
}

// Get arena info (poll game state)
function get_info() {
    if (!arenaId || side === null) {
        console.error("Missing arenaId or side");
        return;
    }

    const body = {
        arena_id: arenaId,
        side: side
    };

    return fetch(server_address + "/wait", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
    })
    .then(res => res.json())
    .then(data => {
        return data;
    })
    .catch(console.error);
}