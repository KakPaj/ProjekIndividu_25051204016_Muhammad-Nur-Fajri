import pygame
import sys
import random

pygame.init()
pygame.joystick.init()

WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("STAR WARS: Battlefield")
clock = pygame.time.Clock()
isGamepad = False
txtC = 0
count = 0

BLACK = (0, 0, 0)
FOV = 300
CENTERX = WIDTH // 2
CENTERY = HEIGHT // 2

cameraX = 0
cameraY = 0
cameraSpeed = 15

class obstacle:
    def __init__(self, image, sound):
        self.image = pygame.image.load(image).convert_alpha()
        self.z = random.randint(7000, 10000)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.sound = pygame.mixer.Sound(sound)
        self.respawn()
        
    def respawn(self):
        if self.z <= 10:
            self.z = random.randint(4000,10000)
        self.x = cameraX + random.randint(-1500, 1500)
        self.y = cameraY + random.randint(-800, 800)
        self.zSpeed = 20
    
    def move(self):
        self.z -= self.zSpeed
        if self.z <= 10:
            self.respawn()

    def rect(self):
        return self.rect

    def summon(self, surface):
        if self.z <= 0: return
        scale = FOV / self.z
        relX = self.x - cameraX
        relY = self.y - cameraY
        screenX = CENTERX + (relX * scale)
        screenY = CENTERY + (relY * scale)
        moveWidth = self.width * scale
        moveHeight = self.height * scale
        if moveWidth > WIDTH or moveWidth <= 0: return

        moveImage = pygame.transform.scale(self.image, (moveHeight, moveWidth))
        self.rect = moveImage.get_rect(center=(screenX, screenY))
        surface.blit(moveImage, self.rect)
    
    def roar(self):
        if self.z < 200:
            self.sound.play()
            self.sound.set_volume(0.7)


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
        global cameraX, cameraY
        self.angle = 0
        if keys[pygame.K_a]:
            self.angle = 15
            cameraX -= cameraSpeed
        if keys[pygame.K_d]:
            self.angle = -15
            cameraX += cameraSpeed
        if keys[pygame.K_s]:
            cameraY += cameraSpeed
        if keys[pygame.K_w]:
            cameraY -= cameraSpeed
    
    def moveG(self, xAxis, yAxis):
        global cameraX, cameraY
        cameraX += cameraSpeed * xAxis
        cameraY += cameraSpeed * yAxis
        targetAngle = xAxis * -20
        self.angle += (targetAngle - self.angle) * 0.25

    def draw(self):
        rotate = pygame.transform.rotate(self.image, self.angle)
        self.rect = rotate.get_rect(center=(WIDTH//2, HEIGHT-150))
        screen.blit(rotate, self.rect)

    def shoot(self):
            self.sound.play()
    
    def rect(self):
        return self.rect

joysticks = []

XWing = XWing(400, 300, "Assets/Image/X-Wing(1).png", "Assets/Sounds/XWingShot.mp3", 0) 

asteroids = []
for x in range(7):
    asteroids.append(obstacle("Assets/Image/TIE-Fighter(0).png", "Assets/Sounds/roar.mp3"))

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
        # print("X:", xHoriz)
        yHoriz = joystick.get_axis(1)
        # print("Y:", yHoriz)

        if joystick.get_button(1):
            running = False
            print("Goodbye!")

        if rTrigger > 0.5:
            if canShoot == 0:
                XWing.shoot()
                canShoot = 1
        elif rTrigger == -1.0:
            canShoot = 0
    print(canShoot)
    screen.fill(BLACK)
    for ast in asteroids: ast.move()
    asteroids.sort(key=lambda obj: obj.z, reverse = True)

    for ast in asteroids:
        ast.summon(screen)
        ast.roar()

    if ast.z < 100 and XWing.rect.colliderect(ast.rect):
        if isGamepad and len(joysticks) > 0:
            joysticks[0].rumble(1.0, 1.0, 700)
        ast.respawn()

    XWing.draw()
    if isGamepad:
        if txtC == 0:
            print("You are using Gamepad, control changed to moveG")
            txtC = 1
        XWing.moveG(xHoriz, yHoriz)
    else:
        if txtC == 0:
            print("You are using Keyboard, control changed to moveK")
            txtC = 1
        XWing.moveK(keys)
    
    pygame.display.flip()

    clock.tick(60)

pygame.quit()
sys.exit()