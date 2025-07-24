import math
import vector
import towers
import training_camp_cards
import goblin_stadium_cards
import bone_pit_cards
import barbarian_bowl_cards
import spell_valley_cards
import builders_workshop_cards
import pekkas_playhouse_cards
import royal_arena_cards
import frozen_peak_cards
import jungle_arena_cards
import hog_mountain_cards
import electro_valley_cards
import spooky_town_cards
import rascals_hideout_cards
import serenity_peak_cards
import miners_mine_cards

import training_camp_evos
import goblin_stadium_evos
import bone_pit_evos
import barbarian_bowl_evos
import spell_valley_evos
import builders_workshop_evos
import pekkas_playhouse_evos
import royal_arena_evos
import frozen_peak_evos
import jungle_arena_evos
import hog_mountain_evos
import electro_valley_evos
import spooky_town_evos
import serenity_peak_evos
import champion_cards
import copy
import random

def can_evo(n):
    return (n == "knight" or n == "archers" or n == "musketeer" or 
            n == "goblincage" or 
            n == "skeletons" or n == "bomber" or n == "valkyrie" or
            n == "barbarians" or n == "battleram" or n == "cannon" or
            n == "wizard" or
            n == "bats" or n == "zap" or n == "mortar" or
            n == "pekka" or n == "goblinbarrel" or 
            n == "royalgiant" or n == "royalrecruits" or
            n == "icespirit" or n == "giantsnowball" or
            n == "dartgoblin" or n == "goblingiant" or n == "skeletonbarrel" or
            n == "hunter" or n == "tesla" or
            n == "infernodragon" or n == "megaknight" or 
            n == "wallbreakers" or n == "firecracker" or n == "electrodragon" or
            n == "goblindrill" or n == "lumberjack" or n == "executioner")

troops = ["knight", "minipekka", "giant", "minions", "archers", "musketeer", 
          "speargoblins", "goblins", 
          "skeletons", "bomber", "valkyrie",
          "barbarians", "megaminion", "battleram",
          "firespirit", "electrospirit", "skeletondragons", "wizard",
          "bats", "hogrider", "flyingmachine",
          "skeletonarmy", "guards", "babydragon", "witch", "pekka",
          "darkprince", "royalhogs", "balloon", "prince", "royalgiant", "royalrecruits", "threemusketeers",
          "icespirit", "icegolem", "battlehealer", "giantskeleton",
          "barbarianbarrel", "beserker", "goblingang", "dartgoblin", "skeletonbarrel", "goblingiant",
          "zappies", "hunter", "minionhorde", "elitebarbarians", "golem",
          "log", "miner", "princess", "electrowizard", "infernodragon", "ramrider", "sparky", "megaknight",
          "wallbreakers", "icewizard", "royalghost", "firecracker", "phoenix", "electrodragon",
          "healspirit", "suspiciousbush", "bandit", "magicarcher", "rascals", "bowler", "electrogiant", "lavahound",
          "elixirgolem", "goblindrill", "lumberjack", "nightwitch", "executioner",
          "fisherman", "motherwitch", "cannoncart"]

spells = ["fireball", "arrows",
          "zap", "rocket",
          "goblinbarrel",
          "giantsnowball", "freeze", "lightning",
          "poison",
          "earthquake", "graveyard",
          "rage", "goblincurse", "royaldelivery",
          "clone", "void", "tornado"]

buildings = ["goblinhut", "goblincage", 
             "tombstone",
             "cannon",
             "bombtower", "infernotower",
             "mortar",
             "barbarianhut",
             "furnace", "tesla", "xbow",
             "elixircollector"]

champions = ["archerqueen", "skeletonking", "goldenknight"]

#total 127
#print(len(troops) + len(spells) + len(buildings))

effect_radius = {
    "arrows" : 4,
    "fireball" : 2.5,
    "cannon" : 5.5,
    "bombtower" : 6,
    "infernotower" : 5.5,
    "mortar" : [11.5, 3.5],
    "zap" : 2.5,
    "rocket" : 2,
    "goblinbarrel" : 1.5,
    "giantsnowball" : 2.5,
    "freeze" : 3,
    "lightning" : 3.5,
    "poison" : 3.5,
    "tesla" : 5.5,
    "xbow" : 11.5,
    "electrowizard" : 2.5,
    "megaknight" : 2.2,
    "icewizard" : 3,
    "earthquake" : 3.5,
    "graveyard" : 4,
    "rage" : 3,
    "goblincurse" : 3,
    "royaldelivery" : 3,
    "clone" : 3,
    "void" : 2.5,
    "tornado" : 5.5,
    "log" : 10.1,
    "barbarianbarrel": 4.6
}

def get_radius(name):
    if name in effect_radius:
        return effect_radius[name]
    else:
        return None
    
def can_defend(name):
    return not name in ["suspiciousbush", "wallbreakers", "icegolem",
                        "elixirgolem", "goblinbarrel",
                        "hogrider", "battleram", 
                        "ramrider", "giant", "balloon", 
                        "royalgiant", "goblingiant", 
                        "lavahound", "electrogiant",
                        "golem"]

def can_anywhere(name):
    return name != "royaldelivery" and name != "log" and name != "barbarianbarrel" and (get_type(name) == "spell" or name == "miner" or name == "goblindrill")

