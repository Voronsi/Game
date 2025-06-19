import os
import pygame

# Инициализация Pygame
pygame.init()

# Разрешения экрана
VIRTUAL_WIDTH = 830
VIRTUAL_HEIGHT = 600
VIRTUAL_ASPECT = VIRTUAL_WIDTH / VIRTUAL_HEIGHT
FULLSCREEN_WIDTH = 1920
FULLSCREEN_HEIGHT = 1080

# Путь к файлу
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (50, 50, 150)
LIGHT_BLUE = (70, 70, 200)
RED = (150, 50, 50)
LIGHT_RED = (200, 70, 70)
GRAY = (100, 100, 100)
DARK_BLUE = (30, 30, 50)
SPIKE_ACTIVE = (255, 50, 50)
SPIKE_INACTIVE = (100, 100, 100)
DUNGEON_BROWN = (70, 40, 20)
DUNGEON_BROWN_HOVER = (100, 60, 30)

# Состояния волка
SLEEPING = 0
AWAKE = 1
REACTING = 2

# Скорости
PLAYER_SPEED = 1
WOLF_SPEED = 10
WOLF_REACTION_TIME = 1