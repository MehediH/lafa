import pygame
from defaults import *

class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.image = pygame.Surface((30, 30))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)
        self.position = pygame.math.Vector2(WIDTH / 2, HEIGHT / 2)
        self.velocity = pygame.math.Vector2(0, 0)
        self.accleration = pygame.math.Vector2(0, 0)

    def jump(self):
        # jump only when standing on a platform
        self.rect.x += 1
        hits = pygame.sprite.pygame.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.x -= 1

        if hits:
            self.velocity.y = -20

    def update(self):
        self.accleration = pygame.math.Vector2(0, PLAYER_GRAVITY)
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.accleration.x = -PLAYER_ACCELERATION

        if keys[pygame.K_RIGHT]:
            self.accleration.x = PLAYER_ACCELERATION

        # motion algo
        self.accleration.x += self.velocity.x * PLAYER_FRICTION
        self.velocity += self.accleration
        self.position += self.velocity + 0.5 * self.accleration

        # wraparound player
        if self.position.x > WIDTH:
            self.position.x = 0
        if self.position.x < 0:
            self.position.x = WIDTH

        self.rect.midbottom = self.position


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((w, h))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y