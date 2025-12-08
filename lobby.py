import pygame
import webbrowser

GRAY = (200, 200, 200)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

WIDTH, HEIGHT = 360 + 128, 640 + 128


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
            
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_in(*event.pos):
                return self.value
        return None
            
    def draw(self, screen):
        rect = pygame.Rect(self.x - self.width/2, self.y - self.height/2, self.width, self.height)
        pygame.draw.rect(screen, GRAY, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)  # Border

        font = pygame.font.Font(None, self.font_size) 
        text = font.render(str(self.value), True, BLACK)  # White text
        text_rect = text.get_rect(center=(self.x, self.y))
        screen.blit(text, text_rect)

class CheckBox(SelectionBox):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, True)
        self.value = True

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

def run_loop(screen):
    normal = SelectionBox(100, HEIGHT/2, 100, 50, "Normal")
    draft = SelectionBox(WIDTH/2, HEIGHT/2, 100, 50, "Draft")
    triple = SelectionBox(WIDTH - 100, HEIGHT/2, 100, 50, "Triple Draft")
    quit = SelectionBox(WIDTH/2, HEIGHT - 50, 70, 50, "Quit")
    double = SelectionBox(100, HEIGHT/2 + 60, 100, 50, "2x Elxiir")
    triple_e = SelectionBox(WIDTH/2, HEIGHT/2 + 60, 100, 50, "3x Elxiir")
    septuple = SelectionBox(WIDTH - 100, HEIGHT/2 + 60, 100, 50, "7x Elxiir")
    mega = SelectionBox(WIDTH/2, HEIGHT/2 + 120, 100, 50, "Mega-Draft")
    fourcard = SelectionBox(100, HEIGHT/2 + 120, 100, 50, "Four Card")
    touchdowndraft = SelectionBox(WIDTH - 100, HEIGHT/2 + 120, 100, 50, "Touchdown Draft")
    twovtwo = SelectionBox(WIDTH/2, HEIGHT/2 + 180, 100, 50, "2v2")
    feedback = SelectionBox(50, HEIGHT - 50, 60, 60, "Feedback")
    deck_select = SelectionBox(WIDTH - 50, HEIGHT - 50, 60, 60, "Decks")

    evo_allowed = CheckBox(WIDTH - 30, 30, 40, 40)
    
    out = None
    running = True
    while running:
        screen.fill((100, 100, 100))

        normal.draw(screen)
        draft.draw(screen)
        triple.draw(screen)
        quit.draw(screen)
        double.draw(screen)
        triple_e.draw(screen)
        septuple.draw(screen)
        mega.draw(screen)
        fourcard.draw(screen)
        touchdowndraft.draw(screen)
        twovtwo.draw(screen)
        feedback.draw(screen)
        deck_select.draw(screen)

        evo_allowed.draw(screen)

        font = pygame.font.Font(None, 24) 
        text = font.render("Press b or escape to return to lobby. Press P to pause.", True, BLACK)  # White text
        text_rect = text.get_rect(center=(WIDTH/2, 200))
        screen.blit(text, text_rect)

        text = font.render("Enable Evolutions?", True, BLACK)  # White text
        text_rect = text.get_rect(center=(WIDTH - 150, 30))
        screen.blit(text, text_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                out = "quit"
                running = False

            if normal.handle_event(event) is not None:
                out = "normal"
                running = False
            if draft.handle_event(event) is not None:
                out = "draft"
                running = False
            if triple.handle_event(event) is not None:
                out = "triple_draft"
                running = False
            if double.handle_event(event) is not None:
                out = "double"
                running = False
            if triple_e.handle_event(event) is not None:
                out = "triple"
                running = False
            if septuple.handle_event(event) is not None:
                out = "septuple"
                running = False
            if mega.handle_event(event) is not None:
                out = "megadraft"
                running = False
            if fourcard.handle_event(event) is not None:
                out = "fourcard"
                running = False
            if touchdowndraft.handle_event(event) is not None:
                out = "touchdowndraft"
                running = False
            if twovtwo.handle_event(event) is not None:
                out = "2v2"
                running = False
            if quit.handle_event(event) is not None:
                out = "quit"
                running = False
            if feedback.handle_event(event) is not None:
                webbrowser.open("https://docs.google.com/forms/d/1hAG7VlG38uD6lM9FJef6nG3XhCRz8WkfT2WNUrUI8IA/viewform?edit_requested=true")
            if deck_select.handle_event(event) is not None:
                out = "edit"
                running = False
            evo_allowed.handle_event(event)

        if running:
            pygame.display.flip()

    return out, bool(evo_allowed.value)
