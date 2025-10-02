from card_factory import random_with_param
from card_factory import can_evo
from cards import Card
import pygame
import random
import time

LIGHT_GRAY = (150, 150, 150)
GRAY = (200, 200, 200)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

RED = (255, 0, 0)
BLUE = (0, 0, 255)

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


class SelectionBox:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.font_size = 14
    
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
        self.font_size = 14
    
    def is_in(self, x, y):
        if x < self.x + self.width/2 and x > self.x - self.width/2:
            if y < self.y + self.height/2 and y > self.y - self.height/2:
                return True

            
    def draw(self, screen, font_color = BLACK):
        rect = pygame.Rect(self.x - self.width/2, self.y - self.height/2, self.width, self.height)
        pygame.draw.rect(screen, LIGHT_GRAY if self.value == "" else GRAY, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)  # Border

        font = pygame.font.Font(None, self.font_size) 
        text = font.render(str(self.value), True, font_color)  # White text
        text_rect = text.get_rect(center=(self.x, self.y))
        screen.blit(text, text_rect)

class CheckBox(SelectionBox):
    def __init__(self, x, y, width, height, text=None):
        super().__init__(x, y, width, height)
        self.value = False
        self.side = None
        self.text = text

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.value and self.is_in(*event.pos):
                self.value = True
                self.side = True
                return True
        return False

    def draw(self, screen):
        rect = pygame.Rect(self.x - self.width / 2, self.y - self.height / 2, self.width, self.height)
        pygame.draw.rect(screen, (220, 220, 220) if not self.value else ((150, 150, 200) if self.side else (200, 150, 150)), rect)
        pygame.draw.rect(screen, BLACK, rect, 2)  # Border
        font = pygame.font.Font(None, self.font_size) 
        text = font.render(str(self.text), True, BLACK)  # White text
        text_rect = text.get_rect(center=(self.x, self.y))
        screen.blit(text, text_rect)

