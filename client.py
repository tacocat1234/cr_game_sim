import socket
import json
import uuid
import pygame
import random
import vector
import time

from card_factory import get_type
from card_factory import get_elixir
from abstract_classes import TICK_TIME

#-----------------------------------------------------------------------------------
#cards avaliable:
#archers, barbarians, battleram, electrospirit, firespirit, skeletons, giant, bomber
#minions, megaminion, speargoblins
#fireball, arrows, zap
#cannon, tombstone, goblinhut = 24,310 possible decks
#-----------------------------------------------------------------------------------
# modify the below to set deck and tower levels
DECK = []
KING_LEVEL = PRINCESS_LEVEL = 11
with open("deck.txt", "r") as file:
    for _ in range(8):
        line = file.readline().strip()
        if line:  # Ensure line is not empty
            card, level = line.rsplit(" ", 1)  # Split at the last space
            DECK.append((card, int(level)))
            
    line = file.readline().strip()
    if line:
        _, KING_LEVEL = line.rsplit(" ", 1)
        KING_LEVEL = int(KING_LEVEL)

    line = file.readline().strip()
    if line:
        _, PRINCESS_LEVEL = line.rsplit(" ", 1)
        PRINCESS_LEVEL = int(PRINCESS_LEVEL)
#
#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------

SERVER_IP = input("What is the server IP? (server device should read \"Server started on {Server IP} : Port\")\n")
SERVER_PORT = 5555
BUFFER_SIZE = 4096

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Generate a unique player ID
player_id = str(uuid.uuid1())
arena_id = None
side = None

IMAGE_CACHE = {}

def load_image_cached(path):
    if path not in IMAGE_CACHE:
        IMAGE_CACHE[path] = pygame.image.load(path).convert_alpha()
    return IMAGE_CACHE[path]

def send_data(data):
    #Send JSON data to the server and receive a response.#
    client_socket.sendto(json.dumps(data).encode(), (SERVER_IP, SERVER_PORT))
    response, _ = client_socket.recvfrom(BUFFER_SIZE)
    return json.loads(response.decode())

def create_arena(a_id, king_level=1, princess_level=1):
    global side
    #Send a request to create an arena.#
    data = {
        "id": player_id,
        "action": "create",
        "arena_id": a_id,
        "king_level": king_level,
        "princess_level": princess_level
    }
    side = True
    return send_data(data)

def join_arena(a_id, king_level=1, princess_level=1):
    global side
    #Send a request to join an existing arena.#
    data = {
        "id": player_id,
        "action": "join",
        "arena_id": a_id,
        "king_level": king_level,
        "princess_level": princess_level
    }
    side = False
    return send_data(data)

def wait(): #no action registered
    action = "wait"
    data = {
        "id": player_id,
        "action": action,
        "arena_id": arena_id,
        "side": side,
    }
    return send_data(data)

def place_card(x, y, card, level=1): #valid card place registered
    action = "created" if side else "joined"
    data = {
        "id": player_id,
        "action": action,
        "arena_id": arena_id,
        "x": round(x),
        "y": round(y),
        "side": side,
        "level": level,
        "place": card
    }
    return send_data(data)

def exit_arena():
    #Exit the arena.#
    data = {
        "id": player_id,
        "action": "exit",
        "arena_id": arena_id
    }
    return send_data(data)

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

def convert_to_pygame(x, y):
    pygame_x = int(WIDTH / 2 + x * SCALE)
    pygame_y = int(HEIGHT / 2 - 60 - y * SCALE)  # Invert Y-axis 
    return pygame_x, pygame_y


def convert_from_pygame(pygame_x, pygame_y):
    x = (pygame_x - WIDTH / 2) // SCALE
    y = (HEIGHT / 2 - 60 - pygame_y) // SCALE  # Invert Y-axis back
    return vector.Vector(x, y)

def convert_from_pygame(pygame_x, pygame_y):
    x = (pygame_x - WIDTH / 2) // SCALE
    y = (HEIGHT / 2 - 60 - pygame_y) // SCALE  # Invert Y-axis back
    return x, y


def cycle(hand, index, queue):
    queue.append(hand[index])
    hand[index] = queue.pop(0)

