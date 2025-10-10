import pygame
import random
from cards import Card
from abstract_classes import TICK_TIME
from card_factory import get_radius
from card_factory import can_anywhere
from card_factory import generate_random_deck
from card_factory import can_evo
from card_factory import champions
import arena
import deck_select
import deck_select_4c
import triple_draft_2p
import draft_2p
import megadraft_2p
import lobby
import towers
import vector
import math
import deck_save

from electro_valley_cards import Log
from jungle_arena_cards import BarbarianBarrel

game_arena = arena.Arena()
image_cache = {}

def load_image(path):
    if not path in image_cache:
        image = pygame.image.load(path).convert_alpha()
        image_cache[path] = image
    return image_cache[path]

deck = []
bot_deck = []


KING_LEVEL = PRINCESS_LEVEL = BOT_K_L = BOT_P_L = 0
TOWER_TYPE = BOT_TOWER_TYPE = ""
player_random_deck = False
bot_random_deck = False
    
used = []
'''
# Load Player Deck
with open("decks/deck.txt", "r") as file:
    for _ in range(8):
        line = file.readline().strip()
        if line:
            err = False
            try:
                card, level = line.rsplit(" ", 1)
            except:
                err = True
            if err:
                raise Exception("you typed \"" + line + "\" you forgot to type the level")
            if card == "allrandom":
                player_random_deck = True
                KING_LEVEL = PRINCESS_LEVEL = int(level)
                TOWER_TYPE = random.choice(["princesstower", "cannoneer", "daggerduchess", "royalchef"])
                break
            is_evo, actual = parse_input(card, used)
            used.append(actual)
            deck.append(Card(True, actual, int(level), is_evo))

    if not player_random_deck:
        line = file.readline().strip()
        if line:
            _, KING_LEVEL = line.rsplit(" ", 1)
            KING_LEVEL = int(KING_LEVEL)

        line = file.readline().strip()
        if line:
            TOWER_TYPE, PRINCESS_LEVEL = line.rsplit(" ", 1)
            PRINCESS_LEVEL = int(PRINCESS_LEVEL)

used = []

# Load Bot Deck
with open("decks/bot_deck.txt", "r") as file:
    for _ in range(8):
        line = file.readline().strip()
        if line:
            card, level = line.rsplit(" ", 1)
            if card == "allrandom":
                bot_random_deck = True
                BOT_K_L = BOT_P_L = int(level)
                BOT_TOWER_TYPE = random.choice(["princesstower", "cannoneer", "daggerduchess", "royalchef"])
                break
            _, actual = parse_input(card, used)
            used.append(actual)
            bot_deck.append(Card(True, actual, int(level), can_evo(actual)))

    if not bot_random_deck:
        line = file.readline().strip()
        if line:
            _, BOT_K_L = line.rsplit(" ", 1)
            BOT_K_L = int(BOT_K_L)

        line = file.readline().strip()
        if line:
            BOT_TOWER_TYPE, BOT_P_L = line.rsplit(" ", 1)
            BOT_P_L = int(BOT_P_L)

'''

#height comp screen ~ 800
#20x20 per tile
# 18 x 32
BUFFER = 256
FULL_WIDTH = (360 + 128) * 2 + BUFFER
WIDTH, HEIGHT = 360 + 128, 640 + 128

SCALE = 20  # Scale factor to map game coordinates to screen

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
R_RED = (255, 0, 150)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
R_BLUE = (150, 0, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
R_GRAY = (255, 150, 255)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)
GRAY_PURPLE = (255, 150, 255)

BG_TEMP = (150, 150, 150)
RIVER_TEMP = (79, 66, 181)
BRIDGE_TEMP = (193, 154, 107)

def raged_color(color):
    if color == BLUE:
        return R_BLUE
    elif color == RED:
        return R_RED
    elif color == GRAY:
        return R_GRAY
    else:
        return color

