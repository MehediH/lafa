import pygame, random, pyrebase # import pygame and other modules

from defaults import * # bring in the default params
from sprites import * # bring in the sprites
from os import path

class CustomException(ValueError): # raised if data conversion fails
    def __init__(self, message):
        self.message = message
        print("There was a problem converting data")


# main lafa class
class Lafa:
    def __init__(self):
        # initialize game window
        pygame.init() 
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Lafa")
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.match_font(FONT_NAME)
        self.loadAssets()
        self.events = pygame.event.get()

        self.user = ""
        self.pw = ""
        self.pwalt = ""
        self.dp = ""
        self.userSet = False
        self.pwSet = False

        # intialize firebase
        config = {
            "apiKey": "AIzaSyCBXc6LF3h5bqiUj-1wzsznkIDDsTjkQu8",
            "authDomain": "lafa-a28d0.firebaseapp.com",
            "databaseURL": "https://lafa-a28d0.firebaseio.com",
            "projectId": "lafa-a28d0",
            "storageBucket": "lafa-a28d0.appspot.com"
        }

        self.firebase = pyrebase.initialize_app(config)

        self.auth = self.firebase.auth()
        self.db = self.firebase.database()

    def loadAssets(self):
        self.dir = path.dirname(__file__)
        imageDir = path.join(self.dir, 'inc/sheets/')

        self.spritesheet = Spritesheet(path.join(imageDir, SPRITESHEET))
        self.platformsheet = Platformsheet(path.join(imageDir, PLATFORMSHEET))

        self.soundDir = path.join(self.dir, 'inc/sounds/')
        self.jumpSound = pygame.mixer.Sound(path.join(self.soundDir, 'jump.wav'))
        self.boostSound = pygame.mixer.Sound(path.join(self.soundDir, 'pup.wav'))
        self.killSound = pygame.mixer.Sound(path.join(self.soundDir, 'kill.wav'))
        self.lifeSound = pygame.mixer.Sound(path.join(self.soundDir, 'life.wav'))

    def renderSplash(self):
        pygame.mixer.music.load(path.join(self.soundDir, 'bg.ogg'))
        pygame.mixer.music.play(loops =- 1)
        pygame.mixer.music.set_volume(0)
        self.screen.fill(GREENALT)
        self.renderText("LAFA", 50, WHITE, WIDTH / 2, HEIGHT / 4)
        self.renderText("Use arrows to move, space to jump.", 25, WHITE, WIDTH / 2, HEIGHT / 2)
        self.renderText("Enter your username and password to get started", 22, WHITE, WIDTH / 2, HEIGHT - 40)
        pygame.display.flip()
        self.askUser()
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
                pygame.mixer.music.set_volume(0)
                pygame.mixer.music.play(loops = -1)
                musicPlayed = True

        pygame.mixer.music.stop()
    
    # run a new game
    def newGame(self):
        self.score = 0
        self.deaths = 10
        self.sprites = pygame.sprite.LayeredUpdates()
        self.platforms = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.player = Player(self)
        self.enemyTimer = 0
        self.userExists = False

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
                        self.player.isjumping = False
            
        # keep going up
        if self.player.rect.top <= HEIGHT / 4:
            self.player.position.y += max(abs(self.player.velocity.y), 2)

            for platform in self.platforms:
                platform.rect.y += max(abs(self.player.velocity.y), 2)
                if platform.rect.top >= HEIGHT:
                    platform.kill()
                    self.score += 1

            for enemy in self.enemies:
                enemy.rect.y += max(abs(self.player.velocity.y), 2)
                if enemy.rect.top >= HEIGHT:
                    enemy.kill()

        # create new platforms
        while len(self.platforms) < 6:
            width = random.randrange(50, 100)
            Platform(self, random.randrange(0, WIDTH - width), random.randrange(-75, -30))
        
        # power up detection
        power_hits = pygame.sprite.spritecollide(self.player, self.powerups, True)

        for power in power_hits:
            if power.type == "boost":
                self.boostSound.play()
                self.player.velocity.y = -BOOST
                self.player.isjumping = False

            if power.type == "life":
                self.lifeSound.play()
                self.deaths += 1

        # spawn a enemy
        now = pygame.time.get_ticks()
        if now - self.enemyTimer > 5000 + random.choice([-1000, -500, 0, 500, 1000]):
            self.enemyTimer = now
            Enemy(self)

        # enemy detection
        enemy_hits = pygame.sprite.spritecollide(self.player, self.enemies, True, pygame.sprite.collide_mask)

        if enemy_hits:
            self.deaths -= 1
            self.killSound.play()

            if(self.deaths <= 0):
                self.playing = False

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
             if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                 self.player.jump()

         if event.type == pygame.KEYUP:
             if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                 self.player.jumpCut()

    # render game elmenets
    def render(self):
        self.screen.fill(GREENALT)
        self.sprites.draw(self.screen)
        self.renderText(str(self.score) + " (LIVES: " + str(self.deaths) + ")", 30, WHITE, WIDTH / 2, 15)
        pygame.display.flip()
        

    def renderSplashGO(self):
        if not self.running:
            return
         
        self.screen.fill(MAROON)

        try:
            if(self.user["score"] < self.score):
                self.user["score"] = self.score
                self.renderText("NEW HIGH SCORE, BABY!", 50, WHITE, WIDTH / 2, HEIGHT / 3)
        except:
            self.user["score"] = self.score

        self.db.child("users/" + self.dp).update(self.user, self.user['idToken'])

        self.renderText("GAME OVER", 50, WHITE, WIDTH / 2, HEIGHT / 4)
        self.renderText("Your score: " + str(self.score), 25, WHITE, WIDTH / 2, HEIGHT / 2)
        self.renderText("You had " + str(self.deaths) + " lives left!", 25, WHITE, WIDTH / 2, HEIGHT / 2 +  40)
        self.renderText("Press any key to start again", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        pygame.display.flip()
        pygame.mixer.music.load(path.join(self.soundDir, 'go.ogg'))
        pygame.mixer.music.play(loops =- 1)
        pygame.mixer.music.set_volume(0)
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
                    if(chr(event.key) != "h"):
                        waiting = False
                    else:
                        self.showLeaderboard()

    def askUser(self):
        waiting = True
        allowed = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890.,;"
        allowed = list(allowed)

        while waiting:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_BACKSPACE:
                        if(not self.userSet):
                            self.user = self.user[:-1]
                            self.screen.fill(GREENALT, (0, HEIGHT * 3 / 4 - 50, WIDTH, 20))
                            self.renderText("Username: " + str(self.user), 25, WHITE, WIDTH / 2, HEIGHT * 3 / 4 - 50)

                        if(self.userSet):
                            self.pw = self.pw[:-1]
                            self.pwalt = self.pwalt[:-1]
                            self.screen.fill(GREENALT, (0, HEIGHT * 3 / 4 - 20, WIDTH, 20))
                            self.renderText("Password: " + str(self.pwalt), 25, WHITE, WIDTH / 2, HEIGHT * 3 / 4 - 20)

                    elif event.key == pygame.K_RETURN:
                        self.userSet = True
                        self.screen.fill(GREENALT, (0, HEIGHT * 3 / 4 - 20, WIDTH, 20))
                        self.renderText("Password: " + str(self.pwalt), 25, WHITE, WIDTH / 2, HEIGHT * 3 / 4 - 20)

                        if len(self.pw) > 6 and self.pwSet:
                            waiting = False
                            self.saveUser()
                        else:
                            self.killSound.play()

                    if(chr(event.key) in allowed):
                        if(not self.userSet):
                            if len(self.user) < 10:
                                self.user += chr(event.key)
                                self.screen.fill(GREENALT, (0, HEIGHT * 3 / 4 - 50, WIDTH, 20))
                                self.renderText("Username: " + str(self.user), 25, WHITE, WIDTH / 2, HEIGHT * 3 / 4 - 50)
                            else:
                                self.userSet = True
                                self.killSound.play()

                        if(self.userSet):
                            if len(self.pw) < 15:
                                self.pw += chr(event.key)
                                self.pwalt += "•"
                                self.screen.fill(GREENALT, (0, HEIGHT * 3 / 4 - 20, WIDTH, 20))
                                self.renderText("Password: " + str(self.pwalt), 25, WHITE, WIDTH / 2, HEIGHT * 3 / 4 - 20)
                                self.pwSet = True
                            else:
                                self.pwSet = True
                                self.killSound.play()

                    pygame.display.flip()

    def saveUser(self):
        email = self.user + "@outlook.com"
        pw = self.pw

        try:
            user = self.auth.sign_in_with_email_and_password(email, pw)
            self.user = user
            self.userExists = True
        except:
            self.userExists = False
        
        if(not self.userExists):
            try:
                self.user = self.auth.create_user_with_email_and_password(email, pw)
            except:
                self.screen.fill(GREENALT, (0, HEIGHT * 3 / 4 - 20, WIDTH, 20))
                self.renderText("Something went wrong, please try again", 25, WHITE, WIDTH / 2, HEIGHT * 3 / 4 - 50)

        self.dp = email.replace("@outlook.com", "")
       
        self.user.update({"displayName": self.dp})

        self.db.child("users/" + self.dp).update(self.user, self.user['idToken'])

    def showLeaderboard(self):
        users = self.db.child("users").get(self.user['idToken']).val()
        leaderboard = {}

        for i in users:
            user = users[i]

            leaderboard[user["displayName"]] = user["score"]

        leaderboard = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)

        re = True

        while re:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                pass

            self.screen.fill(GREENALT)
            self.renderText("LEADERBOARD", 45, WHITE, WIDTH / 2, 80)

            x = 0
            y = 10
            for i in leaderboard:
                self.renderText(str(leaderboard[x][1]) + " by " + leaderboard[x][0], 25, WHITE, WIDTH / 2, 120 + y) 
                y += 20
                x += 1

            pygame.display.flip()
        
# kick start the game
lafa = Lafa()
lafa.renderSplash()
while lafa.running:
    lafa.newGame()
    lafa.renderSplashGO()

pygame.quit()