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

pygame.mixer.music.load("Assets/Sounds/Resistance.mp3")
pygame.mixer.music.play(-1, 0, 0)

isGamepad = False
txtC = 0
kills = 0
isBoss = False
boss_spawned = False
boss_start_time = 0
victory = False
defeat = False
font = pygame.font.SysFont("Arial", 40, bold=True)
win_font = pygame.font.SysFont("Arial", 60, bold=True)

BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
FOV = 300
CENTERX = WIDTH // 2
CENTERY = HEIGHT // 2

cameraX = 0
cameraY = 0
cameraSpeed = 15

last_shot_time = 0 
cooldown = 200 
wing_offset = 200
laser_list = []
boss_lasers = []

crosshair = pygame.image.load("Assets/Image/crosshair.png").convert_alpha()
crosshairRect = crosshair.get_rect(center=(CENTERX, CENTERY + 52))

class bossLaser:
    def __init__(self, worldX, worldY, worldZ):
        self.x = worldX
        self.y = worldY
        self.z = worldZ
        self.color = GREEN
        self.zSpeed = 10
        self.baseSize = 40
        self.isActive = True
        self.rect = pygame.Rect(0, 0, 0, 0)

    def move(self):
        self.z -= self.zSpeed
        if self.z < 0:
            self.isActive = False

    def summon(self, surface):
        if self.z <= 0: return
        scale = FOV / self.z
        relX = self.x - cameraX
        relY = self.y - cameraY
        screenX = CENTERX + (relX * scale)
        screenY = CENTERY + (relY * scale)
        summonSize = self.baseSize * scale
        
        if summonSize > 0:
            self.rect = pygame.Rect(0, 0, summonSize, summonSize)
            self.rect.center = (int(screenX), int(screenY))
            pygame.draw.rect(surface, self.color, self.rect)

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
        screenY = CENTERY + (relY * scale) + 40
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
        self.hp = 6
        self.is_exploding = False
        self.has_roared = False
        self.explosion_timer = 0
        self.explosion_max = 15 
        self.respawn()
        
    def respawn(self):
        self.is_exploding = False
        self.has_roared = False
        self.hp = 6 
        if self.z <= 10:
            self.z = random.randint(4000,10000)
        self.x = cameraX + random.randint(-2500, 2500)
        self.y = cameraY + random.randint(-1200, 1200)
        self.zSpeed = 20
    
    def move(self):
        if not self.is_exploding:
            self.z -= self.zSpeed
            if self.z <= 10:
                self.respawn()

    def rect(self):
        return self.rect

    def take_damage(self):
        global kills
        if not self.is_exploding:
            self.hp -= 1
            if self.hp <= 0:
                kills += 1
                self.destroy()

    def destroy(self):
        if not self.is_exploding:
            self.is_exploding = True
            self.explosion_timer = self.explosion_max

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
        self.sound.set_volume(0.2)

class starDestroyer(obstacle):
    def __init__(self, image, sound):
        super().__init__(image, sound)
        self.hp = 100
        self.x = cameraX
        self.y = cameraY
        self.z = 5000
        self.sound = pygame.mixer.Sound(sound)
        self.zSpeed = 1000
        self.last_shot = 0
        self.shoot_delay = random.randint(500, 1500)

    def respawn(self):
        self.is_exploding = False
        self.z = -1000

    def move(self):
        if not self.is_exploding:
            if self.z > 1000:
                self.z -= self.zSpeed

    def shoot(self, target_list):
        if self.z <= 1000 and not self.is_exploding:
            now = pygame.time.get_ticks()
            if now - self.last_shot > self.shoot_delay:
                side = random.choice([-550, 350]) 
                target_list.append(bossLaser(self.x + side, self.y, self.z))
                self.last_shot = now
                self.shoot_delay = random.randint(2000, 3000)
                self.sound.play()

class Player:
    def __init__(self, x, y, image, sound, angle):
        self.image = pygame.image.load(image).convert_alpha()
        self.angle = angle
        self.x = x
        self.y = y
        self.rect = self.image.get_rect(center=(x,y))
        self.sound = pygame.mixer.Sound(sound)
        self.is_exploding = False
        self.explosion_timer = 0
        self.explosion_max = 30
        self.is_dead = False

    def destroy(self):
        global defeat
        if not self.is_exploding and not self.is_dead:
            self.is_exploding = True
            self.explosion_timer = self.explosion_max
            defeat = True

    def draw(self):
        if self.is_dead: return

        if self.is_exploding:
            progress = 1 - (self.explosion_timer / self.explosion_max)
            radius = int(150 * progress)
            if radius > 0:
                pygame.draw.circle(screen, (255, 165, 0), self.rect.center, radius)
                pygame.draw.circle(screen, (255, 0, 0), self.rect.center, int(radius * 0.7))
            
            self.explosion_timer -= 1
            if self.explosion_timer <= 0:
                self.is_exploding = False
                self.is_dead = True
        else:
            screen.blit(self.image, self.rect)