def get_type(name):
    if name in troops:
        if name == "log" or name == "barbarianbarrel":
            return "spell"
        if name == "goblindrill":
            return "building"
        return "troop"
    elif name in spells:
        return "spell"
    elif name in buildings:
        return "building"
    elif name in champions:
        return "troop"

def card_factory(side, position, name, level):
    if name in troops:
        return "troop", troop_factory(side, position, name, level)
    elif name in spells:
        return "spell", spell_factory(side, position, name, level)
    elif name in buildings:
        return "building", building_factory(side, position, name, level)
    elif name in champions:
        return "troop", champion_factory(side, position, name, level)
    
def tower_factory(side, name, level):
    if name == "princesstower":
        return [
            towers.PrincessTower(side, level, True),
            towers.PrincessTower(side, level, False),
            towers.KingTower(side, level)
        ]
    elif name == "cannoneer":
        return [
            towers.Cannoneer(side, level, True),
            towers.Cannoneer(side, level, False),
            towers.KingTower(side, level)
        ]
    elif name == "daggerduchess":
        return [
            towers.DaggerDuchess(side, level, True),
            towers.DaggerDuchess(side, level, False),
            towers.KingTower(side, level)
        ]
    else:
        raise Exception("Invalid tower type.")

def get_clone(obj):
    if obj.__class__.__name__.lower() in champions:
        return None
    if obj.__class__.__name__ == "Miner":
        return electro_valley_cards.Miner(obj.side, copy.deepcopy(obj.position), obj.level, True)
    if not obj.evo:
        return type(obj)(obj.side, copy.deepcopy(obj.position), obj.level)
    else:
        n = obj.__class__.__name__
        if n == "EvolutionKnight":
            return training_camp_cards.Knight(obj.side, copy.deepcopy(obj.position), obj.level)
        elif n == "EvolutionArcher":
            return training_camp_cards.Archer(obj.side, copy.deepcopy(obj.position), obj.level)
        elif n == "EvolutionMusketeer":
            return training_camp_cards.Musketeer(obj.side, copy.deepcopy(obj.position), obj.level)
        elif n == "EvolutionSkeleton":
            return bone_pit_cards.Skeleton(obj.side, copy.deepcopy(obj.position), obj.level)
        elif n == "EvolutionBomber":
            return bone_pit_cards.Bomber(obj.side, copy.deepcopy(obj.position), obj.level)
        elif n == "EvolutionValkyrie":
            return bone_pit_cards.Valkyrie(obj.side, copy.deepcopy(obj.position), obj.level)
        elif n == "EvolutionBarbarian":
            return barbarian_bowl_cards.Barbarian(obj.side, copy.deepcopy(obj.position), obj.level)
        elif n == "EvolutionBattleRam":
            return barbarian_bowl_cards.BattleRam(obj.side, copy.deepcopy(obj.position), obj.level)
        elif n == "EvolutionWizard":
            return spell_valley_cards.Wizard(obj.side, copy.deepcopy(obj.position), obj.level)
        elif n == "EvolutionBat":
            return builders_workshop_cards.Bat(obj.side, copy.deepcopy(obj.position), obj.level)
        elif n == "EvolutionPekka":
            return pekkas_playhouse_cards.Pekka(obj.side, copy.deepcopy(obj.position), obj.level)
        elif n == "EvolutionRoyalGiant":
            return royal_arena_cards.RoyalGiant(obj.side, copy.deepcopy(obj.position), obj.level)
        elif n == "EvolutionRoyalRecruit":
            return royal_arena_cards.RoyalRecruit(obj.side, copy.deepcopy(obj.position), obj.level)
        elif n == "EvolutionIceSpirit":
            return frozen_peak_cards.IceSpirit(obj.side, copy.deepcopy(obj.position), obj.level)
        elif n == "EvolutionDartGoblin":
            return jungle_arena_cards.DartGoblin(obj.side, copy.deepcopy(obj.position), obj.level)
        elif n == "EvolutionGoblinGiant":
            return jungle_arena_cards.GoblinGiant(obj.side, copy.deepcopy(obj.position), obj.level)
        elif n == "EvolutionHunter":
            return hog_mountain_cards.Hunter(obj.side, copy.deepcopy(obj.position), obj.level)
        elif n == "EvolutionInfernoDragon":
            return electro_valley_cards.InfernoDragon(obj.side, copy.deepcopy(obj.position), obj.level)
        elif n == "EvolutionMegaKnight":
            return electro_valley_cards.MegaKnight(obj.side, copy.deepcopy(obj.position), obj.level)
        elif n == "EvolutionFirecracker":
            return spooky_town_cards.Firecracker(obj.side, copy.deepcopy(obj.position), obj.level)
        elif n == "EvolutionElectroDragon":
            return spooky_town_cards.ElectroDragon(obj.side, copy.deepcopy(obj.position), obj.level)
        elif n == "EvolutionWallBreaker":
            return spooky_town_cards.WallBreaker(obj.side, copy.deepcopy(obj.position), obj.level)
        elif n == "EvolutionLumberjack":
            return serenity_peak_cards.Lumberjack(obj.side, copy.deepcopy(obj.position), obj.level)
        elif n == "EvolutionExecutioner":
            return serenity_peak_cards.Executioner(obj.side, copy.deepcopy(obj.position), obj.level)
        elif n == "EvolutionSkeletonBarrel":
            return jungle_arena_cards.SkeletonBarrel(obj.side, copy.deepcopy(obj.position), obj.level)
        else:
            raise Exception(n + " is not actually an evo")
        
