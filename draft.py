from card_factory import troops, spells, buildings
from card_factory import random_with_param
from cards import Card
import pygame

LIGHT_GRAY = (150, 150, 150)
GRAY = (200, 200, 200)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

RIVER_TEMP = (79, 66, 181)
BRIDGE_TEMP = (193, 154, 107)

WIDTH, HEIGHT = 360 + 128, 640 + 128

def draw_tower(screen, tower_x, tower_y):
    tower_rect_width = 40
    tower_rect_height = tower_rect_width
    tower_x -= tower_rect_width / 2
    tower_y -= tower_rect_height / 2

    tower_color = GRAY
    
    pygame.draw.rect(screen, (90, 100, 90), (tower_x - 10, tower_y - 10, tower_rect_width + 20, tower_rect_height + 20))  # Tower base
    pygame.draw.rect(screen, tower_color, (tower_x, tower_y, tower_rect_width, tower_rect_height))  # Tower square
    hpfont = pygame.font.Font(None, 16)
    hp_text = hpfont.render("3631" if tower_y < HEIGHT/2 - 64 else "4393", True, WHITE)  # Convert HP to int and render in white
    text_rect = hp_text.get_rect(center=(tower_x + tower_rect_width / 2, tower_y - 10))
    screen.blit(hp_text, text_rect)

    # Health bar
    pygame.draw.rect(screen, GREEN, (tower_x - 5, tower_y - 5, ((tower_rect_width + 10)), 3))

def draw_towers(screen):
    draw_tower(screen, WIDTH/2 + 110, HEIGHT/2 - 64 + 190)
    draw_tower(screen, WIDTH/2 + 110, HEIGHT/2 - 64 - 190)
    draw_tower(screen, WIDTH/2 - 110, HEIGHT/2 - 64 + 190)
    draw_tower(screen, WIDTH/2 - 110, HEIGHT/2 - 64 - 190)

    tower_x = WIDTH/2
    tower_y = HEIGHT/2 - 64 - 260

    tower_rect_width = 56
    tower_rect_height = tower_rect_width
    tower_x -= tower_rect_width / 2
    tower_y -= tower_rect_height / 2

    tower_color = GRAY
    
    pygame.draw.rect(screen, (90, 100, 90), (tower_x - 10, tower_y - 10, tower_rect_width + 20, tower_rect_height + 20))  # Tower base
    pygame.draw.rect(screen, tower_color, (tower_x, tower_y, tower_rect_width, tower_rect_height))  # Tower square

    tower_x = WIDTH/2
    tower_y = HEIGHT/2 - 64 + 260

    tower_x -= tower_rect_width / 2
    tower_y -= tower_rect_height / 2
    
    pygame.draw.rect(screen, (90, 100, 90), (tower_x - 10, tower_y - 10, tower_rect_width + 20, tower_rect_height + 20))  # Tower base
    pygame.draw.rect(screen, tower_color, (tower_x, tower_y, tower_rect_width, tower_rect_height))  # Tower square


option_types = [
    ["troop", 3, 6],
    ["troop", 1, 2],
    ["spell", 1, 3],
    ["any", 1, 9]
]

other_types = [
    ["troop", 5, 9],
    ["troop", 2, 4],
    ["building", 1, 9],
    ["spell", 4, 6],
]

class Options:
    def __init__(self, n1, n2):
        self.op1 = SelectionBox(WIDTH/2 - 80, HEIGHT/2, 120, 120, n1)
        self.op2 = SelectionBox(WIDTH/2 + 80, HEIGHT/2, 120, 120, n2)

    def draw(self, screen): 
        self.op1.draw(screen)
        self.op2.draw(screen)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.op1.is_in(*event.pos):
                return self.op1.value, self.op2.value
            elif self.op2.is_in(*event.pos):
                return self.op2.value, self.op1.value
        return None, None


class SelectionBox:
    def __init__(self, x, y, width, height, name):
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.value = name
        self.font_size = 16
    
    def is_in(self, x, y):
        if x < self.x + self.width/2 and x > self.x - self.width/2:
            if y < self.y + self.height/2 and y > self.y - self.height/2:
                return True
            
    def draw(self, screen):
        rect = pygame.Rect(self.x - self.width/2, self.y - self.height/2, self.width, self.height)
        pygame.draw.rect(screen, LIGHT_GRAY if self.value == "" else GRAY, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)  # Border

        font = pygame.font.Font(None, self.font_size) 
        text = font.render(str(self.value), True, BLACK)  # White text
        text_rect = text.get_rect(center=(self.x, self.y))
        screen.blit(text, text_rect)

