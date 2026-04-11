import pygame
import sys

pygame.init()
pygame.joystick.init()

WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("STAR WARS: Battlefield")
clock = pygame.time.Clock()
isGamepad = False
txtC = 0

WHITE = (255, 255, 255)

class Player:
    def __init__(self, x, y, image, sound, angle):
        self.image = pygame.image.load(image).convert_alpha()
        self.angle = angle
        self.x = x
        self.y = y
        self.rect = self.image.get_rect(center=(x,y))
        self.speed = 5
        self.sound = pygame.mixer.Sound(sound)

    def draw(self):
        screen.blit(self.image, self.rect)

class XWing(Player):
    def moveK(self, keys):
        self.angle = 0
        if keys[pygame.K_a]:
            self.angle = 15
            self.rect.x -= self.speed
        if keys[pygame.K_d]:
            self.angle = -15
            self.rect.x += self.speed
        if keys[pygame.K_s]:
            self.rect.y += self.speed
        if keys[pygame.K_w]:
            self.rect.y -= self.speed
    
    def moveG(self, keys):
        self.angle = 0
        if keys == "kiri":
            self.angle = 15
            self.rect.x -= self.speed
        if keys == "kanan":
            self.angle = -15
            self.rect.x += self.speed
        if keys == "bawah":
            self.rect.y += self.speed
        if keys == "atas":
            self.rect.y -= self.speed

    def cry(self):
            self.sound.play()
    
    def draw(self):
        rotate = pygame.transform.rotate(self.image, self.angle)
        newShip = rotate.get_rect(center=self.rect.center)
        screen.blit(rotate, newShip)

joysticks = []

XWing = XWing(400, 300, "Assets/Image/X-Wing(1).png", "Assets/Sounds/XWingShot.mp3", 0) 

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            print("Goodbye!")
            running = False
        if event.type == pygame.JOYDEVICEADDED:
            joy = pygame.joystick.Joystick(event.device_index)
            joysticks.append(joy)
            print(joysticks[0])
            isGamepad = True
            txtC = 0
        if event.type == pygame.JOYDEVICEREMOVED:
            isGamepad = False
            txtC = 0

    if isGamepad:
        keys = ""
    else:
        keys = pygame.key.get_pressed()

    canShoot = 0
    for joystick in joysticks:
        lTrigger = joystick.get_axis(2)
        rTrigger = joystick.get_axis(5)
        xHoriz = joystick.get_axis(0)

        if xHoriz > 0.1:
            keys = "kanan"
        elif xHoriz < -0.1:
            keys = "kiri"

        if rTrigger > 0.5:
            if canShoot == 0:
                XWing.cry()
                canShoot = 1
        elif rTrigger == -1.0:
            canShoot = 0

    screen.fill(WHITE)
    XWing.draw()
    if isGamepad:
        if txtC == 0:
            print("You are using Gamepad, control changed to moveG")
            txtC = 1
        XWing.moveG(keys)
    else:
        if txtC == 0:
            print("You are using keyboard, control changed to moveK")
            txtC = 1
        XWing.moveK(keys)
    
    pygame.display.flip()

    clock.tick(60)

pygame.quit()
sys.exit()