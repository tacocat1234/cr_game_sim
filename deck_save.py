from card_factory import troops, buildings, spells, champions
from card_factory import can_evo
from card_factory import generate_random_remaining
from card_factory import get_type
from card_factory import elixir_map
from cards import Card
import random
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

class DeckBox(SelectionBox):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.value = "New Deck"

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_in(*event.pos):
                x, y = event.pos
                if x > self.x + self.width / 2 - self.height - 20:
                    return False  # Clicked on the delete button
                return True
            
    def draw(self, screen):
        rect = pygame.Rect(self.x - self.width/2, self.y - self.height/2, self.width, self.height)
        pygame.draw.rect(screen, LIGHT_GRAY if not self.active else GRAY, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)  # Border

        font = pygame.font.Font(None, self.font_size)
        text = font.render(str(self.value), True, BLACK)
        text_rect = text.get_rect(center=(self.x, self.y))
        screen.blit(text, text_rect)

        # Draw red delete box with X
        delete_box_size = self.height - 20
        delete_box_x = self.x + self.width / 2 - delete_box_size - 10
        delete_box_y = self.y - self.height / 2 + 10
        delete_rect = pygame.Rect(delete_box_x, delete_box_y, delete_box_size, delete_box_size)
        pygame.draw.rect(screen, (200, 0, 0), delete_rect)
        pygame.draw.rect(screen, BLACK, delete_rect, 2)

        # Draw X
        pygame.draw.line(screen, BLACK, delete_rect.topleft, delete_rect.bottomright, 3)
        pygame.draw.line(screen, BLACK, delete_rect.topright, delete_rect.bottomleft, 3)

class DeckListBox(SelectionBox):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.decks = []
        self.deck_boxes = []

    def new_deck(self, screen, evo_enabled=True):
        deck = create_deck(screen, evo_enabled, "ND" + str(len(self.deck_boxes) + 1))
        if deck is not None:
            self.deck_boxes.append(DeckBox(self.x, self.y - self.height/2 + 35 + len(self.deck_boxes) * (60), self.width - 20, 50))
            level, cards, tower_type, name = deck
            self.deck_boxes[len(self.deck_boxes) - 1].value = name
            self.decks.append((name, cards, tower_type, level))

    def edit_deck(self, screen, index, evo_enabled=True):
        if 0 <= index < len(self.deck_boxes):
            deck = create_deck(screen, evo_enabled, self.deck_boxes[index].value, self.decks[index][3], self.decks[index][1], self.decks[index][2])
            if deck is not None:
                level, cards, tower_type, name = deck
                self.deck_boxes[index].value = name
                self.decks[index] = (name, cards, tower_type, level)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_in(*event.pos):
                for i in range(len(self.deck_boxes)):
                    h = self.deck_boxes[i].handle_event(event)
                    if h is not None:
                        if h:
                            return i  #index of the deck box clicked
                        else:
                            # Handle delete button click
                            del self.deck_boxes[i]
                            del self.decks[i]
                            for j in range(i, len(self.deck_boxes)):
                                self.deck_boxes[j].y -= 60
                            return None  # Deck deleted

    def draw(self, screen):
        rect = pygame.Rect(self.x - self.width/2, self.y - self.height/2, self.width, self.height)
        pygame.draw.rect(screen, LIGHT_GRAY if not self.active else GRAY, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)  # Border

        for each in self.deck_boxes:
            each.draw(screen)

def deck_list_loop(screen, evo_enabled = True, decks=None):
    deck_list = DeckListBox(WIDTH/2, HEIGHT/2, 300, 640)

    if decks is not None:
        for name, cards, tower_type, level in decks:
            deck_list.deck_boxes.append(DeckBox(deck_list.x, deck_list.y - deck_list.height/2 + 35 + len(deck_list.deck_boxes) * 60, deck_list.width - 20, 50))
            deck_list.deck_boxes[-1].value = name
            deck_list.decks.append((name, cards, tower_type, level))

    return_box = SubmitBox(WIDTH/2, HEIGHT - 60, 100, 50)
    new_deck_button = SubmitBox(WIDTH/2, 50, 50, 50) #modify position later
    new_deck_button.value = "+"
    new_deck_button.font_size = 48
    return_box.value = "Return"

    running = True
    while running:
        screen.fill((100, 100, 100))
        deck_list.draw(screen)
        return_box.draw(screen)
        new_deck_button.draw(screen)

        font = pygame.font.Font(None, 24) 
        t = "Deck List"
        text = font.render(t, True, BLACK)
        text_rect = text.get_rect(center=(WIDTH/2, 15))
        screen.blit(text, text_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
            i = deck_list.handle_event(event)
            return_box.handle_event(event)
            new_deck_button.handle_event(event)

            if new_deck_button.value == True:
                deck_list.new_deck(screen, evo_enabled)
                new_deck_button.value = "+"
            elif i is not None:
                deck_list.edit_deck(screen, i, evo_enabled)
            elif return_box.value == True:
                return deck_list.decks
        pygame.display.flip()
        


def create_deck(screen, evo_enabled = True, default_name = "New Deck", level=None, cards=None, tower_type=None):
    lev = SelectionBox(100, 100, 50, 50)
    lev.font_size = 24
    lev.value = "11"
    deck_name = SelectionBox(WIDTH/2, 200, 300, 50)
    deck_name.value = default_name
    deck_name.font_size = 24
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

    if cards is not None:
        for i in range(len(cards)):
            all[i].value = cards[i].name
            if cards[i].is_evo and evo_enabled:
                display_evo[i] = True
                evo[i].value = True
            else:
                display_evo[i] = False
                evo[i].value = False

    if level is not None:
        lev.value = str(level)

    if tower_type is not None:
        tower.value = tower_type

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
        deck_name.draw(screen)

        font = pygame.font.Font(None, 24) 

        t = "Deck Editor"
        text = font.render(t, True, BLACK)  # White text
        text_rect = text.get_rect(center=(WIDTH/2, 15))
        screen.blit(text, text_rect)

        text = font.render("Type in boxes", True, BLACK)  # White text
        text_rect = text.get_rect(center=(WIDTH/2, 100))
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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
            for each in all:
                each.handle_event(event)
            for i in range(8):
                if display_evo[i] and evo_enabled:
                    evo[i].handle_event(event)
            lev.handle_event(event)
            tower.handle_event(event)
            submit.handle_event(event)
            deck_name.handle_event(event)
            if submit.value != "Submit":
                running = False
        pygame.display.flip()

    


    out = []

    rand_input = []
    for i in range(8):
        if all[i].value != "":
            n = fuzzy_match(all[i].value, troops + buildings + spells + champions + ["mirror", "oldgoblinhut"])
            rand_input.append([get_type(n), elixir_map[n], n, bool(evo[i].value)])

    temp = []

    temp = [[each[2], each[3]] for each in rand_input]

    for each in temp:
        out.append(Card(True, each[0], int(lev.value), each[1])) #not nesscarily full deck, side also gets rewritten later

    t = "" if tower.value == "" else fuzzy_match(tower.value, ["princesstower", "cannoneer", "daggerduchess", "royalchef"])

    return int(lev.value), out, t, deck_name.value