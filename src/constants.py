"""Game constants for Pygame Pong."""

import os

# Screen dimensions and display settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 30
WINDOW_TITLE = "Pygame Pong"

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Available paddle colors
RGB_COLORS = {
    "Red": RED,
    "Green": GREEN,
    "Blue": BLUE,
}

# Paddle settings
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 90
PADDLE_SPEED = 7.0
PADDLE_MARGIN = 30

# Ball settings
BALL_SIZE = 15
BALL_INITIAL_SPEED_X = 5.0
BALL_INITIAL_SPEED_Y = 5.0
BALL_SPEED_INCREMENT = 1.05
BALL_ACCELERATION_INCREMENT = 0.2
BALL_MAX_SPEED = 15.0

# Gameplay rules
TARGET_SCORE = 11

# Fonts
FONT_SIZE_SCORE = 48
FONT_SIZE_MESSAGE = 36
FONT_SIZE_TITLE = 56
FONT_SIZE_NAME = 24
FONT_SIZE_SMALL = 20

# Paths to sound assets
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
SOUND_BOUNCE = os.path.join(SOUNDS_DIR, "bounce.wav")
SOUND_WALL = os.path.join(SOUNDS_DIR, "wall.wav")
SOUND_SCORE = os.path.join(SOUNDS_DIR, "score.wav")
