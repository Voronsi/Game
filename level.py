import os
import pygame
from pytmx.util_pygame import load_pygame
from settings import SCRIPT_DIR, SPIKE_ACTIVE, SPIKE_INACTIVE

def load_level(level_name):
    try:
        TMX_PATH = os.path.join(SCRIPT_DIR, "lvl1.tmx" if level_name == "level1" else "lvl2.tmx")
        tmx_dir = os.path.dirname(TMX_PATH)
        tmx_data = load_pygame(TMX_PATH, base_path=tmx_dir)
        tile_size = tmx_data.tilewidth

        # Создаем карту коллизий
        collision_map = []
        collision_layer = tmx_data.get_layer_by_name("Collision")
        if collision_layer:
            for y in range(collision_layer.height):
                row = []
                for x in range(collision_layer.width):
                    gid = collision_layer.data[y][x]
                    row.append(gid != 0)
                collision_map.append(row)
        else:
            collision_map = [[False] * tmx_data.width for _ in range(tmx_data.height)]

        # Загрузка объектов
        spawn_points = []
        victory_triggers = []
        spikes = []
        wolf_spawns = []

        try:
            spike_inactive_img = pygame.image.load(os.path.join(SCRIPT_DIR, "textures", "spike_inactive.png"))
            spike_active_img = pygame.image.load(os.path.join(SCRIPT_DIR, "textures", "spike_active.png"))
        except:
            spike_inactive_img = pygame.Surface((32, 32))
            spike_inactive_img.fill(SPIKE_INACTIVE)
            spike_active_img = pygame.Surface((32, 32))
            spike_active_img.fill(SPIKE_ACTIVE)

        for layer in tmx_data.layers:
            if not hasattr(layer, 'data'):
                for obj in layer:
                    if hasattr(obj, 'properties'):
                        obj_type = obj.properties.get("obj_type", "")
                        if obj_type == "spawn_point":
                            spawn_points.append({
                                'x': obj.x, 'y': obj.y, 'dir': obj.properties.get("direction", "south")
                            })
                        elif obj_type == "victory":
                            victory_triggers.append({'rect': pygame.Rect(obj.x, obj.y, obj.width, obj.height)})
                        elif obj_type == "spike":
                            scaled_inactive = pygame.transform.scale(spike_inactive_img, (obj.width, obj.height))
                            scaled_active = pygame.transform.scale(spike_active_img, (obj.width, obj.height))
                            spikes.append({
                                'rect': pygame.Rect(obj.x, obj.y, obj.width, obj.height),
                                'active': False,
                                'active_img': scaled_active,
                                'inactive_img': scaled_inactive
                            })
                        elif obj_type == "spawn_wolf":
                            wolf_spawns.append({'x': obj.x, 'y': obj.y})

        if not spawn_points: spawn_points.append({'x': 100, 'y': 100, 'dir': 'south'})
        has_spikes = len(spikes) > 0
        return tmx_data, collision_map, tile_size, spawn_points[0], victory_triggers, spikes, has_spikes, wolf_spawns

    except Exception as e:
        print(f"Ошибка загрузки уровня {level_name}: {e}")
        return None, None, None, None, None, None, False, []