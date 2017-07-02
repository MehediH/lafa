# all the default parramaters 

WIDTH = 500
HEIGHT = 700
FPS = 60
FONT_NAME = 'CircularStd-Black'
SPRITESHEET = 'spritesheet_complete.png'
PLATFORMSHEET = 'platform.png'

# set the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (91, 255, 159)
GREENALT = (55, 98, 239)
MAROON = (135, 35, 51)

# layers
PLAYER_LAYER = 2
PLATFORM_LAYER = 1
POWER_LAYER = 1 
ENEMY_LAYER = 2

# game props
BOOST = 60
POW_SPAWN_HZ = 10
ENEMY_SPAWN_HZ = 5000 # 5ms

# platforms
PLATFORM_LIST = [
    (60, 80),
    (320, 220),
    (110, 400),
    (330, 580),
    (60, 750)
]
# player props
PLAYER_ACCELERATION = 0.7
PLAYER_FRICTION = -0.10
PLAYER_GRAVITY = 1
PLAYER_STRENGTH = -25