class XWing(Player):
    def moveK(self, keys):
        if self.is_exploding or self.is_dead: return
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
        if self.is_exploding or self.is_dead: return
        global cameraX, cameraY
        cameraX += cameraSpeed * xAxis
        cameraY += cameraSpeed * yAxis
        targetAngle = xAxis * -20
        self.angle += (targetAngle - self.angle) * 0.25

    def draw(self):
        if self.is_dead: return
        if self.is_exploding:
            super().draw()
        else:
            rotate = pygame.transform.rotate(self.image, self.angle)
            self.rect = rotate.get_rect(center=(WIDTH//2, HEIGHT-180))
            screen.blit(rotate, self.rect)

    def shootG(self):
        if not self.is_exploding and not self.is_dead:
            self.sound.play()

joysticks = []
XWing = XWing(400, 300, "Assets/Image/X-Wing(1).png", "Assets/Sounds/XWingShot.mp3", 0)

asteroids = []
for ast in range(30):
    asteroids.append(obstacle("Assets/Image/asteroid.png", "Assets/Sounds/whoosh.mp3"))

tiefighter = []
for tie in range(20):
    tiefighter.append(obstacle("Assets/Image/TIE-Fighter(0).png", "Assets/Sounds/roar.mp3"))

StarDestroyer = starDestroyer("Assets/Image/StarDestroyer1.png", "Assets/Sounds/sdlaser.mp3")

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
            isGamepad = True
            txtC = 0
        if event.type == pygame.JOYDEVICEREMOVED:
            isGamepad = False
            txtC = 0

    if isGamepad:
        keys = ""
        xHoriz = joysticks[0].get_axis(0)
        yHoriz = joysticks[0].get_axis(1)
        rTrigger = joysticks[0].get_axis(5)
    else:
        keys = pygame.key.get_pressed()

    if not victory and not defeat:
        if (isGamepad and rTrigger > 0.5) or (not isGamepad and keys[pygame.K_SPACE]):
            if current_time - last_shot_time > cooldown:
                XWing.shootG()
                laser_start_z = 100 
                left_world_x = ((XWing.rect.centerx - wing_offset - CENTERX) * laser_start_z / FOV) + cameraX
                right_world_x = ((XWing.rect.centerx + wing_offset - CENTERX) * laser_start_z / FOV) + cameraX
                world_y = ((XWing.rect.centery - CENTERY) * laser_start_z / FOV) + cameraY
                
                laser_list.append(shiplaser(left_world_x, world_y, laser_start_z))
                laser_list.append(shiplaser(right_world_x, world_y, laser_start_z))
                last_shot_time = current_time

    if kills >= 10 and not boss_spawned:
        isBoss = True
        boss_spawned = True
        boss_start_time = pygame.time.get_ticks()
        laser_list.clear()

    if not isBoss:
        if not defeat: screen.blit(font.render(f"KILLS: {max(0, kills)}", True, RED), (WIDTH-200, 20))
        
        laser_list = [laser for laser in laser_list if laser.isActive]
        
        for ast in asteroids: 
            ast.move()
            if not ast.has_roared and not ast.is_exploding and ast.z < 1000:
                ast.roar()
                ast.has_roared = True

            if not XWing.is_exploding and ast.z < 100 and XWing.rect.colliderect(ast.rect):
                XWing.destroy()
                ast.destroy()

        for tie in tiefighter:
            tie.move()
            if not tie.has_roared and not tie.is_exploding and tie.z < 1000:
                tie.roar()
                tie.has_roared = True

            if not tie.is_exploding and tie.z < 7000: 
                for lsr in laser_list:
                    if lsr.isActive and lsr.rect.colliderect(tie.rect):
                        distX = lsr.x - tie.x
                        distY = lsr.y - tie.y
                        if (distX**2 + distY**2)**0.5 < 300: 
                            tie.take_damage()
                            lsr.isActive = False
                            break
            if not XWing.is_exploding and tie.z < 100 and XWing.rect.colliderect(tie.rect):
                XWing.destroy()
                tie.destroy()

        tiefighter.sort(key=lambda obj: obj.z, reverse=True)
        for laser in laser_list: laser.move()
        allObjects = tiefighter + laser_list + asteroids
        allObjects.sort(key=lambda obj: obj.z, reverse=True)
        for obj in allObjects: obj.summon(screen)
    else:
        if not victory and not defeat:
            elapsed_boss_time = (pygame.time.get_ticks() - boss_start_time) // 1000
            timer_countdown = 30 - elapsed_boss_time
            
            if timer_countdown <= 0 and StarDestroyer.hp > 0:
                XWing.destroy()

            StarDestroyer.move()
            StarDestroyer.shoot(boss_lasers)

            if StarDestroyer.hp <= 0 and StarDestroyer.z < 0:
                victory = True

        boss_lasers = [bl for bl in boss_lasers if bl.isActive]
        for bl in boss_lasers:
            bl.move()
            if not XWing.is_exploding and bl.rect.colliderect(XWing.rect):
                if isGamepad: joysticks[0].rumble(1.0, 1.0, 500)
                XWing.destroy()
                bl.isActive = False

        laser_list = [lsr for lsr in laser_list if lsr.isActive]
        for lsr in laser_list:
            lsr.move()
            if lsr.rect.colliderect(StarDestroyer.rect):
                StarDestroyer.hp -= 1
                lsr.isActive = False
                if StarDestroyer.hp <= 0:
                    StarDestroyer.destroy()

        all_boss_scene = [StarDestroyer] + laser_list + boss_lasers
        all_boss_scene.sort(key=lambda obj: obj.z, reverse=True)
        for obj in all_boss_scene: obj.summon(screen)

        if not victory and not defeat:
            screen.blit(font.render(f"TIME: {max(0, timer_countdown)}", True, RED), (WIDTH-200, 20))
            screen.blit(font.render(f"BOSS HP: {max(0, StarDestroyer.hp)}", True, GREEN), (20, 20))

    if victory:
        win_text = win_font.render("RESISTANCE WIN", True, GREEN)
        screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT - 380))
    elif defeat:
        lose_text = win_font.render("FIRST ORDER WIN", True, RED)
        screen.blit(lose_text, (WIDTH//2 - lose_text.get_width()//2, HEIGHT - 380))

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

    if not defeat and not victory:
        screen.blit(crosshair, crosshairRect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()