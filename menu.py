import pygame
import os
import sys
from settings import *
from utils import calculate_letterbox

# Загрузка шрифтов
try:
    title_font = pygame.font.Font(os.path.join(SCRIPT_DIR, "fonts", "medieval.ttf"), 72)
    button_font = pygame.font.Font(os.path.join(SCRIPT_DIR, "fonts", "medieval.ttf"), 36)
    level_select_font = pygame.font.Font(os.path.join(SCRIPT_DIR, "fonts", "medieval.ttf"), 48)
except:
    title_font = pygame.font.SysFont(None, 72)
    button_font = pygame.font.SysFont(None, 36)
    level_select_font = pygame.font.SysFont(None, 48)

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.font_size = 36  # Начальный размер шрифта
        self.max_font_size = 36  # Максимальный размер
        self.min_font_size = 24  # Минимальный размер

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)
        
        # Автоподбор размера шрифта
        font = button_font
        text_surf = font.render(self.text, True, WHITE)
        
        # Если текст не помещается - уменьшаем шрифт
        while text_surf.get_width() > self.rect.width - 20 and self.font_size > self.min_font_size:
            self.font_size -= 1
            try:
                font = pygame.font.Font(os.path.join(SCRIPT_DIR, "fonts", "medieval.ttf"), self.font_size)
            except:
                font = pygame.font.SysFont(None, self.font_size)
            text_surf = font.render(self.text, True, WHITE)
        
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
        # Восстанавливаем размер шрифта
        self.font_size = self.max_font_size

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

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

class DeathDialog:
    def __init__(self):
        self.width = 440
        self.height = 200
        self.rect = pygame.Rect(VIRTUAL_WIDTH // 2 - self.width // 2, VIRTUAL_HEIGHT // 2 - self.height // 2,
                                self.width, self.height)
        self.restart_btn = Button(VIRTUAL_WIDTH // 2 - 200, VIRTUAL_HEIGHT // 2 + 20, 180, 50,
                                "Начать заново", DUNGEON_BROWN, DUNGEON_BROWN_HOVER)
        self.menu_btn = Button(VIRTUAL_WIDTH // 2 + 30, VIRTUAL_HEIGHT // 2 + 20, 180, 50,
                            "В меню", RED, RED)
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
            if self.restart_btn.is_clicked(mouse_pos, event): return "restart"
            elif self.menu_btn.is_clicked(mouse_pos, event): return "menu"
        return None

class VictoryDialog:
    def __init__(self):
        self.width = 400
        self.height = 200
        self.rect = pygame.Rect(VIRTUAL_WIDTH // 2 - self.width // 2, VIRTUAL_HEIGHT // 2 - self.height // 2,
                                self.width, self.height)
        self.continue_btn = Button(VIRTUAL_WIDTH // 2 - 180, VIRTUAL_HEIGHT // 2 + 20, 180, 50,
                                "Продолжить", DUNGEON_BROWN, DUNGEON_BROWN_HOVER)
        self.menu_btn = Button(VIRTUAL_WIDTH // 2 + 10, VIRTUAL_HEIGHT // 2 + 20, 180, 50,
                            "В меню", RED, RED)
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
            if self.continue_btn.is_clicked(mouse_pos, event): return "continue"
            elif self.menu_btn.is_clicked(mouse_pos, event): return "menu"
        return None

class GameOverDialog:
    def __init__(self):
        self.width = 510
        self.height = 250
        self.rect = pygame.Rect(VIRTUAL_WIDTH // 2 - self.width // 2, VIRTUAL_HEIGHT // 2 - self.height // 2,
                                self.width, self.height)
        self.menu_btn = Button(VIRTUAL_WIDTH // 2 - 90, VIRTUAL_HEIGHT // 2 + 40, 180, 50,
                            "В меню", RED, RED)
        self.font = level_select_font
        self.active = False

    def draw(self, surface):
        s = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        surface.blit(s, (0, 0))
        pygame.draw.rect(surface, DARK_BLUE, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)
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
            if self.menu_btn.is_clicked(mouse_pos, event): return "menu"
        return None

