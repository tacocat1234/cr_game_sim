import pygame

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

def run_loop(screen):
    normal = SelectionBox(100, HEIGHT/2, 100, 50, "Normal")
    triple = SelectionBox(WIDTH - 100, HEIGHT/2, 100, 50, "Triple Draft")
    quit = SelectionBox(WIDTH/2, HEIGHT - 50, 70, 50, "Quit")
    
    out = None
    running = True
    while running:
        screen.fill((100, 100, 100))

        normal.draw(screen)
        triple.draw(screen)
        quit.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if normal.handle_event(event) is not None:
                out = "normal"
                running = False
            if triple.handle_event(event) is not None:
                out = "triple_draft"
                running = False
            if quit.handle_event(event) is not None:
                out = "quit"
                running = False

        if running:
            pygame.display.flip()

    return out
