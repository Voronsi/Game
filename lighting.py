import pygame
import math
from settings import VIRTUAL_WIDTH, VIRTUAL_HEIGHT

class LightShader:
    def __init__(self):
        self.radius = 4
        self.light_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
        self.light_squares = []

    def calculate_light(self, player_pos, collision_map, tile_size):
        self.light_squares = []
        px, py = player_pos
        player_tx = px // tile_size
        player_ty = py // tile_size

        for dx in range(-self.radius, self.radius + 1):
            for dy in range(-self.radius, self.radius + 1):
                if abs(dx) + abs(dy) > self.radius: continue
                tx = player_tx + dx
                ty = player_ty + dy
                if tx < 0 or tx >= len(collision_map[0]) or ty < 0 or ty >= len(collision_map): continue

                visible = True
                steps = max(abs(dx), abs(dy))
                if steps > 0:
                    for i in range(1, steps + 1):
                        cx = player_tx + int(dx * i / steps)
                        cy = player_ty + int(dy * i / steps)
                        if not (0 <= cx < len(collision_map[0]) and 0 <= cy < len(collision_map)) or collision_map[cy][cx]:
                            visible = False
                            break

                if visible:
                    distance = math.sqrt(dx * dx + dy * dy)
                    alpha = int(200 * (1 - distance / self.radius))
                    if alpha > 0:
                        self.light_squares.append((
                            tx * tile_size, ty * tile_size, 
                            tile_size, tile_size, 
                            (255, 220, 180, alpha)
                        ))

    def render(self, surface):
        self.light_surface.fill((0, 0, 0, 0))
        for square in self.light_squares:
            x, y, w, h, color = square
            pygame.draw.rect(self.light_surface, color, (x, y, w, h))
        surface.blit(self.light_surface, (0, 0))

def apply_dark_overlay(surface, alpha=120):
    darkness = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
    darkness.fill((0, 0, 0, alpha))
    surface.blit(darkness, (0, 0))