def evolution_factory(side, position, name, level):
    if name in troops:
        return "troop", evolution_troop_factory(side, position, name, level)
    elif name in spells:
        return "spell", evolution_spell_factory(side, position, name, level)
    elif name in buildings:
        return "building", evolution_building_factory(side, position, name, level)

def evolution_troop_factory(side, position, name, level):
    if name == "knight":
        return training_camp_evos.EvolutionKnight(side, position, level)
    elif name == "archers":
        pos1 = vector.Vector(1/2, 0)
        pos2 = vector.Vector(-1/2, 0)
        return [training_camp_evos.EvolutionArcher(side, position.added(pos1), level),
                training_camp_evos.EvolutionArcher(side, position.added(pos2), level)]
    elif name == "musketeer":
        return training_camp_evos.EvolutionMusketeer(side, position, level)
    elif name == "skeletons":
        flip = 1 if side else -1
        pos1 = vector.Vector(0, 1/2 * flip)
        pos2 = vector.Vector(-math.sqrt(3)/4, -1/4 * flip)
        pos3 = vector.Vector(math.sqrt(3)/4, -1/4 * flip)
        count = bone_pit_evos.EvolutionSkeletonCounter()
        count.count = 3
        return [bone_pit_evos.EvolutionSkeleton(side, position.added(pos1), level, count), 
                bone_pit_evos.EvolutionSkeleton(side, position.added(pos2), level, count),
                bone_pit_evos.EvolutionSkeleton(side, position.added(pos3), level, count)]
    elif name == "bomber":
        return bone_pit_evos.EvolutionBomber(side, position, level)
    elif name == "valkyrie":
        return bone_pit_evos.EvolutionValkyrie(side, position, level)
    elif name == "barbarians":
        flip = 1 if side else -1
        radius = 0.7
        angles = [(2 * math.pi * k / 5) + (math.pi / 2) for k in range(5)]
        positions = [vector.Vector(radius * math.cos(a), radius * math.sin(a) * flip) for a in angles]
        out = []
        for each in positions:
            out.append(barbarian_bowl_evos.EvolutionBarbarian(side, position.added(each), level))
        return out    
    elif name == "battleram":
        return barbarian_bowl_evos.EvolutionBattleRam(side, position, level)
    elif name == "wizard":
        return spell_valley_evos.EvolutionWizard(side, position, level)
    elif name == "bats":
        flip = 1 if side else -1
        radius = 0.75
        angles = [(2 * math.pi * k / 5) + (math.pi / 2) for k in range(5)]
        positions = [vector.Vector(radius * math.cos(a), radius * math.sin(a) * flip) for a in angles]
        out = []
        for each in positions:
            out.append(builders_workshop_evos.EvolutionBat(side, position.added(each), level))
        return out
    elif name == "pekka":
        return pekkas_playhouse_evos.EvolutionPekka(side, position, level)
    elif name == "royalgiant":
        return royal_arena_evos.EvolutionRoyalGiant(side, position, level)
    elif name == "royalrecruits":
        out = []
        for i in range(6):
            out.append(royal_arena_evos.EvolutionRoyalRecruit(side, position.added(vector.Vector(-7 + (14/5 * i), 0)), level))
        return out
    elif name == "icespirit":
        return frozen_peak_evos.EvolutionIceSpirit(side, position, level)
    elif name == "dartgoblin":
        return jungle_arena_evos.EvolutionDartGoblin(side, position, level)
    elif name == "skeletonbarrel":
        return jungle_arena_evos.EvolutionSkeletonBarrel(side, position, level)
    elif name == "goblingiant":
        return jungle_arena_evos.EvolutionGoblinGiant(side, position, level)
    elif name == "hunter":
        return hog_mountain_evos.EvolutionHunter(side, position, level)
    elif name == "infernodragon":
        return electro_valley_evos.EvolutionInfernoDragon(side, position, level)
    elif name == "megaknight":
        return electro_valley_evos.EvolutionMegaKnight(side, position, level)
    elif name == "firecracker":
        return spooky_town_evos.EvolutionFirecracker(side, position, level)
    elif name == "electrodragon":
        return spooky_town_evos.EvolutionElectroDragon(side, position, level)
    elif name == "wallbreakers":
        pos1 = vector.Vector(0.75, 0)
        pos2 = vector.Vector(-0.75, 0)
        return [spooky_town_evos.EvolutionWallBreaker(side, position.added(pos1), level),
                spooky_town_evos.EvolutionWallBreaker(side, position.added(pos2), level)]
    elif name == "lumberjack":
        return serenity_peak_evos.EvolutionLumberjack(side, position, level)
    elif name == "goblindrill":
        return serenity_peak_evos.EvolutionGoblinDrillMineTroop(side, position, level)
    elif name == "executioner":
        return serenity_peak_evos.EvolutionExecutioner(side, position, level)
    
