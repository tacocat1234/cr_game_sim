import math
import vector
import training_camp_cards
import goblin_stadium_cards

troops = ["knight", "minipekka", "giant", "minions", "archers", "musketeer", "speargoblins", "goblins"]
spells = ["fireball", "arrows"]
buildings = ["goblinhut", "goblincage"]

def get_type(name):
    if name in troops:
        return "troop"
    elif name in spells:
        return "spell"
    elif name in buildings:
        return "building"

def card_factory(side, position, name, level):
    if name in troops:
        return "troop", troop_factory(side, position, name, level)
    elif name in spells:
        return "spell", spell_factory(side, position, name, level)
    elif name in buildings:
        return "building", building_factory(side, position, name, level)

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
    else:
        raise Exception("Invalid troop name.")

def spell_factory(side, position, name, level):
    if name == "fireball":
        return training_camp_cards.Fireball(side, position, level)
    elif name == "arrows":
        return training_camp_cards.Arrows(side, position, level)
    else:
        raise Exception("Invalid spell name.")

def building_factory(side, position, name, level):
    if name == "goblincage":
        return goblin_stadium_cards.GoblinCage(side, position, level)
    elif name == "goblinhut":
        return goblin_stadium_cards.GoblinHut(side, position, level)
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
    "goblinhut" : 5
}