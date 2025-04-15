import pygame
import random
from cards import Card
from abstract_classes import TICK_TIME
from bot import Bot
from bot import place
from card_factory import get_type
import arena
import towers
import vector

game_arena = arena.Arena()

game_arena.towers = [towers.KingTower(True, 1), 
                       towers.PrincessTower(True, 1, True), 
                       towers.PrincessTower(True, 1, False), 
                       towers.KingTower(False, 3), 
                       towers.PrincessTower(False, 2, True), 
                       towers.PrincessTower(False, 2, False)
                       ]
#player deck (mortar)
deck = [Card(True, "goblinbarrel", 1), Card(True, "knight", 1), Card(True, "electrospirit", 1), Card(True, "fireball", 1), 
        Card(True, "archers", 1), Card(True, "minions", 1), Card(True, "arrows", 1), Card(True, "minipekka", 1)]

#bot deck (duh)
bot_deck = [Card(False, "fireball", 2), Card(False, "witch", 2), Card(False, "wizard", 3), Card(False, "valkyrie", 3), 
        Card(False, "speargoblins", 5), Card(False, "skeletondragons", 3), Card(False, "minipekka", 2), Card(False, "arrows", 4)]

bot = Bot(bot_deck)
#height comp screen ~ 800
#20x20 per tile
# 18 x 32
WIDTH, HEIGHT = 360 + 128, 640 + 128

SCALE = 20  # Scale factor to map game coordinates to screen

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)

BG_TEMP = (0, 154, 23)
RIVER_TEMP = (79, 66, 181)
BRIDGE_TEMP = (193, 154, 107)

def convert_to_pygame(coordinate):
    pygame_x = int(WIDTH / 2 + coordinate.x * SCALE)
    pygame_y = int(HEIGHT / 2 - 60 - coordinate.y * SCALE)  # Invert Y-axis 
    return pygame_x, pygame_y

def convert_from_pygame(pygame_x, pygame_y):
    x = (pygame_x - WIDTH / 2) // SCALE + 0.5
    y = (HEIGHT / 2 - 60 - pygame_y) // SCALE + 0.5# Invert Y-axis back
    return vector.Vector(x, y)


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Crash Royale Arena")    
font = pygame.font.Font(None, 12) 

#temp
#game_arena.troops.append(training_camp_cards.Giant(True, vector.Vector(-2, -3), 1))
#game_arena.troops.append(training_camp_cards.Archer(True, vector.Vector(-3, -4), 1))
#game_arena.troops.append(training_camp_cards.Giant(False, vector.Vector(-3, 3), 1))
#game_arena.troops.append(training_camp_cards.MiniPekka(True, vector.Vector(-3, -4), 1))
#temp

def cycle(hand, index, queue):
    queue.append(hand[index])
    hand[index] = queue.pop(0)

