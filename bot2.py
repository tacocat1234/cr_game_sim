import random
import copy
import math
import statistics
import vector
from abstract_classes import Troop, Tower
from card_factory import elixir_map, get_radius, get_type
from card_factory import champions
from builders_workshop_cards import Mortar
from hog_mountain_cards import XBow
from card_factory import can_defend

'''
Improvements:
sample by area rather than by expensive troop when defending
fix overcommitment of elixir on nothingburger pushes

types:
swarm
lowattackspeed (minipekka, pekka, only non splash)
highattackspeed 
lowdps
highdps
tank
minitank
splash
control (stun/slow/freeze)
charge (inferno, prince, ramrider, things that get reset by control)
building
towertargeting
kite

subcat:
air
antiair (ground, hits air)
ground

traits:
ranged
melee
'''

#type : {counters/isnotcountered by, iscountered by}
counter_type_chart = { #defensively only
    "swarm": {"lowattackspeed": 2, "tank": 2, "minitank": 2, "control": 1.5, "splash": 0.25},
    "lowattackspeed": {"swarm": 0.25, "control": 0.5, "kite" : 0.5},
    "highattackspeed": {"swarm": 1.5, "lowattackspeed": 2, "lowdps": 2, "charge": 1.5, "tank": 0.5},
    "lowdps": {"swarm": 0.5, "tank": 0.5, "highdps": 0.5},
    "highdps": {"tank": 2, "minitank": 2, "building": 2, "charge": 2, "swarm": 0.5},
    "tank": {"building": 2, "towertargeting": 1.5, "highdps": 0.5, "swarm": 0.5, "kite" : 0.5, "control" : 2},
    "minitank": {"charge": 1.5, "towertargeting": 1.5, "highdps": 0.5, "swarm" : 0.5, "kite" : 0.5},
    "splash": {"swarm": 4, "minitank" : 0.5, "tank": 0.5},
    "control": {"charge": 2, "tank" : 2, "lowattackspeed": 2, "swarm": 0.5, "building": 0.5},
    "charge": {"lowdps": 2, "building": 1.5, "control": 0.5, "minitank": 0.5, "kite" : 0.5},
    "building": {"towertargeting": 2, "charge": 2, "highdps": 0.5, "tank": 0.5},
    "towertargeting": {"kite" : 999, "building": 2, "swarm": 0.5, "highdps" : 0.25, "minitank": 0.25, "tank" : 0.25, "charge" : 0.25},
    "kite" : {"lowattackspeed" : 2, "charge" : 2, "swarm" : 0.5, "building" : 0.5, "highdps" : 0.5}
}