def evolution_spell_factory(side, position, name, level):
    if name == "zap":
        return builders_workshop_evos.EvolutionZap(side, position, level)
    elif name == "goblinbarrel":
        return pekkas_playhouse_evos.EvolutionGoblinBarrel(side, position, level)
    elif name == "giantsnowball":
        return frozen_peak_evos.EvolutionGiantSnowball(side, position, level)

def evolution_building_factory(side, position, name, level):
    if name == "goblincage":
        return goblin_stadium_evos.EvolutionGoblinCage(side, position, level)
    elif name == "cannon":
        return barbarian_bowl_evos.EvolutionCannon(side, position, level)
    elif name == "mortar":
        return builders_workshop_evos.EvolutionMortar(side, position, level)
    elif name == "tesla":
        return hog_mountain_evos.EvolutionTesla(side, position, level)
    
def champion_factory(side, position, name, level):
    if name == "archerqueen":
        return champion_cards.ArcherQueen(side, position, level)
    elif name == "skeletonking":
        return champion_cards.SkeletonKing(side, position, level)
    elif name == "goldenknight":
        return champion_cards.GoldenKnight(side, position, level)
    else:
        raise Exception("Invalid champion name")

def troop_factory(side, position, name, level):
    if name == "knight":
        return training_camp_cards.Knight(side, position, level)
    elif name == "minipekka":
        return training_camp_cards.MiniPekka(side, position, level)
    elif name == "giant":
        return training_camp_cards.Giant(side, position, level)
    elif name == "minions":
        flip = 1 if side else -1
        pos1 = vector.Vector(0, 1/2 * flip)
        pos2 = vector.Vector(-math.sqrt(3)/4, -1/4 * flip)
        pos3 = vector.Vector(math.sqrt(3)/4, -1/4 * flip)
        return [training_camp_cards.Minion(side, position.added(pos1), level), 
                training_camp_cards.Minion(side, position.added(pos2), level),
                training_camp_cards.Minion(side, position.added(pos3), level)]
    elif name == "archers":
        pos1 = vector.Vector(1/2, 0)
        pos2 = vector.Vector(-1/2, 0)
        return [training_camp_cards.Archer(side, position.added(pos1), level),
                training_camp_cards.Archer(side, position.added(pos2), level)]
    elif name == "musketeer":
        return training_camp_cards.Musketeer(side, position, level)
    elif name == "speargoblins":
        flip = 1 if side else -1
        pos1 = vector.Vector(0, 1/2 * flip)
        pos2 = vector.Vector(-math.sqrt(3)/4, -1/4 * flip)
        pos3 = vector.Vector(math.sqrt(3)/4, -1/4 * flip)
        return [goblin_stadium_cards.SpearGoblin(side, position.added(pos1), level), 
                goblin_stadium_cards.SpearGoblin(side, position.added(pos2), level),
                goblin_stadium_cards.SpearGoblin(side, position.added(pos3), level)]
    elif name == "goblins":
        pos1 = vector.Vector(1/2, 1/2)
        pos2 = vector.Vector(-1/2, 1/2)
        pos3 = vector.Vector(1/2, -1/2)
        pos4 = vector.Vector(-1/2, -1/2)
        return [goblin_stadium_cards.Goblin(side, position.added(pos1), level),
                goblin_stadium_cards.Goblin(side, position.added(pos2), level),
                goblin_stadium_cards.Goblin(side, position.added(pos3), level),
                goblin_stadium_cards.Goblin(side, position.added(pos4), level),]
    elif name == "skeletons":
        flip = 1 if side else -1
        pos1 = vector.Vector(0, 1/2 * flip)
        pos2 = vector.Vector(-math.sqrt(3)/4, -1/4 * flip)
        pos3 = vector.Vector(math.sqrt(3)/4, -1/4 * flip)
        return [bone_pit_cards.Skeleton(side, position.added(pos1), level), 
                bone_pit_cards.Skeleton(side, position.added(pos2), level),
                bone_pit_cards.Skeleton(side, position.added(pos3), level)]
    elif name == "bomber":
        return bone_pit_cards.Bomber(side, position, level)
    elif name == "valkyrie":
        return bone_pit_cards.Valkyrie(side, position, level)
    elif name == "megaminion":
        return barbarian_bowl_cards.MegaMinion(side, position, level)
    elif name == "barbarians":
        flip = 1 if side else -1
        radius = 0.7
        angles = [(2 * math.pi * k / 5) + (math.pi / 2) for k in range(5)]
        positions = [vector.Vector(radius * math.cos(a), radius * math.sin(a) * flip) for a in angles]
        out = []
        for each in positions:
            out.append(barbarian_bowl_cards.Barbarian(side, position.added(each), level))
        return out
    elif name == "battleram":
        return barbarian_bowl_cards.BattleRam(side, position, level)
    elif name == "firespirit":
        return spell_valley_cards.FireSpirit(side, position, level)
    elif name == "electrospirit":
        return spell_valley_cards.ElectroSpirit(side, position, level)
    elif name == "wizard":
        return spell_valley_cards.Wizard(side, position, level)
    elif name == "skeletondragons":
        pos1 = vector.Vector(0.75, 0)
        pos2 = vector.Vector(-0.75, 0)
        return [spell_valley_cards.SkeletonDragon(side, position.added(pos1), level),
                spell_valley_cards.SkeletonDragon(side, position.added(pos2), level)]
    elif name == "bats":
        flip = 1 if side else -1
        radius = 0.75
        angles = [(2 * math.pi * k / 5) + (math.pi / 2) for k in range(5)]
        positions = [vector.Vector(radius * math.cos(a), radius * math.sin(a) * flip) for a in angles]
        out = []
        for each in positions:
            out.append(builders_workshop_cards.Bat(side, position.added(each), level))
        return out
    elif name == "hogrider":
        return builders_workshop_cards.HogRider(side, position, level)
    elif name == "flyingmachine":
        return builders_workshop_cards.FlyingMachine(side, position, level)
    elif name == "skeletonarmy":
        out = []
        for _ in range(15):
            out.append(bone_pit_cards.Skeleton(side, position.added(vector.Vector(random.uniform(-2, 2), random.uniform(-2, 2))), level))
        return out
    elif name == "guards":
        flip = 1 if side else -1
        pos1 = vector.Vector(0, 1/2 * flip)
        pos2 = vector.Vector(-math.sqrt(3)/4, -1/4 * flip)
        pos3 = vector.Vector(math.sqrt(3)/4, -1/4 * flip)
        return [pekkas_playhouse_cards.Guard(side, position.added(pos1), level), 
                pekkas_playhouse_cards.Guard(side, position.added(pos2), level),
                pekkas_playhouse_cards.Guard(side, position.added(pos3), level)]
    elif name == "babydragon":
        return pekkas_playhouse_cards.BabyDragon(side, position, level)
    elif name == "witch":
        return pekkas_playhouse_cards.Witch(side, position, level)
    elif name == "pekka":
        return pekkas_playhouse_cards.Pekka(side, position, level)
    elif name == "darkprince":
        return royal_arena_cards.DarkPrince(side, position, level)
    elif name == "royalhogs":
        out = []
        for i in range(4):
            out.append(royal_arena_cards.RoyalHog(side, position.added(vector.Vector(-3.5/2 + (3.5/3 * i), 0)), level))
        return out
    elif name == "prince":
        return royal_arena_cards.Prince(side, position, level)
    elif name == "balloon":
        return royal_arena_cards.Balloon(side, position, level)
    elif name == "royalgiant":
        return royal_arena_cards.RoyalGiant(side, position, level)
    elif name == "royalrecruits":
        out = []
        for i in range(6):
            out.append(royal_arena_cards.RoyalRecruit(side, position.added(vector.Vector(-7 + (14/5 * i), 0)), level))
        return out
    elif name == "threemusketeers":
        flip = 1 if side else -1
        pos1 = vector.Vector(0, 1/2 * flip)
        pos2 = vector.Vector(-math.sqrt(3)/4, -1/4 * flip)
        pos3 = vector.Vector(math.sqrt(3)/4, -1/4 * flip)
        return [training_camp_cards.Musketeer(side, position.added(pos1), level), 
                training_camp_cards.Musketeer(side, position.added(pos2), level),
                training_camp_cards.Musketeer(side, position.added(pos3), level)]
    elif name == "icespirit":
        return frozen_peak_cards.IceSpirit(side, position, level)
    elif name == "icegolem":
        return frozen_peak_cards.IceGolem(side, position, level)
    elif name == "battlehealer":
        return frozen_peak_cards.BattleHealer(side, position, level)
    elif name == "giantskeleton":
        return frozen_peak_cards.GiantSkeleton(side, position, level)
    elif name == "beserker":
        return jungle_arena_cards.Beserker(side, position, level)
    elif name == "barbarianbarrel":
        return jungle_arena_cards.BarbarianBarrel(side, position, level)
    elif name == "goblingang":
        flip = 1 if side else -1
        radius = 1
        angles = [(2 * math.pi * k / 6) + (math.pi / 6) for k in range(6)]
        positions = [vector.Vector(radius * math.cos(a), radius * math.sin(a) * flip) for a in angles]
        out = []
        i = 0
        for each in positions:
            if i < 3:
                out.append(goblin_stadium_cards.Goblin(side, position.added(each), level))
            else:
                out.append(goblin_stadium_cards.SpearGoblin(side, position.added(each), level))
            i += 1
        return out
    elif name == "dartgoblin":
        return jungle_arena_cards.DartGoblin(side, position, level)
    elif name == "skeletonbarrel":
        return jungle_arena_cards.SkeletonBarrel(side, position, level)
    elif name == "goblingiant":
        return jungle_arena_cards.GoblinGiant(side, position, level)
    elif name == "zappies":
        flip = 1 if side else -1
        radius = 1
        angles = [(2 * math.pi * k / 3) + (math.pi / 2) for k in range(3)]
        positions = [vector.Vector(radius * math.cos(a), radius * math.sin(a) * flip) for a in angles]
        out = []
        for each in positions:
            out.append(hog_mountain_cards.Zappy(side, position.added(each), level))
        return out
    elif name == "hunter":
        return hog_mountain_cards.Hunter(side, position, level)
    elif name == "minionhorde":
        flip = 1 if side else -1
        radius = 0.6
        angles = [(2 * math.pi * k / 6) + (math.pi / 2) for k in range(6)]
        positions = [vector.Vector(radius * math.cos(a), radius * math.sin(a) * flip) for a in angles]
        out = []
        for each in positions:
            out.append(training_camp_cards.Minion(side, position.added(each), level))
        return out
    elif name == "elitebarbarians":
        pos1 = vector.Vector(0.35, 0)
        pos2 = vector.Vector(-0.35, 0)
        return [hog_mountain_cards.EliteBarbarian(side, position.added(pos1), level),
                hog_mountain_cards.EliteBarbarian(side, position.added(pos2), level)]
    elif name == "golem":
        return hog_mountain_cards.Golem(side, position, level)
    elif name == "log":
        return electro_valley_cards.Log(side, position, level)
    elif name == "miner":
        return electro_valley_cards.Miner(side, position, level)
    elif name == "princess":
        return electro_valley_cards.Princess(side, position, level)
    elif name == "electrowizard":
        return electro_valley_cards.ElectroWizard(side, position, level)
    elif name == "infernodragon":
        return electro_valley_cards.InfernoDragon(side, position, level)
    elif name == "ramrider":
        return electro_valley_cards.RamRider(side, position, level)
    elif name == "sparky":
        return electro_valley_cards.Sparky(side, position, level)
    elif name == "megaknight":
        return electro_valley_cards.MegaKnight(side, position, level)
    elif name == "wallbreakers":
        pos1 = vector.Vector(0.75, 0)
        pos2 = vector.Vector(-0.75, 0)
        return [spooky_town_cards.WallBreaker(side, position.added(pos1), level),
                spooky_town_cards.WallBreaker(side, position.added(pos2), level)]
    elif name == "icewizard":
        return spooky_town_cards.IceWizard(side, position, level)
    elif name == "royalghost":
        return spooky_town_cards.RoyalGhost(side, position, level)
    elif name == "firecracker":
        return spooky_town_cards.Firecracker(side, position, level)
    elif name == "phoenix":
        return spooky_town_cards.Phoenix(side, position, level)
    elif name == "electrodragon":
        return spooky_town_cards.ElectroDragon(side, position, level)
    elif name == "healspirit":
        return rascals_hideout_cards.HealSpirit(side, position, level)
    elif name == "suspiciousbush":
        return rascals_hideout_cards.SuspiciousBush(side, position, level)
    elif name == "bandit":
        return rascals_hideout_cards.Bandit(side, position, level)
    elif name == "magicarcher":
        return rascals_hideout_cards.MagicArcher(side, position, level)
    elif name == "rascals":
        flip = 1 if side else -1
        pos1 = vector.Vector(0, 3/2 * flip)
        pos2 = vector.Vector(-3*math.sqrt(3)/4, -3/4 * flip)
        pos3 = vector.Vector(3*math.sqrt(3)/4, -3/4 * flip)
        return [rascals_hideout_cards.RascalBoy(side, position.added(pos1), level), 
                rascals_hideout_cards.RascalGirl(side, position.added(pos2), level),
                rascals_hideout_cards.RascalGirl(side, position.added(pos3), level)]
    elif name == "bowler":
        return rascals_hideout_cards.Bowler(side, position, level)
    elif name == "electrogiant":
        return rascals_hideout_cards.ElectroGiant(side, position, level)
    elif name == "lavahound":
        return rascals_hideout_cards.LavaHound(side, position, level)
    elif name == "elixirgolem":
        return serenity_peak_cards.ElixirGolem(side, position, level)
    elif name == "goblindrill":
        return serenity_peak_cards.GoblinDrillMineTroop(side, position, level)
    elif name == "lumberjack":
        return serenity_peak_cards.Lumberjack(side, position, level)
    elif name == "nightwitch":
        return serenity_peak_cards.NightWitch(side, position, level)
    elif name == "executioner":
        return serenity_peak_cards.Executioner(side, position, level)
    elif name == "fisherman":
        return miners_mine_cards.Fisherman(side, position, level)
    elif name == "motherwitch":
        return miners_mine_cards.MotherWitch(side, position, level)
    elif name == "cannoncart":
        return miners_mine_cards.CannonCart(side, position, level)
    else:
        raise Exception("Invalid troop name.")

