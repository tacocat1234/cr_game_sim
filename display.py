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

game_arena = arena.Arena()

game_arena.towers = [towers.KingTower(True, 1), 
                       towers.PrincessTower(True, 1, True), 
                       towers.PrincessTower(True, 1, False), 
                       towers.KingTower(False, 1), 
                       towers.PrincessTower(False, 1, True), 
                       towers.PrincessTower(False, 1, False)
                       ]

#temp
game_arena.troops.append(training_camp_cards.Knight(False, vector.Vector(-2, 3), 1))
game_arena.troops.append(training_camp_cards.Archer(True, vector.Vector(-2, -4), 1))
game_arena.troops.append(training_camp_cards.Archer(True, vector.Vector(-3, -4), 1))
game_arena.troops.append(training_camp_cards.Giant(False, vector.Vector(-3, 3), 1))
game_arena.troops.append(training_camp_cards.MiniPekka(True, vector.Vector(-3, -4), 1))
game_arena.troops.append(training_camp_cards.Musketeer(False, vector.Vector(0, 4), 1))
#temp

def draw():
    screen.fill(BG_TEMP)

    # Draw river
    pygame.draw.rect(screen, RIVER_TEMP, (0, HEIGHT/2 - 60 - SCALE, WIDTH, SCALE * 2)) 
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

        # Draw circle with the radius being equal to the troop's collision_radius
        pygame.draw.circle(screen, troop_color, (troop_x, troop_y), troop.collision_radius * SCALE)

        # Health bar
        pygame.draw.rect(screen, BLACK, (troop_x - 10, troop_y - 12, 20, 3))
        pygame.draw.rect(screen, GREEN, (troop_x - 10, troop_y - 12, int(20 * (troop.cur_hp / troop.hit_points)), 3))

    # Draw Attack Entities (Projectiles)
    for attack in game_arena.active_attacks:
        attack_x, attack_y= convert_to_pygame(attack.position)
        pygame.draw.circle(screen, YELLOW, (attack_x, attack_y), 5)  # Attack circle

    pygame.display.flip()

# Main Loop
running = True
clock = pygame.time.Clock()

while running:
    clock.tick(60)  # 60 FPS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    game_arena.tick()  # Update game logic
    game_arena.cleanup()
    draw()  # Redraw screen

pygame.quit()