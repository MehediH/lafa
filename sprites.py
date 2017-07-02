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
    def __init__(self, game):
        self.groups = game.sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.walking = False
        self.isjumping = False
        self.current_frame = 0 # current frame
        self.last_update = 0
        self.loadCharacters()
        self.image = self.standing[0]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)
        self.position = pygame.math.Vector2(WIDTH / 2, HEIGHT / 2)
        self.velocity = pygame.math.Vector2(0, 0)
        self.accleration = pygame.math.Vector2(0, 0)

    def loadCharacters(self):
        self.standing = [
            self.game.spritesheet.get_image(890, 0, 38, 50),
            self.game.spritesheet.get_image(890, 51, 38, 50)
        ]

        for frame in self.standing:
            frame.set_colorkey(BLACK)

        self.walking_r = [
            self.game.spritesheet.get_image(890, 366, 38, 50),
            self.game.spritesheet.get_image(889, 963, 38, 48),
            self.game.spritesheet.get_image(889, 877, 38, 48)
        ]

        self.walking_l = []

        for frame in self.walking_r:
            frame.set_colorkey(BLACK)
            self.walking_l.append(pygame.transform.flip(frame, True, False))
            
            
        self.jumping = [
            self.game.spritesheet.get_image(890, 51, 38, 50),
            self.game.spritesheet.get_image(849, 877, 38, 43),
            self.game.spritesheet.get_image(849, 429, 40, 39)
        ]


    def jump(self):
        # jump only when standing on a platform
        self.rect.x += 1
        hits = pygame.sprite.pygame.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.x -= 1

        if hits and not self.jumping:
            self.game.jumpSound.play()
            self.jumping = True
            self.velocity.y = PLAYER_STRENGTH

    def jumpCut(self):
        if self.jumping:
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


class Platform(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
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
        self.groups = game.sprites, game.powerups
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.plat = plat
        self.type = choice(['boost'])
        self.image = self.game.spritesheet.get_image(929, 317, 32, 30)
        self.image.set_colorkey(BLACK)

        self.rect = self.image.get_rect()
        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom = self.plat.rect.top - 5

    def update(self):
        self.rect.bottom = self.plat.rect.top - 5
        if not self.game.platforms.has(self.plat):
            self.kill()