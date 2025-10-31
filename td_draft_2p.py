from card_factory import troops, spells, buildings
from card_factory import random_with_param
from card_factory import can_evo
from cards import Card
import pygame

LIGHT_GRAY = (150, 150, 150)
GRAY = (200, 200, 200)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

RIVER_TEMP = (79, 66, 181)
BRIDGE_TEMP = (193, 154, 107)

BUFFER = 256
WIDTH, HEIGHT = 360 + 128, 640 + 128
OFFSET = WIDTH + BUFFER
FULL_WIDTH = 2 * WIDTH + BUFFER


option_types = [
    ["troop", 3, 9],
    ["troop", 1, 3],
    ["spell", 1, 3],
    ["any", 1, 9]
]

other_types = [
    ["troop", 3, 9],
    ["troop", 1, 3],
    ["building", 1, 4],
    ["spell", 4, 6],
]

class Options:
    def __init__(self, n1, n2, offset=False):
        extra = OFFSET if offset else 0
        self.op1 = SelectionBox(WIDTH/2 - 80 + extra, HEIGHT/2, 120, 120, n1)
        self.op2 = SelectionBox(WIDTH/2 + 80 + extra, HEIGHT/2, 120, 120, n2)

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

    def draw_offset(self, screen):
        rect = pygame.Rect(self.x - self.width/2 + OFFSET, self.y - self.height/2, self.width, self.height)
        pygame.draw.rect(screen, LIGHT_GRAY if self.value == "" else GRAY, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)  # Border

        font = pygame.font.Font(None, self.font_size) 
        text = font.render(str(self.value), True, BLACK)  # White text
        text_rect = text.get_rect(center=(self.x + OFFSET, self.y))
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
    
    def draw_offset(self, screen):
        rect = pygame.Rect(self.x - self.width/2 + OFFSET, HEIGHT - (self.y - self.height/2), self.width, self.height)
        pygame.draw.rect(screen, LIGHT_GRAY if self.value == "" else GRAY, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)  # Border

        font = pygame.font.Font(None, self.font_size) 
        text = font.render(str(self.value), True, BLACK)  # White text
        text_rect = text.get_rect(center=(self.x + OFFSET, HEIGHT - self.y))
        screen.blit(text, text_rect)


def run_loop(screen, evo_enabled = False, side = True):
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

    all2 = [
        Label(WIDTH/9 + OFFSET, 40, 50, 50),
        Label(2*WIDTH/9 + OFFSET, 40, 50, 50),
        Label(3*WIDTH/9 + OFFSET, 40, 50, 50),
        Label(4*WIDTH/9 + OFFSET, 40, 50, 50),
        Label(5*WIDTH/9 + OFFSET, 40, 50, 50),
        Label(6*WIDTH/9 + OFFSET, 40, 50, 50),
        Label(7*WIDTH/9 + OFFSET, 40, 50, 50),
        Label(8*WIDTH/9 + OFFSET, 40, 50, 50)
    ]

    bot_all2 = [
        Label(WIDTH/9 + OFFSET, HEIGHT - 40, 50, 50),
        Label(2*WIDTH/9 + OFFSET, HEIGHT - 40, 50, 50),
        Label(3*WIDTH/9 + OFFSET, HEIGHT - 40, 50, 50),
        Label(4*WIDTH/9 + OFFSET, HEIGHT - 40, 50, 50),
        Label(5*WIDTH/9 + OFFSET, HEIGHT - 40, 50, 50),
        Label(6*WIDTH/9 + OFFSET, HEIGHT - 40, 50, 50),
        Label(7*WIDTH/9 + OFFSET, HEIGHT - 40, 50, 50),
        Label(8*WIDTH/9 + OFFSET, HEIGHT - 40, 50, 50)
    ]

    

    i = 0
    used = ["miner", "goblindrill", "graveyard", "goblinbarrel"] #exclude those 4 (op)
    n1 = random_with_param(*option_types[i], used)
    used.append(n1)
    n2 = random_with_param(*option_types[i], used)
    used.append(n2)

    j = 0

    n3 = random_with_param(*other_types[j], used)
    used.append(n3)
    n4 = random_with_param(*other_types[j], used)
    used.append(n4)

    option = Options(n1, n2)
    option2 = Options(n3, n4, True)

    out = []
    out2 = []

    one_done = False
    two_done = False

    running = True

    background_img = pygame.image.load("sprites/td_background.png").convert_alpha()
    while running:
        screen.fill((100, 100, 100))
        bg_rect = background_img.get_rect(center=(WIDTH / 2, (HEIGHT - 128) / 2))
        screen.blit(background_img, bg_rect)
        SCALE = 20

        bg_rect = background_img.get_rect(center=(WIDTH / 2 + OFFSET, (HEIGHT - 128) / 2))
        screen.blit(background_img, bg_rect)
        
        for each in all:
            each.draw(screen)
        for each in bot_all:
            each.draw(screen)
        for each in all2:
            each.draw(screen)
        for each in bot_all2:
            each.draw(screen)

        if not one_done:
            option.draw(screen)
        if not two_done:
            option2.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if not one_done:
                choose, not_choose = option.handle_event(event)
                if choose is not None: #if chose
                    all[i].value = choose
                    bot_all[7 - i].value = not_choose

                    all2[7 - i].value = "?"
                    bot_all2[i].value = "?"
                    

                    i += 1

                    out.append(Card(side, choose, 11, evo_enabled and can_evo(choose)))
                    out2.append(Card(side, not_choose, 11, evo_enabled and can_evo(not_choose))) #temp

                    if i < 4:
                        n1 = random_with_param(*option_types[i], used)
                        used.append(n1)
                        n2 = random_with_param(*option_types[i], used)
                        used.append(n2)

                        option = Options(n1, n2)

                    else:
                        one_done = True
            if not two_done:
                choose, not_choose = option2.handle_event(event)
                if choose is not None: #if chose
                    all2[j].value = choose
                    bot_all2[7 - j].value = not_choose

                    all[7 - j].value = "?"
                    bot_all[j].value = "?"
                    

                    j += 1

                    out2.append(Card(side, choose, 11, evo_enabled and can_evo(choose)))
                    out.append(Card(side, not_choose, 11, evo_enabled and can_evo(not_choose))) #temp

                    if j < 4:
                        n1 = random_with_param(*other_types[j], used)
                        used.append(n1)
                        n2 = random_with_param(*other_types[j], used)
                        used.append(n2)

                        option2 = Options(n1, n2, True)

                    else:
                        two_done = True

        if one_done and two_done:
            running = False
                
        pygame.display.flip()
    
    return out, "princesstower", out2, "princesstower"