def show_main_menu(virtual_screen, stone_texture, clock):
    menu_active = True
    play_btn = Button(VIRTUAL_WIDTH // 2 - 130, 300, 260, 60, "Вход в Подземелье", DUNGEON_BROWN, DUNGEON_BROWN_HOVER)
    exit_btn = Button(VIRTUAL_WIDTH // 2 - 130, 380, 260, 60, "Выход", (70, 20, 20), (100, 40, 30))

    while menu_active:
        current_screen = pygame.display.get_surface()
        screen_width, screen_height = current_screen.get_size()
        scaled_width, scaled_height, x_offset, y_offset, scale = calculate_letterbox(
            VIRTUAL_WIDTH, VIRTUAL_HEIGHT, screen_width, screen_height
        )
        mouse_pos = pygame.mouse.get_pos()
        virtual_mouse_pos = ((mouse_pos[0] - x_offset) / scale, (mouse_pos[1] - y_offset) / scale)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11: continue
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                if pygame.mixer.music.get_busy(): pygame.mixer.music.pause()
                else: pygame.mixer.music.unpause()

            play_btn.check_hover(virtual_mouse_pos)
            exit_btn.check_hover(virtual_mouse_pos)
            if play_btn.is_clicked(virtual_mouse_pos, event):
                level = show_level_select(virtual_screen, stone_texture, clock)
                if level: return level
            elif exit_btn.is_clicked(virtual_mouse_pos, event): pygame.quit(); sys.exit()

        virtual_screen.blit(stone_texture, (0, 0))
        overlay = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        virtual_screen.blit(overlay, (0, 0))
        title_text = title_font.render("Подземелья Ужаса", True, (200, 150, 50))
        title_shadow = title_font.render("Подземелья Ужаса", True, (100, 50, 0))
        virtual_screen.blit(title_shadow, (VIRTUAL_WIDTH // 2 - title_shadow.get_width() // 2 + 3, 103))
        virtual_screen.blit(title_text, (VIRTUAL_WIDTH // 2 - title_text.get_width() // 2, 100))
        pygame.draw.line(virtual_screen, (150, 100, 0), (VIRTUAL_WIDTH // 2 - 180, 170), (VIRTUAL_WIDTH // 2 + 180, 170), 3)
        play_btn.draw(virtual_screen)
        exit_btn.draw(virtual_screen)
        music_status = "Музыка: ВКЛ" if pygame.mixer.music.get_busy() else "Музыка: ВЫКЛ"
        music_text = pygame.font.SysFont(None, 24).render(music_status, True, WHITE)
        virtual_screen.blit(music_text, (VIRTUAL_WIDTH - 150, 20))
        scaled_surface = pygame.transform.scale(virtual_screen, (scaled_width, scaled_height))
        current_screen.fill(BLACK)
        current_screen.blit(scaled_surface, (x_offset, y_offset))
        pygame.display.flip()
        clock.tick(60)

def show_level_select(virtual_screen, stone_texture, clock):
    level_active = True
    level1_btn = Button(VIRTUAL_WIDTH // 2 - 130, 250, 260, 60, "Уровень 1", DUNGEON_BROWN, DUNGEON_BROWN_HOVER)
    level2_btn = Button(VIRTUAL_WIDTH // 2 - 130, 330, 260, 60, "Уровень 2", DUNGEON_BROWN, DUNGEON_BROWN_HOVER)
    back_btn = Button(VIRTUAL_WIDTH // 2 - 130, 410, 260, 60, "Назад", (70, 20, 20), (100, 40, 30))
    level_in_dev_dialog = LevelInDevDialog()

    while level_active:
        current_screen = pygame.display.get_surface()
        screen_width, screen_height = current_screen.get_size()
        scaled_width, scaled_height, x_offset, y_offset, scale = calculate_letterbox(
            VIRTUAL_WIDTH, VIRTUAL_HEIGHT, screen_width, screen_height
        )
        mouse_pos = pygame.mouse.get_pos()
        virtual_mouse_pos = ((mouse_pos[0] - x_offset) / scale, (mouse_pos[1] - y_offset) / scale)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11: continue
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                if pygame.mixer.music.get_busy(): pygame.mixer.music.pause()
                else: pygame.mixer.music.unpause()

            if level_in_dev_dialog.active:
                if level_in_dev_dialog.handle_event(event, virtual_mouse_pos): level_in_dev_dialog.active = False
                continue

            level1_btn.check_hover(virtual_mouse_pos)
            level2_btn.check_hover(virtual_mouse_pos)
            back_btn.check_hover(virtual_mouse_pos)
            if level1_btn.is_clicked(virtual_mouse_pos, event):
                level_path = os.path.join(SCRIPT_DIR, "lvl1.tmx")
                if os.path.exists(level_path): return "level1"
                else: level_in_dev_dialog.active = True
            elif level2_btn.is_clicked(virtual_mouse_pos, event):
                level_path = os.path.join(SCRIPT_DIR, "lvl2.tmx")
                if os.path.exists(level_path): return "level2"
                else: level_in_dev_dialog.active = True
            elif back_btn.is_clicked(virtual_mouse_pos, event): return None

        virtual_screen.blit(stone_texture, (0, 0))
        overlay = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        virtual_screen.blit(overlay, (0, 0))
        title_text = level_select_font.render("Выберите уровень", True, (200, 150, 50))
        title_shadow = level_select_font.render("Выберите уровень", True, (100, 50, 0))
        virtual_screen.blit(title_shadow, (VIRTUAL_WIDTH // 2 - title_shadow.get_width() // 2 + 3, 103))
        virtual_screen.blit(title_text, (VIRTUAL_WIDTH // 2 - title_text.get_width() // 2, 100))
        pygame.draw.line(virtual_screen, (150, 100, 0), (VIRTUAL_WIDTH // 2 - 180, 170), (VIRTUAL_WIDTH // 2 + 180, 170), 3)
        level1_btn.draw(virtual_screen)
        level2_btn.draw(virtual_screen)
        back_btn.draw(virtual_screen)
        if level_in_dev_dialog.active: level_in_dev_dialog.draw(virtual_screen)
        music_status = "Музыка: ВКЛ" if pygame.mixer.music.get_busy() else "Музыка: ВЫКЛ"
        music_text = pygame.font.SysFont(None, 24).render(music_status, True, WHITE)
        virtual_screen.blit(music_text, (VIRTUAL_WIDTH - 150, 20))
        scaled_surface = pygame.transform.scale(virtual_screen, (scaled_width, scaled_height))
        current_screen.fill(BLACK)
        current_screen.blit(scaled_surface, (x_offset, y_offset))
        pygame.display.flip()
        clock.tick(60)