troop_types = {"knight" : ["minitank"], 
    "minipekka" : ["highdps", "minitank", "lowattackspeed"], 
    "giant" : ["tank", "towertargeting", "kite"], 
    "minions" : ["swarm", "highdps"], 
    "archers" : ["swarm"], 
    "musketeer" : ["highdps"], 
    "speargoblins" : ["swarm", "lowdps"], 
    "goblins" : ["swarm", "highdps"], 
    "skeletons" : ["swarm", "lowdps"], 
    "bomber" : ["splash", "lowdps"], 
    "valkyrie" : ["splash", "minitank"],
    "barbarians" : ["swarm", "highdps"], 
    "megaminion" : ["minitank", "highdps"], 
    "battleram" : ["charge", "minitank", "towertargeting", "kite"],
    "firespirit" : ["splash", "lowdps"], 
    "electrospirit" : ["splash", "control", "lowdps"], 
    "skeletondragons" : ["splash", "lowdps"], 
    "wizard" : ["splash"],
    "bats" : ["swarm", "highdps"], 
    "hogrider" : ["towertargeting", "minitank"], 
    "flyingmachine" : ["highdps"],
    "skeletonarmy" : ["swarm", "highdps"], 
    "guards" : ["swarm"], 
    "babydragon" : ["splash"], 
    "witch" : ["swarm", "splash"], 
    "pekka" : ["highdps", "lowattackspeed", "tank"],
    "darkprince" : ["charge", "splash", "minitank"], 
    "royalhogs" : ["swarm", "towertargeting"], 
    "balloon" : ["towertargeting", "tank", "highdps"], 
    "prince" : ["lowattackspeed", "minitank", "highdps", "charge"], 
    "royalgiant" : ["towertargeting", "tank"], 
    "royalrecruits" : ["swarm", "minitank"], 
    "threemusketeers" : ["highdps"],
    "icespirit" : ["splash", "control", "lowdps"], 
    "icegolem" : ["minitank", "kite", "towertargeting", "lowdps"], 
    "battlehealer" : ["minitank"], 
    "giantskeleton" : ["tank"],
    "beserker" : ["highattackspeed"], 
    "goblingang" : ["swarm", "highdps", "highattackspeed"], 
    "dartgoblin" : ["highattackspeed"], 
    "skeletonbarrel" : ["swarm", "towertargeting", "highdps"], 
    "goblingiant" : ["towertargeting", "tank"],
    "zappies" : ["control", "swarm", "lowdps"], 
    "hunter" : ["highdps"], 
    "minionhorde" : ["swarm"], 
    "elitebarbarians" : ["minitank", "highdps"], 
    "golem" : ["tank", "towertargeting"],
    "miner" : ["minitank"], 
    "princess" : ["splash", "lowattackspeed"], 
    "electrowizard" : ["control", "lowdps"], 
    "infernodragon" : ["charge", "highdps", "lowattackspeed"], 
    "ramrider" : ["charge", "towertargeting", "minitank"], 
    "sparky" : ["lowattackspeed", "splash", "highdps"], 
    "megaknight" : ["lowattackspeed", "splash", "tank"],
    "wallbreakers" : ["towertargeting", "kite"], 
    "icewizard" : ["control", "lowdps", "splash"],  
    "royalghost" : ["splash"], 
    "firecracker" : ["splash"], 
    "phoenix" : ["highdps", "minitank"], 
    "electrodragon" : ["splash", "control", "lowdps"],
    "healspirit" : ["splash", "lowdps"], 
    "suspiciousbush" : ["towertargeting", "swarm"], 
    "bandit" : ["minitank", "charge"], 
    "magicarcher" : ["splash", "lowdps"], 
    "rascals" : ["tank", "swarm", "highdps"], 
    "bowler" : ["tank", "splash", "lowdps"], 
    "electrogiant" : ["tank", "towertargeting", "splash", "control"],
    "lavahound" : ["tank", "towertargeting"],
    "elixirgolem" : ["tank", "towertargeting"], 
    "lumberjack" : ["highattackspeed", "minitank"], 
    "nightwitch" : ["swarm", "minitank"], 
    "executioner" : ["splash"],
    "fisherman" : ["minitank", "control", "lowattackspeed"], 
    "motherwitch" : ["splash"], 
    "cannoncart" : ["highdps"],
    "goblinmachine" : ["tank", "lowattackspeed"],
    "speargoblin" : ["swarm", "lowdps"],
    "goblin" : ["swarm"],
    "fakegoblin" : ["swarm"],   
    "rascalboy" : ["tank"],
    "rascalgirl" : ["lowdps"],
    "skeleton" : ["swarm"],
    "golemite" : ["minitank", "towertargeting"],
    "elixirgolemite" : ["minitank", "towertargeting"],
    "elixirblob" : ["minitank", "towertargeting"],
    "furnace" : ["minitank", "splash"],
    "zappy" : ["control", "lowdps"],
    "cursedhog" : ["swarm"],
    "archer" : ["kite"], #not acutally but matches typewise
    "goblinbrawler" : ["minitank"],
    "bat" : ["swarm"],
    "barbarian" : ["swarm"],
    "skeletondragon" : ["splash", "lowdps"],
    "guard" : ["swarm"],
    "royalhog" : ["swarm", "minitank"],
    "royalrecruit" : ["minitank"],
    "elitebarbarian" : ["minitank", "highdps"],
    "wallbreaker" : ["towertargeting", "kite"],
    "rebornphoenix" : ["minitank"],
    "bushgoblin" : ["highdps", "towertargeting", "swarm"],
    "lavapup" : ["swarm", "lowdps"],
    "cartcannon" : ["highdps"],
    "guardienne" : ["minitank"],
    "skeletonbarreldeathbarrel" : ["swarm", "splash"],
    "goblinhut" : ["building", "swarm"], 
    "goblincage" : ["building", "minitank"], 
    "tombstone" : ["building", "swarm"],
    "cannon" : ["building"],
    "bombtower" : ["building", "splah"], 
    "infernotower" : ["building", "charge"],
    "mortar" : ["building", "splash", "lowattackspeed"],
    "barbarianhut" : ["building", "swarm"],
    "tesla" : ["building"], 
    "xbow" : ["building", "highattackspeed"],
    "elixircollector" : ["building", "tank", "towertargeting"],
    "barbarianbarrel" : ["splash", "minitank"],
    "royaldelivery" : ["splash", "minitank"],
    "archerqueen" : ["highdps", "highattackspeed"],
    "skeletonking" : ["splash", "swarm"],
    "bossbandit" : ["highdps", "minitank"],
    "littleprince" : ["charge"],
    "goblinstein" : ["control", "lowdps"],
    "goblinsteinmonster" : ["towertargeting", "tank"],
    "goldenknight" : ["highattackspeed", "minitank"],
    "mightyminer" : ["charge", "minitank"]
    }

