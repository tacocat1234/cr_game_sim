import random
import copy
import math
import statistics
import vector
from abstract_classes import TICK_TIME
from abstract_classes import Troop
from card_factory import elixir_map, get_radius
from card_factory import champions
from builders_workshop_cards import Mortar
from hog_mountain_cards import XBow
from card_factory import can_defend

single_elixir_map = {
    "speargoblin" : 2/3,
    "goblin" : 1/2,
    "rascalboy" : 3,
    "rascalgirl" : 1,
    "skeleton" : 1/3,
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
    "lavapup" : 5/6
}

def get_elixir(name):
    mod = 1
    if name.startswith("evolution"):
        name = name[9:]
        mod = 4/3
    if name in elixir_map:
        return elixir_map[name] * mod
    elif name in single_elixir_map:
        return single_elixir_map[name] * mod
    else:
        return 0


spell_damage = {
    "freeze":115,
    "tornado":168,
    "goblincurse":183,
    "zap":192,
    "giantsnowball":192,
    "rage":192,
    "barbarianbarrel":241,
    "earthquake":246,
    "log":290,
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
    def __init__(self, cards):
        self.cards = cards
        random.shuffle(self.cards)

        self.hand = [0, 1, 2, 3]
        self.queue = [4, 5, 6, 7]

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
                if card.name == "barbarianbarrel":
                    pos = target
                    if pos.y < -4.7:
                        return None
                    elif pos.y < 0:
                        pos.y = 1
                elif card.name == "log":
                    pos = target
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

        goal = "wait" if elixir < 8 else "place"
        threat = None
        threat_level = 0

        main = None
        main_threat_level = 0
        if things:
            attack_investment = 0
            defense_investment = 0
            for each in things:
                e = get_elixir(each.__class__.__name__.lower())
                if not each.side: #bot's
                    if each.position.y < 2 and isinstance(each, XBow) or isinstance(each, Mortar):
                        main_threat_level = 10
                        main = each
                    if each.position.y > 0: #defending
                        defense_investment += e
                    else: #attacking
                        attack_investment += e
                        if e > main_threat_level:
                            main_threat_level = e
                            main = each
                else:
                    if each.position.y > -2 and isinstance(each, XBow) or isinstance(each, Mortar):
                        threat_level = 10
                        threat = each
                    if each.position.y > 0: #attacking
                        defense_investment -= e
                        if e > threat_level:
                            threat_level = e
                            threat = each
                    else: #defending
                        attack_investment -= e

            if defense_investment < -2: #3+ more elixir of attackers than defenders
                goal = "defend"
            elif attack_investment > -2: # if they only have 2 or less more elixir of defenders tahn our attackers
                goal = "attack"

        if goal == "wait":
            if random.random() < 1/1600:
                pos = vector.Vector(random.randint(-9, 8) + 0.5, random.randint(1, 15) + 0.5)
                l = [0, 1, 2, 3]
                i = random.choice(l)
                card = self.cards[self.hand[i]]
                while  card.elixir_cost > elixir or n == "log" or n == "barbarianbarrel" or card.type == "spell" or (card.type == "building" and (card.name != "mortar" and card.name != "xbow" and card.name != "goblindrill")) and l:
                    l.remove(i)
                    if not l: #if all spells or builidngs
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
            if random.random() > 0.5:
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
                    return card, pos
                elif card.type == "builidng":
                    pos = vector.Vector(random.randint(-3, 3), random.randint(2, 7))
                    return card, pos

                if card.elixir_cost > 7 or card.elixir_cost <= 5:
                    cycle(self.hand, self.hand.index(i), self.queue, self.champion_index)
                    return card, vector.Vector(-0.5 + random.random(), 15.5) #place in back
                else:
                    p = random.randint(0, 2)
                    cycle(self.hand, self.hand.index(i), self.queue, self.champion_index)
                    if p == 0:               
                        return card, vector.Vector(-0.5 + random.random(), 15.5) #place in back
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
            l = [0, 1, 2, 3]
            i = random.choice(l)
            card = self.cards[self.hand[i]]
            while card.elixir_cost > elixir or (card.type == "spell" or not can_defend(card.name)) and l:
                l.remove(i)
                if not l: #if all spells or cant defend
                    i = random.randint(0, 3)
                    card = self.cards[self.hand[i]] if card.elixir_cost <= elixir else None #pick random
                    if card is None:
                        return None
                    break
                i = random.choice(l)
                card = self.cards[self.hand[i]]

            cycle(self.hand, i, self.queue, self.champion_index)

            pos = None
            if card.type == "building" and threat.position.y < 5:
                pos = vector.Vector(0.5 + random.randint(0, 2) if threat.position.x > 0 else -0.5 - random.randint(0, 2), round(threat.position.y + 2) + 0.5)
            else:
                pos = threat.position.added(vector.Vector(random.randint(-2, 2), random.randint(1, 4)))
                in_p = (pocket == "all" or (pos.x < 0 and pocket == "left") or (pos.x >= 0 and pocket == "right"))
                if in_p and pos.y < -5:
                    pos.y = -5
                elif not in_p and pos.y < 1:
                    pos.y = 1
                return card, pos

            return card, pos
        else:
            l = [0, 1, 2, 3]
            i = random.choice(l)
            card = self.cards[self.hand[i]]
            while card.elixir_cost > elixir or n == "log" or n == "barbarianbarrel" or (card.type == "spell" and card.name != "clone" and card.name != "rage" and card.name != "graveyard" and card.name != "goblinbarrel") or (card.type == "building" and card.name != "goblindrill") and l:
                l.remove(i)
                if not l: #if all spells or builidngs or too expesnive
                    card = None
                    return None
                i = random.choice(l)
                card = self.cards[self.hand[i]]

            if card is not None:
                cycle(self.hand, i, self.queue, self.champion_index)

                base_pos = main.position if main is not None else vector.Vector(random.randint(-9, 8) + 0.5, random.randint(1, 15) + 0.5)

                if card.name == "clone" or card.name == "rage" and main is not None:
                    pos = base_pos.added(vector.Vector(0, 2))
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
                    return card, pos
                elif card.name == "graveyard":
                    pos = None
                    if pocket == "none":
                        pos = vector.Vector(-8.5 if random.random() > 0.5 else 8.5, -9.5)
                    elif pocket == "left":
                        pos = vector.Vector(8.5, -9.5)
                    elif pocket == "right":
                        pos = vector.Vector(-8.5, -9.5)
                    elif pocket == "all":
                        pos = vector.Vector(0.5, -15.5)
                    return card, pos

                pos = base_pos.added(vector.Vector(random.randint(-2, 2), random.randint(0, 4)))
                in_p = (pocket == "all" or (pos.x < 0 and pocket == "left") or (pos.x >= 0 and pocket == "right"))
                if in_p and pos.y < -5:
                    pos.y = -5
                elif not in_p and pos.y < 1:
                    pos.y = 1
                if pos.y > 15.5:
                    pos.y = 15.5
                return card, pos
            else:
                return None
            
            