def run_loop(screen, evo_enabled = False, side = True):
    out = []
    out2 = []

    bounds = [[1, 3], [3, 5], [4, 6], [6, 10]]

    all = []
    used = []
    for row in range(3):
        for i in range(6):
            r = random_with_param("troop", bounds[row][0], bounds[row][1], used)
            all.append(CheckBox(WIDTH/7 * (i + 1), 130 + row * 80, 55, 55, r))
            used.append(r)

    for i in range(6):
        r = random_with_param("spell", 1 if i < 3 else 3, 4 if i < 3 else 10, used)
        all.append(CheckBox(WIDTH/7 * (i + 1), 130 + 3 * 80, 55, 55, r))
        used.append(r)

    for i in range(5):
        r = random_with_param("troop", bounds[3][0], bounds[3][1], used)
        all.append(CheckBox(WIDTH/7 * (i + 1), 130 + 4 * 80, 55, 55, r))
        used.append(r)

    i = 5
    r = random_with_param("building", 1, 10, used)
    all.append(CheckBox(WIDTH/7 * (i + 1), 130 + 4 * 80, 55, 55, r))
    used.append(r)

    for i in range(3):
        r = random_with_param("champion", 1, 10, used)
        all.append(CheckBox(WIDTH/7 * (i + 1), 130 + 5 * 80, 55, 55, r))
        used.append(r)

    for i in range(3, 6):
        r = random_with_param("building", 1, 10, used)
        all.append(CheckBox(WIDTH/7 * (i + 1), 130 + 5 * 80, 55, 55, r))
        used.append(r)

    p_i = 0

    deck = [
        Label(WIDTH/9, HEIGHT - 40, 55, 55),
        Label(2*WIDTH/9, HEIGHT - 40, 55, 55),
        Label(3*WIDTH/9, HEIGHT - 40, 55, 55),
        Label(4*WIDTH/9, HEIGHT - 40, 55, 55),
        Label(5*WIDTH/9, HEIGHT - 40, 55, 55),
        Label(6*WIDTH/9, HEIGHT - 40, 55, 55),
        Label(7*WIDTH/9, HEIGHT - 40, 55, 55),
        Label(8*WIDTH/9, HEIGHT - 40, 55, 55)
    ]

    b_i = 0

    bot_deck = [
        Label(WIDTH/9, 40, 55, 55),
        Label(2*WIDTH/9, 40, 55, 55),
        Label(3*WIDTH/9, 40, 55, 55),
        Label(4*WIDTH/9, 40, 55, 55),
        Label(5*WIDTH/9, 40, 55, 55),
        Label(6*WIDTH/9, 40, 55, 55),
        Label(7*WIDTH/9, 40, 55, 55),
        Label(8*WIDTH/9, 40, 55, 55)
    ]

    turn_label = Label(WIDTH/2, 600, 200, 50)
    turn_label.font_size = 24
    

    running = True

    turn = random.random() > 0.5 
    next_turn = not turn

    turn_label.value = "Your turn" if turn == side else "Opponents Turn"

    chosen = []

    bot_select = [[0, 5], [0, 5], [6, 11], [6, 17], [17, 23], [24, 26], [25, 32], [33, 35]]
    random.shuffle(bot_select)

    background_img = pygame.image.load("sprites/background.png").convert_alpha()

    screen.fill((100, 100, 100))
    
    bg_rect = background_img.get_rect(center=(WIDTH / 2, (HEIGHT - 128) / 2))
    screen.blit(background_img, bg_rect)
    SCALE = 20
    pygame.draw.rect(screen, RIVER_TEMP, (0, HEIGHT/2 - 64 - SCALE, WIDTH, SCALE * 2)) 

    #Draw bridges
    pygame.draw.rect(screen, BRIDGE_TEMP, (64 + 2.5 * SCALE, HEIGHT/2 - 64 - 1.5 * SCALE, SCALE * 2, SCALE * 3)) 
    pygame.draw.rect(screen, BRIDGE_TEMP, (WIDTH - (64 + 4.5 * SCALE), HEIGHT/2 - 64 - 1.5 *SCALE, SCALE * 2, SCALE * 3)) 
    draw_towers(screen)

    turn_label.draw(screen, BLUE if turn == side else RED)

    
    for each in all + deck + bot_deck:
        each.draw(screen)

    pygame.display.flip()

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

        choose = None

        if turn == side:
            for event in pygame.event.get():
                if event == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.unicode == "b" or event.key == pygame.K_ESCAPE:
                        return
    

                each_i = 0
                for each in all:
                    clicked = each.handle_event(event)
                    if clicked:
                        choose = each.text
                        deck[p_i].value = choose
                        p_i += 1
                        chosen.append(each_i)

                        #update turn
                        temp = not next_turn if next_turn == turn else next_turn
                        turn = next_turn
                        next_turn = temp
                        out.append(Card(side, choose, 11, evo_enabled and can_evo(choose)))

                        turn_label.value = "Your turn" if turn == side else "Opponents Turn"

                        break
                    each_i += 1
                
        else:
            time.sleep(random.random() + 0.75)
            low, high = bot_select[b_i]
            # Make a list of possible numbers in that range that are not in chosen
            possible = [n for n in range(low, high + 1) if n not in chosen]

            if possible:
                selected = random.choice(possible)
            else:
                # Fallback: pick any number 0-35 not in chosen
                possible_fallback = [n for n in range(0, 36) if n not in chosen]
                if possible_fallback:
                    selected = random.choice(possible_fallback)
                else:
                    RuntimeError("no valid choices for bot")

            choose = all[selected].text
            chosen.append(selected)

            all[selected].value = True
            all[selected].side = False
            bot_deck[b_i].value = choose
            b_i += 1
            out2.append(Card(side, choose, 12, evo_enabled and can_evo(choose)))

            temp = not next_turn if next_turn == turn else next_turn
            turn = next_turn
            next_turn = temp

            turn_label.value = "Your turn" if turn == side else "Opponents Turn"

        turn_label.draw(screen, BLUE if turn == side else RED)

        for each in all + deck + bot_deck:
            each.draw(screen)

        pygame.display.flip()

        if p_i >= 8 and b_i >= 8:
            time.sleep(1) #make sure player can read bot card
            return out, "princesstower", out2, "princesstower"


        