def spell_factory(side, position, name, level):
    if name == "fireball":
        return training_camp_cards.Fireball(side, position, level)
    elif name == "arrows":
        return training_camp_cards.Arrows(side, position, level)
    elif name == "zap":
        return builders_workshop_cards.Zap(side, position, level)
    elif name == "rocket":
        return builders_workshop_cards.Rocket(side, position, level)
    elif name == "goblinbarrel":
        return pekkas_playhouse_cards.GoblinBarrel(side, position, level)
    elif name == "giantsnowball":
        return frozen_peak_cards.GiantSnowball(side, position, level)
    elif name == "freeze":
        return frozen_peak_cards.Freeze(side, position, level)
    elif name == "lightning":
        return frozen_peak_cards.Lightning(side, position, level)
    elif name == "poison":
        return jungle_arena_cards.Poison(side, position, level)
    elif name == "earthquake":
        return spooky_town_cards.Earthquake(side, position, level)
    elif name == "graveyard":
        return spooky_town_cards.Graveyard(side, position, level)
    elif name == "rage":
        return serenity_peak_cards.Rage(side, position, level)
    elif name == "goblincurse":
        return serenity_peak_cards.GoblinCurse(side, position, level)
    elif name == "royaldelivery":
        return serenity_peak_cards.RoyalDelivery(side, position, level)
    elif name == "clone":
        return miners_mine_cards.Clone(side, position, level)
    elif name == "void":
        return miners_mine_cards.Void(side, position, level)
    elif name == "tornado":
        return miners_mine_cards.Tornado(side, position, level)
    else:
        raise Exception("Invalid spell name.")

