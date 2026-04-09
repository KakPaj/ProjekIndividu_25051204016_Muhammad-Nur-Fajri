import pygame
import sys

pygame.init()

WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))

class Test:
    def __init__(self, x, y, image):
        self.image = pygame.image.load(image).convert_alpha
        self.x = x
        self.y = y
        self.rect = self.image.get_rect()
        self.speed = 0.5

    def draw(self):
        screen.blit(self.image, self.rect)

        

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
sys.exit()
    