import math
import training_camp_cards
import goblin_stadium_cards

troops = ["knight", "minipekka", "giant", "minions", "archers", "musketeer"]
spells = ["fireball", "arrows"]
buildings = []

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
        pos1 = Vector(0, 1/2)
        pos2 = Vector(-math.sqrt(3)/4, -1/4)
        pos3 = Vector(math.sqrt(3)/4, 1/4)
        return [training_camp_cards.Minion(side, position.added(pos1), level), 
                training_camp_cards.Minion(side, position.added(pos2), level),
                training_camp_cards.Minion(side, position.added(pos3), level)]
    elif name == "archers":
        pos1 = Vector(1/2, 0)
        pos2 = Vector(-1/2, 0)
        return [training_camp_cards.Archer(side, position.added(pos1), level),
                training_camp_cards.Archer(side, position.added(pos2), level),]
    elif name == "musketeer":
        return training_camp_cards.Musketeer(side, position, level)
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
    elif name == "goblin hut":
        return goblin_stadium_cards.GoblinHut(side, position, level)
    else:
        raise Exception("Invalid building name")

