import random
import copy
import vector
from abstract_classes import TICK_TIME

class Bot:
    def __init__(self, cards):
        self.cards = cards
        self.internal_timer = random.triangular(0, 16.8, 8.4)

        self.min_elixir = 99
        for each in cards:
            if each.elixir_cost < self.min_elixir:
                self.min_elixir = each.elixir_cost

    def tick(self, elixir):
        if self.internal_timer <= 0 or elixir >= 9:
            self.internal_timer = random.triangular(0, 14, 5.6)

            if (elixir >= self.min_elixir):            
                selected = random.choice(self.cards)
                while selected.elixir_cost > elixir:
                    selected = random.choice(self.cards)
                return selected
            else:
                return None
        else:
            self.internal_timer -= TICK_TIME

    def random_pos(isSpell = False, things = None):
        if (isSpell):
            if not things is None:
                enemy = []
                for each in things:
                    if each.side:
                        enemy.append(each)
                if len(enemy) > 0:
                    return copy.deepcopy(random.choice(enemy).position)
            return vector.Vector(random.randint(-9, 9), random.randint(-10, -7))
        else:
            return vector.Vector(random.randint(-9, 9), random.randint(0, 16))

    
    
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