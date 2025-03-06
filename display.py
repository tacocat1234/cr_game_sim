import pygame
import training_camp_cards
import arena
from abstract_classes import Vector

#height comp screen ~ 800
#16x16 per tile
# 18 x 32
WIDTH, HEIGHT = 288 + 128, 512 + 256

SCALE = 16  # Scale factor to map game coordinates to screen

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
YELLOW = (255, 255, 0)

BG_TEMP = (0, 154, 23)

def convert_to_pygame(coordinate):
    pygame_x = int(WIDTH / 2 + coordinate.x * 16)
    pygame_y = int(HEIGHT / 2 - coordinate.y * 16)  # Invert Y-axis
    return pygame_x, pygame_y


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Crash Royale Arena")

game_arena = arena.Arena()

#temp
game_arena.troops.append(training_camp_cards.Knight(True, Vector(-2, -5), 1))
game_arena.troops.append(training_camp_cards.Giant(False, Vector(-3, 6), 1))
#temp

def draw():
    screen.fill(BG_TEMP)

    # Draw Towers
    for tower in game_arena.towers:
        tower_x, tower_y = convert_to_pygame(troop.position)
        pygame.draw.rect(screen, GRAY, (tower_x, tower_y, 20, 20))  # Tower square

        # Health bar
        pygame.draw.rect(screen, RED, (tower_x, tower_y - 5, 20, 3))
        pygame.draw.rect(screen, GREEN, (tower_x, tower_y - 5, int(20 * (tower.cur_hp / tower.hit_points)), 3))

    # Draw Troops
    for troop in game_arena.troops:
        troop_x = int((troop.position.x + 9) * SCALE)
        troop_y = int((troop.position.y + 16) * SCALE)
        pygame.draw.circle(screen, BLUE, (troop_x, troop_y), 8)  # Troop circle

        # Health bar
        pygame.draw.rect(screen, RED, (troop_x - 10, troop_y - 12, 20, 3))
        pygame.draw.rect(screen, GREEN, (troop_x - 10, troop_y - 12, int(20 * (troop.cur_hp / troop.hit_points)), 3))

    # Draw Attack Entities (Projectiles)
    for attack in game_arena.active_attacks:
        attack_x = int((attack.position.x + 9) * SCALE)
        attack_y = int((attack.position.y + 16) * SCALE)
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
    draw()  # Redraw screen

pygame.quit()