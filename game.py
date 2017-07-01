import pygame # import pygame and other modules

from defaults import * # bring in the default params
from sprites import * # bring in the sprites

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

    def renderSplash(self):
        pass

    # the main function to execute all the code
    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.eventHandler()
            self.update()
            self.render()
    
    # run a new game
    def newGame(self):
        self.sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()

        self.player = Player(self)
        self.sprites.add(self.player)

        for platform in PLATFORM_LIST:
            platform = Platform(*platform)
            self.sprites.add(platform)
            self.platforms.add(platform)

        self.run()

    # refresh frames
    def update(self):
        self.sprites.update()
        if self.player.velocity.y > 0:
            hits = pygame.sprite.pygame.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                self.player.position.y = hits[0].rect.top
                self.player.velocity.y = 0

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

    # render game elmenets
    def render(self):
        self.screen.fill(BLACK)
        self.sprites.draw(self.screen)
        pygame.display.flip()

    def renderSplashGO(self):
        pass


# kick start the game
pooprush = Pooprush()
pooprush.renderSplash()
while pooprush.running:
    pooprush.newGame()
    pooprush.renderSplashGO()

pygame.quit()