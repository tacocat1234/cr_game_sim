import pygame
import training_camp_cards
import arena
import towers
import vector

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


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Crash Royale Arena")    
font = pygame.font.Font(None, 12) 

game_arena = arena.Arena()

game_arena.towers = [towers.KingTower(True, 1), 
                       towers.PrincessTower(True, 1, True), 
                       towers.PrincessTower(True, 1, False), 
                       towers.KingTower(False, 1), 
                       towers.PrincessTower(False, 1, True), 
                       towers.PrincessTower(False, 1, False)
                       ]

#temp
game_arena.troops.append(training_camp_cards.Giant(True, vector.Vector(-2, -3), 1))
#game_arena.troops.append(training_camp_cards.Archer(True, vector.Vector(-3, -4), 1))
#game_arena.troops.append(training_camp_cards.Giant(False, vector.Vector(-3, 3), 1))
game_arena.troops.append(training_camp_cards.MiniPekka(True, vector.Vector(-3, -4), 1))
#temp



def draw():
    screen.fill(BG_TEMP)

    # Draw river
    pygame.draw.rect(screen, RIVER_TEMP, (0, HEIGHT/2 - 60 - SCALE, WIDTH, SCALE * 2)) 
    #Draw bridges

    pygame.draw.rect(screen, GRAY, (0, HEIGHT - 128, WIDTH, 128))

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

        pygame.draw.rect(screen, BLACK, (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height))
        pygame.draw.rect(screen, GREEN, (hp_bar_x, hp_bar_y, int(hp_bar_width * (troop.cur_hp / troop.hit_points)), hp_bar_height))

        # **NEW: Draw Level Indicator**
        level_box_size = 10  # Square size for level indicator
        level_box_x = hp_bar_x - level_box_size - 2  # Slight padding to the left
        level_box_y = hp_bar_y - 2  # Align with HP bar

        pygame.draw.rect(screen, troop_color, (level_box_x, level_box_y, level_box_size, level_box_size))

        # Render level number text
        level_text = font.render(str(troop.level), True, WHITE)  # White text
        text_rect = level_text.get_rect(center=(level_box_x + level_box_size / 2, level_box_y + level_box_size / 2))
        screen.blit(level_text, text_rect)
    # Draw Attack Entities (Projectiles)
    for attack in game_arena.active_attacks:
        attack_x, attack_y= convert_to_pygame(attack.position)
        pygame.draw.circle(screen, YELLOW, (attack_x, attack_y), 5)  # Attack circle

    for spell in game_arena.spells:
        spell_x, spell_y = convert_to_pygame(spell.position)
        size = spell.radius * SCALE if spell.spawn_timer <= 0 else 1 * SCALE
        pygame.draw.circle(screen, PURPLE, (spell_x, spell_y), size)  # Attack circle

    pygame.display.flip()

#count = 0

# Main Loop
running = True
clock = pygame.time.Clock()

# Variables to store click and drag information
click_quarter = None  # Will store which quarter of the screen the player clicked in
drag_start_pos = None  # Starting position of the drag
drag_end_pos = None  # Ending position of the drag

while running:
    clock.tick(60)  # 60 FPS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Detect mouse click in the bottom 128 pixels
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # Check if the click is in the bottom 128 pixels
            if mouse_y > HEIGHT - 128:
                # Determine the quarter (split the width of the screen)
                quarter_width = (WIDTH) // 4  # Total width including bottom bar
                if mouse_x < quarter_width:
                    click_quarter = 1  # First quarter
                elif mouse_x < 2 * quarter_width:
                    click_quarter = 2  # Second quarter
                elif mouse_x < 3 * quarter_width:
                    click_quarter = 3  # Third quarter
                else:
                    click_quarter = 4  # Fourth quarter
                print(f"Clicked in quarter {click_quarter}")

                # Store the starting position of the drag
                drag_start_pos = (mouse_x, mouse_y)

        # Detect mouse drag movement
        elif event.type == pygame.MOUSEMOTION:
            if drag_start_pos is not None:
                # Optionally, you can track the movement visually or for other purposes
                pass

        # Detect when the player releases the mouse button
        elif event.type == pygame.MOUSEBUTTONUP:
            if drag_start_pos is not None:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                # Store the ending position of the drag
                drag_end_pos = (mouse_x, mouse_y)
                print(f"Drag started at {drag_start_pos}, ended at {drag_end_pos}")

                # Reset drag start position after the release
                drag_start_pos = None


    #if count == 120:
    #    game_arena.spells.append(training_camp_cards.Fireball(False, vector.Vector(-6, -5.5), 1))

    game_arena.tick()  # Update game logic
    game_arena.cleanup()
    draw()  # Redraw screen

    #count += 1

pygame.quit()