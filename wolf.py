import pygame
import math
from collections import deque
from settings import *

class Wolf:
    def __init__(self, x, y, tile_size):
        self.tile_size = tile_size
        try:
            self.img_sleep = pygame.transform.scale(
                pygame.image.load(os.path.join(SCRIPT_DIR, "wolf0.png")).convert_alpha(), (32, 32))
            self.img_hunt = pygame.transform.scale(
                pygame.image.load(os.path.join(SCRIPT_DIR, "wolf1.png")).convert_alpha(), (32, 32))
        except:
            self.img_sleep = pygame.Surface((32, 32), pygame.SRCALPHA)
            self.img_hunt = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.rect(self.img_sleep, (150, 150, 150, 255), (0, 0, 32, 32))
            pygame.draw.rect(self.img_hunt, (200, 0, 0, 255), (0, 0, 32, 32))

        x = (x // self.tile_size) * self.tile_size
        y = (y // self.tile_size) * self.tile_size
        self.rect = pygame.Rect(x, y, 32, 32)
        self.state = SLEEPING
        self.facing_right = True
        self.moving = False
        self.start_pos = (x, y)
        self.target_pos = (x, y)
        self.move_progress = 0.0
        self.move_speed = 0.2
        self.awake_distance = 3
        self.move_cooldown = 0
        self.spawn_pos = (x, y)

    def bfs_path(self, start, goal, collision_map):
        visited = set()
        queue = deque([(start, [])])
        while queue:
            current, path = queue.popleft()
            if current == goal: return path
            if current in visited: continue
            visited.add(current)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = current[0] + dx, current[1] + dy
                if 0 <= nx < len(collision_map[0]) and 0 <= ny < len(collision_map):
                    if not collision_map[ny][nx] and (nx, ny) not in visited:
                        queue.append(((nx, ny), path + [(nx, ny)]))
        return None

    def start_move(self, dx, dy, collision_map, tile_size):
        if self.moving: return False
        new_x = self.rect.x + dx * tile_size
        new_y = self.rect.y + dy * tile_size
        temp_rect = pygame.Rect(new_x, new_y, self.rect.width, self.rect.height)
        left = temp_rect.left // tile_size
        right = (temp_rect.right - 1) // tile_size
        top = temp_rect.top // tile_size
        bottom = (temp_rect.bottom - 1) // tile_size

        for ty in range(top, bottom + 1):
            for tx in range(left, right + 1):
                if not (0 <= tx < len(collision_map[0]) and 0 <= ty < len(collision_map)) or collision_map[ty][tx]:
                    return False

        self.moving = True
        self.start_pos = (self.rect.x, self.rect.y)
        self.target_pos = (new_x, new_y)
        self.move_progress = 0.0
        self.facing_right = dx > 0
        self.move_cooldown = 10
        return True

    def update(self, player_pos, collision_map, tile_size):
        if self.moving:
            self.move_progress += self.move_speed
            if self.move_progress >= 1.0:
                self.moving = False
                self.rect.x, self.rect.y = self.target_pos
            else:
                self.rect.x = self.start_pos[0] + (self.target_pos[0] - self.start_pos[0]) * self.move_progress
                self.rect.y = self.start_pos[1] + (self.target_pos[1] - self.start_pos[1]) * self.move_progress

        if self.move_cooldown > 0: self.move_cooldown -= 1

        if self.state == SLEEPING:
            player_tx = player_pos[0] // tile_size
            player_ty = player_pos[1] // tile_size
            wolf_tx = self.rect.centerx // tile_size
            wolf_ty = self.rect.centery // tile_size
            dist_x = abs(player_tx - wolf_tx)
            dist_y = abs(player_ty - wolf_ty)

            if dist_x + dist_y <= self.awake_distance:
                visible = True
                steps = max(dist_x, dist_y)
                for i in range(1, steps + 1):
                    cx = wolf_tx + int((player_tx - wolf_tx) * i / steps)
                    cy = wolf_ty + int((player_ty - wolf_ty) * i / steps)
                    if not (0 <= cx < len(collision_map[0]) and 0 <= cy < len(collision_map)) or collision_map[cy][cx]:
                        visible = False
                        break
                if visible:
                    self.state = REACTING
                    self.move_cooldown = 30

    def take_turn(self, player, collision_map, tile_size):
        if self.state == REACTING:
            self.state = AWAKE
            return False

        if self.state != AWAKE or self.moving or self.move_cooldown > 0:
            return False

        my_tile = (self.rect.centerx // tile_size, self.rect.centery // tile_size)
        player_tile = (player.rect.centerx // tile_size, player.rect.centery // tile_size)

        if abs(my_tile[0] - player_tile[0]) + abs(my_tile[1] - player_tile[1]) == 1:
            return True

        path = self.bfs_path(my_tile, player_tile, collision_map)
        if path and len(path) > 0:
            next_tile = path[0]
            dx = next_tile[0] - my_tile[0]
            dy = next_tile[1] - my_tile[1]
            self.start_move(dx, dy, collision_map, tile_size)

        return False

    def draw(self, surface):
        img = self.img_sleep if self.state == SLEEPING else self.img_hunt
        if not self.facing_right: img = pygame.transform.flip(img, True, False)
        surface.blit(img, self.rect.topleft)

    def reset(self):
        self.rect.x, self.rect.y = self.spawn_pos
        self.state = SLEEPING
        self.moving = False
        self.move_progress = 0.0
        self.move_cooldown = 0