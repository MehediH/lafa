import pygame
from defaults import *
from random import choice, randrange

class Spritesheet:
    # load and parse assets from spritesheets
    def __init__(self, filename):
        self.spritesheet = pygame.image.load(filename).convert()
    
    def get_image(self, x, y, width, height):
        image = pygame.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        return image

class Platformsheet:
    # load and parse assets from spritesheets
    def __init__(self, filename):
        self.platformsheet = pygame.image.load(filename).convert()
    
    def get_image(self, x, y, width, height):
        image = pygame.Surface((width, height))
        image.blit(self.platformsheet, (0, 0), (x, y, width, height))
        return image

class Player(pygame.sprite.Sprite):
    def __init__(self, game, avi):
        self.__layer__ = PLAYER_LAYER
        self.groups = game.sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.walking = False
        self.isjumping = False
        self.falling = False
        self.current_frame = 0 # current frame
        self.last_update = 0
        self.avi = avi
        self.loadCharacters(self.avi)
        self.image = self.standing[0]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)
        self.position = pygame.math.Vector2(WIDTH / 2, HEIGHT / 2)
        self.velocity = pygame.math.Vector2(0, 0)
        self.accleration = pygame.math.Vector2(0, 0)

    def loadCharacters(self, avi):
        
        if(avi == "green"):
            self.standing = [
                self.game.spritesheet.get_image(890, 0, 38, 50),
                self.game.spritesheet.get_image(890, 51, 38, 50)
            ]

            self.walking_r = [
                self.game.spritesheet.get_image(890, 366, 38, 50),
                self.game.spritesheet.get_image(889, 963, 38, 48),
                self.game.spritesheet.get_image(889, 877, 38, 48)
            ]

            self.flying = [
                self.game.spritesheet.get_image(890, 51, 38, 50),
                self.game.spritesheet.get_image(849, 877, 38, 43),
                self.game.spritesheet.get_image(849, 429, 40, 39)
            ]

        if(avi == "red"):
            self.standing = [
                self.game.spritesheet.get_image(850, 518, 39, 48),
                self.game.spritesheet.get_image(850, 469, 39, 48)
            ]

            self.walking_r = [
                self.game.spritesheet.get_image(850, 47, 39, 48),
                self.game.spritesheet.get_image(849, 96, 39, 45),
                self.game.spritesheet.get_image(710, 384, 49, 45)
            ]

            self.flying = [
                self.game.spritesheet.get_image(850, 469, 39, 48),
                self.game.spritesheet.get_image(850, 0, 39, 46),
                self.game.spritesheet.get_image(650, 685, 56, 38)
            ]

        if(avi == "blue"):
            self.standing = [
                self.game.spritesheet.get_image(762, 203, 45, 54),
                self.game.spritesheet.get_image(760, 435, 45, 54)
            ]

            self.walking_r = [
                self.game.spritesheet.get_image(759, 812, 45, 54),
                self.game.spritesheet.get_image(760, 380, 45, 54),
                self.game.spritesheet.get_image(759, 503, 45, 52)
            ]

            self.flying = [
                self.game.spritesheet.get_image(760, 435, 45, 54),
                self.game.spritesheet.get_image(759, 556, 45, 50),
                self.game.spritesheet.get_image(758, 771, 45, 40)
            ]

        if(avi == "grey"):
            self.standing = [
                self.game.spritesheet.get_image(890, 799, 36, 45),
                self.game.spritesheet.get_image(927, 578, 36, 45)
            ]

            self.walking_r = [
                self.game.spritesheet.get_image(927, 791, 36, 45),
                self.game.spritesheet.get_image(890, 417, 37, 43),
                self.game.spritesheet.get_image(890, 494, 37, 42)
            ]

            self.flying = [
                self.game.spritesheet.get_image(927, 578, 36, 45),
                self.game.spritesheet.get_image(890, 537, 37, 40),
                self.game.spritesheet.get_image(764, 55, 44, 36)
            ]

        self.walking_l = []

        for frame in self.walking_r:
            frame.set_colorkey(BLACK)
            self.walking_l.append(pygame.transform.flip(frame, True, False))


        for frame in self.standing:
            frame.set_colorkey(BLACK)

    
    def jump(self):
        # jump only when standing on a platform
        self.rect.x += 1
        hits = pygame.sprite.pygame.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.x -= 1

        if hits and not self.isjumping:
            self.game.jumpSound.play()
            self.isjumping = True
            self.velocity.y = PLAYER_STRENGTH

            now = pygame.time.get_ticks()

            if now - self.last_update > 350:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.flying)
                bottom = self.rect.bottom
                self.image = self.flying[self.current_frame]
                self.image.set_colorkey(BLACK)
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom

    def jumpCut(self):
        if self.isjumping:
            if self.velocity.y < -3:
                self.velocity.y = -3
            

    def update(self):
        self.animate()
        self.accleration = pygame.math.Vector2(0, PLAYER_GRAVITY)
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.accleration.x = -PLAYER_ACCELERATION

        if keys[pygame.K_RIGHT]:
            self.accleration.x = PLAYER_ACCELERATION

        # motion algo
        self.accleration.x += self.velocity.x * PLAYER_FRICTION

        self.velocity += self.accleration

        if abs(self.velocity.x) < 0.1:
            self.velocity.x = 0

        self.position += self.velocity + 0.5 * self.accleration

        # wraparound player
        if self.position.x > WIDTH + self.rect.width / 2:
            self.position.x = 0 - self.rect.width / 2
        if self.position.x < 0 - self.rect.width / 2:
            self.position.x = WIDTH + self.rect.width / 2

        self.rect.midbottom = self.position

    def animate(self):
        now = pygame.time.get_ticks()
        if self.velocity.x != 0:
            self.walking = True
        else:
            self.walking = False

        # show walk animation
        if self.walking:
            if now - self.last_update > 180:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.walking_l)
                bottom = self.rect.bottom

                if self.velocity.x > 0:
                    self.image = self.walking_r[self.current_frame]
                else:
                    self.image = self.walking_l[self.current_frame]

                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        # show idle animation
        if not self.isjumping and not self.walking:
            if now - self.last_update > 350:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.standing)
                bottom = self.rect.bottom
                self.image = self.standing[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom

        self.mask = pygame.mask.from_surface(self.image)


class Platform(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.__layer__ = PLATFORM_LAYER
        self.groups = game.sprites, game.platforms
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.game = game

        images = [
            self.game.platformsheet.get_image(64, 0, 192, 64),
            self.game.platformsheet.get_image(64, 192, 192, 64),
            self.game.platformsheet.get_image(64, 384, 192, 64),
            self.game.platformsheet.get_image(448, 62, 130, 64),
            self.game.platformsheet.get_image(448, 254, 130, 64),
            self.game.platformsheet.get_image(448, 448, 130, 64)
        ]

        self.image = choice(images)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        if randrange(100) < POW_SPAWN_HZ:
            Power(self.game, self)

class Power(pygame.sprite.Sprite):
    def __init__(self, game, plat):
        self.__layer__ = POWER_LAYER
        self.groups = game.sprites, game.powerups
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.plat = plat
        self.type = choice(['boost', 'life'])
        
        if(self.type == "boost"):
            self.image = self.game.spritesheet.get_image(929, 317, 32, 30)
        else:
            self.image = self.game.spritesheet.get_image(928, 138, 34, 39)

        self.image.set_colorkey(BLACK)

        self.rect = self.image.get_rect()
        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom = self.plat.rect.top - 5

    def update(self):
        self.rect.bottom = self.plat.rect.top - 5
        if not self.game.platforms.has(self.plat):
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, game):
        self.__layer__ = ENEMY_LAYER
        self.groups = game.sprites, game.enemies
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        self.flying = self.game.spritesheet.get_image(455, 390, 64, 38)
        self.flyingDown = self.game.spritesheet.get_image(455, 533, 64, 43)
        
        self.image = self.flying
        self.rect = self.image.get_rect()
        self.rect.centerx = choice([-100, WIDTH + 100])
        self.vx = randrange(1, 5)

        if(self.rect.centerx > WIDTH):
            self.vx *= -1 

        self.rect.y = randrange(HEIGHT / 2)
        self.vy = 0

        self.dc = 0.5
        
    
    def update(self):
        self.rect.x += self.vx
        self.vy += self.dc

        if(self.vy > 3 or self.vy < -3):
            self.dc *= -1

        center = self.rect.center 

        if self.dc < 0:
            self.image = self.flying
        else:
            self.image = self.flyingDown

        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.center = center
        self.rect.y += self.vy

        if self.rect.left > WIDTH + 100 or self.rect.right < -100:
            self.kill()

        #   <SubTexture name="enemyFlying_1.png"	x="455"	y="390"	width="64"	height="38" frameX="-0" frameY="-0" frameWidth="64" frameHeight="38"/>
        # 	<SubTexture name="enemyFlying_2.png"	x="455"	y="429"	width="64"	height="38" frameX="-0" frameY="-0" frameWidth="64" frameHeight="38"/>
        # 	<SubTexture name="enemyFlying_3.png"	x="455"	y="533"	width="64"	height="43" frameX="-0" frameY="-0" frameWidth="64" frameHeight="43"/>
        # 	<SubTexture name="enemyFlying_4.png"	x="584"	y="996"	width="60"	height="25" frameX="-0" frameY="-0" frameWidth="60" frameHeight="25"/>