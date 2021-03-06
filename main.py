import pygame
import random
import os
import sys

from pygame.constants import K_SPACE, KEYDOWN
from pygame.event import wait

FPS = 100
WIDTH = 500
HEIGHT = 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("第一个游戏")
#pygame.display.set_icon(pygame.image.load(os.path.join("player.ico")))

# 载入图片
background_img = pygame.image.load(
    os.path.join("img", "background.png")).convert()
player_img = pygame.image.load(os.path.join("img", "player.png")).convert()
player_mini_img = pygame.transform.scale(player_img, (25, 20))
player_mini_img.set_colorkey(BLACK)
#rock_img = pygame.image.load(os.path.join("img", "rock.png")).convert()
pygame.display.set_icon(player_mini_img)
bullet_img = pygame.image.load(os.path.join("img", "bullet.png")).convert()
rock_imgs = []
explode_animation = {}
explode_animation['large'] = []
explode_animation['small'] = []
explode_animation['player'] = []
for i in range(9):
    explode_img = pygame.image.load(os.path.join("img", f"expl{i}.png")).convert()
    explode_img.set_colorkey(BLACK)
    #transfrom.scale 重新定义图片大小
    explode_animation['large'].append(pygame.transform.scale(explode_img, (75, 75)))
    explode_animation['small'].append(pygame.transform.scale(explode_img, (30, 30)))
    player_expolde_img = pygame.image.load(os.path.join("img", f"player_expl{i}.png")).convert()
    player_expolde_img.set_colorkey(BLACK)
    explode_animation['player'].append(player_expolde_img)

for i in range(7):
    # f"{i}" -> 可以使用参数
    rock_imgs.append(pygame.image.load(
        os.path.join("img", f"rock{i}.png")).convert())

power_imgs = {}
power_imgs['shield'] = pygame.image.load(os.path.join("img", f"shield.png")).convert()
power_imgs['gun'] = pygame.image.load(os.path.join("img", f"gun.png")).convert()




# 音效
shoot_sound = pygame.mixer.Sound(os.path.join("sound", "shoot.wav"))
gun_sound = pygame.mixer.Sound(os.path.join("sound", "pow1.wav"))
shield_sound = pygame.mixer.Sound(os.path.join("sound", "pow0.wav"))
player_wreck_sound = pygame.mixer.Sound(os.path.join("sound", "rumble.ogg"))

explode_sounds = [
    pygame.mixer.Sound(os.path.join("sound", "expl0.wav")),
    pygame.mixer.Sound(os.path.join("sound", "expl1.wav"))
]
pygame.mixer.music.load(os.path.join("sound", "background.ogg"))
pygame.mixer.music.set_volume(0.3)

font_name = os.path.join("font.ttf")

def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    # 文字 位置
    surf.blit(text_surface, text_rect)

def new_rock():
    r = Rock()
    all_sprites.add(r)
    rocks.add(r)  # 补充石头

def draw_health(surf, hp, x, y):
    if hp < 0:
        hp = 0
    BAR_LENGTH = 100
    BAR_HERGHT = 10
    fill = (hp / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HERGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HERGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

def draw_lives(surf, lives, img, x, y):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)

def draw_init():
    screen.blit(background_img, (0, 0))
    draw_text(screen, "space shoot!", 64, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, "A(or ←) D(or →)移动飞船，空格发射子弹!", 20, WIDTH / 2, HEIGHT / 2)
    draw_text(screen, "按任意键开始游戏！", 18, WIDTH / 2, HEIGHT * 3 / 4)
    pygame.display.update()
    waiting = True
    while waiting:
        clock.tick(FPS)
        # input   event: []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit("GOOD BYE~")
            elif event.type == pygame.KEYUP:
                waiting = False


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (50, 38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20
        #pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 8
        self.health = 100
        self.lives = 3
        self.hidden = False
        self.hide_time = 0
        self.gun = 1
        self.gun_time = 0
        self.what_is_the_attribute = True

    def update(self):
        now = pygame.time.get_ticks()
        if self.gun > 1 and now - self.gun_time > 5000:
            self.gun -= 1
            ##self.gun_time = now  叠加时间

        if self.hidden and now - self.hide_time > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10


        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_d] or key_pressed[pygame.K_RIGHT]:
            self.rect.x += self.speedx
        if key_pressed[pygame.K_a] or key_pressed[pygame.K_LEFT]:
            self.rect.x -= self.speedx

        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

        if self.rect.left < 0:
            self.rect.left = 0
        #self.rect.x += 2
        # if self.rect.left > WIDTH:
        #    self.rect.right = 0

    def shoot(self):
        if not(self.hidden):
            if self.gun == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
            elif self.gun >= 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)  
            shoot_sound.play()

    def hide(self):
        self.hidden = True
        self.hide_time = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2 , HEIGHT + 500)

    def gunup(self):
        self.gun += 1
        self.gun_time = pygame.time.get_ticks()


