import pygame, sys
from pygame.locals import *
import random, time

pygame.init()
pygame.mixer.init()
crash_sound = pygame.mixer.Sound("crash.wav")

#fps
FPS = 60
FramePerSec = pygame.time.Clock()

#colors
BLUE  = (0,   0,   255)
RED   = (255, 0,   0)
GREEN = (0,   255, 0)
BLACK = (0,   0,   0)
WHITE = (255, 255, 255)
GOLD  = (255, 215, 0)   # color of coin

#screen parameters
SCREEN_WIDTH  = 400
SCREEN_HEIGHT = 600
SPEED         = 5    # Начальная скорость врагов
SCORE         = 0    # Счёт за уклонение
COINS         = 0    # Количество собранных монет

#fonts and text
font       = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)
game_over  = font.render("Game Over", True, BLACK)

#background
bg_img     = pygame.image.load("AnimatedStreet.png")
background = pygame.transform.scale(bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

#window
DISPLAYSURF = pygame.display.set_mode((400, 600))
DISPLAYSURF.fill(WHITE)
pygame.display.set_caption("Game")


#enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        img = pygame.image.load("Enemy.png")
        self.image = pygame.transform.scale(img, (50, 80))
        self.rect  = self.image.get_rect()
        #appears at a horizontal line
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

    def move(self):
        global SCORE
        self.rect.move_ip(0, SPEED)
        #enemy went outside - get a coin and reset
        if self.rect.top > 600:
            SCORE += 1
            self.rect.top    = 0
            self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

#player'c class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        img = pygame.image.load("Player.png")
        self.image = pygame.transform.scale(img, (50, 80))
        self.rect  = self.image.get_rect()
        self.rect.center = (160, 520)  #starting position

    def move(self):
        #read the pressed keys
        pressed_keys = pygame.key.get_pressed()
        #left action with checking the left boundary
        if self.rect.left > 0:
            if pressed_keys[K_LEFT]:
                self.rect.move_ip(-5, 0)
        #right action with checking the right boundary
        if self.rect.right < SCREEN_WIDTH:
            if pressed_keys[K_RIGHT]:
                self.rect.move_ip(5, 0)


#class of coin
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        #drawing a coin
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, GOLD, (10, 10), 10)
        self.rect  = self.image.get_rect()
        #random position of coin
        self.rect.center = (random.randint(20, SCREEN_WIDTH - 20), 0)

    def move(self):
        #speed of coin
        self.rect.move_ip(0, SPEED)
        #if coin went out of a screen we reset it from all groups
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()



P1 = Player()
E1 = Enemy()

#sprite groups
enemies     = pygame.sprite.Group()
coins       = pygame.sprite.Group()  
all_sprites = pygame.sprite.Group()

enemies.add(E1)
all_sprites.add(P1)
all_sprites.add(E1)

INC_SPEED  = pygame.USEREVENT + 1   #adding speed each second
SPAWN_COIN = pygame.USEREVENT + 2   # every 3 sec we put coin
pygame.time.set_timer(INC_SPEED,  1000)
pygame.time.set_timer(SPAWN_COIN, 3000)


while True:

    
    for event in pygame.event.get():
        if event.type == INC_SPEED:
            SPEED += 0.5          
        if event.type == SPAWN_COIN:
            new_coin = Coin()
            coins.add(new_coin)
            all_sprites.add(new_coin)
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    DISPLAYSURF.blit(background, (0, 0))

    scores = font_small.render(f"Score: {SCORE}", True, BLACK)
    DISPLAYSURF.blit(scores, (10, 10))

    coin_text  = font_small.render(f"Coins: {COINS}", True, GOLD)
    coin_x = SCREEN_WIDTH - coin_text.get_width() - 10
    DISPLAYSURF.blit(coin_text, (coin_x, 10))

    for entity in all_sprites:
        DISPLAYSURF.blit(entity.image, entity.rect)
        entity.move()

    collected = pygame.sprite.spritecollide(P1, coins, True) 
    if collected:
        COINS += len(collected)  
    if pygame.sprite.spritecollideany(P1, enemies):
        crash_sound.play()
        time.sleep(0.5)
        DISPLAYSURF.fill(RED)
        DISPLAYSURF.blit(game_over, (30, 250))
        final_coins = font_small.render(f"Coins collected: {COINS}", True, GOLD)
        DISPLAYSURF.blit(final_coins, (110, 330))
        pygame.display.update()
        time.sleep(2)
        pygame.quit()
        sys.exit()

    pygame.display.update()
    FramePerSec.tick(FPS)