def draw(server_data): #takes list of all vector.Vector objects of positions
     # Extract data from server response
    troop_x = server_data["troop_x"]
    troop_y = server_data["troop_y"]
    troop_l = server_data["troop_l"]
    troop_hp_ratio = server_data["troop_hp"]
    troop_sprites = server_data["troop_sprite"]
    troop_dir = server_data["troop_dir"]
    troop_side = server_data["troop_side"]

    spell_x = server_data["spell_x"]
    spell_y = server_data["spell_y"]
    spell_sprites = server_data["spell_sprite"]

    building_x = server_data["building_x"]
    building_y = server_data["building_y"]
    building_l = server_data["building_l"]
    building_hp = server_data["building_hp"]
    building_sprites = server_data["building_sprite"]
    building_dir = server_data["building_dir"]
    building_side = server_data["building_side"]

    attack_x = server_data["attack_x"]
    attack_y = server_data["attack_y"]
    attack_r = server_data["attack_r"]

    tower_x = server_data["tower_x"]
    tower_y = server_data["tower_y"]
    tower_l = server_data["tower_l"]
    tower_hp = server_data["tower_hp"]
    tower_sprites = server_data["tower_sprite"]
    
    screen.fill(BG_TEMP)

    # Draw river
    pygame.draw.rect(screen, RIVER_TEMP, (0, HEIGHT/2 - 60 - SCALE, WIDTH, SCALE * 2)) 
   
    #draw card area
    pygame.draw.rect(screen, GRAY, (0, HEIGHT - 128, WIDTH, 128))

    #Draw bridges
    pygame.draw.rect(screen, BRIDGE_TEMP, (64 + 2.5 * SCALE, HEIGHT/2 - 60 - 1.5 * SCALE, SCALE * 2, SCALE * 3)) 
    pygame.draw.rect(screen, BRIDGE_TEMP, (WIDTH - (64 + 4.5 * SCALE), HEIGHT/2 - 60 - 1.5 *SCALE, SCALE * 2, SCALE * 3)) 

    # Draw Towers
    for i in range(len(tower_x)):
        t_x, t_y = convert_to_pygame(tower_x[i], tower_y[i])
        hp_bar_x = t_x - 1.5*SCALE
        hp_bar_y = t_y - 1.7*SCALE
        
        tower_rect_width = 3 * SCALE
        
        if tower_sprites[i]:  # Ensure there is a sprite path
            tower_image = load_image_cached(tower_sprites[i])  # Load image using helper function
            tower_rect = tower_image.get_rect(center=(t_x, t_y))
            screen.blit(tower_image, tower_rect)  # Draw sprite

        # Health bar
        pygame.draw.rect(screen, BLACK, (hp_bar_x, hp_bar_y, tower_rect_width, 3))
        pygame.draw.rect(screen, GREEN, (hp_bar_x, hp_bar_y, int(tower_rect_width * tower_hp[i]), 3))

        level_box_size = 10  # Square size for level indicator
        level_box_x = hp_bar_x - level_box_size - 2  # Slight padding to the left
        level_box_y = hp_bar_y - 2  # Align with HP bar

        pygame.draw.rect(screen, YELLOW, (level_box_x, level_box_y, level_box_size, level_box_size))
        level_text = font.render(str(tower_l[i]), True, WHITE)  # White text
        text_rect = level_text.get_rect(center=(level_box_x + level_box_size / 2, level_box_y + level_box_size / 2))
        screen.blit(level_text, text_rect)

    # Draw Troops
    for i in range(len(troop_x)):
        t_x, t_y = convert_to_pygame(troop_x[i], troop_y[i])
        troop_color = BLUE if not (troop_side[i] ^ side) else RED

        if troop_sprites[i]:  # Ensure sprite exists
            troop_image = load_image_cached(troop_sprites[i])
            troop_image = pygame.transform.rotate(troop_image, troop_dir[i] - 90)  # Adjust rotation
            troop_rect = troop_image.get_rect(center=(t_x, t_y))
            screen.blit(troop_image, troop_rect)

        # Health bar
        hp_bar_x = t_x - 10
        hp_bar_y = t_y - 12
        hp_bar_width = 20
        hp_bar_height = 3

        pygame.draw.rect(screen, BLACK, (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height))
        pygame.draw.rect(screen, GREEN, (hp_bar_x, hp_bar_y, int(hp_bar_width * troop_hp_ratio[i]), hp_bar_height))

        # Draw Level Indicator
        level_box_size = 10  # Square size for level indicator
        level_box_x = hp_bar_x - level_box_size - 2  # Slight padding to the left
        level_box_y = hp_bar_y - 2  # Align with HP bar

        pygame.draw.rect(screen, troop_color, (level_box_x, level_box_y, level_box_size, level_box_size))

        # Render level number text
        level_text = font.render(str(troop_l[i]), True, WHITE)  # White text
        text_rect = level_text.get_rect(center=(level_box_x + level_box_size / 2, level_box_y + level_box_size / 2))
        screen.blit(level_text, text_rect)
    # Draw Attack Entities (Projectiles)

    for i in range(len(building_x)):
        b_x, b_y = convert_to_pygame(building_x[i], building_y[i])

        building_color = BLUE if not (building_side[i] ^ side) else RED

        if building_sprites[i]:  # MODIFY CODE HERE
            building_image = load_image_cached(building_sprites[i] + "_base.png")
            building_rect = building_image.get_rect(center=(b_x, b_y))
            screen.blit(building_image, building_rect)

            building_top_image = load_image_cached(building_sprites[i] + "_top.png")
            rotated_top_image = pygame.transform.rotate(building_top_image, building_dir[i] - 90)  # Rotate to face direction
            top_rect = rotated_top_image.get_rect(center=(b_x, b_y))
            screen.blit(rotated_top_image, top_rect)
            
        # Health bar
        hp_bar_x = b_x - 10
        hp_bar_y = b_y - 12  # Slightly above the building
        hp_bar_width = 20
        hp_bar_height = 3

        pygame.draw.rect(screen, BLACK, (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height))
        pygame.draw.rect(screen, GREEN, (hp_bar_x, hp_bar_y, int(hp_bar_width * building_hp[i]), hp_bar_height))

        # Draw Level Indicator
        level_box_size = 10  # Square size for level indicator
        level_box_x = hp_bar_x - level_box_size - 2  # Slight padding to the left
        level_box_y = hp_bar_y - 2  # Align with HP bar

        pygame.draw.rect(screen, building_color, (level_box_x, level_box_y, level_box_size, level_box_size))

        # Render level number text
        level_text = font.render(str(building_l[i]), True, WHITE)  # White text
        text_rect = level_text.get_rect(center=(level_box_x + level_box_size / 2, level_box_y + level_box_size / 2))
        screen.blit(level_text, text_rect)

    for i in range(len(attack_x)):
        a_x, a_y = convert_to_pygame(attack_x[i], attack_y[i])

        if attack_r[i] != 0.25:
            attack_size = attack_r[i] * SCALE
            attack_surface = pygame.Surface((attack_size * 2, attack_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(attack_surface, (255, 255, 0, 128), (attack_size, attack_size), attack_size)
            screen.blit(attack_surface, (a_x - attack_size, a_y - attack_size))
        else:
            pygame.draw.circle(screen, YELLOW, (a_x, a_y), attack_r[i] * SCALE)
    
    for i in range(len(spell_x)):
        s_x, s_y = convert_to_pygame(spell_x[i], spell_y[i])

        if spell_sprites[i]:  # Ensure sprite exists
            spell_image = load_image_cached(spell_sprites[i])
            spell_rect = spell_image.get_rect(center=(s_x, s_y))
            screen.blit(spell_image, spell_rect)
    
    card_name_font = pygame.font.Font(None, 24)  # Use a larger font for card names

    for i, hand_i in enumerate(hand):
        card = DECK[hand_i]
        card_name_text = card_name_font.render(card[0], True, WHITE)
        card_name_x = (WIDTH * (i + 1)) // 5  # Positions: WIDTH/5, WIDTH*2/5, WIDTH*3/5, WIDTH*4/5
        card_name_y = HEIGHT - 64  # Vertical position at the bottom
        text_rect = card_name_text.get_rect(center=(card_name_x, card_name_y))
        screen.blit(card_name_text, text_rect)

        elixir_cost_circle_x = card_name_x + 30  # Position at the end of the elixir bar
        elixir_cost_circle_y = card_name_y - 30  # Align with the bar
        elixir_cost_circle_radius = 12  # Size of the circle

        pygame.draw.circle(screen, PURPLE, (elixir_cost_circle_x, elixir_cost_circle_y), elixir_cost_circle_radius)  # Draw elixir circle

        # Render the elixir amount text
        elixir_text = card_name_font.render(str(get_elixir(card[0])), True, WHITE)
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

    pygame.display.flip() #draws correct, 
        
again = True
while again:
    random.shuffle(DECK)

    hand = [0, 1, 2, 3]
    cycler = [4, 5, 6, 7]
    elixir = 5

    running = True
    clock = pygame.time.Clock()

    # Variables to store click and drag information
    click_quarter = None  # Will store which quarter of the screen the player clicked in
    drag_start_pos = None  # Starting position of the drag
    drag_end_pos = None  # Ending position of the drag

    elixir_recharge = 2.8
    elixir_timer = elixir_recharge
    recieve = None

    valid = True

    while True:
        create_or_join = input("Create or Join?\n")
        if create_or_join.lower() == "create":
            arena_id = str(uuid.uuid1())
            print("Your arena id is: " + arena_id)
            recieve = create_arena(arena_id, KING_LEVEL, PRINCESS_LEVEL)

        elif create_or_join.lower() == "join":
            arena_id = input("What arena id?\n")
            recieve = join_arena(arena_id, KING_LEVEL, PRINCESS_LEVEL)
            if not recieve["err"] is None:
                print(recieve["err"])
                valid = False

        else:
            print("Invalid option. ", end="")
            valid = False

        if valid:
            break

    print("Waiting...")
    while not recieve["arena_state"] == "active":
        recieve = wait()

    print("Match start.")
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Crash Royale Arena")    
    font = pygame.font.Font(None, 12) 

    resend = False
    resend_data = {
        "x" : 0,
        "y" : 0,
        "name" : None,
        "level" : 0
    }

    frame_count = 0
    start_time = time.time()

    while running:
        draw(recieve)  # Redraw screen
        frame_count += 1

        # Calculate FPS every second
        if time.time() - start_time >= 1:
            fps = frame_count
            print(f"FPS: {fps}")
            start_time = time.time()
            frame_count = 0

        clock.tick(60)  # 60 FPS
        if (elixir_timer < 0):
            elixir = min(elixir + 1, 10)
            elixir_timer = elixir_recharge
        else:
            elixir_timer -= TICK_TIME
        
        if resend:
            recieve = place_card(resend_data["x"], resend_data["y"], resend_data["name"], resend_data["level"])
            if recieve["ack"] is not None: #if its ack
                resend = False #stop resending, otherwise keep trying to resend

        did_recieve = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                did_recieve = True
                recieve = exit_arena()
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
                    cur_card = DECK[hand[click_quarter - 1]]
                    if mouse_y < HEIGHT - 128 and (get_type(cur_card[0]) == "spell" or mouse_y > 320):
                        if get_elixir(cur_card[0]) <= elixir:
                            
                            #place card code
                            #
                            x, y = convert_from_pygame(mouse_x, mouse_y)
                            y = y if side else -y
                            
                            did_recieve = True
                            recieve = place_card(x, y, cur_card[0], cur_card[1]) #send data, recieve data
                            if recieve["ack"] is None: #resend until ack
                                resend = True
                                resend_data = {
                                    "x" : x,
                                    "y" : y,
                                    "name" : cur_card[0],
                                    "level" : cur_card[1]
                                }

                            cycle(hand, click_quarter - 1, cycler)
                            elixir -= get_elixir(cur_card[0])
                    # Reset drag start position after the release
                    
                    drag_start_pos = None
        if not did_recieve:
            recieve = wait()
        if recieve["arena_state"] == "p1_win" or recieve["arena_state"] == "p2_win":
            running = False

    winfont = pygame.font.Font(None, 100)  # Adjust font size as needed

    if (recieve["arena_state"] == "p1_win" and side) or (recieve["arena_state"] == "p2_win" and not side):
        text = winfont.render("YOU WIN", True, WHITE)
    else:
        text = winfont.render("YOU LOSE", True, WHITE)
    # Get text rectangle and center it
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    running = True
    while running:
        screen.fill(BLACK)  # Fill background
        screen.blit(text, text_rect)  # Draw text

        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.MOUSEBUTTONDOWN:
                running = False

        pygame.display.flip()  # Update display


        #count += 1

    pygame.quit()

    ipt = input("\n\nQue again? y/n\n")
    while not (ipt == "y" or ipt == "n"):
        ipt = input("Invalid input. Que again? y/n")
    again = True if ipt == "y" else False