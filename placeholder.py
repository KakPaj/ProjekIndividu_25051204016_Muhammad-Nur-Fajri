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
GREEN = (0, 255, 0)
RED = (255, 0, 0)
FOV = 300
CENTERX = WIDTH // 2
CENTERY = HEIGHT // 2

cameraX = 0
cameraY = 0
cameraSpeed = 15

# Setup Tembakan Laser
last_shot_time = 0 
cooldown = 200 
wing_offset = 200
laser_list = []

class shiplaser:
    def __init__(self, worldX, worldY, worldZ):
        self.x = worldX
        self.y = worldY
        self.z = worldZ
        self.color = RED
        self.zSpeed = 30
        self.baseSize = 5
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.isActive = True

    def move(self):
        self.z += self.zSpeed
        if self.z > 4000:
            self.isActive = False

    def summon(self, surface):
        if self.z <= 0: return
        scale = FOV / self.z
        relX = self.x - cameraX
        relY = self.y - cameraY
        screenX = CENTERX + (relX * scale)
        screenY = CENTERY + (relY * scale) + 50
        summonSize = self.baseSize * scale
        if summonSize <= 0: return

        self.rect = pygame.Rect(0, 0, summonSize, summonSize)
        self.rect.center = (int(screenX), int(screenY))
        pygame.draw.rect(surface, self.color, self.rect)

    def rect(self):
        return self.rect

class obstacle:
    def __init__(self, image, sound):
        self.image = pygame.image.load(image).convert_alpha()
        self.z = random.randint(3000, 5000)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.sound = pygame.mixer.Sound(sound)
        
        # Variabel darah (HP)
        self.hp = 6
        
        # Variabel untuk animasi ledakan
        self.is_exploding = False
        self.explosion_timer = 0
        self.explosion_max = 15 # Durasi ledakan (dalam frame)
        self.respawn()
        
    def respawn(self):
        self.is_exploding = False
        self.hp = 6 # Reset darah saat respawn
        if self.z <= 10:
            self.z = random.randint(4000,10000)
        self.x = cameraX + random.randint(-1500, 1500)
        self.y = cameraY + random.randint(-800, 800)
        self.zSpeed = 20
    
    def move(self):
        # Jika sedang meledak, rintangan berhenti bergerak maju
        if not self.is_exploding:
            self.z -= self.zSpeed
            if self.z <= 10:
                self.respawn()

    def rect(self):
        return self.rect

    def take_damage(self):
        # Kurangi HP, hancur jika HP <= 0
        if not self.is_exploding:
            self.hp -= 1
            if self.hp <= 0:
                self.destroy()

    def destroy(self):
        # Memicu ledakan jika belum meledak
        if not self.is_exploding:
            self.is_exploding = True
            self.explosion_timer = self.explosion_max
            self.roar() # Mainkan suara saat meledak

    def summon(self, surface):
        if self.z <= 0: return
        scale = FOV / self.z
        relX = self.x - cameraX
        relY = self.y - cameraY
        screenX = int(CENTERX + (relX * scale))
        screenY = int(CENTERY + (relY * scale))
        
        if self.is_exploding:
            progress = 1 - (self.explosion_timer / self.explosion_max)
            radius = int(self.width * scale * progress * 2)
            
            if radius > 0:
                pygame.draw.circle(surface, (255, 165, 0), (screenX, screenY), radius)
                pygame.draw.circle(surface, (255, 0, 0), (screenX, screenY), int(radius * 0.7))
            
            self.explosion_timer -= 1
            if self.explosion_timer <= 0:
                self.respawn()
        else:
            moveWidth = self.width * scale
            moveHeight = self.height * scale
            if moveWidth > WIDTH or moveWidth <= 0: return

            moveImage = pygame.transform.scale(self.image, (int(moveWidth), int(moveHeight)))
            self.rect = moveImage.get_rect(center=(screenX, screenY))
            surface.blit(moveImage, self.rect)
    
    def roar(self):
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

    def shootK(self):
        if keys[pygame.K_SPACE]:
            self.sound.play()

    def shootG(self):
        self.sound.play()
    
    def rect(self):
        return self.rect

joysticks = []

XWing = XWing(400, 300, "Assets/Image/X-Wing(1).png", "Assets/Sounds/XWingShot.mp3", 0) 


tiefighter = []
for x in range(10):
    tiefighter.append(obstacle("Assets/Image/TIE-Fighter(0).png", "Assets/Sounds/roar.mp3"))

running = True
while running:

    screen.fill(BLACK)
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            print("Goodbye!, May the Force be with You")
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
        yHoriz = joystick.get_axis(1)

        if joystick.get_button(1):
            running = False
            print("Goodbye!, May the Force be with You")

        if rTrigger > 0.5:
            if canShoot == 0:
                XWing.shootG()
                if current_time - last_shot_time > cooldown:
                    laser_start_z = 100 
                    left_screen_x = XWing.rect.centerx - wing_offset
                    left_world_x = ((left_screen_x - CENTERX) * laser_start_z / FOV) + cameraX
                    
                    right_screen_x = XWing.rect.centerx + wing_offset
                    right_world_x = ((right_screen_x - CENTERX) * laser_start_z / FOV) + cameraX
                    
                    world_y = ((XWing.rect.centery - CENTERY) * laser_start_z / FOV) + cameraY
                    
                    laser_list.append(shiplaser(left_world_x, world_y, laser_start_z))
                    laser_list.append(shiplaser(right_world_x, world_y, laser_start_z))
                    last_shot_time = current_time

                canShoot = 1
        elif rTrigger <= 0:
            canShoot = 0

    laser_list = [laser for laser in laser_list if laser.isActive]

    # Mengubah ast menjadi tie
    for tie in tiefighter:
        tie.move()
        if not tie.is_exploding and tie.z < 3000: 
            for lsr in laser_list:
                if lsr.isActive and lsr.rect.colliderect(tie.rect):
                    dist_x = lsr.x - tie.x
                    dist_y = lsr.y - tie.y
                    jarak = (dist_x**2 + dist_y**2)**0.5
                    if jarak < 300: 
                        tie.take_damage() # Memanggil take_damage, bukan langsung destroy
                        lsr.isActive = False
                        break

    tiefighter.sort(key=lambda obj: obj.z, reverse = True)
    for laser in laser_list: laser.move()

    allObjects = tiefighter + laser_list
    allObjects.sort(key=lambda obj: obj.z, reverse=True)

    for obj in allObjects:
        obj.summon(screen)

    # Perbaikan: Memasukkan tabrakan pemain ke dalam loop agar berlaku untuk semua musuh
    for tie in tiefighter:
        if tie.z < 100 and XWing.rect.colliderect(tie.rect):
            if isGamepad and len(joysticks) > 0:
                joysticks[0].rumble(1.0, 1.0, 700)
            tie.respawn()

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