troop_is_air = {"knight" : "ground", 
    "minipekka" : "ground",
    "giant" : "ground", 
    "minions" : "air", 
    "archers" : "antiair", 
    "musketeer" : "antiair", 
    "speargoblins" : "antiair", 
    "goblins" : "ground", 
    "skeletons" : "ground",
    "bomber" : "ground",
    "valkyrie" : "ground",
    "barbarians" : "ground",
    "megaminion" : "air",
    "battleram" : "ground",
    "firespirit" : "antiair",
    "electrospirit" : "antiair",
    "skeletondragons" : "air",
    "wizard" : "antiair",
    "bats" : "air", 
    "hogrider" : "ground",
    "flyingmachine" : "air",
    "skeletonarmy" : "ground",
    "guards" : "ground",
    "babydragon" : "air", 
    "witch" : "antiair", 
    "pekka" : "ground",
    "darkprince" : "ground",
    "royalhogs" : "ground",
    "balloon" : "air",
    "prince" : "ground",
    "royalgiant" : "ground",
    "royalrecruits" : "ground",
    "threemusketeers" : "antiair",
    "icespirit" : "antiair",
    "icegolem" : "ground",
    "battlehealer" : "ground",
    "giantskeleton" : "ground",
    "beserker" : "ground",
    "goblingang" : "antiair",
    "dartgoblin" : "antiair",
    "skeletonbarrel" : "air",
    "goblingiant" : "ground",
    "zappies" : "antiair",
    "furnace" : "antiair",
    "hunter" : "antiair", 
    "minionhorde" : "air", 
    "elitebarbarians" : "ground",
    "golem" : "ground",
    "miner" : "ground",
    "princess" : "antiair", 
    "electrowizard" : "antiair", 
    "infernodragon" : "air",
    "ramrider" : "ground",
    "sparky" : "ground",
    "megaknight" : "ground",
    "wallbreakers" : "ground",
    "icewizard" : "antiair",
    "royalghost" : "ground",
    "firecracker" : "antiair", 
    "phoenix" : "air", 
    "electrodragon" : "air",
    "healspirit" : "antiair",
    "suspiciousbush" : "ground",
    "bandit" : "ground",
    "magicarcher" : "antiair",
    "rascals" : "antiair",
    "bowler" : "ground",
    "electrogiant" : "ground",
    "lavahound" : "air",
    "elixirgolem" : "ground",
    "lumberjack" : "ground",
    "nightwitch" : "antiair",
    "executioner" : "antiair",
    "fisherman" : "ground",
    "motherwitch" : "antiair",
    "cannoncart" : "ground",
    "speargoblin" : "antiair",
    "goblin" : "ground",
    "fakegoblin" : "ground",
    "rascalboy" : "ground",
    "rascalgirl" : "antiair",
    "skeleton" : "ground",
    "golemite" : "ground",
    "elixirgolemite" : "ground",
    "elixirblob" : "ground",
    "zappy" : "antiair",
    "cursedhog" : "ground",
    "archer" : "antiair",
    "goblinbrawler" : "ground",
    "bat" : "air",
    "barbarian" : "ground",
    "skeletondragon" : "air",
    "guard" : "ground",
    "royalhog" : "ground",
    "royalrecruit" : "ground",
    "elitebarbarian" : "ground",
    "wallbreaker" : "ground",
    "wallbreakerrunner" : "ground",
    "rebornphoenix" : "air",
    "bushgoblin" : "ground",
    "lavapup" : "air",
    "cartcannon" : "ground",
    "goblinmachine" : "ground",
    "guardienne" : "ground", #littleprince summon thing
    "skeletonbarreldeathbarrel" : "ground",
    "archerqueen" : "antiair",
    "skeletonking" : "ground",
    "bossbandit" : "ground",
    "littleprince" : "antiair",
    "goblinstein" : "antiair",
    "goldenknight" : "ground",
    "mightyminer" : "ground",
    "goblinhut" : "antiair",
    "goblincage" : "antiair", 
    "tombstone" : "ground",
    "cannon" : "ground",
    "bombtower" : "ground", 
    "infernotower" : "antiair",
    "mortar" : "ground",
    "barbarianhut" : "ground",
    "tesla" : "ground", 
    "xbow" : "ground",
    "elixircollector" : "antiair"
    }

troop_attack_range = {
    "knight": "short",
    "minipekka": "short",
    "giant": "short",
    "minions": "short",
    "archers": "long",
    "musketeer": "long",
    "speargoblins": "long",
    "goblins": "short",
    "skeletons": "short",
    "bomber": "medium",
    "valkyrie": "short",
    "barbarians": "short",
    "megaminion": "short",
    "battleram": "short",
    "firespirit": "long",
    "electrospirit": "long",
    "skeletondragons": "medium",
    "wizard": "medium",
    "bats": "short",
    "hogrider": "short",
    "flyingmachine": "long",
    "skeletonarmy": "short",
    "guards": "short",
    "babydragon": "medium",
    "witch": "long",
    "pekka": "short",
    "darkprince": "short",
    "royalhogs": "short",
    "balloon": "short",
    "prince": "short",
    "royalgiant": "long",
    "royalrecruits": "short",
    "threemusketeers": "long",
    "icespirit": "long",
    "icegolem": "short",
    "battlehealer": "short",
    "giantskeleton": "short",
    "beserker": "short",
    "goblingang": "medium",
    "dartgoblin": "long",
    "skeletonbarrel": "short",
    "goblingiant": "short",
    "furnace" : "medium",
    "zappies": "long",
    "hunter": "short",
    "minionhorde": "short",
    "elitebarbarians": "short",
    "golem": "short",
    "miner": "short",
    "princess": "long",
    "electrowizard": "medium",
    "infernodragon": "medium",
    "ramrider": "short",
    "sparky": "long",
    "megaknight": "short",
    "wallbreakers": "short",
    "icewizard": "long",
    "royalghost": "short",
    "firecracker": "long",
    "phoenix": "short",
    "electrodragon": "medium",
    "healspirit": "long",
    "suspiciousbush": "short",
    "bandit": "long",
    "magicarcher": "long",
    "rascals": "long",
    "bowler": "medium",
    "electrogiant": "short",
    "lavahound": "medium",
    "elixirgolem": "short",
    "lumberjack": "short",
    "nightwitch": "medium",
    "executioner": "medium",
    "fisherman": "long",
    "motherwitch": "long",
    "cannoncart": "long",
    "speargoblin": "long",
    "goblin": "short",
    "rascalboy": "short",
    "rascalgirl": "long",
    "skeleton": "short",
    "golemite": "short",
    "elixirgolemite": "short",
    "elixirblob": "short",
    "zappy": "long",
    "cursedhog": "short",
    "archer": "long",
    "goblinbrawler": "short",
    "bat": "short",
    "barbarian": "short",
    "skeletondragon": "medium",
    "guard": "short",
    "royalhog": "short",
    "royalrecruit": "short",
    "elitebarbarian": "short",
    "wallbreaker": "short",
    "wallbreakerrunner": "short",
    "rebornphoenix": "short",
    "bushgoblin": "short",
    "lavapup": "medium",
    "cartcannon": "long",
    "goblinmachine" : "medium",
    "guardienne": "short",
    "skeletonbarreldeathbarrel": "short",
    "archerqueen" : "long",
    "skeletonking" : "short",
    "bossbandit" : "long",
    "littleprince" : "long",
    "goblinstein" : "medium",
    "goldenknight" : "short",
    "mightyminer" : "short"
}


