import pygame
import cv2 as cv
import numpy as np
import sys 

class Application:
    def __init__(self):
        pass
    def button():
        pass

#Pygame settings
pygame.init()
screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
running = True

#Window Running
while running:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                screen = pygame.display.set_mode((500,500))
            if event.key == pygame.K_F4:
                screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
            if event.key == pygame.K_F8:
                running = False
        if event.type == pygame.QUIT:
            running = False
        pygame.display.flip()

pygame.quit()
sys.exit()