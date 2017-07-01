import pygame, random# import pygame and other modules

from defaults import * # bring in the default params
from sprites import * # bring in the sprites
from os import path

# main pooprush class
class Pooprush:
    def __init__(self):
        # initialize game window
        pygame.init() 
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pooprush")
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.match_font(FONT_NAME)
        self.loadAssets()

    def loadAssets(self):
        self.dir = path.dirname(__file__)
        imageDir = path.join(self.dir, 'inc/sheets/')

        self.spritesheet = Spritesheet(path.join(imageDir, SPRITESHEET))
        self.platformsheet = Platformsheet(path.join(imageDir, PLATFORMSHEET))

        self.soundDir = path.join(self.dir, 'inc/sounds/')
        self.jumpSound = pygame.mixer.Sound(path.join(self.soundDir, 'jump.wav'))

    def renderSplash(self):
        pygame.mixer.music.load(path.join(self.soundDir, 'bg.ogg'))
        pygame.mixer.music.play(loops =- 1)
        self.screen.fill(GREENALT)
        self.renderText("POOPRUSH", 50, WHITE, WIDTH / 2, HEIGHT / 4)
        self.renderText("Use arrows to move, space to jump.", 25, WHITE, WIDTH / 2, HEIGHT / 2)
        self.renderText("Press any key to play", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        pygame.display.flip()
        self.wait_for_play()
        pygame.mixer.music.stop()

    # the main function to execute all the code
    def run(self):
        self.playing = True
        musicPlayed = False

        while self.playing:
            self.clock.tick(FPS)
            self.eventHandler()
            self.update()
            self.render()

            if(not musicPlayed):
                pygame.mixer.music.load(path.join(self.soundDir, 'main.ogg'))
                pygame.mixer.music.play(loops = -1)
                musicPlayed = True

        pygame.mixer.music.stop()
    
    # run a new game
    def newGame(self):
        self.score = 0
        self.sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.player = Player(self)

        for platform in PLATFORM_LIST:
            Platform(self, *platform)

        self.run()

    # refresh frames
    def update(self):
        self.sprites.update()
        if self.player.velocity.y > 0:
            hits = pygame.sprite.pygame.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                lowest = hits[0]

                for hit in hits:
                    if hit.rect.bottom > lowest.rect.bottom:
                        lowest = hit

                if self.player.position.x < lowest.rect.right + 10 and self.player.position.x > lowest.rect.left - 10:
                    if self.player.position.y < lowest.rect.centery:
                        self.player.position.y = hits[0].rect.top
                        self.player.velocity.y = 0
                        self.player.jumping = False
            
        # keep going up
        if self.player.rect.top <= HEIGHT / 4:
            self.player.position.y += max(abs(self.player.velocity.y), 2)

            for platform in self.platforms:
                platform.rect.y += max(abs(self.player.velocity.y), 2)
                if platform.rect.top >= HEIGHT:
                    platform.kill()
                    self.score += 1

        # create new platforms
        while len(self.platforms) < 6:
            width = random.randrange(50, 100)
            Platform(self, random.randrange(0, WIDTH - width), random.randrange(-75, -30))

        # game over
        if self.player.rect.bottom > HEIGHT:
            for sprite in self.sprites:
                sprite.rect.y -= max(self.player.velocity.y, 10)
                if sprite.rect.bottom < 0:
                    sprite.kill()

        if len(self.platforms) == 0:
            self.playing = False        

    # handle input
    def eventHandler(self):
        for event in pygame.event.get():
         if event.type == pygame.QUIT:
            if self.playing:
                 self.playing = False

            self.running = False

         if event.type == pygame.KEYDOWN:
             if event.key == pygame.K_SPACE:
                 self.player.jump()

         if event.type == pygame.KEYUP:
             if event.key == pygame.K_SPACE:
                 self.player.jumpCut()

    # render game elmenets
    def render(self):
        self.screen.fill(GREENALT)
        self.sprites.draw(self.screen)
        self.renderText(str(self.score), 30, WHITE, WIDTH / 2, 15)
        pygame.display.flip()
        

    def renderSplashGO(self):
        if not self.running:
            return
        
        self.screen.fill(MAROON)
        self.renderText("GAME OVER", 50, WHITE, WIDTH / 2, HEIGHT / 4)
        self.renderText("Your score: " + str(self.score), 25, WHITE, WIDTH / 2, HEIGHT / 2)
        self.renderText("Press any key to play to start again", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        pygame.display.flip()
        pygame.mixer.music.load(path.join(self.soundDir, 'go.ogg'))
        pygame.mixer.music.play(loops =- 1)
        self.wait_for_play()
        pygame.mixer.music.stop()
    
    def renderText(self, text, size, color, x, y):
        font = pygame.font.Font(self.font, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    def wait_for_play(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pygame.KEYUP:
                    waiting = False

# kick start the game
pooprush = Pooprush()
pooprush.renderSplash()
while pooprush.running:
    pooprush.newGame()
    pooprush.renderSplashGO()

pygame.quit()