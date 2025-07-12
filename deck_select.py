from card_factory import troops, buildings, spells
from card_factory import can_evo
from card_factory import generate_random_remaining
from card_factory import get_type
from card_factory import elixir_map
from cards import Card
import pygame

LIGHT_GRAY = (150, 150, 150)
GRAY = (200, 200, 200)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
WIDTH, HEIGHT = 360 + 128, 640 + 128

def word_dist(s1, s2):
    d = {}
    lenstr1 = len(s1)
    lenstr2 = len(s2)
    
    for i in range(-1, lenstr1 + 1):
        d[(i, -1)] = i + 1
    for j in range(-1, lenstr2 + 1):
        d[(-1, j)] = j + 1

    for i in range(lenstr1):
        for j in range(lenstr2):
            cost = 0 if s1[i] == s2[j] else 1
            d[(i, j)] = min(
                d[(i - 1, j)] + 1,     # deletion
                d[(i, j - 1)] + 1,     # insertion
                d[(i - 1, j - 1)] + cost  # substitution
            )
            if i > 0 and j > 0 and s1[i] == s2[j - 1] and s1[i - 1] == s2[j]:
                d[(i, j)] = min(d[(i, j)], d[(i - 2, j - 2)] + cost)  # transposition

    return d[lenstr1 - 1, lenstr2 - 1]

def fuzzy_match(string, list):

    if string in list:
        return string

    min_dist = float("inf")
    out = None
    for each in list:
        d = word_dist(string, each)
        if d < min_dist:
            out = each
            min_dist = d

    return out

class SelectionBox:
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
            
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_in(*event.pos):
                self.active = True
            else:
                self.active = False

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False  # Optionally deactivate after enter
            elif event.key == pygame.K_BACKSPACE:
                self.value = self.value[:-1]
            else:
                self.value += event.unicode
            
    def draw(self, screen):
        rect = pygame.Rect(self.x - self.width/2, self.y - self.height/2, self.width, self.height)
        pygame.draw.rect(screen, LIGHT_GRAY if not self.active else GRAY, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)  # Border

        font = pygame.font.Font(None, self.font_size) 
        text = font.render(str(self.value), True, BLACK)  # White text
        text_rect = text.get_rect(center=(self.x, self.y))
        screen.blit(text, text_rect)

class CheckBox(SelectionBox):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.value = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_in(*event.pos):
                self.value = not self.value

    def draw(self, screen):
        rect = pygame.Rect(self.x - self.width / 2, self.y - self.height / 2, self.width, self.height)
        pygame.draw.rect(screen, (120, 0, 160) if self.value else GRAY, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)  # Border

        if self.value:
            pygame.draw.line(screen, BLACK, rect.topleft, rect.bottomright, 3)
            pygame.draw.line(screen, BLACK, rect.topright, rect.bottomleft, 3)

class SubmitBox(SelectionBox):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.value = "Submit"

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_in(*event.pos):
                self.value = True

def run_loop(screen, evo_enabled = True, side = True):
    lev = SelectionBox(100, 100, 50, 50)
    lev.font_size = 24
    lev.value = "11" if side else "13"
    rand = CheckBox(WIDTH - 100, 100, 50, 50)
    all = [
        SelectionBox(WIDTH/5, HEIGHT/2 - 70, 80, 80),
        SelectionBox(2*WIDTH/5, HEIGHT/2 - 70, 80, 80),
        SelectionBox(3*WIDTH/5, HEIGHT/2 - 70, 80, 80),
        SelectionBox(4*WIDTH/5, HEIGHT/2 - 70, 80, 80),
        SelectionBox(WIDTH/5, HEIGHT/2 + 70, 80, 80),
        SelectionBox(2*WIDTH/5, HEIGHT/2 + 70, 80, 80),
        SelectionBox(3*WIDTH/5, HEIGHT/2 + 70, 80, 80),
        SelectionBox(4*WIDTH/5, HEIGHT/2 + 70, 80, 80)]
    tower = SelectionBox(WIDTH/2, HEIGHT/2 + 200, 80, 80)
    submit = SubmitBox(WIDTH/2, HEIGHT - 60, 100, 50)

    display_evo = [False,
                   False,
                   False,
                   False,
                   False,
                   False,
                   False,
                   False
                ]
    evo = [
        CheckBox(WIDTH/5, HEIGHT/2 - 140, 20, 20),
        CheckBox(2*WIDTH/5, HEIGHT/2 - 140, 20, 20),
        CheckBox(3*WIDTH/5, HEIGHT/2 - 140, 20, 20),
        CheckBox(4*WIDTH/5, HEIGHT/2 - 140, 20, 20),
        CheckBox(WIDTH/5, HEIGHT/2 + 10, 20, 20),
        CheckBox(2*WIDTH/5, HEIGHT/2 + 10, 20, 20),
        CheckBox(3*WIDTH/5, HEIGHT/2 + 10, 20, 20),
        CheckBox(4*WIDTH/5, HEIGHT/2 + 10, 20, 20)
    ]

    running = True
    while running:
        screen.fill((100, 100, 100))
        for i in range(8):
            v = all[i].value
            if v is not None and can_evo(v):
                display_evo[i] = True
            else:
                display_evo[i] = False
                evo[i].value = False

            all[i].draw(screen)

        for i in range(8):
            if display_evo[i] and evo_enabled:
                evo[i].draw(screen)
        lev.draw(screen)
        tower.draw(screen)
        submit.draw(screen)
        rand.draw(screen)

        font = pygame.font.Font(None, 24) 

        text = font.render("Player Deck" if side else "Bot Deck", True, BLACK)  # White text
        text_rect = text.get_rect(center=(WIDTH/2, 15))
        screen.blit(text, text_rect)

        text = font.render("Type in boxes", True, BLACK)  # White text
        text_rect = text.get_rect(center=(WIDTH/2, 210))
        screen.blit(text, text_rect)

        text = font.render("Randomize All Empty", True, BLACK)  # White text
        text_rect = text.get_rect(center=(WIDTH - 100, 50))
        screen.blit(text, text_rect)

        text = font.render("Level", True, BLACK)  # White text
        text_rect = text.get_rect(center=(100, 50))
        screen.blit(text, text_rect)

        text = font.render("Tower Troop", True, BLACK)  # White text
        text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2 + 150))
        screen.blit(text, text_rect)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            for each in all:
                each.handle_event(event)
            for i in range(8):
                if display_evo[i] and evo_enabled:
                    evo[i].handle_event(event)
            lev.handle_event(event)
            tower.handle_event(event)
            submit.handle_event(event)
            rand.handle_event(event)
            if submit.value != "Submit":
                running = False
        pygame.display.flip()

    


    out = []

    rand_input = []
    for i in range(8):
        if all[i].value != "":
            n = fuzzy_match(all[i].value, troops + buildings + spells)
            rand_input.append([get_type(n), elixir_map[n], n])

    temp = []

    if len(rand_input) != 8:
        temp = generate_random_remaining(rand_input)
    else:
        temp = [each[2] for each in rand_input]

    for each in temp:
        out.append(Card(side, each, int(lev.value), bool(evo[i].value)))

    return len(rand_input) == 0, int(lev.value), out, fuzzy_match(tower.value, ["princesstower", "cannoneer", "daggerduchess", "royalchef"])