def building_factory(side, position, name, level):
    if name == "goblincage":
        return goblin_stadium_cards.GoblinCage(side, position, level)
    elif name == "goblinhut":
        return goblin_stadium_cards.GoblinHut(side, position, level)
    elif name == "tombstone":
        return bone_pit_cards.Tombstone(side, position, level)
    elif name == "cannon":
        return barbarian_bowl_cards.Cannon(side, position, level)
    elif name == "bombtower":
        return spell_valley_cards.BombTower(side, position, level)
    elif name == "infernotower":
        return spell_valley_cards.InfernoTower(side, position, level)
    elif name == "mortar":
        return builders_workshop_cards.Mortar(side, position, level)
    elif name == "barbarianhut":
        return jungle_arena_cards.BarbarianHut(side, position, level)
    elif name == "furnace":
        return hog_mountain_cards.Furnace(side, position, level)
    elif name == "tesla":
        return hog_mountain_cards.Tesla(side, position, level)
    elif name == "xbow":
        return hog_mountain_cards.XBow(side, position, level)
    elif name == "elixircollector":
        return miners_mine_cards.ElixirCollector(side, position, level)
    else:
        raise Exception("Invalid building name")

def get_elixir(cardname):
    return elixir_map[cardname]

elixir_map = {
    "arrows" : 3,
    "minions" : 3,
    "archers" : 3,
    "knight" : 3,
    "fireball" : 4,
    "minipekka" : 4,
    "musketeer" : 4,
    "giant" : 5,
    "speargoblins" : 2,
    "goblins" : 2,
    "goblincage" : 4,
    "goblinhut" : 5,
    "skeletons" : 1,
    "bomber" : 2,
    "tombstone" : 3,
    "valkyrie" : 4,
    "megaminion" : 3,
    "cannon" : 3,
    "battleram" : 4,
    "barbarians" : 5,
    "firespirit" : 1,
    "electrospirit" : 1,
    "bombtower" : 4,
    "skeletondragons" : 4,
    "wizard" : 5,
    "infernotower" : 5,
    "zap" : 2,
    "bats" : 2,
    "hogrider": 4,
    "mortar" : 4,
    "flyingmachine" : 4,
    "rocket" : 6,
    "skeletonarmy" : 3,
    "guards" : 3,
    "goblinbarrel" : 3,
    "babydragon" : 4,
    "witch" : 5,
    "pekka": 7,
    "darkprince" : 4,
    "royalhogs" : 5,
    "prince" : 5,
    "balloon" : 5,
    "royalgiant" : 6,
    "royalrecruits" : 7,
    "threemusketeers" : 9,
    "icespirit" : 1,
    "giantsnowball" : 2,
    "icegolem" : 2,
    "freeze" : 4,
    "battlehealer" : 4,
    "giantskeleton" : 6,
    "lightning" : 6,
    "barbarianbarrel" : 2,
    "beserker" : 2,
    "goblingang" : 3,
    "dartgoblin" : 3,
    "skeletonbarrel" : 3,
    "poison" : 4,
    "barbarianhut" : 6,
    "goblingiant" : 6,
    "furnace" : 4,
    "zappies" : 4,
    "hunter" : 4,
    "tesla" : 4,
    "minionhorde" : 5,
    "elitebarbarians" : 6,
    "xbow" : 6,
    "golem" : 8,
    "log" : 2,
    "miner" : 3,
    "princess" : 3,
    "electrowizard" : 4,
    "infernodragon" : 4,
    "ramrider" : 5,
    "sparky" : 6,
    "megaknight" : 7,
    "wallbreakers" : 2,
    "firecracker" : 3,
    "royalghost" : 3,
    "icewizard" : 3,
    "earthquake" : 3,
    "phoenix" : 4,
    "electrodragon" : 5,
    "graveyard" : 5,
    "healspirit" : 1,
    "suspiciousbush" : 2,
    "bandit" : 3,
    "magicarcher" : 4,
    "rascals" : 5,
    "bowler" : 5,
    "electrogiant" : 7,
    "lavahound" : 7,
    "rage" : 2,
    "goblincurse" : 2,
    "royaldelivery" : 3,
    "elixirgolem" : 3,
    "goblindrill" : 3,
    "lumberjack" : 4,
    "nightwitch" : 4,
    "executioner" : 5,
    "clone" : 3,
    "void" : 3,
    "tornado" : 3,
    "fisherman" : 3,
    "motherwitch" : 4,
    "cannoncart" : 5,
    "elixircollector" : 6,
    "skeletonking" : 4,
    "goldenknight" : 4,
    "archerqueen" : 5
}