def calculate_effectiveness(offense, defense):

    o_g = troop_is_air.get(offense, "ground")
    d_g = troop_is_air.get(defense, "ground")
    if o_g == "air" and d_g == "ground" and not get_type(defense) == "building":
        return 0

    if offense not in troop_types:
        return 1
    else:
        weak = {}
        for t_type in troop_types[offense]: #for each type the offense is
            for d_type, effectiveness in counter_type_chart[t_type].items(): #for each type matchup of the offesnive type
                if d_type in weak: #record that typematchup in weak
                    weak[d_type] *= effectiveness
                else:
                    weak[d_type] = effectiveness
        out = 1
        for t, eff in weak.items(): #example: "minitank" : 1/2, "swarm" : 16 -> means gets countered by minitank and not swarm
            if t in troop_types.get(defense, []):
                out /= eff

        return out #higher good




single_elixir_map = {
    "speargoblin" : 2/3,
    "goblin" : 1/2,
    "fakegoblin" : 1/3,
    "rascalboy" : 3,
    "rascalgirl" : 1,
    "skeleton" : 2/5,
    "golemite" : 3,
    "elixirgolemite" : 3,
    "elixirblob" : 1,
    "zappy" : 4/3,
    "cursedhog" : 2,
    "archer" : 3/2,
    "goblinbrawler" : 3,
    "bat" : 2/5,
    "barbarian" : 1,
    "skeletondragon" : 2,
    "guard" : 1,
    "royalhog" : 5/4,
    "royalrecruit" : 7/6,
    "elitebarbarian" : 3,
    "wallbreaker" : 1,
    "rebornphoenix" : 3,
    "bushgoblin" : 1,
    "lavapup" : 5/6,
    "cartcannon" : 3,
    "guardienne" : 3,
    "skeletonbarreldeathbarrel" : 3,
    "goblinsteinmonster" : 3
}

def can_attack(name):
    return not (name in ["icegolem", "icewizard", "guards", "electrowizard", "skeletons"])

def get_elixir(name):
    mod = 1
    if name.startswith("evolution"):
        name = name[9:]
        mod = 4/3
    if name == "elixirgolem":
        mod = 2
    if name in elixir_map:
        return elixir_map[name] * mod
    elif name in single_elixir_map:
        return single_elixir_map[name] * mod
    else:
        return 0


spell_damage = {
    "clone":0,
    "goblinbarrel":0,
    "graveyard":0,
    "freeze":115,
    "tornado":168,
    "goblincurse":183,
    "zap":192,
    "giantsnowball":192,
    "rage":192,
    "barbarianbarrel":241,
    "earthquake":246,
    "log":290,
    "vines":330,
    "void":366,
    "arrows":366,
    "royaldelivery":437,
    "fireball":689,
    "poison":728,
    "lightning":1056,
    "rocket":1484,
    
}

def cycle(hand, index, queue, champion_index):
    if hand[index] != champion_index:
        queue.append(hand[index])
    hand[index] = queue.pop(0)

def get_spell_damage(spell, level):
    return spell_damage[spell] * pow(1.1, level - 11)

