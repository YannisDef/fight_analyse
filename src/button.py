import pygame
from tools import draw_text

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (75, 75, 75)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
PINK = (255, 182, 193)
PURPLE = (128, 0, 128)

class Button:
    def __init__(self, x, y, height, width, colour, border, curve, text, textColour, is_selected = False):
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.colour = colour
        self.border = border
        self.curve = curve
        self.text = text
        self.textColour = textColour
        self.is_selected = is_selected

    def draw_rect(self, screen, font, event):
        button = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.colour if self.is_selected else GRAY, button, self.border, self.curve)
        if self.text != "":
            self.draw_text(screen, font)
        pygame.display.flip()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if button.collidepoint(event.pos):
                return True

        return False

    def draw_text(self, screen, font):
        text_surf = font.render(self.text, True, self.textColour)
        text_rect = text_surf.get_rect(center=(self.x+self.width//2, self.y+self.height//2))
        screen.blit(text_surf, text_rect)