def filter_cards(card_list, min_elixir, max_elixir, used_cards):
    return [card for card in card_list
            if min_elixir <= elixir_map.get(card, 0) <= max_elixir and card not in used_cards]

def generate_random_deck():
    deck = []
    used = set()

    # 1st: troop with elixir 1–2
    options = filter_cards(troops, 1, 2, used)
    choice = random.choice(options)
    deck.append(choice)
    used.add(choice)

    # 2nd: troop with elixir 2–3
    options = filter_cards(troops, 2, 3, used)
    choice = random.choice(options)
    deck.append(choice)
    used.add(choice)

    # 3rd–5th: troops with elixir 3–5
    options = filter_cards(troops, 3, 5, used)
    choices = random.sample(options, 3)
    deck.extend(choices)
    used.update(choices)

    # 6th: troop with elixir 5–9
    options = filter_cards(troops, 5, 9, used)
    choice = random.choice(options)
    deck.append(choice)
    used.add(choice)

    # 7th: spell with elixir 1–3
    options = filter_cards(spells, 1, 3, used)
    choice = random.choice(options)
    deck.append(choice)
    used.add(choice)

    # 8th: spell with elixir = 4
    options = filter_cards(spells, 4, 4, used)
    choice = random.choice(options)
    deck.append(choice)
    used.add(choice)

    if random.randint(1, 4) == 1:
        deck[2] = random.choice(buildings)

    if random.randint(1, 5) == 1:
        deck[3] = random_with_param("spell", 5, 9, used)
    
    if random.randint(1, 5) == 1:
        deck[4] = "mirror"
    elif random.randint(1, 5) == 1:
        deck[4] = random_with_param("champion", 1, 10, used)

    return deck