def draw():
    screen.fill(BG_TEMP)

    # Draw river
    pygame.draw.rect(screen, RIVER_TEMP, (0, HEIGHT/2 - 60 - SCALE, WIDTH, SCALE * 2)) 
   
    #draw card area
    pygame.draw.rect(screen, GRAY, (0, HEIGHT - 128, WIDTH, 128))

    #Draw bridges
    pygame.draw.rect(screen, BRIDGE_TEMP, (64 + 2.5 * SCALE, HEIGHT/2 - 60 - 1.5 * SCALE, SCALE * 2, SCALE * 3)) 
    pygame.draw.rect(screen, BRIDGE_TEMP, (WIDTH - (64 + 4.5 * SCALE), HEIGHT/2 - 60 - 1.5 *SCALE, SCALE * 2, SCALE * 3)) 

    # Draw Towers
    for tower in game_arena.towers:
        tower_x, tower_y = convert_to_pygame(tower.position)
        
        # Adjust position so that the rectangle is centered at the tower's coordinates
        tower_rect_width = 3 * SCALE
        tower_rect_height = 3 * SCALE
        tower_x -= tower_rect_width // 2
        tower_y -= tower_rect_height // 2
        
        pygame.draw.rect(screen, GRAY, (tower_x, tower_y, tower_rect_width, tower_rect_height))  # Tower square

        # Health bar
        pygame.draw.rect(screen, BLACK, (tower_x, tower_y - 5, tower_rect_width, 3))
        pygame.draw.rect(screen, GREEN, (tower_x, tower_y - 5, int(tower_rect_width * (tower.cur_hp / tower.hit_points)), 3))

    # Draw Troops
    for troop in game_arena.troops:
        troop_x, troop_y = convert_to_pygame(troop.position)
        troop_color = BLUE if troop.side else RED

        # Draw troop circle
        pygame.draw.circle(screen, troop_color, (troop_x, troop_y), troop.collision_radius * SCALE)

        # Health bar
        hp_bar_x = troop_x - 10
        hp_bar_y = troop_y - 12
        hp_bar_width = 20
        hp_bar_height = 3

        if not troop.invulnerable:
            pygame.draw.rect(screen, BLACK, (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height))
            if troop.has_shield and troop.shield_hp > 0:
                pygame.draw.rect(screen, GREEN, (hp_bar_x, hp_bar_y, int(hp_bar_width * (troop.shield_hp / troop.shield_max_hp)), hp_bar_height))
            else:
                pygame.draw.rect(screen, GREEN, (hp_bar_x, hp_bar_y, int(hp_bar_width * (troop.cur_hp / troop.hit_points)), hp_bar_height))
            
            

        # Draw Level Indicator
        level_box_size = 10  # Square size for level indicator
        level_box_x = hp_bar_x - level_box_size - 2  # Slight padding to the left
        level_box_y = hp_bar_y - 2  # Align with HP bar

        if troop.has_shield and troop.shield_hp > 0:
            # Draw an upside-down triangle
            point1 = (level_box_x + level_box_size / 2, level_box_y + level_box_size)  # bottom center
            point2 = (level_box_x, level_box_y)  # top left
            point3 = (level_box_x + level_box_size, level_box_y)  # top right
            pygame.draw.polygon(screen, troop_color, [point1, point2, point3])
        else:
            # Draw square
            pygame.draw.rect(screen, troop_color, (level_box_x, level_box_y, level_box_size, level_box_size))


        # Render level number text
        level_text = font.render(str(troop.level), True, WHITE)  # White text
        text_rect = level_text.get_rect(center=(level_box_x + level_box_size / 2, level_box_y + level_box_size / 2))
        screen.blit(level_text, text_rect)
    # Draw Attack Entities (Projectiles)

    for building in game_arena.buildings:
        building_x, building_y = convert_to_pygame(building.position)
        building_color = BLUE if building.side else RED

        # Draw building square
        building_size = building.collision_radius * 2 * SCALE
        pygame.draw.rect(screen, building_color, (building_x - building_size // 2, building_y - building_size // 2, building_size, building_size))

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

        # Render level number text
        level_text = font.render(str(building.level), True, WHITE)  # White text
        text_rect = level_text.get_rect(center=(level_box_x + level_box_size / 2, level_box_y + level_box_size / 2))
        screen.blit(level_text, text_rect)

    for attack in game_arena.active_attacks:
        attack_x, attack_y= convert_to_pygame(attack.position)
        if attack.display_size != 0.25:
            # Create a transparent surface
            attack_size = attack.display_size * SCALE
            attack_surface = pygame.Surface((attack_size * 2, attack_size * 2), pygame.SRCALPHA)
            
            # Draw a semi-transparent yellow circle
            pygame.draw.circle(attack_surface, (255, 255, 0, 128), (attack_size, attack_size), attack_size)
            
            # Blit the surface onto the screen
            screen.blit(attack_surface, (attack_x - attack_size, attack_y - attack_size))
        else:
            # Regular solid yellow circle for small attacks
            pygame.draw.circle(screen, YELLOW, (attack_x, attack_y), attack.display_size * SCALE)
    for spell in game_arena.spells:
        spell_x, spell_y = convert_to_pygame(spell.position)
        size = spell.radius * SCALE if spell.spawn_timer <= 0 else 1 * SCALE
        if spell.spawn_timer <= 0:
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
    
    card_name_font = pygame.font.Font(None, 24)  # Use a larger font for card names

    for i, hand_i in enumerate(hand):
        card = deck[hand_i]
        card_name_text = card_name_font.render(card.name, True, BLACK)
        card_name_x = (WIDTH * (i + 1)) // 5  # Positions: WIDTH/5, WIDTH*2/5, WIDTH*3/5, WIDTH*4/5
        card_name_y = HEIGHT - 64  # Vertical position at the bottom
        text_rect = card_name_text.get_rect(center=(card_name_x, card_name_y))
        screen.blit(card_name_text, text_rect)

        elixir_cost_circle_x = card_name_x + 30  # Position at the end of the elixir bar
        elixir_cost_circle_y = card_name_y - 30  # Align with the bar
        elixir_cost_circle_radius = 12  # Size of the circle

        pygame.draw.circle(screen, PURPLE, (elixir_cost_circle_x, elixir_cost_circle_y), elixir_cost_circle_radius)  # Draw elixir circle

        # Render the elixir amount text
        elixir_text = card_name_font.render(str(card.elixir_cost), True, WHITE)
        text_rect = elixir_text.get_rect(center=(elixir_cost_circle_x, elixir_cost_circle_y))
        screen.blit(elixir_text, text_rect)  # Display elixir text


    #draw elixir bar
    elixir_bar_height = 15  
    elixir_bar_width = int((elixir / 10) * WIDTH)  
    pygame.draw.rect(screen, PURPLE, (0, HEIGHT - elixir_bar_height - 10, elixir_bar_width, elixir_bar_height))  
    pygame.draw.rect(screen, WHITE, (0, HEIGHT - elixir_bar_height - 10, WIDTH, elixir_bar_height), 2)  

    elixir_circle_x = elixir_bar_width  # Position at the end of the elixir bar
    elixir_circle_y = HEIGHT - elixir_bar_height // 2 - 10  # Align with the bar
    elixir_circle_radius = 12  # Size of the circle

    pygame.draw.circle(screen, PURPLE, (elixir_circle_x, elixir_circle_y), elixir_circle_radius)  # Draw elixir circle

    # Render the elixir amount text
    elixir_text = card_name_font.render(str(elixir), True, WHITE)
    text_rect = elixir_text.get_rect(center=(elixir_circle_x, elixir_circle_y))
    screen.blit(elixir_text, text_rect)  # Display elixir text

    pygame.display.flip()

random.shuffle(deck)

hand = [0, 1, 2, 3]
cycler = [4, 5, 6, 7]
elixir = 5
bot_elixir = 9 #for bot

# Main Loop
running = True
clock = pygame.time.Clock()

# Variables to store click and drag information
click_quarter = None  # Will store which quarter of the screen the player clicked in
drag_start_pos = None  # Starting position of the drag
drag_end_pos = None  # Ending position of the drag

elixir_recharge = 2.8
elixir_timer = elixir_recharge



while running:
    clock.tick(60)  # 60 FPS

    if (elixir_timer < 0):
        elixir = min(elixir + 1, 10)
        bot_elixir = min(bot_elixir + 1, 10)
        elixir_timer = elixir_recharge
    else:
        elixir_timer -= TICK_TIME

    bot_card = bot.tick(bot_elixir)
    if not bot_card is None:
        print(bot_card.name)
        bot_pos = Bot.random_pos(get_type(bot_card.name) == "spell", game_arena.troops + game_arena.buildings)
        if bot_pos:
            bot_elixir -= bot_card.elixir_cost
            bot_card_type, bot_summon = bot_card.summon(bot_pos)
            place(bot_card_type, bot_summon, game_arena)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Detect mouse click in the bottom 128 pixels
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # Check if the click is in the bottom 128 pixels
            if mouse_y > HEIGHT - 128:
                # Determine the quarter (split the width of the screen)
                quarter_width = (WIDTH) // 5  # Total width including bottom bar
                if mouse_x < WIDTH/10 + quarter_width:
                    click_quarter = 1  # First quarter
                elif mouse_x < WIDTH/10 + 2 * quarter_width:
                    click_quarter = 2  # Second quarter
                elif mouse_x < WIDTH/10 + 3 * quarter_width:
                    click_quarter = 3  # Third quarter
                else:
                    click_quarter = 4  # Fourth quarter
                #print(f"Clicked in quarter {click_quarter}")

                # Store the starting position of the drag
                drag_start_pos = (mouse_x, mouse_y)

        # Detect mouse drag movement
        elif event.type == pygame.MOUSEMOTION:
            if drag_start_pos is not None:
                # add code to animate thign at mouse pos later
                pass

        # Detect when the player releases the mouse button
        elif event.type == pygame.MOUSEBUTTONUP:
            if drag_start_pos is not None:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                # Store the ending position of the drag
                drag_end_pos = (mouse_x, mouse_y)
                cur_card = deck[hand[click_quarter - 1]]
                if mouse_y < HEIGHT - 128 and (get_type(cur_card.name) == "spell" or mouse_y > 320):
                    if (cur_card.elixir_cost <= elixir):
                        card_type, card = deck[hand[click_quarter - 1]].summon(convert_from_pygame(mouse_x, mouse_y))

                        if card_type == "troop":
                            if isinstance(card, list):
                                game_arena.troops.extend(card)
                            else:
                                game_arena.troops.append(card)
                        elif card_type == "spell":
                            if isinstance(card, list):
                                game_arena.spells.extend(card)
                            else:
                                game_arena.spells.append(card)
                        elif card_type == "building":
                            if isinstance(card, list):
                                game_arena.buildings.extend(card)
                            else:
                                game_arena.buildings.append(card)

                        cycle(hand, click_quarter - 1, cycler)
                        elixir -= cur_card.elixir_cost

                # Reset drag start position after the release
                drag_start_pos = None


        a = 0
    b = 0
    for tower in game_arena.towers:
        if tower.side:
            a += 1
        else:
            b += 1
    
    if a == 0 or b == 0:
        break

    game_arena.tick()  # Update game logic
    game_arena.cleanup()
    draw()  # Redraw screen

winfont = pygame.font.Font(None, 100)  # Adjust font size as needed
text = None
a = 0
b = 0
for tower in game_arena.towers:
    if tower.side:
        a += 1
    else:
        b += 1

if b == 0:
    text = winfont.render("YOU WIN", True, WHITE)
elif a == 0:
    text = winfont.render("YOU LOSE", True, WHITE)
else:
    text = winfont.render("quit_screen_text", True, WHITE)

# Get text rectangle and center it
text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

while running:
    screen.fill(BLACK)  # Fill background
    screen.blit(text, text_rect)  # Draw text

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()  # Update display


    #count += 1

pygame.quit()