class Bot:
    def __init__(self, cards, tower_type = "princesstower"):
        self.cards = cards
        self.tower_type = tower_type
        random.shuffle(self.cards)

        self.hand = [0, 1, 2, 3]
        self.queue = [4, 5, 6, 7]
        self.goal = "wait"

        self.champion_index = None
        i = 0
        for each in cards:
            if each.name in champions:
                self.champion_index = i
            i += 1

    def process_champion(self, champion, arena):
        if champion is not None and champion.cur_hp > 1/8 * champion.hit_points and champion.ability_cooldown_timer <= 0:
            n = champion.__class__.__name__.lower()
            if n == "archerqueen" and champion.target is not None:
                champion.activate_ability(arena)
            elif n == "skeletonking" and (champion.position.y < -4 or champion.amount > 13):
                champion.activate_ability(arena)
            elif n == "goldenknight" and champion.cur_hp > 1/4 * champion.hit_points:
                champion.activate_ability(arena)
            elif n == "mightyminer" and champion.target is not None and champion.target.hit_points <= champion.hit_damage * 4 and vector.distance(champion.target.position, champion.position) <= champion.hit_range + champion.collision_radius + champion.target.collision_radius:
                champion.activate_ability(arena)    
            elif n == "bossbandit" and champion.ability_count > 0 and not (champion.dashing or champion.should_dash) and champion.target is not None and champion.target.cur_hp > champion.hit_damage * 2.1 and vector.distance(champion.target.position, champion.position) <= champion.hit_range + champion.collision_radius + champion.target.collision_radius:
                champion.activate_ability(arena)
            elif n == "littleprince" and (champion.position.y < 1 and (champion.position.x > 3 or champion.position.x < -3)) or (champion.target is not None and ((champion.target.target is champion and champion.target.ground) or champion.cur_hp < 1/2 * champion.hit_points)):
                champion.activate_ability(arena)
            elif n == "goblinstein" and ("swarm" in troop_types.get(champion.target.__class__.__name__.lower(), [])) or isinstance(champion.target, Tower):
                champion.activate_ability(arena)

    def tick(self, elixir, things = None, pocket = "none"):
        s = []
        for each in self.hand:
            n = self.cards[each].name
            if n == "log" or n == "barbarianbarrel" or self.cards[each].type == "spell" and n != "graveyard" and n != "clone" and n != "goblinbarrel" and self.cards[each].elixir_cost <= elixir:
                s.append([get_spell_damage(n, self.cards[each].level), get_radius(n), self.cards[each].elixir_cost, each])

        for each in s: #18 long x 32 tall grid, -9, 9 x -16, 16
            #[xbegin, xend, ybegin, yend, [all]]
            side_len = each[1] * 2
            squares = [[[x_i * side_len - 9, min(((x_i + 1) * side_len), 18) - 9, y_i * side_len - 16, min(((y_i + 1) * side_len), 32) - 16, []] for x_i in range(math.ceil(18/side_len))] for y_i in range(math.ceil(32/side_len))]
            for thing in things:
                if thing.side:
                    x = thing.position.x
                    y = thing.position.y

                    # Compute indices directly
                    x_index = int((x + 9) // side_len)
                    y_index = int((y + 16) // side_len)

                    # Clamp indices in case they are on the boundary
                    x_index = min(x_index, len(squares[0]) - 1)
                    y_index = min(y_index, len(squares) - 1)

                    # Append to the correct square
                    squares[y_index][x_index][4].append(thing)

            target = None
            most = 0
            for row in squares:
                for square in row:
                    valid = True
                    enemies = [troop for troop in square[4] if isinstance(troop, Troop)]

                    if len(enemies) == 0:
                        valid = False
                    else:
                        average_position = vector.Vector(0,0)
                        for enem in enemies:
                            average_position.add(enem.position)
                        average_position.scale(1/len(enemies))

                        if vector.distance(average_position, vector.Vector(0, -13)) <= each[1] + 2:
                            valid = False
                        else:
                            if len(enemies) < 2 and True in [troop.cur_hp < troop.hit_points * 0.1 for troop in enemies]:
                                valid = False
                            median_hp = statistics.median([troop.cur_hp for troop in enemies])
                            e_total = sum([get_elixir(enem.__class__.__name__.lower()) for enem in enemies])
                            
                            if median_hp > 1.1 * each[0] or e_total < each[2] + 1:
                                valid = False

                    if valid and len(enemies) > most:
                        most = len(enemies)
                        target = average_position

            if target is not None:
                ind = each[3]
                card = self.cards[ind]
                pos = target
                if card.name == "barbarianbarrel":
                    if pos.y < -4.7:
                        return None
                    elif pos.y < 0:
                        pos.y = 1
                elif card.name == "log":
                    if pos.y < -10.1:
                        return None
                    elif pos.y < 0:
                        pos.y = 1
                elif card.name == "royaldelivery":
                    pos = target.added(vector.Vector(0, 2.0))
                    if pos.y <= 0:
                        return None
                else:
                    pos = target.added(vector.Vector(0, 1.5))
                cycle(self.hand, self.hand.index(ind), self.queue, self.champion_index)
                return card, pos

        goal = "wait" if elixir < 7 else "place"
        threat = None
        swarm_threats = {}
        threat_level = 0

        main = None
        main_threat_level = 0
        if things:
            attack_investment = 0
            defense_investment_right = 0
            defense_investment_left = 0
            for each in things:
                e = get_elixir(each.__class__.__name__.lower())
                if not each.side: #bot's
                    if each.position.y < 3 and (isinstance(each, XBow) or isinstance(each, Mortar)):
                        main_threat_level = 99
                        attack_investment += 99
                        main = each
                    if each.position.y > 0: #defending
                        if each.position.x > 0:
                            defense_investment_right += e
                        else:
                            defense_investment_left += e
                    else: #attacking
                        if pocket == "all" or pocket == "none" or ("pocket" == "left" and each.position.x > -1) or ("pocket" == "right" and each.position.x < 1):
                            attack_investment += e
                            if e > main_threat_level:
                                main_threat_level = e
                                main = each
                else:
                    if each.position.y > -3 and (isinstance(each, XBow) or isinstance(each, Mortar)):
                        threat_level = 99
                        if each.position.x > 0:
                            defense_investment_right -= 99
                        else:
                            defense_investment_left -= 99
                        threat = each
                    elif each.position.y >= -1.5 and threat_level < 5 and each.__class__.__name__.lower() == "princess":
                        threat_level = 5
                        threat = each
                        if each.position.x > 0:
                            defense_investment_right -= 5
                        else:
                            defense_investment_left -= 5
                        
                    if each.position.y > 0: #attacking

                        if each.position.y > 9.5 - each.hit_range:
                            e *= 3/2
                        
                        if each.position.x > 0:
                            defense_investment_right -= e
                        else:
                            defense_investment_left -= e

                        each_n = each.__class__.__name__.lower()
                        if "swarm" in troop_types.get(each_n, []):
                            key = str(math.floor(each.position.x/4)) + "|" + str(math.floor(each.position.y/4))
                            section = swarm_threats.get(key, [None, 0, 0])
                            if section[0] is None or each.position.y > section[0].position.y: #greater than because that would mean closer to tower
                                swarm_threats[key] = [each, section[1] + e, section[2] + 1]
                            else:
                                swarm_threats[key] = [section[0], section[1] + e, section[2] + 1]
                        
                        if e > threat_level:
                            threat_level = e
                            threat = each
                    if each.position.y < 0 or each.position.y > 8: #defending or dangerous
                        attack_investment -= e

            for value in swarm_threats.values():
                s_mult = 1 if value[2] <= 3 else (1.2 if value[2] <= 7 else 1.5)
                if self.tower_type == "cannoneer":
                    s_mult *= 2 
                if value[1] * s_mult > threat_level:
                    threat = value[0]
                    threat_level = value[1] * s_mult

            if defense_investment_left < -2 or defense_investment_right < -2: #3+ more elixir of attackers than defenders
                goal = "defend"
            elif attack_investment >= 0: # if you have greater or equal amounts of offensive troop
                if attack_investment < 5: #push isnt strong enough
                    counter = 0
                    for each in things:
                        if each.side and can_defend(each.__class__.__name__.lower()) and (main is None or ((each.position.x < 0 and main.position.x > 0) or (each.position.x > 0 and main.position.x < 0))):
                            counter += get_elixir(each.__class__.__name__.lower())
                    if counter <= 7: #tune val for aggresivness, greater val is greater agressiveness
                        goal = "attack"
                else: #push is strong enough, dont worry about defense
                    goal = "attack"
        
        if goal == "attack" and elixir > 9: #if attackign and a lot of elixir
            valid_attack = False
            for i in range(4):
                card = self.cards[self.hand[i]]
                if not (card.elixir_cost > elixir or (not can_attack(card.name)) or card.name == "log" or card.name == "barbarianbarrel" or (card.type == "spell" and card.name != "clone" and card.name != "rage" and card.name != "graveyard" and card.name != "goblinbarrel") or (card.type == "building" and card.name != "goblindrill")):
                    valid_attack = True
                    break
            if not valid_attack: #if no ways to attack with hand
                goal == "place" #cycle

        self.goal = goal

        if goal == "wait":
            if random.random() < 1/300: #about once every 5 seconds
                for index in self.hand:
                    if self.cards[index].name == "goblinbarrel" or self.cards[index].name == "goblindrill" or self.cards[index].name == "miner":
                        pos = None
                        if pocket == "none":
                            pos = vector.Vector((-5.5 if random.random() > 0.5 else 5.5) + random.random() - 0.5, -9.5 + random.random() - 0.5)
                        elif pocket == "left":
                            pos = vector.Vector(5.5 + random.random() - 0.5, -9.5 + random.random() - 0.5)
                        elif pocket == "right":
                            pos = vector.Vector(-5.5 + random.random() - 0.5, -9.5 + random.random() - 0.5)
                        elif pocket == "all":
                            pos = vector.Vector(random.random() - 0.5, -13 + random.random() - 0.5)

                        card = self.cards[index]
                        cycle(self.hand, self.hand.index(index), self.queue, self.champion_index)
                        return card, pos

            if random.random() < 1/1600:
                pos = vector.Vector(random.randint(-9, 8) + 0.5, random.randint(1, 15) + 0.5)
                l = [0, 1, 2, 3]
                i = random.choice(l)
                card = self.cards[self.hand[i]]
                while  card.elixir_cost > elixir or card.name == "log" or card.name == "barbarianbarrel" or card.type == "spell" or (card.type == "building" and (card.name != "mortar" and card.name != "xbow" and card.name != "goblindrill")) and l:
                    l.remove(i)
                    if not l: #if all spells or buildings
                        card = None
                        return None
                    i = random.choice(l)
                    card = self.cards[self.hand[i]]

                if card is not None:
                    cycle(self.hand, i, self.queue, self.champion_index)
                    if card.name == "mortar" or card.name == "xbow":
                        pos = vector.Vector(5.5 if random.random() < 0.5 else -5.5, 2)
                    return card, pos

            return None
        elif goal == "place":
            card = None
            i = -1
            if random.random() > 0.7: #30% low elixir, 70% high elixir
               minimum = 99
               for ind in self.hand:
                   c = self.cards[ind]
                   if c.elixir_cost < minimum and c.elixir_cost <= elixir and c.type != "spell":
                       card = c
                       minimum = c.elixir_cost
                       i = ind
            else:
               maximum = 0
               for ind in self.hand:
                   c = self.cards[ind]
                   if c.elixir_cost > maximum and c.elixir_cost <= elixir and c.type != "spell":
                       card = c
                       maximum = c.elixir_cost
                       i = ind

            if i > -1:
                if card.name == "mortar" or card.name == "xbow":
                    pos = vector.Vector(5.5 if random.random() < 0.5 else -5.5, 2)
                    cycle(self.hand, self.hand.index(i), self.queue, self.champion_index)
                    return card, pos
                elif card.type == "building":
                    pos = vector.Vector(random.randint(-3, 3), random.randint(2, 7))
                    cycle(self.hand, self.hand.index(i), self.queue, self.champion_index)
                    return card, pos
                
                elif card.name == "goblinbarrel" or card.name == "goblindrill":
                    pos = None
                    if pocket == "none":
                        pos = vector.Vector((-5.5 if random.random() > 0.5 else 5.5) + random.random() - 0.5, -9.5 + random.random() - 0.5)
                    elif pocket == "left":
                        pos = vector.Vector(5.5 + random.random() - 0.5, -9.5 + random.random() - 0.5)
                    elif pocket == "right":
                        pos = vector.Vector(-5.5 + random.random() - 0.5, -9.5 + random.random() - 0.5)
                    elif pocket == "all":
                        pos = vector.Vector(random.random() - 0.5, -13 + random.random() - 0.5)

                    cycle(self.hand, self.hand.index(i), self.queue, self.champion_index)
                    return card, pos

                if card.elixir_cost > 7 or card.elixir_cost <= 5:
                    cycle(self.hand, self.hand.index(i), self.queue, self.champion_index)
                    return card, vector.Vector(-0.5 + random.random(), 15.5) #place in back
                else:
                    p = random.randint(0, 2)
                    cycle(self.hand, self.hand.index(i), self.queue, self.champion_index)
                    if p == 0:
                        pos = None
                            
                        if pocket == "left":
                            pos = vector.Vector(0.5, 15.5)
                        elif pocket == "right":
                            pos = vector.Vector(-0.5, 15.5)
                        else:
                            pos = vector.Vector(-0.5 + random.random(), 15.5)
                        return card, pos #place in back
                    if p == 1:
                        if pocket == "all" or pocket == "left":
                            return card, vector.Vector(-0.5, -4.5) #place in pocket
                        else:
                            return card, vector.Vector(-5.5, 1.5) #place on bridge
                    else:
                        if pocket == "all" or pocket == "right":
                            return card, vector.Vector(0.5, -4.5) #place in pocket
                        else:
                            return card, vector.Vector(5.5, 1.5) #place on bridge
            else:
                return None
        elif goal == "defend":
            best = None
            card = None
            best_effectiveness = 0
            i = None
            for ind in range(4):
                card = self.cards[self.hand[ind]]
                if can_defend(card.name) and card.elixir_cost <= elixir:
                    if best_effectiveness < 0.9 and card.type == "spell" and card.name != "barbarianbarrel" and card.name != "royaldelivery":
                        d = get_spell_damage(card.name, card.level)
                        if d > threat.cur_hp/2 and d > threat.hit_points/3:
                            best_effectiveness = 0.9
                            best = card
                            i = ind
                    else:
                        defense_effectiveness = calculate_effectiveness(threat.__class__.__name__.lower(), card.name)
                        if defense_effectiveness > best_effectiveness:
                            best_effectiveness = defense_effectiveness
                            best = card
                            i = ind
            
            if best_effectiveness > 0:
                card = best
            else:
                return None

            pos = None
            if card.type == "spell":
                if card.name == "barbarianbarrel":
                    if threat.position.y < -4.7:
                        return None
                    elif threat.position.y < 0:
                        pos = vector.Vector(threat.position.x, 1)
                    else:
                        pos = threat.position.added(vector.Vector(0, 1.5))
                elif card.name == "log":
                    if threat.position.y < -10.1:
                        return None
                    elif threat.position.y < 0:
                        pos = vector.Vector(threat.position.x, 1)
                    else:
                        pos = threat.position.added(vector.Vector(0, 1.5))
                elif card.name == "royaldelivery":
                    pos = threat.position.added(vector.Vector(0, 2.0))
                    if pos.y <= 0:
                        return None
                else:
                    pos = threat.position.added(vector.Vector(0, 1.5))
                cycle(self.hand, i, self.queue, self.champion_index)
            elif card.type == "building":
                cycle(self.hand, i, self.queue, self.champion_index)
                if threat.position.y < 5:
                    pos = vector.Vector(0.5 + random.randint(0, 1) if threat.position.x > 0 else -0.5 - random.randint(0, 1), round(threat.position.y + 3) + 0.5)
                elif threat.position.y < 9:
                    pos = vector.Vector(1.5 + random.randint(0, 2) if threat.position.x > 0 else -1.5 - random.randint(0, 2), round(threat.position.y + 2) + 0.5)
                else:
                    pos = threat.position.added(vector.Vector(random.randint(-2, 2), random.randint(1, 3)))
                in_p = (pocket == "all" or (pos.x < 0 and pocket == "left") or (pos.x >= 0 and pocket == "right"))
                if in_p and pos.y < -5:
                    pos.y = -5
                elif not in_p and pos.y < 1:
                    pos.y = 1
            elif card.name == "icegolem" or card.name == "wallbreakers":
                if isinstance(threat.target, Tower):
                    return None
                if threat.position.y < 5 and (threat.position.x < 5 and threat.position.x > -5):
                    cycle(self.hand, i, self.queue, self.champion_index)
                    pos = vector.Vector(-0.5 if threat.position.x > 0 else 0.5, round(threat.position.y + 1) + 0.5) #kite
                    in_p = (pocket == "all" or (pos.x < 0 and pocket == "left") or (pos.x >= 0 and pocket == "right"))
                    if in_p and pos.y < -5:
                        pos.y = -5
                    elif not in_p and pos.y < 1:
                        pos.y = 1
                elif threat.position.y < 8:
                    cycle(self.hand, i, self.queue, self.champion_index)
                    pos = vector.Vector(threat.position.x, threat.position.y - 2)
                    in_p = (pocket == "all" or (pos.x < 0 and pocket == "left") or (pos.x >= 0 and pocket == "right"))
                    if in_p and pos.y < -5:
                        pos.y = -5
                    elif not in_p and pos.y < 1:
                        pos.y = 1
                else:
                    return None
            elif card.name == "suspiciousbush":
                return None
            elif card.name == "tornado":
                cycle(self.hand, i, self.queue, self.champion_index)
                pos = threat.position.added(vector.Vector(-5, 1)) if threat.position.x > 0 else threat.position.added(vector.Vector(5, 1))
                if threat.position.x < 5 and threat.position.x > -5:
                    pos.x = 0
                return card, pos
            else:
                cycle(self.hand, i, self.queue, self.champion_index)
                pos = None
                if card.name != "miner":
                    r = troop_attack_range.get(card.name, "short")
                    y_range = random.randint(0, 2) if r == "short" else (random.randint(3, 5) if r == "medium" else random.randint(5, 6))
                    pos = threat.position.added(vector.Vector(random.randint(-2, 2), y_range))
                    in_p = (pocket == "all" or (pos.x < 0 and pocket == "left") or (pos.x >= 0 and pocket == "right"))
                    if in_p and pos.y < -5:
                        pos.y = -5
                    elif not in_p and pos.y < 1:
                        pos.y = 1
                else:
                    pos = threat.position.added(vector.Vector(0, -3))
                return card, pos

            return card, pos
        else:
            l = [0, 1, 2, 3]
            i = random.choice(l)
            card = self.cards[self.hand[i]]
            while card.elixir_cost > elixir or (not can_attack(card.name)) or card.name == "log" or card.name == "barbarianbarrel" or (card.type == "spell" and card.name != "clone" and card.name != "rage" and card.name != "graveyard" and card.name != "goblinbarrel") or (card.type == "building" and card.name != "goblindrill") and l:
                l.remove(i)
                if not l: #if all spells or buildings or too expesnive
                    card = None
                    return None
                i = random.choice(l)
                card = self.cards[self.hand[i]]

            if card is not None:
                pos = None

                base_pos = None
                if main is None:
                    if pocket == "none":
                        base_pos = vector.Vector(random.randint(-9, 8) + 0.5, random.randint(1, 9) + 0.5)
                    elif pocket == "all":
                        base_pos = vector.Vector(random.randint(-9, 8) + 0.5, random.randint(-5, 9) + 0.5)
                    elif pocket == "left":
                        base_pos = vector.Vector(random.randint(0, 8) + 0.5, random.randint(1, 9) + 0.5)
                    else:
                        base_pos = vector.Vector(random.randint(-9, -1) + 0.5, random.randint(1, 9) + 0.5)
                else:
                    base_pos = main.position

                if card.name == "clone" or card.name == "rage" and isinstance(main, Troop):
                    cycle(self.hand, i, self.queue, self.champion_index)
                    pos = base_pos.added(vector.Vector(0, 2))
                    return card, pos
                elif card.name == "goblinbarrel" or card.name == "goblindrill":
                    cycle(self.hand, i, self.queue, self.champion_index)
                    pos = None
                    if pocket == "none":
                        pos = vector.Vector((-5.5 if random.random() > 0.5 else 5.5) + random.random() - 0.5, -9.5 + random.random() - 0.5)
                    elif pocket == "left":
                        pos = vector.Vector(5.5 + random.random() - 0.5, -9.5 + random.random() - 0.5)
                    elif pocket == "right":
                        pos = vector.Vector(-5.5 + random.random() - 0.5, -9.5 + random.random() - 0.5)
                    elif pocket == "all":
                        pos = vector.Vector(random.random() - 0.5, -13 + random.random() - 0.5)
                    return card, pos
                elif card.name == "graveyard":
                    pos = None
                    if main is None:
                        return None
                    elif main.position.x > 0:
                        if pocket == "none":
                            cycle(self.hand, i, self.queue, self.champion_index)
                            pos = vector.Vector(8.5, -9.5)
                        elif pocket == "left":
                            cycle(self.hand, i, self.queue, self.champion_index)
                            pos = vector.Vector(8.5, -9.5)
                        elif pocket == "right":
                            return None
                        elif pocket == "all":
                            return None
                    else:
                        if pocket == "none":
                            cycle(self.hand, i, self.queue, self.champion_index)
                            pos = vector.Vector(-8.5, -9.5)
                        elif pocket == "left":
                            return None
                        elif pocket == "right":
                            cycle(self.hand, i, self.queue, self.champion_index)
                            pos = vector.Vector(-8.5, -9.5)
                        elif pocket == "all":
                            return None
                    return card, pos
                elif card.name != "miner":
                    cycle(self.hand, i, self.queue, self.champion_index)
                    pos = base_pos.added(vector.Vector(random.randint(-2, 2), random.randint(0, 4)))
                    in_p = (pocket == "all" or (pos.x < 0 and pocket == "left") or (pos.x >= 0 and pocket == "right"))
                    if in_p and pos.y < -5:
                        pos.y = -5
                    elif not in_p and pos.y < 1:
                        pos.y = 1
                    if pos.y > 15.5:
                        pos.y = 15.5
                else:
                    cycle(self.hand, i, self.queue, self.champion_index)
                    pos = base_pos.added(vector.Vector(0, -3))

                return card, pos
            else:
                return None
            
            
