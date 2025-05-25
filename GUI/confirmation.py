import pygame
import sys
from pygame import *

pygame.init()
screen = pygame.display.set_mode((800, 800), pygame.FULLSCREEN)
pygame.display.set_caption("Cancel")

# Define colors
RED = (255, 0, 0)
GREEN = (0, 200, 0)
HOVER_COLOR = (240, 230, 180)
FONT_COLOR = "black"
BACKGROUND = "white"

# Font setup
font = pygame.font.SysFont("arial", 40)
big_font = pygame.font.SysFont("arial", 50)

class Button():
    def __init__(self, width, height, x_pos, y_pos, text_input, default_color):
        self.width = width
        self.height = height
        self.default_color = default_color
        self.hover_color = HOVER_COLOR
        self.current_color = self.default_color
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (self.x_pos, self.y_pos)
        self.text_input = text_input
        self.text = font.render(self.text_input, True, FONT_COLOR)
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

    def update(self):
        pygame.draw.rect(screen, self.current_color, self.rect, border_radius=20)
        screen.blit(self.text, self.text_rect)

    def checkForInput(self, position):
        if self.rect.collidepoint(position):
            print(f"{self.text_input} button clicked!")

    def changeColor(self, position):
        if self.rect.collidepoint(position):
            self.current_color = self.hover_color
        else:
            self.current_color = self.default_color

# lagyan mo ng if statement
cancel_button = Button(250, 100, 425, 600, "Cancel", RED)
confirm_button = Button(250, 100, 725, 600, "Confirm", GREEN)

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == K_F8:
                pygame.quit()
                sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            cancel_button.checkForInput(mouse_pos)
            confirm_button.checkForInput(mouse_pos)

    screen.fill(BACKGROUND)

    # Centered text
    name_text = big_font.render("Name:", True, FONT_COLOR)
    student_text = big_font.render("Student Number:", True, FONT_COLOR)

    screen.blit(name_text, name_text.get_rect(center=(screen.get_width() // 3.2, 250)))
    screen.blit(student_text, student_text.get_rect(center=(screen.get_width() // 2.55, 320)))

    # Update buttons
    mouse_pos = pygame.mouse.get_pos()
    cancel_button.changeColor(mouse_pos)
    confirm_button.changeColor(mouse_pos)

    cancel_button.update()
    confirm_button.update()

    pygame.display.update()
