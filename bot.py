import random
import copy
import vector
from abstract_classes import TICK_TIME

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

    def tick(self, elixir):
        if self.internal_timer <= 0 or elixir >= 9:
            if elixir >= 7:
                self.internal_timer = 0
            else:
                self.internal_timer = random.triangular(0, 14, 5.6)

            cur_min = 11
            for each in self.cards:
                if each.name not in self.buffer and each.elixir_cost < cur_min:
                    cur_min = each.elixir_cost
            if elixir >= cur_min:
                selected = random.choice(self.cards)
                while selected.elixir_cost > elixir or selected.name in self.buffer:
                    selected = random.choice(self.cards)
                
                if len(self.buffer) < self.buffer_check:
                    self.buffer.append(selected.name)
                else:
                    self.buffer.pop(0)
                    self.buffer.append(selected.name)
                return selected
            else:
                return None
        else:
            self.internal_timer -= TICK_TIME

    def random_pos(isSpell = False, things = None):
        enemy = []
        friendly = []
        if not things is None:
            for each in things:
                    if each.side:
                        enemy.append(each)
                    else:
                        friendly.append(each)
        if (isSpell):
            if len(enemy) > 0:
                r = random.choice(enemy)
                if r.cur_hp < 400: #cannot use rocket properly
                    return copy.deepcopy(r.position)
            return False
        else:
            offensive_count = 0
            left_count = 0
            for each in enemy:
                if each.position.y > 0:
                    offensive_count += 1
                if each.position.x < 0:
                    left_count += 1

            if offensive_count > len(enemy) - offensive_count: # if more offensive opps than defensive
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
                return vector.Vector(round(random.triangular(-9, 9, weight)), random.randint(0, 16))
            else: # if more defensive opps than offensive, or equal
                if len(friendly) > 0 and random.random() < 0.8:
                    friend_pos = random.choice(friendly).position
                    friend_pos = friend_pos.added(vector.Vector(random.randint(-1, 1), random.randint(0, 4)))

                    if friend_pos.x > 9:
                        friend_pos.x = 9
                    elif friend_pos.x < -9:
                        friend_pos.x = -9
                    
                    
                    if friend_pos.y < 0:
                        friend_pos.y = 0
                    if friend_pos.y > 16:
                        friend_pos.y = 16

                    return friend_pos
                #if illegal friend pos for any reason
                weight = -4.5 if left_count < len(enemy) - left_count else 4.5 #towards left if more troops on right else left
                return vector.Vector(round(random.triangular(-9, 9, weight)), random.randint(0, 16))


    
    
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