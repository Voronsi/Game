import pygame
import os
from settings import SCRIPT_DIR

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.color = (255, 0, 0)
        self.facing_right = True

        try:
            self.original_image = pygame.image.load(os.path.join(SCRIPT_DIR, "hero.png")).convert_alpha()
            self.image = pygame.transform.scale(self.original_image, (32, 32))
        except Exception as e:
            print(f"Ошибка загрузки текстуры игрока: {e}")
            self.image = None

        self.moving = False
        self.move_direction = None
        self.start_pos = (x, y)
        self.target_pos = (x, y)
        self.move_progress = 0.0
        self.move_speed = 0.2
        self.just_moved = False

    def start_move(self, direction, collision_map, tile_size):
        if self.moving: return False

        dx, dy = 0, 0
        if direction == "left": dx = -1; self.facing_right = False
        elif direction == "right": dx = 1; self.facing_right = True
        elif direction == "up": dy = -1
        elif direction == "down": dy = 1

        new_x = self.rect.x + dx * tile_size
        new_y = self.rect.y + dy * tile_size

        if self.check_collision_at_position(new_x, new_y, collision_map, tile_size): return False

        self.moving = True
        self.move_direction = direction
        self.start_pos = (self.rect.x, self.rect.y)
        self.target_pos = (new_x, new_y)
        self.move_progress = 0.0
        self.just_moved = False
        return True

    def update(self):
        if self.moving:
            self.move_progress += self.move_speed
            if self.move_progress >= 1.0:
                self.moving = False
                self.rect.x, self.rect.y = self.target_pos
                self.just_moved = True
            else:
                self.rect.x = self.start_pos[0] + (self.target_pos[0] - self.start_pos[0]) * self.move_progress
                self.rect.y = self.start_pos[1] + (self.target_pos[1] - self.start_pos[1]) * self.move_progress
        else:
            self.just_moved = False

    def check_collision_at_position(self, x, y, collision_map, tile_size):
        temp_rect = pygame.Rect(x, y, self.rect.width, self.rect.height)
        left_tile = temp_rect.left // tile_size
        right_tile = (temp_rect.right - 1) // tile_size
        top_tile = temp_rect.top // tile_size
        bottom_tile = (temp_rect.bottom - 1) // tile_size

        for ty in range(top_tile, bottom_tile + 1):
            for tx in range(left_tile, right_tile + 1):
                if tx < 0 or tx >= len(collision_map[0]) or ty < 0 or ty >= len(collision_map):
                    return True
                if collision_map[ty][tx]:
                    return True
        return False

    def check_trigger(self, trigger_rect):
        return self.rect.colliderect(trigger_rect)

    def draw(self, surface):
        if self.image:
            img = pygame.transform.flip(self.image, True, False) if not self.facing_right else self.image
            surface.blit(img, (self.rect.x, self.rect.y))
        else:
            pygame.draw.rect(surface, self.color, self.rect)