def parse_input(string, current_used):
    components = string.split(".")
    if components[0] != "random":
        sp = components[0].split(" ")
        if len(sp) > 1:
            return sp[0] == "evolution", sp[1]
        return False, components[0]
    else:
        lower, upper = components[2].split("-")
        n = random_with_param(components[1], int(lower), int(upper), current_used)
        return can_evo(n), n

def random_with_param(t, lower, upper, used):
    out = None
    if t == "troop":
        options = filter_cards(troops, lower, upper, used)
        out = random.choice(options)
        while out == "log" or out == "barbarianbarrel" or out == "goblindrill":
            out = random.choice(options)
    elif t == "spell":
        options = filter_cards(spells + ["log", "barbarianbarrel"], lower, upper, used)
        out = random.choice(options)
    elif t == "building":
        options = filter_cards(buildings + ["goblindrill"], lower, upper, used)
        out = random.choice(options)
    elif t == "any":
        options = filter_cards(spells + buildings + troops, lower, upper, used)
        out = random.choice(options)
    elif t == "champion":
        options = filter_cards(champions, lower, upper, used)
        out = random.choice(options)
    return out


def generate_random_remaining(filled, evo_enabled = True):
    used = []
    out = [None, None, None, None,
           None, None, None, None]
    missing = [["troop", [1, 2]], ["troop", [2, 3]], ["troop", [3, 5]], ["troop", [3, 5]],
               ["troop", [3, 5]], ["troop", [5, 9]], ["spell", [1, 3]], ["spell", [4, 4]]]
    
    priority = [4, 3, 2, 5, 1, 0, 6, 7]

    fill = []

    for each in filled:
        has_spot = False
        if each[0] == "troop":
            e = each[1]
            if e >= 1 and e <= 2 and missing[0] is not None:
                out[0] = [each[2], each[3]]
                priority.remove(0)
                missing[0] = None
                has_spot = True
            elif e >= 2 and e <= 3 and missing[1] is not None:
                out[1] = [each[2], each[3]]
                priority.remove(1)
                missing[1] = None
                has_spot = True
            elif e >= 3 and e <= 5:
                if missing[4] is not None:
                    out[4] = [each[2], each[3]]
                    priority.remove(4)
                    missing[4] = None
                    has_spot = True
                elif missing[3] is not None:
                    out[3] = [each[2], each[3]]
                    priority.remove(3)
                    missing[3] = None
                    has_spot = True
                elif missing[2] is not None:
                    out[2] = [each[2], each[3]]
                    priority.remove(2)
                    missing[2] = None
                    has_spot = True

            if not has_spot and e >= 5 and missing[5] is not None:
                out[5] = [each[2], each[3]]
                priority.remove(5)
                missing[5] = None
                has_spot = True
        elif each[0] == "spell":
            e = each[1]
            if e >= 1 and e <= 3 and missing[6] is not None:
                out[6] = [each[2], each[3]]
                priority.remove(6)
                missing[6] = None
                has_spot = True
            elif e == 4 and missing[7] is not None:
                out[7] = [each[2], each[3]]
                priority.remove(7)
                missing[7] = None
                has_spot = True
        
        if not has_spot:
            fill.append(each)
        else:
            used.append(each[2])
    
    for each in fill:
        i = priority.pop(0)
        out[i] = [each[2], each[3]]
        missing[i] = None

    i = 0
    for each in missing:
        if each is not None:
            n = None
            if i == 2 and random.randint(1, 4) == 1:
                n = random.choice(buildings)
            elif i == 3 and random.randint(1, 5) == 1:
                n = random_with_param("spell", 5, 9, used)
            elif i == 4 and random.randint(1, 5) == 1:
                n = "mirror"
            else:
                n = random_with_param(each[0], each[1][0], each[1][1], used)
            out[i] = [n, evo_enabled and can_evo(n)]
            used.append(n)
        i += 1

    return out