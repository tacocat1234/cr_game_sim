import random
import copy
import vector
from abstract_classes import TICK_TIME
from abstract_classes import Troop
from card_factory import get_type
from card_factory import get_elixir
from builders_workshop_cards import Mortar
from hog_mountain_cards import XBow
from card_factory import can_defend

counters = {
    "minipekka" : ["skeletons", vector.Vector(0, 0)],
    "musketeer" : ["fireball", vector.Vector(0, -2)],
    "valkyrie" : ["minipekka", vector.Vector(0, 0)]
}

class Bot:
    def __init__(self, cards):
        self.cards = cards
        self.internal_timer = random.triangular(0, 16.8, 8.4)

        self.min_elixir = 99
        for each in cards:
            if each.elixir_cost < self.min_elixir:
                self.min_elixir = each.elixir_cost

        self.buffer_check = 2
        self.buffer = []

    def tick(self, elixir, things = None):
        if not things is None:
            danger_level = 0
            for each in things:
                    if each.side:
                        if (isinstance(each, XBow) or isinstance(each, Mortar)) and each.position.y >= -3:
                            danger_level += 99 #immediate threat
                        if each.position.y > 0:
                            if each.position.y > 9.5 - each.hit_range:
                                danger_level += 1.75
                            elif each.position.y > 7:
                                danger_level += 1.5
                            elif each.position.y > 4:
                                danger_level += 1
                            elif each.position.y > 2:
                                danger_level += 0.5
                            else:
                                danger_level += 0.25
            if danger_level >= 2:
                self.internal_timer = 0
        if self.internal_timer <= 0 or elixir >= 9:
            if elixir >= 7:
                self.internal_timer = 0
            else:
                self.internal_timer = random.triangular(0, 14, 5.6)

            remaining = copy.deepcopy(self.cards)
            
            selected = random.choice(remaining)
            while selected.elixir_cost > elixir or selected.name in self.buffer or (danger_level >= 2 and not can_defend(selected.name)):
                remaining.remove(selected)
                if not remaining:
                    return None
                selected = random.choice(remaining)
            
            if len(self.buffer) < self.buffer_check:
                self.buffer.append(selected.name)
            else:
                self.buffer.pop(0)
                self.buffer.append(selected.name)
            return selected
        else:
            self.internal_timer -= TICK_TIME

    def random_pos(name, things = None):
        isSpell = get_type(name) == "spell" or name == "barbarianbarrel" or name == "log" or name == "miner" or name == "goblindrill"
        enemy = []
        friendly = []
        if not things is None:
            for each in things:
                    if each.side:
                        enemy.append(each)
                    else:
                        friendly.append(each)
        danger_level = 0
        offensive_count = 0
        left_count = 0
        most_dangerous = None
        m_d_c = 0
        for each in enemy:
            if (isinstance(each, XBow) or isinstance(each, Mortar)) and each.position.y >= -3:
                    danger_level += 99 #immediate threat
                    most_dangerous = each
                    m_d_c = 99
                    offensive_count += 1
            if each.position.y > 0:
                offensive_count += 1
                if each.position.y > 7:
                    if (m_d_c < 1.5):
                        m_d_c = 1.5
                        most_dangerous = each
                    danger_level += 1.5
                elif each.position.y > 4:
                    if (m_d_c < 1):
                        m_d_c = 1
                        most_dangerous = each
                    danger_level += 1
                elif each.position.y > 2:
                    if (m_d_c < 0.5):
                        m_d_c = 0.5
                        most_dangerous = each
                    danger_level += 0.5
                else:
                    if (m_d_c < 0.25):
                        m_d_c = 0.25
                        most_dangerous = each
                    danger_level += 0.25

            if each.position.x < 0:
                left_count += 1
        if (isSpell):
            if name == "rage":
                if not friendly:
                    return False
                return random.choice(friendly).position.added(vector.Vector(0, -2.75))
            elif name == "clone":
                if not friendly:
                    return False
                return random.choice(friendly).position.added(vector.Vector(0, 0))
            if name == "tornado":
                if not enemy:
                    return False
                r = random.choice(enemy)
                pos = r.position.subtracted(vector.Vector(5, 0)) if r.position.x > 0 else r.position.added(vector.Vector(5, 0))
                if r.position.x < 5 and r.position.x > -5:
                    pos.x = 0
                return pos
            if danger_level >= 2:
                min = most_dangerous
                return min.position.added(vector.Vector(0, 1.5))
            if len(enemy) > 0:
                r = random.choice(enemy)
                while name == "earthquake" or name == "log" or name == "barbarianbarrel" and isinstance(r, Troop) and r.ground == False:
                    enemy.remove(r)
                    if not enemy:
                        return False
                    r = random.choice(enemy)
                
                if name == "miner":
                    return copy.deepcopy(r.position)
                if name == "goblinbarrel" or name == "graveyard" or name == "goblindrill":
                    if random.random() > 0.5:
                        return vector.Vector(-6 + random.random(), -10 + random.random())
                    else:
                        return vector.Vector(6 + random.random(), -10 + random.random())
                if r.cur_hp < 900: #cannot use rocket properly
                    if name == "barbarianbarrel":
                        pos = copy.deepcopy(r.position)
                        if pos.y < -4.7:
                            return False
                        elif pos.y < 0:
                            pos.y = 0
                        return pos
                    elif name == "log":
                        pos = copy.deepcopy(r.position)
                        if pos.y < -10.1:
                            return False
                        elif pos.y < 0:
                            pos.y = 0
                        return pos
                    elif name == "royaldelivery":
                        pos = r.position.added(vector.Vector(0, 2.0))
                        if pos.y > 0:
                            return pos
                        else:
                            return False
                    return r.position.added(vector.Vector(0, 1.5))
                    
            return False
        else:
            if offensive_count > len(enemy) - offensive_count: # if more offensive opps than defensive
                if danger_level >= 2:
                    min = most_dangerous
                    return min.position.added(vector.Vector(random.randint(-2, 2), random.randint(1, 3)))
                if random.randint(0, 2) >= 1 and len(friendly) > 0:
                    friend_pos = random.choice(friendly).position
                    friend_pos = friend_pos.added(vector.Vector(random.randint(-2, 2), random.randint(1, 3)))

                    if friend_pos.x > 9:
                        friend_pos.x = 9
                    elif friend_pos.x < -9:
                        friend_pos.x = -9
                    
                    
                    if friend_pos.y >= 0:
                        if friend_pos.y > 16:
                            friend_pos.y = 16

                        return friend_pos # if legal friend pos
                
                weight = -4.5 if left_count > len(enemy) - left_count else 4.5 #towards left if more troops on left else right
                return vector.Vector(round(random.triangular(-9, 9, weight)), random.randint(1, 16))
            else: # if more defensive opps than offensive, or equal
                if danger_level >= 4:
                    min = most_dangerous
                    return min.position.added(vector.Vector(random.randint(-2, 2), random.randint(1, 3)))
                if len(friendly) > 0 and random.random() < 0.8:
                    friend_pos = random.choice(friendly).position
                    friend_pos = friend_pos.added(vector.Vector(random.randint(-1, 1), random.randint(0, 4)))

                    if friend_pos.x > 9:
                        friend_pos.x = 9
                    elif friend_pos.x < -9:
                        friend_pos.x = -9
                    
                    if friend_pos.y < 0:
                        friend_pos.y = 1
                    if friend_pos.y > 16:
                        friend_pos.y = 16

                    return friend_pos
                #if illegal friend pos for any reason
                weight = -4.5 if left_count < len(enemy) - left_count else 4.5 #towards left if more troops on right else left
                return vector.Vector(round(random.triangular(-9, 9, weight)), random.randint(1, 16))


    
    
def place(card_type, card, arena):
    if card_type == "troop":
        if isinstance(card, list):
            arena.troops.extend(card)
        else:
            arena.troops.append(card)
    elif card_type == "spell":
        if isinstance(card, list):
            arena.spells.extend(card)
        else:
            arena.spells.append(card)
    elif card_type == "building":
        if isinstance(card, list):
            arena.buildings.extend(card)
        else:
            arena.buildings.append(card)