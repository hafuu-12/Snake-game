"""
settings.py

Just a place to dump all the constants so I'm not hardcoding numbers
all over the other files. Learned this the hard way after my first
version had "20" typed in like 15 different places and changing the
tile size meant hunting through everything lol.
"""

import os

# ---------- paths ----------
# using abspath so the game still finds its files even if you run it
# from a different folder (this bit me during testing more than once)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets")
SOUND_DIR = os.path.join(ASSET_DIR, "sounds")
MUSIC_DIR = os.path.join(ASSET_DIR, "music")
DATA_DIR = os.path.join(BASE_DIR, "data")

HIGHSCORE_FILE = os.path.join(DATA_DIR, "highscore.txt")
PROGRESS_FILE = os.path.join(DATA_DIR, "progress.json")

# make sure data folder actually exists before we try to read/write files in it
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# ---------- screen / grid ----------
TILE_SIZE = 24
HUD_HEIGHT = 60  # strip at the top for score / level text

# board size presets (cols, rows) -> picked from the settings screen
BOARD_SIZES = {
    "Small": (18, 14),
    "Medium": (26, 18),
    "Large": (32, 22),
}

FPS = 60  # main loop fps, NOT snake speed (that's handled separately with a timer)

# ---------- difficulty ----------
# these are move intervals in milliseconds - lower = faster snake
DIFFICULTY_SPEEDS = {
    "Easy": 150,
    "Medium": 110,
    "Hard": 75,
}

# floor so the game doesn't become literally unplayable at high scores
MIN_MOVE_INTERVAL = {
    "Easy": 95,
    "Medium": 65,
    "Hard": 45,
}

SPEEDUP_EVERY_N_POINTS = 5
SPEEDUP_AMOUNT_MS = 3

# ---------- colors ----------
WHITE = (245, 245, 245)
BLACK = (15, 15, 15)
GRAY = (90, 90, 90)
LIGHT_GRAY = (200, 200, 200)
RED = (210, 45, 45)
DARK_RED = (150, 20, 20)
GOLD = (240, 195, 60)
BLUE = (60, 120, 220)

# day / night background + grid colors
DAY_BG = (225, 235, 220)
DAY_GRID = (200, 210, 200)
NIGHT_BG = (18, 22, 30)
NIGHT_GRID = (32, 38, 50)

# snake color themes -> (head_color, body_color)
THEMES = {
    "Classic Green": ((40, 160, 70), (60, 200, 100)),
    "Neon": ((255, 0, 200), (0, 220, 220)),
    "Retro": ((230, 140, 30), (250, 190, 80)),
    "Blue Ice": ((40, 90, 200), (110, 170, 250)),
}

# powerup colors just so I can tell them apart on screen
POWERUP_COLORS = {
    "slow": (130, 200, 255),
    "double": (255, 215, 0),
    "shield": (180, 180, 255),
}

POWERUP_NAMES = {
    "slow": "Slow Motion",
    "double": "Double Points",
    "shield": "Shield",
}

# how long a powerup effect lasts once picked up (ms)
POWERUP_DURATION = {
    "slow": 5000,
    "double": 8000,
    "shield": 999999,  # shield doesn't expire on a timer, it expires when used
}

POWERUP_LIFETIME_ON_BOARD = 7000  # disappears if not grabbed in time
BONUS_FOOD_LIFETIME = 5000
BONUS_FOOD_POINTS = 5

OBSTACLE_SCORE_MILESTONE = 40  # new obstacle pair every 40 points
OBSTACLES_PER_MILESTONE = 2

# survivor achievement threshold
SURVIVOR_TIME_MS = 3 * 60 * 1000  # 3 minutes

FONT_NAME = None  # None = pygame default font, didn't bother finding a custom one
