import pygame
import sys

pygame.init()

WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("STAR WARS: Battlefield")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)

class Player:
    def __init__(self, x, y, image, sound):
        self.image = pygame.image.load(image).convert_alpha()
        self.x = x
        self.y = y
        self.rect = self.image.get_rect(center=(x,y))
        self.speed = 5
        self.sound = pygame.mixer.Sound(sound)

    def draw(self):
        screen.blit(self.image, self.rect)

class Bunny(Player):
    def move(self, keys):
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_d]:
            self.rect.x += self.speed
        if keys[pygame.K_s]:
            self.rect.y += self.speed
        if keys[pygame.K_w]:
            self.rect.y -= self.speed

    def cry(self, keys):
        if keys[pygame.K_z]:
            
            self.sound.play()
            print

Scorbunny = Bunny(400, 300, "Assets/Image/Scorbunny.png", "Assets/Sounds/Scorbunny.mp3") 

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            print("Goodbye!")
            running = False
    
    keys = pygame.key.get_pressed()

    screen.fill(WHITE)
    Scorbunny.draw()
    Scorbunny.cry(keys)
    Scorbunny.move(keys)
    pygame.display.flip()

    clock.tick(120)

pygame.quit()
sys.exit()