class Label:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.active = False
        self.value = ""
        self.font_size = 16
    
    def is_in(self, x, y):
        if x < self.x + self.width/2 and x > self.x - self.width/2:
            if y < self.y + self.height/2 and y > self.y - self.height/2:
                return True

            
    def draw(self, screen):
        rect = pygame.Rect(self.x - self.width/2, self.y - self.height/2, self.width, self.height)
        pygame.draw.rect(screen, LIGHT_GRAY if self.value == "" else GRAY, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)  # Border

        font = pygame.font.Font(None, self.font_size) 
        text = font.render(str(self.value), True, BLACK)  # White text
        text_rect = text.get_rect(center=(self.x, self.y))
        screen.blit(text, text_rect)


def run_loop(screen, side = True):
    all = [
        Label(WIDTH/9, HEIGHT - 40, 50, 50),
        Label(2*WIDTH/9, HEIGHT - 40, 50, 50),
        Label(3*WIDTH/9, HEIGHT - 40, 50, 50),
        Label(4*WIDTH/9, HEIGHT - 40, 50, 50),
        Label(5*WIDTH/9, HEIGHT - 40, 50, 50),
        Label(6*WIDTH/9, HEIGHT - 40, 50, 50),
        Label(7*WIDTH/9, HEIGHT - 40, 50, 50),
        Label(8*WIDTH/9, HEIGHT - 40, 50, 50)
    ]

    bot_all = [
        Label(WIDTH/9, 40, 50, 50),
        Label(2*WIDTH/9, 40, 50, 50),
        Label(3*WIDTH/9, 40, 50, 50),
        Label(4*WIDTH/9, 40, 50, 50),
        Label(5*WIDTH/9, 40, 50, 50),
        Label(6*WIDTH/9, 40, 50, 50),
        Label(7*WIDTH/9, 40, 50, 50),
        Label(8*WIDTH/9, 40, 50, 50)
    ]

    i = 0
    used = []
    n1 = random_with_param(*option_types[i], used)
    used.append(n1)
    n2 = random_with_param(*option_types[i], used)
    used.append(n2)

    option = Options(n1, n2)

    out = []
    out2 = []

    running = True

    background_img = pygame.image.load("sprites/background.png").convert_alpha()
    while running:
        screen.fill((100, 100, 100))
        bg_rect = background_img.get_rect(center=(WIDTH / 2, (HEIGHT - 128) / 2))
        screen.blit(background_img, bg_rect)
        SCALE = 20
        pygame.draw.rect(screen, RIVER_TEMP, (0, HEIGHT/2 - 64 - SCALE, WIDTH, SCALE * 2)) 

        #Draw bridges
        pygame.draw.rect(screen, BRIDGE_TEMP, (64 + 2.5 * SCALE, HEIGHT/2 - 64 - 1.5 * SCALE, SCALE * 2, SCALE * 3)) 
        pygame.draw.rect(screen, BRIDGE_TEMP, (WIDTH - (64 + 4.5 * SCALE), HEIGHT/2 - 64 - 1.5 *SCALE, SCALE * 2, SCALE * 3)) 
        draw_towers(screen)
        
        for each in all:
            each.draw(screen)
        for each in bot_all:
            each.draw(screen)
        option.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            choose, not_choose = option.handle_event(event)
            if choose is not None: #if chose
                all[i].value = choose
                bot_all[7 - i].value = not_choose
                

                i += 1

                out.append(Card(side, choose, 11))
                out2.append(Card(side, not_choose, 13))

                if i < 4:
                    n1 = random_with_param(*option_types[i], used)
                    used.append(n1)
                    n2 = random_with_param(*option_types[i], used)
                    used.append(n2)

                    option = Options(n1, n2)

                else:
                    running = False
                
        pygame.display.flip()
    
    for each in other_types:
        n = random_with_param(*each, used)
        out.append(Card(side, n, 11))
        used.append(n)

    for each in other_types:
        n = random_with_param(*each, used)
        out2.append(Card(side, n, 13))
        used.append(n)
        
    return out, "princesstower", out2, "princesstower"