def format_time(seconds):
    if seconds >= 180:
        sec = 300 - seconds
    else:
        sec = 180 - seconds
    m = str(int((sec // 60)))
    s = round(sec % 60)
    s = str(s) if s >= 10 else "0" + str(s)
    return m + ":" + s

def is_beam(attack):
    return attack.__class__.__name__.lower() in [
        "goblinsteinabilityattackentity", 
        "infernodragonattackentity", 
        "electrowizardattackentity", 
        "infernotowerattackentity", 
        "zappyattackentity", 
        "teslaattackentity"
    ]

def convert_to_pygame(coordinate, side):
    pygame_x = int(WIDTH / 2 + coordinate.x * SCALE) + (0 if side else WIDTH + BUFFER)
    pygame_y = int(HEIGHT / 2 - 64 - coordinate.y * SCALE)  # Invert Y-axis 
    if not side:
        pygame_y = HEIGHT - 128 - pygame_y
    return pygame_x, pygame_y

def convert_from_pygame(pygame_x, pygame_y, side): #using trueblue
    x = (pygame_x - WIDTH / 2 - (0 if side else WIDTH + BUFFER)) // SCALE + 0.5
    y = (HEIGHT / 2 - 64 - pygame_y) // SCALE + 0.5# Invert Y-axis back
    if not side:
        y = -y
    return vector.Vector(x, y)

def in_pocket(x, y, isRight): #360 + 128, 640 + 128
    if isRight:
        return (x > 244 and x < 424 and y > 11 * SCALE and y < 15 * SCALE) or (x > 334 and x < 374 and y > 300 and y < 340)
    else:
        return (x > 64 and x < 244 and y > 11 * SCALE and y < 15 * SCALE) or (x > 114 and x < 154 and y > 300 and y < 340)

pygame.init()
screen = pygame.display.set_mode((FULL_WIDTH, HEIGHT))
pygame.display.set_caption("Crash Royale Arena")    
font = pygame.font.Font(None, 12) 
background_img = pygame.image.load("sprites/background.png").convert_alpha()
select_img = pygame.image.load("sprites/tileselect.png").convert_alpha()
dd_symbol_img = pygame.image.load("sprites/daggerduchess/duchess_symbol.png").convert_alpha()
rc_symbol_img = pygame.image.load("sprites/royalchefkingtower/royalchef_symbol.png").convert_alpha()
elixir_int_img = pygame.image.load("sprites/elixir_bar.png").convert_alpha()
timer_images = []
for i in range(9):
    img = pygame.image.load(f"sprites/timer/timer_{i}.png").convert_alpha()
    w, h = img.get_size()
    img = pygame.transform.scale(img, (w // 2.5, h // 2.5))  # scale to 1/2 size
    timer_images.append(img)
timer_images_red = []
for i in range(9):
    img = pygame.image.load(f"sprites/timer_red/timer_{i}.png").convert_alpha()
    w, h = img.get_size()
    img = pygame.transform.scale(img, (w // 2.5, h // 2.5))  # scale to 1/2 size
    timer_images_red.append(img)
loss_images = [pygame.image.load(f"sprites/elixir_loss/{i + 1}.png").convert_alpha() for i in range (10)]


#temp
#game_arena.troops.append(training_camp_cards.Giant(True, vector.Vector(-2, -3)
#game_arena.troops.append(training_camp_cards.Archer(True, vector.Vector(-3, -4)
#game_arena.troops.append(training_camp_cards.Giant(False, vector.Vector(-3, 3)
#game_arena.troops.append(training_camp_cards.MiniPekka(True, vector.Vector(-3, -4)
#temp

p1_c_index = None
p2_c_index = None

def cycle(hand, index, queue, side):
    i = hand[index]

    if side:
        if deck[i] is p_champion:
            global p1_c_index
            p1_c_index = i
        else:
            queue.append(hand[index])
    else:
        if deck[i] is b_champion:
            global p2_c_index
            p2_c_index = i
        else:
            queue.append(hand[index])

    hand[index] = queue.pop(0)

def four_card_cycle(hand, index, hand_delay):
    i = hand[index]
    hand[index] = -1
    hand_delay[i] = 0.3

def process_hand_delay(hand, hand_delay):
    for i in range(4):
        hand_delay[i] -= TICK_TIME
        if hand_delay[i] < 0 and hand_delay[i] != -1:
            hand_delay[i] = -1
            hand[i] = i

def display_evo_cannon(pos, side): #pos is accurate
    all = [
        vector.Vector(2.5, pos.y + (1.5 if side else -1.5)), #true position
        vector.Vector(-2.5, pos.y + (1.5 if side else -1.5)), 
        vector.Vector(7.5, pos.y + (1.5 if side else -1.5)),
        vector.Vector(-7.5, pos.y + (1.5 if side else -1.5)),
        vector.Vector(0, pos.y + (8.5 if side else -8.5)), 
        vector.Vector(4.5, pos.y + (8.5 if side else -8.5)),
        vector.Vector(-4.5, pos.y + (8.5 if side else -8.5)),
        vector.Vector(8.5, pos.y + (8.5 if side else -8.5)),
        vector.Vector(-8.5, pos.y + (8.5 if side else -8.5))
    ]

    for each in all:
        pygame.draw.circle(screen, (224, 255, 232), convert_to_pygame(each, side), 1.5 * SCALE, width=1)

def draw(side):

    offset = BUFFER + WIDTH if not side else 0

    if side:
        screen.fill(BG_TEMP)
        pygame.draw.rect(screen, (0, 0, 0), (WIDTH, 0, BUFFER, HEIGHT))
    bg_rect = background_img.get_rect(center=(WIDTH / 2 + offset, (HEIGHT - 128) / 2))
    screen.blit(background_img, bg_rect)
    # Draw river
    pygame.draw.rect(screen, RIVER_TEMP, (offset, HEIGHT/2 - 64 - SCALE, WIDTH, SCALE * 2)) 
   
    #draw card area
    pygame.draw.rect(screen, GRAY, (offset, HEIGHT - 128, WIDTH, 128))

    #Draw bridges
    pygame.draw.rect(screen, BRIDGE_TEMP, (64 + 2.5 * SCALE + offset, HEIGHT/2 - 64 - 1.5 * SCALE, SCALE * 2, SCALE * 3)) 
    pygame.draw.rect(screen, BRIDGE_TEMP, (WIDTH - (64 + 4.5 * SCALE) + offset, HEIGHT/2 - 64 - 1.5 *SCALE, SCALE * 2, SCALE * 3)) 

    #Time Left:
    #format_time(game_arena.timer)
    #game_arena.state

    

    #draw hovered
    hov = hovered if side else hovered2
    if not hov is None:
        screen.blit(select_img, (hov[0], hov[1]))
        s_r = select_radius if side else select_radius2
        if not s_r is None:
            if s_r == 10.1:
                #1.95 * 2 * SCALE wide, 10.1 * SCALE long, bottom center is hovered[0] + 10, hovered[1] + 10
                width = 1.95 * 2 * SCALE
                height = 10.6 * SCALE
                bottom_center_x = hov[0] + 10
                bottom_center_y = hov[1] + 20
                top_left_x = bottom_center_x - width / 2
                top_left_y = bottom_center_y - height
                pygame.draw.rect(screen, (224, 255, 232), (top_left_x, top_left_y, width, height), width=1)
            elif s_r == 4.6:
                #1.3 * 2 * SCALE wide, 10.1 * SCALE long, bottom center is hovered[0] + 10, hovered[1] + 10
                width = 1.3 * 2 * SCALE
                height = 5 * SCALE
                bottom_center_x = hov[0] + 10
                bottom_center_y = hov[1] + 20
                top_left_x = bottom_center_x - width / 2
                top_left_y = bottom_center_y - height
                pygame.draw.rect(screen, (224, 255, 232), (top_left_x, top_left_y, width, height), width=1)
                        
            elif isinstance(s_r, list):
                h = hovered if side else hovered2
                for each in s_r:
                    pygame.draw.circle(screen, (224, 255, 232), (h[0] + 10, h[1] + 10), each * SCALE, width=1)
            else:
                d = deck if side else bot_deck
                h = hand if side else hand2
                c_q = click_quarter if side else click_quarter2
                hov = hovered if side else hovered2
                pygame.draw.circle(screen, (224, 255, 232), (hov[0] + 10, hov[1] + 10), s_r * SCALE, width=1)
                if d[h[c_q - 1]].name == "cannon" and d[h[c_q - 1]].cycles_left == 0:
                    display_evo_cannon(convert_from_pygame(0, hov[1], side), side)
    
    if side:
        if not drag_start_pos is None:
            cur_name = deck[hand[click_quarter - 1]].name

            if cur_name == "mirror" and p_prev is not None:
                cur_name = p_prev.name

            if not can_anywhere(cur_name):
                place_surface = pygame.Surface((488, 340), pygame.SRCALPHA)

                pygame.draw.rect(place_surface, (238, 75, 43, 128), pygame.Rect(64, 0, 360, 220))
                if false_has_right:
                    pygame.draw.rect(place_surface, (238, 75, 43, 128), pygame.Rect(244, 220, 180, 120))
                if false_has_left:
                    pygame.draw.rect(place_surface, (238, 75, 43, 128), pygame.Rect(64, 220, 180, 120))
                screen.blit(place_surface, (0,0))
    else:
        if not drag_start_pos2 is None:
            cur_name = bot_deck[hand2[click_quarter2 - 1]].name

            if cur_name == "mirror" and b_prev is not None:
                cur_name = b_prev.name

            if not can_anywhere(cur_name):
                place_surface = pygame.Surface((488, 340), pygame.SRCALPHA)

                pygame.draw.rect(place_surface, (238, 75, 43, 128), pygame.Rect(64, 0, 360, 220))
                if true_has_right:
                    pygame.draw.rect(place_surface, (238, 75, 43, 128), pygame.Rect(244, 220, 180, 120))
                if true_has_left:
                    pygame.draw.rect(place_surface, (238, 75, 43, 128), pygame.Rect(64, 220, 180, 120))
                screen.blit(place_surface, (offset,0))
    #draw time
    nfont = pygame.font.Font(None, 24)

    time_text = f"Time Left: {format_time(game_arena.timer)}"

    time_surface = nfont.render(time_text, True, (255, 255, 255))  # White text
    state_surface = nfont.render(game_arena.state, True, (255, 255, 255))

    # Position: top right with some padding
    padding = 10
    time_rect = time_surface.get_rect(topright=(WIDTH - padding + offset, padding))
    state_rect = state_surface.get_rect(topright=(WIDTH - padding + offset, padding + time_rect.height + 5))

    screen.blit(time_surface, time_rect)
    screen.blit(state_surface, state_rect)

    cfont = pygame.font.Font(None, 64)
    center_text = ""
    if game_arena.timer < 180 and game_arena.timer >= 170:
        center_text = str(round(180 - game_arena.timer))
    elif game_arena.timer < 300 and game_arena.timer >= 290:
        center_text = str(round(300 - game_arena.timer))
    elif game_arena.timer >= 300:
        center_text = "Tiebreaker"
    
    center_surface = cfont.render(center_text, True, (255, 255, 255))
    center_rect = center_surface.get_rect(center=(WIDTH/2 + offset, HEIGHT/2 - 64))

    screen.blit(center_surface, center_rect)

    if side:
        if game_arena.p1_champion is not None:
            ab_img = load_image(game_arena.p1_champion.ability_sprite_path)
            ab_rect = ab_img.get_rect(center=(WIDTH - 35 + offset, HEIGHT - 128 - 35))
            screen.blit(ab_img, ab_rect)
    else:
        if game_arena.p2_champion is not None:
            ab_img = load_image(game_arena.p2_champion.ability_sprite_path)
            ab_rect = ab_img.get_rect(center=(WIDTH - 35 + offset, HEIGHT - 128 - 35))
            screen.blit(ab_img, ab_rect)

    # Draw Towers
    for tower in game_arena.towers:
        tower_x, tower_y = convert_to_pygame(tower.position, side)
        
        # Adjust position so that the rectangle is centered at the tower's coordinates
        tower_rect_width = tower.collision_radius * SCALE * 2
        tower_rect_height = tower_rect_width
        tower_x -= tower_rect_width / 2
        tower_y -= tower_rect_height / 2

        tower_color = GRAY

        if tower.rage_timer > 0:
            tower_color = raged_color(tower_color)
        
        pygame.draw.rect(screen, (90, 100, 90), (tower_x - 10, tower_y - 10, tower_rect_width + 20, tower_rect_height + 20))  # Tower base
        pygame.draw.rect(screen, tower_color, (tower_x, tower_y, tower_rect_width, tower_rect_height))  # Tower square

        if tower.activated:
            #health text
            hpfont = pygame.font.Font(None, 16)
            hp_text = hpfont.render(str(int(tower.cur_hp)), True, WHITE)  # Convert HP to int and render in white
            text_rect = hp_text.get_rect(center=(tower_x + tower_rect_width / 2, tower_y - 10))
            screen.blit(hp_text, text_rect)

            # Health bar
            pygame.draw.rect(screen, BLACK, (tower_x - 5, tower_y - 5, tower_rect_width + 10, 3))
            pygame.draw.rect(screen, GREEN, (tower_x - 5, tower_y - 5, ((tower_rect_width + 10) * (tower.cur_hp / tower.hit_points)), 3))

        if tower.type == "dd":
            ammo_ratio = tower.ammo / 8
            pygame.draw.rect(screen, BLACK, (tower_x + 4, tower_y + 5, tower_rect_width - 2, 4))  # Background
            pygame.draw.rect(screen, YELLOW, (tower_x + 4, tower_y + 5, ((tower_rect_width - 2) * ammo_ratio), 4))  # Ammo bar
            screen.blit(dd_symbol_img, (tower_x - 7, tower_y))
        elif tower.type == "rckt":
            cooking_ratio = 1 - (tower.cooking_timer / 21)
            off = 50 if tower.side == side else 5
            pygame.draw.rect(screen, BLACK, (tower_x + 9, tower_y + off, tower_rect_width - 12, 4))  # Background
            pygame.draw.rect(screen, YELLOW, (tower_x + 9, tower_y + off, ((tower_rect_width - 12) * cooking_ratio), 4))  # Ammo bar
            screen.blit(rc_symbol_img, (tower_x - 3, tower_y + off - 8))
    
    for building in game_arena.buildings:
        if not (building.preplace and building.side != side):
            building_x, building_y = convert_to_pygame(building.position, side)
            building_color = BLUE if building.side == side else RED

            if building.preplace:
                building_color = GRAY
            elif not building.targetable:
                building_color = (255, 127, 127)

            if building.rage_timer > 0:
                building_color = raged_color(building_color)

            # Draw building square
            building_size = building.collision_radius * 2 * SCALE
            true_color = ((255, 0, 255) if building.rage_timer > 0 else (120, 0, 160)) if building.evo else building_color
            pygame.draw.rect(screen, true_color, (building_x - building_size / 2, building_y - building_size / 2, building_size, building_size))

            class_name = building.__class__.__name__
            text_surface = font.render(class_name, True, (255, 255, 255))  # White color text
            text_rect = text_surface.get_rect(center=(building_x, building_y))  # 10 pixels above the troop
            screen.blit(text_surface, text_rect)

            # Health bar
            hp_bar_x = building_x - 10
            hp_bar_y = building_y - 12 - building_size // 2  # Slightly above the building
            hp_bar_width = 20
            hp_bar_height = 3

            pygame.draw.rect(screen, BLACK, (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height))
            pygame.draw.rect(screen, GREEN, (hp_bar_x, hp_bar_y, int(hp_bar_width * (building.cur_hp / building.hit_points)), hp_bar_height))

            # Draw Level Indicator
            level_box_size = 10  # Square size for level indicator
            level_box_x = hp_bar_x - level_box_size - 2  # Slight padding to the left
            level_box_y = hp_bar_y - 2  # Align with HP bar

            pygame.draw.rect(screen, building_color, (level_box_x, level_box_y, level_box_size, level_box_size))

            if building.deploy_time > 0 and not building.preplace:
                ratio = max(0, min(1, 1 - building.deploy_time / 1))  # clamp between 0–1
                index = int(ratio * 8)  # 0 → timer_0, 1 → timer_8
                timer_img = timer_images[index] if building.side == side else timer_images_red[index]
                timer_rect = timer_img.get_rect(center=(building_x, building_y))
                screen.blit(timer_img, timer_rect)

            # Render level number text
            level_text = font.render(str(building.level), True, WHITE)  # White text
            text_rect = level_text.get_rect(center=(level_box_x + level_box_size / 2, level_box_y + level_box_size / 2))
            screen.blit(level_text, text_rect)


    # Draw Troops
    flying = []
    for troop in game_arena.troops:
        if troop.ground:
            if not (troop.preplace and troop.side != side):
                troop_x, troop_y = convert_to_pygame(troop.position, side)
                troop_color = GRAY if troop.preplace else (BLUE if troop.side == side else RED)

                if troop.rage_timer > 0:
                    troop_color = raged_color(troop_color)
                if troop.cloned:
                    troop_color = (troop_color[0], min(troop_color[1] + 160, 255), min(troop_color[2] + 160, 255))

                # Draw troop circle
                if isinstance(troop, Log) or isinstance(troop, BarbarianBarrel):
                    width = troop.collision_radius * SCALE
                    height = 1.2 * SCALE
                    rect_x = troop_x - width / 2
                    rect_y = troop_y - height / 2
                    pygame.draw.rect(screen, troop_color, pygame.Rect(rect_x, rect_y, width, height))
                    display_y = rect_y
                else:
                    true_color = ((255, 0, 255) if troop.rage_timer > 0 else (120, 0, 160)) if troop.evo else troop_color
                    circle_pos = (troop_x, troop_y)
                    circle_radius = int(troop.collision_radius * SCALE)

                    if not troop.targetable and (not troop.invulnerable or troop.__class__.__name__ == "EvolutionSkeletonArmy"):
                        # Make semi-transparent circle
                        temp_surface = pygame.Surface((circle_radius * 2, circle_radius * 2), pygame.SRCALPHA)
                        
                        # Draw circle on temp surface with 25% opacity
                        rgba_color = (*true_color, 64)  # 64/255 ≈ 25% opacity
                        
                        pygame.draw.circle(temp_surface, rgba_color, (circle_radius, circle_radius), circle_radius)
                        
                        # Blit temp surface to screen, adjust for offset
                        screen.blit(temp_surface, (troop_x - circle_radius, troop_y - circle_radius))
                    else:
                        # Draw normal opaque circle
                        pygame.draw.circle(screen, true_color, circle_pos, circle_radius)

                    # Text display position remains the same
                    display_y = troop_y - circle_radius
                class_name = troop.__class__.__name__
                text_surface = font.render(class_name, True, (255, 255, 255))  # White color text
                text_rect = text_surface.get_rect(center=(troop_x, troop_y))  # 10 pixels above the troop
                screen.blit(text_surface, text_rect)

                # Health bar
                hp_bar_x = troop_x - 10
                if isinstance(troop, Log) or isinstance(troop, BarbarianBarrel):
                    hp_bar_y = troop_y - 12
                else:
                    hp_bar_y = troop_y - troop.collision_radius * SCALE - 2
                hp_bar_width = 20
                hp_bar_height = 3

                if not troop.invulnerable:
                    pygame.draw.rect(screen, BLACK, (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height))
                    if troop.has_shield and troop.shield_hp > 0:
                        pygame.draw.rect(screen, (250, 250, 250), (hp_bar_x, hp_bar_y, int(hp_bar_width * (troop.shield_hp / troop.shield_max_hp)), hp_bar_height))
                    else:
                        pygame.draw.rect(screen, GREEN, (hp_bar_x, hp_bar_y, int(hp_bar_width * (troop.cur_hp / troop.hit_points)), hp_bar_height))
                        if troop.cur_hp > troop.hit_points:
                            pygame.draw.rect(screen, (0, 200, 255), (hp_bar_x + hp_bar_width, hp_bar_y, int(hp_bar_width * (troop.cur_hp / troop.hit_points - 1)), hp_bar_height))

                    

                # Draw Level Indicator
                level_box_size = 10  # Square size for level indicator
                level_box_x = hp_bar_x - level_box_size - 2  # Slight padding to the left
                level_box_y = hp_bar_y - 2  # Align with HP bar

                if troop.has_shield and troop.shield_hp > 0:
                    # Draw an upside-down triangle
                    top_left = (level_box_x - 0.5, level_box_y - 0.5)
                    top_right = (level_box_x + level_box_size + 0.5, level_box_y - 0.5)
                    bottom_right = (level_box_x + level_box_size + 0.5, level_box_y + level_box_size + 0.5)
                    bottom_left = (level_box_x - 0.5, level_box_y + level_box_size + 0.5)

                    # Define the bottom triangle point
                    triangle_tip = (level_box_x + level_box_size / 2, level_box_y + level_box_size + level_box_size / 2)

                    # Draw pentagon (square + downward triangle)
                    pygame.draw.polygon(screen, troop_color, [
                        top_left,          # Top-left corner
                        top_right,         # Top-right corner
                        bottom_right,      # Bottom-right corner
                        triangle_tip,      # Bottom center triangle tip
                        bottom_left        # Bottom-left corner
                    ])
                else:
                    # Draw square
                    pygame.draw.rect(screen, troop_color, (level_box_x, level_box_y, level_box_size, level_box_size))

                if troop.deploy_time > 0 and not troop.preplace:
                    ratio = max(0, min(1, 1 - troop.deploy_time / 1))  # clamp between 0–1
                    index = int(ratio * 8)  # 0 → timer_0, 1 → timer_8
                    timer_img = timer_img = timer_images[index] if troop.side == side else timer_images_red[index]
                    timer_rect = timer_img.get_rect(center=(troop_x, troop_y))
                    screen.blit(timer_img, timer_rect)

                # Render level number text 
                level_text = font.render(str(troop.level), True, WHITE)  # White text
                text_rect = level_text.get_rect(center=(level_box_x + level_box_size / 2, level_box_y + level_box_size / 2))
                screen.blit(level_text, text_rect)

                if troop.__class__.__name__ == "SkeletonKing" and troop.amount > 6:
                    hp_bar_y -= 10
                    hp_bar_width = 20
                    hp_bar_height = 3

                    pygame.draw.rect(screen, BLACK, (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height))
                    pygame.draw.rect(screen, (60, 200, 220), (hp_bar_x, hp_bar_y, int(hp_bar_width * (troop.amount / troop.amount_max)), hp_bar_height))
        else:
            flying.append(troop)
    # Draw Attack Entities (Projectiles)

    for troop in flying:
        if not (troop.preplace and troop.side != side):
            troop_x, troop_y = convert_to_pygame(troop.position, side)
            troop_color = GRAY if troop.preplace else (BLUE if troop.side == side else RED)
            if troop.rage_timer > 0:
                troop_color = raged_color(troop_color)
            if troop.cloned:
                troop_color = (troop_color[0], min(troop_color[1] + 160, 255), min(troop_color[2] + 160, 255))

            # Draw troop circle
            true_color = ((255, 0, 255) if troop.rage_timer > 0 else (120, 0, 160)) if troop.evo else troop_color
            pygame.draw.circle(screen, true_color, (troop_x, troop_y), troop.collision_radius * SCALE)
            display_y = troop_y - troop.collision_radius * SCALE  # Use circle's top for text position
            class_name = troop.__class__.__name__
            text_surface = font.render(class_name, True, (255, 255, 255))  # White color text
            text_rect = text_surface.get_rect(center=(troop_x, display_y + 10))  # 10 pixels above the troop
            screen.blit(text_surface, text_rect)

            # Health bar
            hp_bar_x = troop_x - 10
            hp_bar_y = troop_y - 12
            hp_bar_width = 20
            hp_bar_height = 3

            if not troop.invulnerable:
                pygame.draw.rect(screen, BLACK, (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height))
                if troop.has_shield and troop.shield_hp > 0:
                    pygame.draw.rect(screen, (250, 250, 250), (hp_bar_x, hp_bar_y, int(hp_bar_width * (troop.shield_hp / troop.shield_max_hp)), hp_bar_height))
                else:
                    pygame.draw.rect(screen, GREEN, (hp_bar_x, hp_bar_y, int(hp_bar_width * (troop.cur_hp / troop.hit_points)), hp_bar_height))
                    if troop.cur_hp > troop.hit_points:
                        pygame.draw.rect(screen, (0, 90, 255), (hp_bar_x + hp_bar_width, hp_bar_y, int(hp_bar_width * (troop.cur_hp / troop.hit_points - 1)), hp_bar_height))

                

            # Draw Level Indicator
            level_box_size = 10  # Square size for level indicator
            level_box_x = hp_bar_x - level_box_size - 2  # Slight padding to the left
            level_box_y = hp_bar_y - 2  # Align with HP bar

            if troop.has_shield and troop.shield_hp > 0:
                # Draw an upside-down triangle
                top_left = (level_box_x - 0.5, level_box_y - 0.5)
                top_right = (level_box_x + level_box_size + 0.5, level_box_y - 0.5)
                bottom_right = (level_box_x + level_box_size + 0.5, level_box_y + level_box_size + 0.5)
                bottom_left = (level_box_x - 0.5, level_box_y + level_box_size + 0.5)

                # Define the bottom triangle point
                triangle_tip = (level_box_x + level_box_size / 2, level_box_y + level_box_size + level_box_size / 2)

                # Draw pentagon (square + downward triangle)
                pygame.draw.polygon(screen, troop_color, [
                    top_left,          # Top-left corner
                    top_right,         # Top-right corner
                    bottom_right,      # Bottom-right corner
                    triangle_tip,      # Bottom center triangle tip
                    bottom_left        # Bottom-left corner
                ])
            else:
                # Draw square
                pygame.draw.rect(screen, troop_color, (level_box_x, level_box_y, level_box_size, level_box_size))

            if troop.deploy_time > 0 and not troop.preplace:
                ratio = max(0, min(1, 1 - troop.deploy_time / 1))  # clamp between 0–1
                index = int(ratio * 8)  # 0 → timer_0, 1 → timer_8
                timer_img = timer_img = timer_images[index] if troop.side == side else timer_images_red[index]
                timer_rect = timer_img.get_rect(center=(troop_x, troop_y))
                screen.blit(timer_img, timer_rect)

            # Render level number text 
            level_text = font.render(str(troop.level), True, WHITE)  # White text
            text_rect = level_text.get_rect(center=(level_box_x + level_box_size / 2, level_box_y + level_box_size / 2))
            screen.blit(level_text, text_rect)

    

    for attack in game_arena.active_attacks:
        attack_x = attack_y = None
        if not side and attack.__class__.__name__ == "EvolutionCannonSpecialAttackEntity":
            attack_x, attack_y= convert_to_pygame(attack.mirrored_position, side)
        else:
            attack_x, attack_y= convert_to_pygame(attack.position, side)

        if is_beam(attack):
            attack_x2, attack_y2 = convert_to_pygame(attack.target.position, side)
            pygame.draw.line(
                screen,
                YELLOW,
                (attack_x, attack_y),
                (attack_x2, attack_y2),
                int(attack.display_size * SCALE)
            )
        elif attack.__class__.__name__.lower() == "goblinmachinetargetindicator":
            pygame.draw.circle(screen, (224, 255, 232), (attack_x, attack_y), 1.2 * SCALE, width=1)
        elif attack.__class__.__name__.lower() == "evolutionbabydragonwindentity":
            attack_size = 8*SCALE
            attack_surface = pygame.Surface((attack_size * 2, attack_size * 2), pygame.SRCALPHA)
            rect = pygame.Rect(0, 0, attack_size, attack_size)
            rect.center = (attack_size // 2, attack_size // 2)
            pygame.draw.rect(attack_surface, (0, 200, 200, 60), rect)
            screen.blit(attack_surface, (attack_x - attack_size//2, attack_y - attack_size//2))    
        elif attack.display_size != 0.25 and attack.resize == False:
            # Create a transparent surface
            attack_size = attack.display_size * SCALE
            attack_surface = pygame.Surface((attack_size * 2, attack_size * 2), pygame.SRCALPHA)
            
            # Draw a semi-trfansparent yellow circle
            c =  (60, 255, 60, 128) if attack.__class__.__name__.lower() == "vinesdisplayentity" else  (255, 255, 0, 128)
            pygame.draw.circle(attack_surface, c, (attack_size, attack_size), attack_size)
            
            # Blit the surface onto the screen
            screen.blit(attack_surface, (attack_x - attack_size, attack_y - attack_size))
        else:
            # Regular solid yellow circle for small attacks
            pygame.draw.circle(screen, YELLOW, (attack_x, attack_y), attack.display_size * SCALE)
    for spell in game_arena.spells:
        if not (spell.preplace and spell.side != side):
            if spell.preplace:
                spell_x, spell_y = convert_to_pygame(spell.target_pos, side)
                size = spell.radius * SCALE
                spell_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)  # Creating transparent surface
                
                # Fill the surface with the purple color and set transparency (alpha channel)
                pygame.draw.circle(spell_surface, (128, 128, 128, 128), (size, size), size)
                # Draw the surface onto the screen at the correct position
                screen.blit(spell_surface, (spell_x - size, spell_y - size))  # Centering the spell's circle
            else:
                spell_x, spell_y = convert_to_pygame(spell.position, side)
                is_gs = spell.__class__.__name__ == "EvolutionGiantSnowball"
                size = spell.radius * SCALE if not is_gs and spell.spawn_timer <= 0 else 1 * SCALE


                if spell.spawn_timer <= 0 and not is_gs:
                    # Partially transparent when the spell has spawned
                    # Create a surface to represent the spell
                    spell_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)  # Creating transparent surface
                    
                    # Fill the surface with the purple color and set transparency (alpha channel)
                    pygame.draw.circle(spell_surface, (128, 0, 128, 128), (size, size), size)
                    # Draw the surface onto the screen at the correct position
                    screen.blit(spell_surface, (spell_x - size, spell_y - size))  # Centering the spell's circle
                else:
                    # Non-transparent when the spell is in its "flying" phase (spawn_timer > 0)
                    pygame.draw.circle(screen, PURPLE, (spell_x, spell_y), size)
                class_name = spell.__class__.__name__
                text_surface = font.render(class_name, True, (255, 255, 255))  # White color text
                text_rect = text_surface.get_rect(center=(spell_x, spell_y))  # 10 pixels above the troop
                screen.blit(text_surface, text_rect)

    for tracker in game_arena.elixir_trackers:
        if tracker.side == side:
            timer_img = loss_images[tracker.amount - 1]

            # scale factor based on tracker.timer (0 → shrink, 1 → grow)
            # at 0.5 → normal size (1.0 scale)
            a = 1.7
            scale = -(a*(tracker.timer - (1 - 1/a)))**4 + 1
            off = (scale - 1) * (1 if side else -1)

            # calculate new size
            new_size = (
                int(timer_img.get_width() * scale),
                int(timer_img.get_height() * scale)
            )

            # resize the image
            scaled_img = pygame.transform.smoothscale(timer_img, new_size)

            # keep image centered
            timer_rect = scaled_img.get_rect(
                center=convert_to_pygame(vector.Vector(tracker.x, tracker.y + off), side)
            )

            screen.blit(scaled_img, timer_rect)
        
    card_name_font = pygame.font.Font(None, 24)  # Use a larger font for card names
    
    h = hand if side else hand2
    for i, hand_i in enumerate(h):
        if hand_i == -1:
            continue
        card = deck[hand_i] if side else bot_deck[hand_i]
        card_name_text = card_name_font.render(card.name, True, BLACK)
        card_name_x = (WIDTH * (i + 1)) // 5  + offset# Positions: WIDTH/5, WIDTH*2/5, WIDTH*3/5, WIDTH*4/5
        card_name_y = HEIGHT - 64  # Vertical position at the bottom
        text_rect = card_name_text.get_rect(center=(card_name_x, card_name_y))
        screen.blit(card_name_text, text_rect)

        if side:
            if (card.name == "mirror") and p_prev is not None:
                mirror_text = card_name_font.render("(" + p_prev.name + ")", True, BLACK) #nono, accessing global in local function but easiest
                text_rect = mirror_text.get_rect(center=(card_name_x, card_name_y + 15))
                screen.blit(mirror_text, text_rect)
        else:
            if (card.name == "mirror") and b_prev is not None:
                mirror_text = card_name_font.render("(" + b_prev.name + ")", True, BLACK) #nono, accessing global in local function but easiest
                text_rect = mirror_text.get_rect(center=(card_name_x, card_name_y + 15))
                screen.blit(mirror_text, text_rect)

        elixir_cost_circle_x = card_name_x + 30  # Position at the end of the elixir bar
        elixir_cost_circle_y = card_name_y - 30  # Align with the bar
        elixir_cost_circle_radius = 12  # Size of the circle

        if card.is_evo:
            all = card.cycles
            full = all - card.cycles_left
            radius = 6
            color = (150, 0, 200)
            background_color = (60, 60, 60)

            # Circle layout setup
            spacing = 2 * radius + 4  # Space between circles
            total_width = (all - 1) * spacing
            start_x = card_name_x - total_width // 2
            y = card_name_y - 60  # 50 units above

            # Calculate rectangle bounds
            rect_padding = 4
            rect_width = total_width + 2 * radius + rect_padding * 2
            rect_height = 2 * radius + rect_padding * 2
            rect_x = start_x - radius - rect_padding
            rect_y = y - radius - rect_padding

            # Draw rectangle background
            pygame.draw.rect(screen, background_color, (rect_x, rect_y, rect_width, rect_height), border_radius=4)

            # Draw evolution progress circles
            for j in range(all):
                circle_color = color if j < full else BLACK
                x = start_x + j * spacing
                pygame.draw.circle(screen, circle_color, (x, y), radius)
        pygame.draw.circle(screen, PURPLE, (elixir_cost_circle_x, elixir_cost_circle_y), elixir_cost_circle_radius)  # Draw elixir circle

        # Render the elixir amount text
        elixir_text = card_name_font.render(str(card.elixir_cost), True, WHITE)
        text_rect = elixir_text.get_rect(center=(elixir_cost_circle_x, elixir_cost_circle_y))
        screen.blit(elixir_text, text_rect)  # Display elixir text

    elixir_amount = game_arena.p1_elixir if side else game_arena.p2_elixir
    #draw elixir bar
    elixir_bar_height = 15  
    elixir_bar_width = int((elixir_amount / 10) * WIDTH)  
    elixir_bar_int_width = max((math.floor(elixir_amount) / 10) * WIDTH, 0)

    pygame.draw.rect(screen, PURPLE, (offset, HEIGHT - elixir_bar_height - 10, elixir_bar_int_width, elixir_bar_height))

    # Draw the GRAY_PURPLE portion (fractional elixir)
    if elixir_bar_width > elixir_bar_int_width:
        pygame.draw.rect(screen, GRAY_PURPLE, (elixir_bar_int_width + offset, HEIGHT - elixir_bar_height - 10,
                                            elixir_bar_width - elixir_bar_int_width, elixir_bar_height))
        
    e_rect = elixir_int_img.get_rect(midtop=(WIDTH // 2 + offset, HEIGHT - elixir_bar_height - 11))
    screen.blit(elixir_int_img, e_rect)

    pygame.draw.rect(screen, (189, 240, 255), (offset, HEIGHT - elixir_bar_height - 10, WIDTH, elixir_bar_height), 2)  
    

    elixir_circle_x = elixir_bar_int_width + offset  # Position at the end of the elixir bar
    elixir_circle_y = HEIGHT - elixir_bar_height // 2 - 10  # Align with the bar
    elixir_circle_radius = 12  # Size of the circle

    pygame.draw.circle(screen, PURPLE, (elixir_circle_x, elixir_circle_y), elixir_circle_radius)  # Draw elixir circle

    # Render the elixir amount text
    elixir_text = card_name_font.render(str(max(math.floor(elixir_amount), 0)), True, WHITE)
    text_rect = elixir_text.get_rect(center=(elixir_circle_x, elixir_circle_y))
    screen.blit(elixir_text, text_rect)  # Display elixir text

running = True
saved_decks = None
while True:
    game_type = None
    four_card = False
    while game_type != "quit":
        game_type, evo_enabled = lobby.run_loop(screen)
        if game_type == "edit":
            decks = deck_save.deck_list_loop(screen, evo_enabled, saved_decks)
            if decks is not None:
                if len(decks) == 0:
                    saved_decks = None
                saved_decks = decks
        if game_type == "triple_draft":
            player_random_deck = False
            bot_random_deck = False
            KING_LEVEL = 11
            BOT_K_L = 11
            deck, TOWER_TYPE, bot_deck, BOT_TOWER_TYPE = triple_draft_2p.run_loop(screen, evo_enabled)
            break
        elif game_type == "draft":
            player_random_deck = False
            bot_random_deck = False
            KING_LEVEL = 11
            BOT_K_L = 11
            deck, TOWER_TYPE, bot_deck, BOT_TOWER_TYPE = draft_2p.run_loop(screen, evo_enabled)
            break
        elif game_type == "normal":
            tup = deck_select.run_loop(screen, evo_enabled, True, False, saved_decks)
            if tup is not None:
                player_random_deck, KING_LEVEL, deck, TOWER_TYPE = tup
                tup = deck_select.run_loop(screen, evo_enabled, False, False, saved_decks)
                if tup is not None:
                    bot_random_deck, BOT_K_L, bot_deck, BOT_TOWER_TYPE = tup
                    break
        elif game_type == "double":
            tup = deck_select.run_loop(screen, evo_enabled, True, False, saved_decks)
            if tup is not None:
                player_random_deck, KING_LEVEL, deck, TOWER_TYPE = tup
                tup = deck_select.run_loop(screen, evo_enabled, False, False, saved_decks)
                if tup is not None:
                    game_arena.elixir_rate = 2
                    bot_random_deck, BOT_K_L, bot_deck, BOT_TOWER_TYPE = tup
                    break
        elif game_type == "triple":
            tup = deck_select.run_loop(screen, evo_enabled, True, False, saved_decks)
            if tup is not None:
                player_random_deck, KING_LEVEL, deck, TOWER_TYPE = tup
                tup = deck_select.run_loop(screen, evo_enabled, False, False, saved_decks)
                if tup is not None:
                    game_arena.elixir_rate = 3
                    bot_random_deck, BOT_K_L, bot_deck, BOT_TOWER_TYPE = tup
                    break
        elif game_type == "septuple":
            tup = deck_select.run_loop(screen, evo_enabled, True, False, saved_decks)
            if tup is not None:
                player_random_deck, KING_LEVEL, deck, TOWER_TYPE = tup
                tup = deck_select.run_loop(screen, evo_enabled, False, False, saved_decks)
                if tup is not None:
                    bot_random_deck, BOT_K_L, bot_deck, BOT_TOWER_TYPE = tup
                    game_arena.elixir_rate = 7
                    break
        elif game_type == "fourcard":
            tup = deck_select_4c.run_loop(screen, evo_enabled, True, True, saved_decks)
            if tup is not None:
                player_random_deck, KING_LEVEL, deck, TOWER_TYPE = tup
                tup = deck_select_4c.run_loop(screen, evo_enabled, False, True, saved_decks)
                if tup is not None:
                    four_card = True
                    bot_random_deck, BOT_K_L, bot_deck, BOT_TOWER_TYPE = tup
                    break
        elif game_type == "megadraft":
            player_random_deck = False
            bot_random_deck = False
            KING_LEVEL = 11
            BOT_K_L = 11
            tup = megadraft_2p.run_loop(screen, evo_enabled)
            if tup is not None:
                deck, TOWER_TYPE, bot_deck, BOT_TOWER_TYPE = tup
                break
        else:
            TOWER_TYPE = "randomtower"
            BOT_TOWER_TYPE = "randomtower"

    PRINCESS_LEVEL = KING_LEVEL
    BOT_P_L = BOT_K_L

    if player_random_deck:
        deck = [Card(True, card, KING_LEVEL, evo_enabled and evo_enabled and can_evo(card)) for card in generate_random_deck()]
        if TOWER_TYPE is None:
            TOWER_TYPE = "randomtower"

    # Generate Random Bot Deck
    if bot_random_deck:
        if BOT_TOWER_TYPE is None:
            BOT_TOWER_TYPE = "randomtower"
        bot_deck = [Card(False, card, BOT_K_L, evo_enabled and can_evo(card)) for card in generate_random_deck()]

    p_mirror = next((each for each in deck if each.name == "mirror"), None)
    b_mirror = next((each for each in bot_deck if each.name == "mirror"), None)
    
    p_champion = next((each for each in deck if each.name in champions), None)
    b_champion = next((each for each in bot_deck if each.name in champions), None)
    
    # Initialize Player Towers
    p_k = towers.KingTower(True, KING_LEVEL)

    if TOWER_TYPE.lower() == "randomtower":
        TOWER_TYPE = random.choice(["princesstower", "cannoneer", "daggerduchess", "royalchef"])

    if TOWER_TYPE.lower() == "princesstower":
        player_tower_a = towers.PrincessTower(True, PRINCESS_LEVEL, True)
        player_tower_b = towers.PrincessTower(True, PRINCESS_LEVEL, False)
    elif TOWER_TYPE.lower() == "cannoneer":
        player_tower_a = towers.Cannoneer(True, PRINCESS_LEVEL, True)
        player_tower_b = towers.Cannoneer(True, PRINCESS_LEVEL, False)
    elif TOWER_TYPE.lower() == "daggerduchess":
        player_tower_a = towers.DaggerDuchess(True, PRINCESS_LEVEL, True)
        player_tower_b = towers.DaggerDuchess(True, PRINCESS_LEVEL, False)
    elif TOWER_TYPE.lower() == "royalchef":
        player_tower_a = towers.RoyalChef(True, PRINCESS_LEVEL, True)
        player_tower_b = towers.RoyalChef(True, PRINCESS_LEVEL, False)
        p_k = towers.RoyalChefKingTower(True, KING_LEVEL)

    # Initialize Bot Towers
    b_k = towers.KingTower(False, BOT_K_L)

    if BOT_TOWER_TYPE.lower() == "randomtower":
        BOT_TOWER_TYPE = random.choice(["princesstower", "cannoneer", "daggerduchess", "royalchef"])

    if BOT_TOWER_TYPE.lower() == "princesstower":
        bot_tower_a = towers.PrincessTower(False, BOT_P_L, True)
        bot_tower_b = towers.PrincessTower(False, BOT_P_L, False)
    elif BOT_TOWER_TYPE.lower() == "cannoneer":
        bot_tower_a = towers.Cannoneer(False, BOT_P_L, True)
        bot_tower_b = towers.Cannoneer(False, BOT_P_L, False)
    elif BOT_TOWER_TYPE.lower() == "daggerduchess":
        bot_tower_a = towers.DaggerDuchess(False, BOT_P_L, True)
        bot_tower_b = towers.DaggerDuchess(False, BOT_P_L, False)
    elif BOT_TOWER_TYPE.lower() == "royalchef":
        bot_tower_a = towers.RoyalChef(False, PRINCESS_LEVEL, True)
        bot_tower_b = towers.RoyalChef(False, PRINCESS_LEVEL, False)
        b_k = towers.RoyalChefKingTower(False, BOT_K_L)

    err = False

    game_arena.towers = [p_k, 
                            player_tower_a,  # a
                            player_tower_b,  # b
                            b_k, 
                            bot_tower_a,
                            bot_tower_b
                        ]

    if err:
        raise Exception("you either typed too many cards (8 only + 1 kingtower + 1 towertroop) or misspelled a tower type")

    #player deck


    random.shuffle(deck)

    hand = [0, 1, 2, 3]
    cycler = [4, 5, 6, 7]
    hand_delay = [-1, -1, -1, -1]

    hand2 = [0, 1, 2, 3]
    cycler2 = [4, 5, 6, 7]
    hand2_delay = [-1, -1, -1, -1]

    # Main Loop
    running = game_type != "quit"

    clock = pygame.time.Clock()

    # Variables to store click and drag information
    click_quarter = None  # Will store which quarter of the screen the player clicked in
    click_quarter2 = None
    drag_start_pos = None  # Starting position of the drag
    drag_start_pos2 = None
    hovered = None
    hovered2 = None
    select_radius = None
    select_radius2 = None
    win = None
    false_has_left = True
    false_has_right = True
    true_has_left = True
    true_has_right = True



    game_arena.p2_elixir = 7
    #game_arena.p2_elixir = -999 #disable bot for testing
    p_prev = None
    b_prev = None
    OFFSET = WIDTH + BUFFER
    paused = False
    while running:
        clock.tick(60)  # 60 FPS

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_type = "quit"
                running = False
            if event.type == pygame.KEYDOWN:
                if event.unicode == "b" or event.key == pygame.K_ESCAPE:
                    running = False
                if event.unicode == "p":
                    paused = not paused
            # Detect finger click in the bottom 128 pixels
            elif event.type == pygame.FINGERDOWN:
                finger_x = event.x * FULL_WIDTH#
                finger_y = event.y * HEIGHT

                if finger_x < WIDTH:
                    hovered = None
                elif finger_x > OFFSET:
                    hovered2 = None

                if finger_x < WIDTH - 10 and finger_x > WIDTH - 60 and finger_y > HEIGHT - 128 - 60 and finger_y < HEIGHT - 128 - 10 and game_arena.p1_champion is not None:
                    game_arena.p1_champion.activate_ability(game_arena)
                elif finger_x < WIDTH - 10 + BUFFER + WIDTH and finger_x > WIDTH - 60 + BUFFER + WIDTH and finger_y > HEIGHT - 128 - 60 and finger_y < HEIGHT - 128 - 10 and game_arena.p2_champion is not None:
                    game_arena.p2_champion.activate_ability(game_arena)

                # Check if the click is in the bottom 128 pixels
                if finger_y > HEIGHT - 128:
                    if finger_x < WIDTH:
                        # Determine the quarter (split the width of the screen)
                        quarter_width = (WIDTH) // 5  # Total width including bottom bar
                        if finger_x < WIDTH/10 + quarter_width:
                            click_quarter = 1  # First quarter
                        elif finger_x < WIDTH/10 + 2 * quarter_width:
                            click_quarter = 2  # Second quarter
                        elif finger_x < WIDTH/10 + 3 * quarter_width:
                            click_quarter = 3  # Third quarter
                        else:
                            click_quarter = 4  # Fourth quarter
                        #print(f"Clicked in quarter {click_quarter}")

                        # Store the starting position of the drag
                        drag_start_pos = (finger_x, finger_y)

                    if finger_x > OFFSET:
                        # Determine the quarter (split the width of the screen)
                        quarter_width = (WIDTH) // 5  # Total width including bottom bar
                        if finger_x < WIDTH/10 + quarter_width + OFFSET:
                            click_quarter2 = 1  # First quarter
                        elif finger_x < WIDTH/10 + 2 * quarter_width + OFFSET:
                            click_quarter2 = 2  # Second quarter
                        elif finger_x < WIDTH/10 + 3 * quarter_width + OFFSET:
                            click_quarter2 = 3  # Third quarter
                        else:
                            click_quarter2 = 4  # Fourth quarter
                        #print(f"Clicked in quarter {click_quarter}")

                        # Store the starting position of the drag
                        drag_start_pos2 = (finger_x, finger_y)

            # Detect finger drag movement
            elif event.type == pygame.FINGERMOTION:
                finger_x = event.x * FULL_WIDTH#
                finger_y = event.y * HEIGHT


                if finger_x < WIDTH:
                    if drag_start_pos is not None:
                        cur_name = deck[hand[click_quarter - 1]].name
                        if cur_name == "mirror" and p_prev is not None:
                            cur_name = p_prev.name

                        if finger_x > 64 and finger_x < WIDTH - 64 and finger_y < HEIGHT - 128 and (can_anywhere(cur_name) or finger_y > 340) or (not false_has_right and in_pocket(finger_x, finger_y, True)) or (not false_has_left and in_pocket(finger_x, finger_y, False)):
                            hovered = (((finger_x - 64)// SCALE) * SCALE + 64, (finger_y // SCALE) * SCALE)
                            select_radius = get_radius(cur_name)
                        else:
                            hovered = None
                elif finger_x > OFFSET:
                    if drag_start_pos2 is not None:
                        cur_name = bot_deck[hand2[click_quarter2 - 1]].name
                        if cur_name == "mirror" and b_prev is not None:
                            cur_name = b_prev.name

                        if finger_x > 64 + OFFSET and finger_x < WIDTH - 64 + OFFSET and finger_y < HEIGHT - 128 and (can_anywhere(cur_name) or finger_y > 340) or (not true_has_right and in_pocket(finger_x - OFFSET, finger_y, True)) or (not true_has_left and in_pocket(finger_x - OFFSET, finger_y, False)):
                            hovered2 = (((finger_x - 64)// SCALE) * SCALE + 64, (finger_y // SCALE) * SCALE)
                            select_radius2 = get_radius(cur_name)
                        else:
                            hovered2 = None

            # Detect when the player releases the finger button
            elif event.type == pygame.FINGERUP:
                finger_x = event.x * FULL_WIDTH#
                finger_y = event.y * HEIGHT

                if finger_x < WIDTH:
                    hovered = None
                    if drag_start_pos is not None:
                        cur_card = deck[hand[click_quarter - 1]]
                        legal_place = False
                        c = can_anywhere(cur_card.name) if cur_card.name != "mirror" or p_prev is None else can_anywhere(p_prev.name)
                        if (c or finger_y > 340) or (not false_has_right and in_pocket(finger_x, finger_y, True)) or (not false_has_left and in_pocket(finger_x, finger_y, False)):
                            legal_place = True
                        elif not c and finger_y > 280 and finger_y <= 340:
                            legal_place = True
                            finger_y = 341
                        elif finger_y > 8 * SCALE and finger_y <= 11 * SCALE and not false_has_right and in_pocket(finger_x, 11 * SCALE + 1, True):
                            legal_place = True
                            finger_y = 11 * SCALE + 1
                        elif finger_y > 8 * SCALE and finger_y <= 11 * SCALE and not false_has_left and in_pocket(finger_x, 11 * SCALE + 1, False):
                            legal_place = True
                            finger_y = 11 * SCALE + 1
                        
                        if finger_x > 64 and finger_x < WIDTH - 64 and finger_y < HEIGHT - 128 and legal_place:
                            pos = convert_from_pygame(finger_x, finger_y, True)
                            if cur_card.name == "royalrecruits":
                                if pos.x < -1.5:
                                    pos.x = -1.5
                                elif pos.x > 1.5:
                                    pos.x = 1.5
                            name = cur_card.name if cur_card.name != "mirror" or p_prev is None else p_prev.name
                            level = cur_card.level if cur_card.name != "mirror" or p_prev is None else p_prev.level + 1
                            
                            succesful = game_arena.add(True, pos, name, cur_card.elixir_cost, level, cur_card.cycles_left == 0 if cur_card.name != "mirror" else False)
                            if succesful:
                                if cur_card.name not in champions:
                                    p_prev = cur_card
                                    if p_mirror is not None:
                                        p_mirror.elixir_cost = cur_card.elixir_cost + 1
                                
                                if four_card:
                                    four_card_cycle(hand, click_quarter - 1, hand_delay)
                                else:
                                    cycle(hand, click_quarter - 1, cycler, True)
                                cur_card.cycle_evo()

                        # Reset drag start position after the release
                        drag_start_pos = None

                elif finger_x > OFFSET:
                    hovered2 = None
                    if drag_start_pos2 is not None:
                        cur_card = bot_deck[hand2[click_quarter2 - 1]]
                        legal_place = False
                        c = can_anywhere(cur_card.name) if cur_card.name != "mirror" or b_prev is None else can_anywhere(b_prev.name)
                        if (c or finger_y > 340) or (not true_has_right and in_pocket(finger_x - OFFSET, finger_y, True)) or (not true_has_left and in_pocket(finger_x - OFFSET, finger_y, False)):
                            legal_place = True
                        elif not c and finger_y > 280 and finger_y <= 340:
                            legal_place = True
                            finger_y = 341
                        elif finger_y > 8 * SCALE and finger_y <= 11 * SCALE and not true_has_right and in_pocket(finger_x - OFFSET, 11 * SCALE + 1, True):
                            legal_place = True
                            finger_y = 11 * SCALE + 1
                        elif finger_y > 8 * SCALE and finger_y <= 11 * SCALE and not true_has_left and in_pocket(finger_x - OFFSET, 11 * SCALE + 1, False):
                            legal_place = True
                            finger_y = 11 * SCALE + 1
                        
                        if finger_x > 64 + OFFSET and finger_x < WIDTH - 64 + OFFSET and finger_y < HEIGHT - 128 and legal_place:
                            pos = convert_from_pygame(finger_x, finger_y, False)
                            if cur_card.name == "royalrecruits":
                                if pos.x < -1.5:
                                    pos.x = -1.5
                                elif pos.x > 1.5:
                                    pos.x = 1.5
                            name = cur_card.name if cur_card.name != "mirror" or b_prev is None else b_prev.name
                            level = cur_card.level if cur_card.name != "mirror" or b_prev is None else b_prev.level + 1
                            
                            succesful = game_arena.add(False, pos, name, cur_card.elixir_cost, level, cur_card.cycles_left == 0 if cur_card.name != "mirror" else False)
                            if succesful:
                                if cur_card.name not in champions:
                                    b_prev = cur_card
                                    if b_mirror is not None:
                                        b_mirror.elixir_cost = cur_card.elixir_cost + 1
                                
                                if four_card:
                                    four_card_cycle(hand2, click_quarter2 - 1, hand2_delay)
                                else:
                                    cycle(hand2, click_quarter2 - 1, cycler2, False)
                                cur_card.cycle_evo()

                        # Reset drag start position after the release
                        drag_start_pos2 = None

        if four_card:
            process_hand_delay(hand, hand_delay)
            process_hand_delay(hand2, hand2_delay)
            
        false_has_left = False
        false_has_right = False
        true_has_left = False
        true_has_right = False
        for each in game_arena.towers:
            if not each.side:
                if each.position.x > 0: #is positive
                    false_has_right = True
                elif each.position.x < 0: #is negative
                    false_has_left = True
            else:
                if each.position.x > 0: #is positive
                    true_has_right = True
                elif each.position.x < 0: #is negative
                    true_has_left = True

        if not paused:
            for card_i in hand:
                if deck[card_i].name == "spiritempress":
                    if game_arena.p1_elixir >= 6:
                        deck[card_i].elixir_cost = 6
                    else:
                        deck[card_i].elixir_cost = 3
            for card_i in hand2:
                if bot_deck[card_i].name == "spiritempress":
                    if game_arena.p2_elixir >= 6:
                        bot_deck[card_i].elixir_cost = 6
                    else:
                        bot_deck[card_i].elixir_cost = 3
            game_arena.tick()  # Update game logic
            fin = game_arena.cleanup()

            if p1_c_index is not None and game_arena.p1_champion is None:
                cycler.append(p1_c_index)
                p1_c_index = None

            if p2_c_index is not None and game_arena.p2_champion is None:
                cycler.append(p2_c_index)
                p2_c_index = None

            if fin is not None:
                win = fin
                break
            
            draw(True)  # Redraw screen
            draw(False)
            pygame.display.flip()

    winfont = pygame.font.Font(None, 100)  # Adjust font size as needed
    text = None
    if win is None:
        text = winfont.render("quit_screen_text", True, WHITE)
    elif win:
        text = winfont.render("Player 1 Win", True, WHITE)
    else:
        text = winfont.render("Player 2 Win", True, WHITE)



    # Get text rectangle and center it
    text_rect = text.get_rect(center=(BUFFER // 2 + WIDTH, HEIGHT // 2))
    tip = font.render("CLICK TO RETURN TO LOBBY", True, WHITE)
    tip_rect = tip.get_rect(center=(BUFFER // 2 + WIDTH, HEIGHT // 2 + 60))

    pause = 60

    if running:
        screen.blit(text, text_rect)  # Draw text
        screen.blit(tip, tip_rect)
        pygame.display.flip()  # Update display

    while running:
        clock.tick(60)  # 60 FPS
        pause -= 1

        if pause <= 0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.MOUSEBUTTONDOWN:
                    running = False

       


        #count += 1

    if game_type == "quit":
        break

    game_arena = arena.Arena()
    p1_c_index = None
    p2_c_index = None

pygame.quit()