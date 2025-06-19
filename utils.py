import pygame
from settings import VIRTUAL_WIDTH, VIRTUAL_HEIGHT, FULLSCREEN_WIDTH, FULLSCREEN_HEIGHT

def calculate_letterbox(virtual_width, virtual_height, screen_width, screen_height):
    virtual_aspect = virtual_width / virtual_height
    screen_aspect = screen_width / screen_height

    if virtual_aspect > screen_aspect:
        scale = screen_width / virtual_width
        scaled_width = screen_width
        scaled_height = int(virtual_height * scale)
        x_offset = 0
        y_offset = (screen_height - scaled_height) // 2
    else:
        scale = screen_height / virtual_height
        scaled_width = int(virtual_width * scale)
        scaled_height = screen_height
        x_offset = (screen_width - scaled_width) // 2
        y_offset = 0

    return scaled_width, scaled_height, x_offset, y_offset, scale