class Rock(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_original = random.choice(rock_imgs)
        self.image_original.set_colorkey(BLACK)
        self.image = self.image_original.copy()

        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * 0.85 / 2)
        #pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-180, -100)
        self.speedy = random.randrange(2, 10)
        self.speedx = random.randrange(-3, 3)
        self.total_degree = 0
        self.rotate_degree = random.randrange(-3, 3)

    def rotate(self):
        self.total_degree += self.rotate_degree
        self.total_degree = self.total_degree % 360
        self.image = pygame.transform.rotate(
            self.image_original, self.total_degree)
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center

    def update(self):
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx

        if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(2, 10)
            self.speedx = random.randrange(-3, 3)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explode_animation[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        #初始化到现在经过的毫秒数
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explode_animation[self.size]):
                self.kill()
            else:
                self.image = explode_animation[self.size][self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = center


class Power(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = power_imgs[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 3


    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()




#播放背景音乐
pygame.mixer.music.play(-1)

running = True
show_init = True
while running:
    if show_init:
        draw_init()
        show_init = False
        all_sprites = pygame.sprite.Group()
        #用于判断是否发生碰撞
        rocks = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powers = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        for i in range(8):
            new_rock()
        score = 0

    clock.tick(FPS)
    # input   event: []
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    #update all_sprites elements
    all_sprites.update()
    """
        pygame.sprite.groupcollide()
        return dict: key->rock, value->bullet
    """
    hits = pygame.sprite.groupcollide(rocks, bullets, True, True)
    for hit in hits:
        random.choice(explode_sounds).play()
        score += hit.radius
        expl = Explosion(hit.rect.center, 'large')
        all_sprites.add(expl)
        if random.random() > 0.9:
            pow = Power(hit.rect.center)
            all_sprites.add(pow)
            powers.add(pow)
        new_rock()



    hits = pygame.sprite.spritecollide(
        player, rocks, True, pygame.sprite.collide_circle)
    for hit in hits:
        new_rock()
        random.choice(explode_sounds).play()
        player.health -= hit.radius
        expl = Explosion(hit.rect.center, 'small')
        all_sprites.add(expl)
        if player.health <= 0:
            wreck = Explosion(player.rect.center, 'player')
            all_sprites.add(wreck)
            player_wreck_sound.play()
            #复活 减命
            player.lives -= 1
            player.health = 100
            player.hide()

    hits = pygame.sprite.spritecollide(player, powers, True)
    for hit in hits:

        if hit.type == "shield":
            player.health += 20
            if player.health >= 100:
                player.health = 100
            shield_sound.play()
        elif hit.type == "gun":
            player.gunup()
            gun_sound.play()

    if player.lives == 0 and not(wreck.alive()):
        show_init = True

    screen.fill(BLACK)
    # draw
    screen.blit(background_img, (0, 0))

    # draw elements to screen
    all_sprites.draw(screen)
    draw_text(screen, str(score), 18, WIDTH / 2, 10)
    draw_health(screen, player.health, 5, 15)
    draw_lives(screen, player.lives, player_mini_img, WIDTH - 100, 15)
    # update surface 更新画面
    pygame.display.update()


pygame.quit()
