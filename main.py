import pygame
import os
import sys
import random
from settings import *
from utils import calculate_letterbox
from menu import show_main_menu, LevelInDevDialog, DeathDialog, VictoryDialog, GameOverDialog
from level import load_level
from player import Player
from wolf import Wolf
from lighting import LightShader, apply_dark_overlay

# Инициализация
pygame.init()

# Создание окна
screen = pygame.display.set_mode((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Tiled Map Game")
clock = pygame.time.Clock()

# Загрузка звуков
try:
    spike_activate_sound = pygame.mixer.Sound(os.path.join(SCRIPT_DIR, "sounds", "spikes.wav"))
    spike_deactivate_sound = pygame.mixer.Sound(os.path.join(SCRIPT_DIR, "sounds", "spikes.wav"))
    footstep_sound = pygame.mixer.Sound(os.path.join(SCRIPT_DIR, "sounds", "footstep.wav"))
    footstep_sound.set_volume(0.5)
    death_sound = pygame.mixer.Sound(os.path.join(SCRIPT_DIR, "sounds", "death.wav"))
    pygame.mixer.music.load(os.path.join(SCRIPT_DIR, "sounds", "background_music.mp3"))
    pygame.mixer.music.set_volume(0.4)
    pygame.mixer.music.play(-1)
except Exception as e:
    print(f"Ошибка загрузки звуков: {e}")
    spike_activate_sound = pygame.mixer.Sound(buffer=bytearray())
    spike_deactivate_sound = pygame.mixer.Sound(buffer=bytearray())
    footstep_sound = pygame.mixer.Sound(buffer=bytearray())
    death_sound = pygame.mixer.Sound(buffer=bytearray())
    print("Созданы заглушки для звуков")

# Виртуальная поверхность
virtual_screen = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
window_size = (VIRTUAL_WIDTH, VIRTUAL_HEIGHT)
fullscreen = False
normal_window_size = window_size

# Загрузка текстур
stone_texture = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
try:
    stone_img = pygame.image.load(os.path.join(SCRIPT_DIR, "textures", "stone_wall.png"))
    stone_img = pygame.transform.scale(stone_img, (VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
    stone_texture.blit(stone_img, (0, 0))
except:
    for x in range(0, VIRTUAL_WIDTH, 40):
        for y in range(0, VIRTUAL_HEIGHT, 40):
            shade = random.randint(70, 100)
            pygame.draw.rect(stone_texture, (shade, shade, shade), (x, y, 40, 40), 1)

# Создаем экземпляры диалогов
level_in_dev_dialog = LevelInDevDialog()
death_dialog = DeathDialog()
victory_dialog = VictoryDialog()
game_over_dialog = GameOverDialog()

def toggle_fullscreen():
    global screen, fullscreen, normal_window_size
    fullscreen = not fullscreen
    if fullscreen:
        normal_window_size = screen.get_size()
        screen = pygame.display.set_mode((FULLSCREEN_WIDTH, FULLSCREEN_HEIGHT), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode(normal_window_size, pygame.RESIZABLE)

def game_loop(level_name):
    global screen, fullscreen, normal_window_size, window_size

    tmx_data, collision_map, tile_size, spawn, victory_triggers, spikes, has_spikes, wolf_spawns = load_level(level_name)
    if not tmx_data: return

    player = Player(spawn['x'], spawn['y'])
    wolves = [Wolf(sp['x'], sp['y'], tile_size) for sp in wolf_spawns]
    light_shader = LightShader()

    # Разделение слоев
    under_layers = []
    over_layers = []
    walls_layer_name = "Walls"
    for layer in tmx_data.visible_layers:
        if layer.name == walls_layer_name: over_layers.append(layer)
        else: under_layers.append(layer)

    player_turn = True
    running = True
    font = pygame.font.SysFont(None, 24)
    level_complete = False
    game_complete = False
    player_dead = False
    turns_count = 0
    spikes_active = False
    prev_spikes_active = False

    while running:
        current_screen = pygame.display.get_surface()
        screen_width, screen_height = current_screen.get_size()
        scaled_width, scaled_height, x_offset, y_offset, scale = calculate_letterbox(
            VIRTUAL_WIDTH, VIRTUAL_HEIGHT, screen_width, screen_height
        )
        mouse_pos = pygame.mouse.get_pos()
        virtual_mouse_pos = ((mouse_pos[0] - x_offset) / scale, (mouse_pos[1] - y_offset) / scale)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False

            if player_dead:
                result = death_dialog.handle_event(event, virtual_mouse_pos)
                if result == "restart":
                    player = Player(spawn['x'], spawn['y'])
                    wolves = [Wolf(sp['x'], sp['y'], tile_size) for sp in wolf_spawns]
                    player_dead = level_complete = game_complete = False
                    turns_count = spikes_active = prev_spikes_active = False
                    for spike in spikes: spike['active'] = False
                    player_turn = True
                elif result == "menu": return
            elif level_complete or game_complete:
                if game_complete: result = game_over_dialog.handle_event(event, virtual_mouse_pos)
                else: result = victory_dialog.handle_event(event, virtual_mouse_pos)
                if result == "menu": return
                elif result == "continue":
                    if level_name == "level1":
                        try:
                            if os.path.exists(os.path.join(SCRIPT_DIR, "lvl2.tmx")):
                                game_loop("level2")
                                return
                            else: level_complete = False; game_complete = True
                        except: level_complete = False; game_complete = True
                    else: level_complete = False; game_complete = True
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: running = False
                    elif event.key == pygame.K_r:
                        player = Player(spawn['x'], spawn['y'])
                        wolves = [Wolf(sp['x'], sp['y'], tile_size) for sp in wolf_spawns]
                        player_dead = level_complete = game_complete = False
                        turns_count = spikes_active = prev_spikes_active = False
                        for spike in spikes: spike['active'] = False
                        player_turn = True
                    elif event.key == pygame.K_F11: toggle_fullscreen()
                    elif event.key == pygame.K_m:
                        if pygame.mixer.music.get_busy(): pygame.mixer.music.pause()
                        else: pygame.mixer.music.unpause()
                    elif player_turn and not player.moving:
                        direction = None
                        if event.key in [pygame.K_w, pygame.K_UP]: direction = "up"
                        elif event.key in [pygame.K_s, pygame.K_DOWN]: direction = "down"
                        elif event.key in [pygame.K_a, pygame.K_LEFT]: direction = "left"
                        elif event.key in [pygame.K_d, pygame.K_RIGHT]: direction = "right"
                        if direction and player.start_move(direction, collision_map, tile_size):
                            footstep_sound.play()
                            player_turn = False
                elif event.type == pygame.VIDEORESIZE and not fullscreen:
                    window_size = (event.w, event.h)
                    screen = pygame.display.set_mode(window_size, pygame.RESIZABLE)

        if not level_complete and not game_complete and not player_dead:
            player.update()
            for wolf in wolves: wolf.update((player.rect.x, player.rect.y), collision_map, tile_size)

            if player.just_moved:
                turns_count += 1
                if has_spikes and turns_count >= 3:
                    spikes_active = not spikes_active
                    turns_count = 0
                    for spike in spikes: spike['active'] = spikes_active

                wolf_attacked = False
                for wolf in wolves:
                    if wolf.take_turn(player, collision_map, tile_size):
                        death_sound.play()
                        player_dead = death_dialog.active = True
                        wolf_attacked = True
                        break
                if not wolf_attacked: player_turn = True
                player.just_moved = False

        if not player_dead and not level_complete:
            for trigger in victory_triggers:
                if player.check_trigger(trigger['rect']):
                    if level_name == "level2": game_complete = game_over_dialog.active = True
                    else: level_complete = victory_dialog.active = True

        if has_spikes and spikes_active and not player_dead:
            for spike in spikes:
                if spike['active'] and player.rect.colliderect(spike['rect']):
                    death_sound.play()
                    player_dead = death_dialog.active = True
                    break

        if has_spikes and spikes_active != prev_spikes_active:
            if spikes_active: spike_activate_sound.play()
            else: spike_deactivate_sound.play()
            prev_spikes_active = spikes_active

        # Отрисовка
        virtual_screen.fill(DARK_BLUE)
        for layer in under_layers:
            if hasattr(layer, 'data'):
                for x in range(layer.width):
                    for y in range(layer.height):
                        gid = layer.data[y][x]
                        if gid:
                            tile = tmx_data.get_tile_image_by_gid(gid)
                            if tile: virtual_screen.blit(tile, (x * tile_size, y * tile_size))
        
        if has_spikes:
            for spike in spikes:
                img = spike['active_img'] if spike['active'] else spike['inactive_img']
                virtual_screen.blit(img, spike['rect'].topleft)
        
        light_shader.calculate_light(player.rect.center, collision_map, tile_size)
        light_shader.render(virtual_screen)
        apply_dark_overlay(virtual_screen, alpha=120)
        
        for wolf in wolves: wolf.draw(virtual_screen)
        if not player_dead: player.draw(virtual_screen)
        
        for layer in over_layers:
            if hasattr(layer, 'data'):
                for x in range(layer.width):
                    for y in range(layer.height):
                        gid = layer.data[y][x]
                        if gid:
                            tile = tmx_data.get_tile_image_by_gid(gid)
                            if tile: virtual_screen.blit(tile, (x * tile_size, y * tile_size))

        # Отладочная информация
        debug_text = [
            f"Уровень: {level_name}", f"Игрок: {player.rect.x // tile_size}, {player.rect.y // tile_size}",
            f"Ход: {'Игрок' if player_turn else 'Волки'}", f"Ходы до шипов: {3 - turns_count}",
            f"Шипы: {'АКТИВНЫ' if spikes_active and has_spikes else 'неактивны' if has_spikes else 'отсутствуют'}",
            f"Волков: {len(wolves)}", "ESC: Выход в меню", "R: Сброс позиции", 
            "F11: Полный экран", "M: Вкл/Выкл музыку"
        ]
        for i, text in enumerate(debug_text):
            text_surf = font.render(text, True, WHITE)
            virtual_screen.blit(text_surf, (VIRTUAL_WIDTH - text_surf.get_width() - 10, 10 + i * 25))
        
        music_status = "Музыка: ВКЛ" if pygame.mixer.music.get_busy() else "Музыка: ВЫКЛ"
        music_text = font.render(music_status, True, WHITE)
        virtual_screen.blit(music_text, (10, 10))
        
        if player_dead: death_dialog.draw(virtual_screen)
        elif level_complete: victory_dialog.draw(virtual_screen)
        elif game_complete: game_over_dialog.draw(virtual_screen)

        scaled_surface = pygame.transform.scale(virtual_screen, (scaled_width, scaled_height))
        current_screen.fill(BLACK)
        current_screen.blit(scaled_surface, (x_offset, y_offset))
        pygame.display.flip()
        clock.tick(60)

def main():
    while True:
        selected_level = show_main_menu(virtual_screen, stone_texture, clock)
        if selected_level: game_loop(selected_level)

if __name__ == "__main__":
    main()
    pygame.quit()
    sys.exit()