import pygame
import os
import sys
import random
import math
from pytmx.util_pygame import load_pygame
from collections import deque

# Инициализация
pygame.init()

# Разрешения экрана
VIRTUAL_WIDTH = 830
VIRTUAL_HEIGHT = 600
VIRTUAL_ASPECT = VIRTUAL_WIDTH / VIRTUAL_HEIGHT
FULLSCREEN_WIDTH = 1920
FULLSCREEN_HEIGHT = 1080

# Создание окна
screen = pygame.display.set_mode((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Tiled Map Game")
clock = pygame.time.Clock()

# Загрузка звуков
try:
    # Звуки для шипов
    spike_activate_sound = pygame.mixer.Sound(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds", "spikes.wav"))
    spike_deactivate_sound = pygame.mixer.Sound(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds", "spikes.wav"))

    # Звук шагов
    footstep_sound = pygame.mixer.Sound(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds", "footstep.wav"))
    footstep_sound.set_volume(0.5)

    # Звук смерти
    death_sound = pygame.mixer.Sound(os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds", "death.wav"))

    # Фоновая музыка
    pygame.mixer.music.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds", "background_music.mp3"))
    pygame.mixer.music.set_volume(0.4)  # Установка громкости
    pygame.mixer.music.play(-1)  # Бесконечное повторение
except Exception as e:
    print(f"Ошибка загрузки звуков: {e}")
    # Создаем пустые звуки если файлы не найдены
    spike_activate_sound = pygame.mixer.Sound(buffer=bytearray())
    spike_deactivate_sound = pygame.mixer.Sound(buffer=bytearray())
    footstep_sound = pygame.mixer.Sound(buffer=bytearray())
    death_sound = pygame.mixer.Sound(buffer=bytearray())
    print("Созданы заглушки для звуков")

# Виртуальная поверхность для рендеринга
virtual_screen = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
# Переменные для управления окном
window_size = (VIRTUAL_WIDTH, VIRTUAL_HEIGHT)
fullscreen = False
normal_window_size = window_size

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
SPIKE_ACTIVE = (255, 50, 50)  # Красный для активных шипов
SPIKE_INACTIVE = (100, 100, 100)  # Серый для неактивных шипов

# Загрузка средневекового шрифта
try:
    title_font = pygame.font.Font(os.path.join(SCRIPT_DIR, "fonts", "medieval.ttf"), 72)
    button_font = pygame.font.Font(os.path.join(SCRIPT_DIR, "fonts", "medieval.ttf"), 36)
    level_select_font = pygame.font.Font(os.path.join(SCRIPT_DIR, "fonts", "medieval.ttf"), 48)
except:
    # Если шрифт не найден, используем системный
    title_font = pygame.font.SysFont(None, 72)
    button_font = pygame.font.SysFont(None, 36)
    level_select_font = pygame.font.SysFont(None, 48)

# Загрузка текстур
stone_texture = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
try:
    stone_img = pygame.image.load(os.path.join(SCRIPT_DIR, "textures", "stone_wall.png"))
    stone_img = pygame.transform.scale(stone_img, (VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
    stone_texture.blit(stone_img, (0, 0))
except:
    # Если текстура не найдена, создаем простую каменную текстуру
    for x in range(0, VIRTUAL_WIDTH, 40):
        for y in range(0, VIRTUAL_HEIGHT, 40):
            shade = random.randint(70, 100)
            pygame.draw.rect(stone_texture, (shade, shade, shade), (x, y, 40, 40), 1)


# Функция для переключения полноэкранного режима
def toggle_fullscreen():
    global screen, fullscreen, normal_window_size
    fullscreen = not fullscreen
    if fullscreen:
        normal_window_size = screen.get_size()
        screen = pygame.display.set_mode((FULLSCREEN_WIDTH, FULLSCREEN_HEIGHT), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode(normal_window_size, pygame.RESIZABLE)


# Функция для расчета масштабирования
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


# Класс кнопки
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)

        text_surf = button_font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False


# Класс диалога "Уровень в разработке"
class LevelInDevDialog:
    def __init__(self):
        self.width = 400
        self.height = 200
        self.rect = pygame.Rect(VIRTUAL_WIDTH // 2 - self.width // 2, VIRTUAL_HEIGHT // 2 - self.height // 2,
                                self.width, self.height)
        self.ok_btn = Button(VIRTUAL_WIDTH // 2 - 50, VIRTUAL_HEIGHT // 2 + 40, 100, 40, "OK", BLUE, LIGHT_BLUE)
        self.font = level_select_font
        self.active = False

    def draw(self, surface):
        s = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        surface.blit(s, (0, 0))

        pygame.draw.rect(surface, DARK_BLUE, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)

        text = self.font.render("Уровень в разработке", True, WHITE)
        text_rect = text.get_rect(center=(VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT // 2 - 20))
        surface.blit(text, text_rect)

        self.ok_btn.draw(surface)

    def handle_event(self, event, mouse_pos):
        self.ok_btn.check_hover(mouse_pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.ok_btn.is_clicked(mouse_pos, event):
                self.active = False
                return True
        return False


# Класс диалога смерти игрока
class DeathDialog:
    def __init__(self):
        self.width = 440
        self.height = 200
        self.rect = pygame.Rect(VIRTUAL_WIDTH // 2 - self.width // 2, VIRTUAL_HEIGHT // 2 - self.height // 2,
                                self.width, self.height)
        self.restart_btn = Button(VIRTUAL_WIDTH // 2 - 200, VIRTUAL_HEIGHT // 2 + 20, 180, 50,
                                  "Начать заново", BLUE, LIGHT_BLUE)
        self.menu_btn = Button(VIRTUAL_WIDTH // 2 + 30, VIRTUAL_HEIGHT // 2 + 20, 180, 50,
                               "В меню", RED, LIGHT_RED)
        self.font = level_select_font
        self.active = False

    def draw(self, surface):
        s = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        surface.blit(s, (0, 0))

        pygame.draw.rect(surface, DARK_BLUE, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)

        text = self.font.render("Игрок погиб!", True, WHITE)
        text_rect = text.get_rect(center=(VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT // 2 - 40))
        surface.blit(text, text_rect)

        self.restart_btn.draw(surface)
        self.menu_btn.draw(surface)

    def handle_event(self, event, mouse_pos):
        self.restart_btn.check_hover(mouse_pos)
        self.menu_btn.check_hover(mouse_pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.restart_btn.is_clicked(mouse_pos, event):
                return "restart"
            elif self.menu_btn.is_clicked(mouse_pos, event):
                return "menu"
        return None


# Класс диалога победы
class VictoryDialog:
    def __init__(self):
        self.width = 400
        self.height = 200
        self.rect = pygame.Rect(VIRTUAL_WIDTH // 2 - self.width // 2, VIRTUAL_HEIGHT // 2 - self.height // 2,
                                self.width, self.height)

        # Новые цвета для кнопки "Продолжить" - коричневый как в главном меню
        DUNGEON_BROWN = (70, 40, 20)
        DUNGEON_BROWN_HOVER = (100, 60, 30)

        self.continue_btn = Button(VIRTUAL_WIDTH // 2 - 180, VIRTUAL_HEIGHT // 2 + 20, 150, 50,
                                   "Продолжить", DUNGEON_BROWN, DUNGEON_BROWN_HOVER)
        self.menu_btn = Button(VIRTUAL_WIDTH // 2 + 30, VIRTUAL_HEIGHT // 2 + 20, 150, 50,
                               "В меню", RED, LIGHT_RED)
        self.font = level_select_font
        self.active = False

    def draw(self, surface):
        s = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        surface.blit(s, (0, 0))

        pygame.draw.rect(surface, DARK_BLUE, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)

        text = self.font.render("Уровень пройден!", True, WHITE)
        text_rect = text.get_rect(center=(VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT // 2 - 40))
        surface.blit(text, text_rect)

        self.continue_btn.draw(surface)
        self.menu_btn.draw(surface)

    def handle_event(self, event, mouse_pos):
        self.continue_btn.check_hover(mouse_pos)
        self.menu_btn.check_hover(mouse_pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.continue_btn.is_clicked(mouse_pos, event):
                self.active = False
                return "continue"
            elif self.menu_btn.is_clicked(mouse_pos, event):
                return "menu"
        return None


# Класс диалога завершения игры
class GameOverDialog:
    def __init__(self):
        self.width = 510
        self.height = 250
        self.rect = pygame.Rect(VIRTUAL_WIDTH // 2 - self.width // 2, VIRTUAL_HEIGHT // 2 - self.height // 2,
                                self.width, self.height)
        self.menu_btn = Button(VIRTUAL_WIDTH // 2 - 75, VIRTUAL_HEIGHT // 2 + 20, 150, 50,
                               "В меню", BLUE, LIGHT_BLUE)
        self.font = level_select_font
        self.active = False

    def draw(self, surface):
        s = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        surface.blit(s, (0, 0))

        pygame.draw.rect(surface, DARK_BLUE, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)

        # Измененный текст
        text = self.font.render("Ты прошел игру!", True, WHITE)
        text_rect = text.get_rect(center=(VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT // 2 - 40))
        surface.blit(text, text_rect)

        text2 = self.font.render("Скоро будет больше уровней!", True, WHITE)
        text2_rect = text2.get_rect(center=(VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT // 2))
        surface.blit(text2, text2_rect)

        self.menu_btn.draw(surface)

    def handle_event(self, event, mouse_pos):
        self.menu_btn.check_hover(mouse_pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.menu_btn.is_clicked(mouse_pos, event):
                return "menu"
        return None


# Создаем экземпляры диалогов
level_in_dev_dialog = LevelInDevDialog()
death_dialog = DeathDialog()
victory_dialog = VictoryDialog()
game_over_dialog = GameOverDialog()


# Главное меню с анимированными факелами
def show_main_menu():
    menu_active = True

    # Создание кнопок с стилистикой данжа
    play_btn = Button(VIRTUAL_WIDTH // 2 - 130, 300, 260, 60, "Вход в Подземелье", (70, 40, 20), (100, 60, 30))
    exit_btn = Button(VIRTUAL_WIDTH // 2 - 130, 380, 260, 60, "Выход", (70, 20, 20), (100, 40, 30))

    while menu_active:
        current_screen = pygame.display.get_surface()
        screen_width, screen_height = current_screen.get_size()

        scaled_width, scaled_height, x_offset, y_offset, scale = calculate_letterbox(
            VIRTUAL_WIDTH, VIRTUAL_HEIGHT, screen_width, screen_height
        )

        mouse_pos = pygame.mouse.get_pos()
        virtual_mouse_pos = (
            (mouse_pos[0] - x_offset) / scale,
            (mouse_pos[1] - y_offset) / scale
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                toggle_fullscreen()
                continue
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                # Пауза/воспроизведение музыки по нажатию M
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.pause()
                else:
                    pygame.mixer.music.unpause()

            play_btn.check_hover(virtual_mouse_pos)
            exit_btn.check_hover(virtual_mouse_pos)

            if play_btn.is_clicked(virtual_mouse_pos, event):
                level = show_level_select()
                if level:
                    return level
            elif exit_btn.is_clicked(virtual_mouse_pos, event):
                pygame.quit()
                sys.exit()

        # Отрисовка
        virtual_screen.blit(stone_texture, (0, 0))

        # Добавление затемнения для лучшей читаемости
        overlay = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        virtual_screen.blit(overlay, (0, 0))

        # Заголовок с эффектом металла
        title_text = title_font.render("Подземелья Ужаса", True, (200, 150, 50))
        title_shadow = title_font.render("Подземелья Ужаса", True, (100, 50, 0))

        # Эффект объема для текста
        virtual_screen.blit(title_shadow, (VIRTUAL_WIDTH // 2 - title_shadow.get_width() // 2 + 3, 103))
        virtual_screen.blit(title_text, (VIRTUAL_WIDTH // 2 - title_text.get_width() // 2, 100))

        # Подчеркивание
        pygame.draw.line(virtual_screen, (150, 100, 0),
                         (VIRTUAL_WIDTH // 2 - 180, 170),
                         (VIRTUAL_WIDTH // 2 + 180, 170), 3)

        # Кнопки
        play_btn.draw(virtual_screen)
        exit_btn.draw(virtual_screen)

        # Отображение статуса музыки
        music_font = pygame.font.SysFont(None, 24)
        music_status = "Музыка: ВКЛ" if pygame.mixer.music.get_busy() else "Музыка: ВЫКЛ"
        music_text = music_font.render(music_status, True, WHITE)
        virtual_screen.blit(music_text, (VIRTUAL_WIDTH - 150, 20))

        scaled_surface = pygame.transform.scale(virtual_screen, (scaled_width, scaled_height))
        current_screen.fill(BLACK)
        current_screen.blit(scaled_surface, (x_offset, y_offset))
        pygame.display.flip()


# Меню выбора уровня
def show_level_select():
    level_active = True

    # Создание кнопок с стилистикой данжа
    level1_btn = Button(VIRTUAL_WIDTH // 2 - 130, 250, 260, 60, "Уровень 1", (70, 40, 20), (100, 60, 30))
    level2_btn = Button(VIRTUAL_WIDTH // 2 - 130, 330, 260, 60, "Уровень 2", (70, 40, 20), (100, 60, 30))
    back_btn = Button(VIRTUAL_WIDTH // 2 - 130, 410, 260, 60, "Назад", (70, 20, 20), (100, 40, 30))

    while level_active:
        current_screen = pygame.display.get_surface()
        screen_width, screen_height = current_screen.get_size()

        scaled_width, scaled_height, x_offset, y_offset, scale = calculate_letterbox(
            VIRTUAL_WIDTH, VIRTUAL_HEIGHT, screen_width, screen_height
        )

        mouse_pos = pygame.mouse.get_pos()
        virtual_mouse_pos = (
            (mouse_pos[0] - x_offset) / scale,
            (mouse_pos[1] - y_offset) / scale
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                toggle_fullscreen()
                continue
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                # Пауза/воспроизведение музыки по нажатию M
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.pause()
                else:
                    pygame.mixer.music.unpause()

            if level_in_dev_dialog.active:
                if level_in_dev_dialog.handle_event(event, virtual_mouse_pos):
                    level_in_dev_dialog.active = False
                continue

            level1_btn.check_hover(virtual_mouse_pos)
            level2_btn.check_hover(virtual_mouse_pos)
            back_btn.check_hover(virtual_mouse_pos)

            if level1_btn.is_clicked(virtual_mouse_pos, event):
                level_path = os.path.join(SCRIPT_DIR, "demo_lvl.tmx")
                if os.path.exists(level_path):
                    return "level1"
                else:
                    level_in_dev_dialog.active = True
            elif level2_btn.is_clicked(virtual_mouse_pos, event):
                level_path = os.path.join(SCRIPT_DIR, "lvl2new.tmx")
                if os.path.exists(level_path):
                    return "level2"
                else:
                    level_in_dev_dialog.active = True
            elif back_btn.is_clicked(virtual_mouse_pos, event):
                return None

        # Отрисовка фона
        virtual_screen.blit(stone_texture, (0, 0))

        # Добавление затемнения для лучшей читаемости
        overlay = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        virtual_screen.blit(overlay, (0, 0))

        # Заголовок
        title_text = level_select_font.render("Выберите уровень", True, (200, 150, 50))
        title_shadow = level_select_font.render("Выберите уровень", True, (100, 50, 0))

        # Эффект объема для текста
        virtual_screen.blit(title_shadow, (VIRTUAL_WIDTH // 2 - title_shadow.get_width() // 2 + 3, 103))
        virtual_screen.blit(title_text, (VIRTUAL_WIDTH // 2 - title_text.get_width() // 2, 100))

        # Подчеркивание
        pygame.draw.line(virtual_screen, (150, 100, 0),
                         (VIRTUAL_WIDTH // 2 - 180, 170),
                         (VIRTUAL_WIDTH // 2 + 180, 170), 3)

        # Кнопки
        level1_btn.draw(virtual_screen)
        level2_btn.draw(virtual_screen)
        back_btn.draw(virtual_screen)

        if level_in_dev_dialog.active:
            level_in_dev_dialog.draw(virtual_screen)

        # Отображение статуса музыки
        music_font = pygame.font.SysFont(None, 24)
        music_status = "Музыка: ВКЛ" if pygame.mixer.music.get_busy() else "Музыка: ВЫКЛ"
        music_text = music_font.render(music_status, True, WHITE)
        virtual_screen.blit(music_text, (VIRTUAL_WIDTH - 150, 20))

        scaled_surface = pygame.transform.scale(virtual_screen, (scaled_width, scaled_height))
        current_screen.fill(BLACK)
        current_screen.blit(scaled_surface, (x_offset, y_offset))
        pygame.display.flip()
        clock.tick(60)


# Загрузка уровня с шипами и волками
def load_level(level_name):
    try:
        if level_name == "level1":
            TMX_PATH = os.path.join(SCRIPT_DIR, "demo_lvl.tmx")
        else:
            TMX_PATH = os.path.join(SCRIPT_DIR, "lvl2new.tmx")

        tmx_data = load_pygame(TMX_PATH)
        print(f"Карта {level_name} успешно загружена!")

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
        spikes = []  # Список для шипов
        wolf_spawns = []  # Список для точек спавна волков

        # Загрузка текстур шипов
        try:
            # Загружаем текстуры для активных и неактивных шипов
            spike_inactive_img = pygame.image.load(os.path.join(SCRIPT_DIR, "textures", "spike_inactive.png"))
            spike_active_img = pygame.image.load(os.path.join(SCRIPT_DIR, "textures", "spike_active.png"))
        except pygame.error as e:
            print(f"Ошибка загрузки текстур шипов: {e}")
            # Создаем запасные текстуры
            spike_inactive_img = pygame.Surface((32, 32))
            spike_inactive_img.fill(SPIKE_INACTIVE)
            spike_active_img = pygame.Surface((32, 32))
            spike_active_img.fill(SPIKE_ACTIVE)

        for layer in tmx_data.layers:
            if not hasattr(layer, 'data'):  # Объектные слои
                for obj in layer:
                    if hasattr(obj, 'properties'):
                        obj_type = obj.properties.get("obj_type", "")
                        if obj_type == "spawn_point":
                            spawn_points.append({
                                'x': obj.x,
                                'y': obj.y,
                                'dir': obj.properties.get("direction", "south")
                            })
                        elif obj_type == "victory":
                            victory_triggers.append({
                                'rect': pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                            })
                        elif obj_type == "spike":  # Загружаем шипы
                            # Масштабируем текстуры под размер объекта
                            scaled_inactive = pygame.transform.scale(
                                spike_inactive_img,
                                (obj.width, obj.height)
                            )
                            scaled_active = pygame.transform.scale(
                                spike_active_img,
                                (obj.width, obj.height)
                            )

                            spikes.append({
                                'rect': pygame.Rect(obj.x, obj.y, obj.width, obj.height),
                                'active': False,  # Изначально неактивны
                                'active_img': scaled_active,
                                'inactive_img': scaled_inactive
                            })
                        elif obj_type == "spawn_wolf":  # Загружаем точки спавна волков
                            wolf_spawns.append({
                                'x': obj.x,
                                'y': obj.y
                            })

        if not spawn_points:
            spawn_points.append({'x': 100, 'y': 100, 'dir': 'south'})

        # Проверяем, есть ли на уровне шипы
        has_spikes = len(spikes) > 0

        return tmx_data, collision_map, tile_size, spawn_points[0], victory_triggers, spikes, has_spikes, wolf_spawns

    except Exception as e:
        print(f"Ошибка загрузки уровня {level_name}: {e}")
        return None, None, None, None, None, None, False, []


# Константы для состояний волка
SLEEPING = 0
AWAKE = 1
REACTING = 2

# Константы для скорости
PLAYER_SPEED = 1
WOLF_SPEED = 10
WOLF_REACTION_TIME = 1


# Класс игрока с пошаговым перемещением и анимацией
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.color = (255, 0, 0)  # Красный (запасной вариант)
        self.facing_right = True  # Направление взгляда

        # Загрузка текстуры игрока
        try:
            self.original_image = pygame.image.load(os.path.join(SCRIPT_DIR, "hero.png")).convert_alpha()
            # Масштабируем изображение до 32x32
            self.image = pygame.transform.scale(self.original_image, (32, 32))
            print("Текстура игрока успешно загружена")
        except Exception as e:
            print(f"Ошибка загрузки текстуры игрока: {e}")
            self.image = None

        # Состояние движения
        self.moving = False
        self.move_direction = None
        self.start_pos = (x, y)
        self.target_pos = (x, y)
        self.move_progress = 0.0
        self.move_speed = 0.2  # Скорость анимации (0.0-1.0 за шаг)
        self.just_moved = False  # Флаг, что игрок только что завершил ход

    def start_move(self, direction, collision_map, tile_size):
        """Начинает движение в указанном направлении"""
        if self.moving:
            return False

        dx, dy = 0, 0
        if direction == "left":
            dx = -1
            self.facing_right = False
        elif direction == "right":
            dx = 1
            self.facing_right = True
        elif direction == "up":
            dy = -1
        elif direction == "down":
            dy = 1

        # Рассчитываем новую позицию
        new_x = self.rect.x + dx * tile_size
        new_y = self.rect.y + dy * tile_size

        # Проверяем коллизии для новой позиции
        if self.check_collision_at_position(new_x, new_y, collision_map, tile_size):
            return False

        # Воспроизведение звука шага
        footstep_sound.play()

        # Начинаем движение
        self.moving = True
        self.move_direction = direction
        self.start_pos = (self.rect.x, self.rect.y)
        self.target_pos = (new_x, new_y)
        self.move_progress = 0.0
        self.just_moved = False
        return True

    def update(self):
        """Обновляет состояние игрока (анимация движения)"""
        if self.moving:
            self.move_progress += self.move_speed
            if self.move_progress >= 1.0:
                # Движение завершено
                self.moving = False
                self.rect.x = self.target_pos[0]
                self.rect.y = self.target_pos[1]
                self.just_moved = True  # Устанавливаем флаг, что ход завершен
            else:
                # Плавное перемещение
                self.rect.x = self.start_pos[0] + (self.target_pos[0] - self.start_pos[0]) * self.move_progress
                self.rect.y = self.start_pos[1] + (self.target_pos[1] - self.start_pos[1]) * self.move_progress
        else:
            self.just_moved = False

    def check_collision_at_position(self, x, y, collision_map, tile_size):
        """Проверяет коллизию для указанной позиции"""
        # Создаем временный прямоугольник для проверки
        temp_rect = pygame.Rect(x, y, self.rect.width, self.rect.height)

        # Проверяем все тайлы, с которыми пересекается игрок
        left_tile = temp_rect.left // tile_size
        right_tile = (temp_rect.right - 1) // tile_size
        top_tile = temp_rect.top // tile_size
        bottom_tile = (temp_rect.bottom - 1) // tile_size

        for ty in range(top_tile, bottom_tile + 1):
            for tx in range(left_tile, right_tile + 1):
                # Проверяем границы карты
                if tx < 0 or tx >= len(collision_map[0]) or ty < 0 or ty >= len(collision_map):
                    return True

                # Проверяем коллизию тайла
                if collision_map[ty][tx]:
                    return True

        return False

    def check_trigger(self, trigger_rect):
        return self.rect.colliderect(trigger_rect)

    def draw(self, surface):
        """Отрисовывает игрока"""
        if self.image:
            # Отражаем изображение при движении влево
            if not self.facing_right:
                flipped_image = pygame.transform.flip(self.image, True, False)
                surface.blit(flipped_image, (self.rect.x, self.rect.y))
            else:
                surface.blit(self.image, (self.rect.x, self.rect.y))
        else:
            pygame.draw.rect(surface, self.color, self.rect)


# Класс волка с ИИ
SLEEPING = 0
AWAKE = 1
REACTING = 2


# Класс волка с ИИ (должен быть определен ДО game_loop)
class Wolf:
    def __init__(self, x, y, tile_size):
        self.tile_size = tile_size

        try:
            self.img_sleep = pygame.transform.scale(
                pygame.image.load(os.path.join(SCRIPT_DIR, "wolf0.png")).convert_alpha(), (32, 32))
            self.img_hunt = pygame.transform.scale(
                pygame.image.load(os.path.join(SCRIPT_DIR, "wolf1.png")).convert_alpha(), (32, 32))
        except Exception as e:
            print(f"Ошибка загрузки текстур волка: {e}")
            self.img_sleep = pygame.Surface((32, 32), pygame.SRCALPHA)
            self.img_hunt = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.rect(self.img_sleep, (150, 150, 150, 255), (0, 0, 32, 32))
            pygame.draw.rect(self.img_hunt, (200, 0, 0, 255), (0, 0, 32, 32))

        # Выравнивание по тайлу
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
        print(f"🐺 Волк создан @ {self.rect.x},{self.rect.y}")

    def bfs_path(self, start, goal, collision_map):
        visited = set()
        queue = deque()
        queue.append((start, []))

        while queue:
            current, path = queue.popleft()
            if current == goal:
                return path

            if current in visited:
                continue
            visited.add(current)

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = current[0] + dx, current[1] + dy
                if 0 <= nx < len(collision_map[0]) and 0 <= ny < len(collision_map):
                    if not collision_map[ny][nx] and (nx, ny) not in visited:
                        queue.append(((nx, ny), path + [(nx, ny)]))

        return None

    def start_move(self, dx, dy, collision_map, tile_size):
        if self.moving:
            return False

        new_x = self.rect.x + dx * tile_size
        new_y = self.rect.y + dy * tile_size
        temp_rect = pygame.Rect(new_x, new_y, self.rect.width, self.rect.height)

        # Проверка коллизии
        left = temp_rect.left // tile_size
        right = (temp_rect.right - 1) // tile_size
        top = temp_rect.top // tile_size
        bottom = (temp_rect.bottom - 1) // tile_size

        for ty in range(top, bottom + 1):
            for tx in range(left, right + 1):
                if 0 <= tx < len(collision_map[0]) and 0 <= ty < len(collision_map):
                    if collision_map[ty][tx]:
                        return False
                else:
                    return False

        # Движение разрешено
        self.moving = True
        self.start_pos = (self.rect.x, self.rect.y)
        self.target_pos = (new_x, new_y)
        self.move_progress = 0.0
        self.facing_right = dx > 0
        self.move_cooldown = 10
        return True

    def update(self, player_pos, collision_map, tile_size):
        # Анимация движения
        if self.moving:
            self.move_progress += self.move_speed
            if self.move_progress >= 1.0:
                self.moving = False
                self.rect.x = self.target_pos[0]
                self.rect.y = self.target_pos[1]
            else:
                self.rect.x = self.start_pos[0] + (self.target_pos[0] - self.start_pos[0]) * self.move_progress
                self.rect.y = self.start_pos[1] + (self.target_pos[1] - self.start_pos[1]) * self.move_progress

        if self.move_cooldown > 0:
            self.move_cooldown -= 1

        # Пробуждение волка
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
                    if 0 <= cx < len(collision_map[0]) and 0 <= cy < len(collision_map):
                        if collision_map[cy][cx]:
                            visible = False
                            break
                    else:
                        visible = False
                        break

                if visible:
                    self.state = REACTING
                    self.move_cooldown = 30
                    print("🐺 Волк проснулся!")

    def take_turn(self, player, collision_map, tile_size):
        if self.state == REACTING:
            self.state = AWAKE
            return False

        if self.state != AWAKE or self.moving or self.move_cooldown > 0:
            return False

        my_tile = (self.rect.centerx // tile_size, self.rect.centery // tile_size)
        player_tile = (player.rect.centerx // tile_size, player.rect.centery // tile_size)

        # Если игрок рядом - атака
        if abs(my_tile[0] - player_tile[0]) + abs(my_tile[1] - player_tile[1]) == 1:
            return True

        # Поиск пути
        path = self.bfs_path(my_tile, player_tile, collision_map)
        if path and len(path) > 0:
            next_tile = path[0]
            dx = next_tile[0] - my_tile[0]
            dy = next_tile[1] - my_tile[1]
            self.start_move(dx, dy, collision_map, tile_size)

        return False

    def draw(self, surface):
        img = self.img_sleep if self.state == SLEEPING else self.img_hunt
        if not self.facing_right:
            img = pygame.transform.flip(img, True, False)
        surface.blit(img, self.rect.topleft)

    def reset(self):
        self.rect.x, self.rect.y = self.spawn_pos
        self.state = SLEEPING
        self.moving = False
        self.move_progress = 0.0
        self.move_cooldown = 0


# 4. Шейдер освещения
class LightShader:
    def __init__(self):
        self.radius = 4  # Радиус в тайлах
        self.light_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
        self.light_squares = []  # Буфер для световых квадратов

    def calculate_light(self, player_pos, collision_map, tile_size):  # Добавлен параметр tile_size
        """Рассчитывает видимые квадраты освещения"""
        self.light_squares = []
        px, py = player_pos
        player_tx = px // tile_size
        player_ty = py // tile_size

        # Перебираем тайлы в радиусе освещения
        for dx in range(-self.radius, self.radius + 1):
            for dy in range(-self.radius, self.radius + 1):
                # Пропускаем слишком далекие тайлы
                if abs(dx) + abs(dy) > self.radius:
                    continue

                tx = player_tx + dx
                ty = player_ty + dy

                # Проверяем границы карты
                if tx < 0 or tx >= len(collision_map[0]) or ty < 0 or ty >= len(collision_map):
                    continue

                # Проверяем видимость
                visible = True
                # Простая проверка по линии
                steps = max(abs(dx), abs(dy))
                if steps > 0:
                    for i in range(1, steps + 1):
                        check_x = player_tx + int(dx * i / steps)
                        check_y = player_ty + int(dy * i / steps)

                        if 0 <= check_x < len(collision_map[0]) and 0 <= check_y < len(collision_map):
                            if collision_map[check_y][check_x]:
                                visible = False
                                break
                        else:
                            visible = False
                            break

                if visible:
                    # Рассчитываем прозрачность на основе расстояния
                    distance = math.sqrt(dx * dx + dy * dy)
                    alpha = int(200 * (1 - distance / self.radius))
                    if alpha > 0:
                        self.light_squares.append((
                            tx * tile_size,
                            ty * tile_size,
                            tile_size,
                            tile_size,
                            (255, 220, 180, alpha)
                        ))

    def render(self, surface):
        """Отрисовывает освещение"""
        # 1) Световые квадраты
        self.light_surface.fill((0, 0, 0, 0))
        for square in self.light_squares:
            x, y, w, h, color = square
            pygame.draw.rect(self.light_surface, color, (x, y, w, h))

        # 2) Накладываем свет
        surface.blit(self.light_surface, (0, 0))


def apply_dark_overlay(surface, alpha=120):
    """Накладывает тёмное полупрозрачное покрытие на весь экран"""
    darkness = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
    darkness.fill((0, 0, 0, alpha))  # Чёрный с прозрачностью alpha (0–255)
    surface.blit(darkness, (0, 0))


# Основная игровая функция
def game_loop(level_name):
    global screen, fullscreen, normal_window_size, window_size, death_dialog, victory_dialog, game_over_dialog

    # Загружаем уровень с шипами и волками
    tmx_data, collision_map, tile_size, spawn, victory_triggers, spikes, has_spikes, wolf_spawns = load_level(
        level_name)
    if not tmx_data:
        return

    player = Player(spawn['x'], spawn['y'])
    wolves = [Wolf(sp['x'], sp['y'], tile_size) for sp in wolf_spawns]
    light_shader = LightShader()

    # Разделение слоев для корректной отрисовки
    under_layers = []
    over_layers = []
    walls_layer_name = "Walls"  # Имя слоя стен

    for layer in tmx_data.visible_layers:
        if layer.name == walls_layer_name:
            over_layers.append(layer)
        else:
            under_layers.append(layer)

    player_turn = True  # Игрок начинает первым
    running = True
    font = pygame.font.SysFont(None, 24)
    level_complete = False
    game_complete = False
    player_dead = False  # Флаг смерти игрока

    # Переменные для управления шипами
    turns_count = 0  # Счетчик ходов игрока
    spikes_active = False  # Состояние шипов
    prev_spikes_active = False  # Предыдущее состояние шипов для отслеживания изменений

    while running:
        current_screen = pygame.display.get_surface()
        screen_width, screen_height = current_screen.get_size()

        scaled_width, scaled_height, x_offset, y_offset, scale = calculate_letterbox(
            VIRTUAL_WIDTH, VIRTUAL_HEIGHT, screen_width, screen_height
        )

        mouse_pos = pygame.mouse.get_pos()
        virtual_mouse_pos = (
            (mouse_pos[0] - x_offset) / scale,
            (mouse_pos[1] - y_offset) / scale
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if player_dead:
                result = death_dialog.handle_event(event, virtual_mouse_pos)
                if result == "restart":
                    # ПОЛНЫЙ РЕСТАРТ УРОВНЯ
                    player = Player(spawn['x'], spawn['y'])  # Создаем нового игрока
                    wolves = [Wolf(sp['x'], sp['y'], tile_size) for sp in wolf_spawns]  # Пересоздаем волков
                    player_dead = False
                    level_complete = False
                    game_complete = False

                    # Сбрасываем шипы
                    turns_count = 0
                    spikes_active = False
                    prev_spikes_active = False
                    for spike in spikes:
                        spike['active'] = False

                    # Сбрасываем флаги управления
                    player_turn = True

                elif result == "menu":
                    return
            elif level_complete or game_complete:
                if game_complete:
                    result = game_over_dialog.handle_event(event, virtual_mouse_pos)
                else:
                    result = victory_dialog.handle_event(event, virtual_mouse_pos)

                if result == "menu":
                    return
                elif result == "continue":
                    if level_name == "level1":
                        next_level = "level2"
                        try:
                            TMX_PATH = os.path.join(SCRIPT_DIR, "lvl2new.tmx")
                            if os.path.exists(TMX_PATH):
                                game_loop(next_level)
                                return
                            else:
                                level_complete = False
                                game_complete = True
                        except:
                            level_complete = False
                            game_complete = True
                    else:
                        # После второго уровня просто показываем финальный экран
                        level_complete = False
                        game_complete = True
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        # РЕСТАРТ ПО КЛАВИШЕ R
                        player = Player(spawn['x'], spawn['y'])  # Создаем нового игрока
                        wolves = [Wolf(sp['x'], sp['y'], tile_size) for sp in wolf_spawns]  # Пересоздаем волков
                        player_dead = False
                        level_complete = False
                        game_complete = False

                        # Сбрасываем шипы
                        turns_count = 0
                        spikes_active = False
                        prev_spikes_active = False
                        for spike in spikes:
                            spike['active'] = False

                        # Сбрасываем флаги управления
                        player_turn = True

                    elif event.key == pygame.K_F11:
                        toggle_fullscreen()
                    elif event.key == pygame.K_m:
                        # Пауза/воспроизведение музыки по нажатию M
                        if pygame.mixer.music.get_busy():
                            pygame.mixer.music.pause()
                        else:
                            pygame.mixer.music.unpause()
                    elif player_turn and not player.moving:
                        direction = None
                        if event.key == pygame.K_w or event.key == pygame.K_UP: direction = "up"
                        if event.key == pygame.K_s or event.key == pygame.K_DOWN: direction = "down"
                        if event.key == pygame.K_a or event.key == pygame.K_LEFT: direction = "left"
                        if event.key == pygame.K_d or event.key == pygame.K_RIGHT: direction = "right"

                        if direction:
                            if player.start_move(direction, collision_map, tile_size):
                                player_turn = False
                elif event.type == pygame.VIDEORESIZE:
                    if not fullscreen:
                        window_size = (event.w, event.h)
                        screen = pygame.display.set_mode(window_size, pygame.RESIZABLE)

        if not level_complete and not game_complete and not player_dead:
            player.update()
            # Обновляем волков
            for wolf in wolves:
                wolf.update((player.rect.x, player.rect.y), collision_map, tile_size)

            # Ходы волков после игрока
            if player.just_moved:
                # Увеличиваем счетчик ходов
                turns_count += 1

                # Активируем/деактивируем шипы каждые 3 хода
                if has_spikes and turns_count >= 3:
                    spikes_active = not spikes_active
                    turns_count = 0
                    # Обновляем состояние всех шипов
                    for spike in spikes:
                        spike['active'] = spikes_active

                # Волки делают ход
                wolf_attacked = False
                for wolf in wolves:
                    if wolf.take_turn(player, collision_map, tile_size):
                        print("Волк атаковал игрока!")
                        death_sound.play()
                        player_dead = True
                        death_dialog.active = True
                        wolf_attacked = True
                        break

                # ВОССТАНАВЛИВАЕМ ХОД ИГРОКА ПОСЛЕ ХОДА ВОЛКОВ
                if not wolf_attacked:
                    player_turn = True
                player.just_moved = False

        # Проверка триггера победы
        if not player_dead and not level_complete:
            for trigger in victory_triggers:
                if player.check_trigger(trigger['rect']):
                    print("Активирован триггер победы! Победа достигнута!")

                    # Если это второй уровень - показываем финальный экран
                    if level_name == "level2":
                        game_complete = True
                        game_over_dialog.active = True
                    else:
                        level_complete = True
                        victory_dialog.active = True

        # Проверка столкновения с активными шипами
        if has_spikes and spikes_active and not player_dead:
            for spike in spikes:
                if spike['active'] and player.rect.colliderect(spike['rect']):
                    print("Игрок погиб на шипах!")
                    death_sound.play()
                    player_dead = True
                    death_dialog.active = True
                    break

        # Воспроизведение звуков при изменении состояния шипов
        if has_spikes and spikes_active != prev_spikes_active:
            if spikes_active:
                spike_activate_sound.play()
            else:
                spike_deactivate_sound.play()
            prev_spikes_active = spikes_active

        # === Отрисовка на виртуальном экране ===
        virtual_screen.fill(DARK_BLUE)

        # Отрисовка слоев под игроком
        for layer in under_layers:
            if hasattr(layer, 'data'):
                for x in range(layer.width):
                    for y in range(layer.height):
                        gid = layer.data[y][x]
                        if gid:
                            tile = tmx_data.get_tile_image_by_gid(gid)
                            if tile:
                                virtual_screen.blit(tile, (x * tile_size, y * tile_size))

        # Отрисовываем шипы
        if has_spikes:
            for spike in spikes:
                if spike['active']:
                    virtual_screen.blit(spike['active_img'], spike['rect'].topleft)
                else:
                    virtual_screen.blit(spike['inactive_img'], spike['rect'].topleft)

        # Расчет и отрисовка освещения
        light_shader.calculate_light(player.rect.center, collision_map, tile_size)
        light_shader.render(virtual_screen)

        # Затемнение
        apply_dark_overlay(virtual_screen, alpha=120)

        # Отрисовка волков
        for wolf in wolves:
            wolf.draw(virtual_screen)

        # Отрисовка игрока
        if not player_dead:
            player.draw(virtual_screen)

        # Отрисовка слоев стен
        for layer in over_layers:
            if hasattr(layer, 'data'):
                for x in range(layer.width):
                    for y in range(layer.height):
                        gid = layer.data[y][x]
                        if gid:
                            tile = tmx_data.get_tile_image_by_gid(gid)
                            if tile:
                                virtual_screen.blit(tile, (x * tile_size, y * tile_size))

        # Отладочная информация - ПЕРЕМЕЩЕНА ВПРАВО
        debug_text = [
            f"Уровень: {level_name}",
            f"Игрок: {player.rect.x // tile_size}, {player.rect.y // tile_size}",
            f"Ход: {'Игрок' if player_turn else 'Волки'}",
            f"Ходы до шипов: {3 - turns_count}",
            f"Шипы: {'АКТИВНЫ' if spikes_active and has_spikes else 'неактивны' if has_spikes else 'отсутствуют'}",
            f"Волков: {len(wolves)}",
            "ESC: Выход в меню",
            "R: Сброс позиции",
            "F11: Полный экран",
            "M: Вкл/Выкл музыку"
        ]

        # Рисуем текст в правом верхнем углу
        for i, text in enumerate(debug_text):
            text_surface = font.render(text, True, WHITE)
            # Вычисляем позицию справа с отступом 10 пикселей
            x_pos = VIRTUAL_WIDTH - text_surface.get_width() - 10
            virtual_screen.blit(text_surface, (x_pos, 10 + i * 25))

        # Отображение статуса музыки - ПЕРЕМЕЩЕНО ВЛЕВО ВЕРХНИЙ УГОЛ
        music_status = "Музыка: ВКЛ" if pygame.mixer.music.get_busy() else "Музыка: ВЫКЛ"
        music_text = font.render(music_status, True, WHITE)
        virtual_screen.blit(music_text, (10, 10))  # Левый верхний угол

        # Отображение диалогов
        if player_dead:
            death_dialog.draw(virtual_screen)
        elif level_complete:
            victory_dialog.draw(virtual_screen)
        elif game_complete:
            game_over_dialog.draw(virtual_screen)

        scaled_surface = pygame.transform.scale(virtual_screen, (scaled_width, scaled_height))
        current_screen.fill(BLACK)
        current_screen.blit(scaled_surface, (x_offset, y_offset))
        pygame.display.flip()
        clock.tick(60)


# Основной цикл программы
def main():
    while True:
        selected_level = show_main_menu()
        if selected_level:
            game_loop(selected_level)


if __name__ == "__main__":
    main()
    pygame.quit()
    sys.exit()