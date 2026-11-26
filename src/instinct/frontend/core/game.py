
import pygame

from instinct.frontend.core.scene_manager import SceneManager
from instinct.frontend.interface.theme_manager import ThemeManager
from instinct.frontend.windows.window_manager import WindowManager
from instinct.frontend.settings import (
    DEFAULT_THEME,
    FULLSCREEN,
    RESIZABLE,
    TARGET_FPS,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
    WINDOW_WIDTH,
)


class Game:
    """Coordina el funcionamiento general de la aplicación."""

    def __init__(self):
        pygame.init()

        desktop_sizes = pygame.display.get_desktop_sizes()

        if desktop_sizes:
            desktop_width, desktop_height = desktop_sizes[0]

            if desktop_width > 0 and desktop_height > 0:
                self.windowed_size = (
                    min(WINDOW_WIDTH, int(desktop_width * 0.90)),
                    min(WINDOW_HEIGHT, int(desktop_height * 0.88)),
                )
            else:
                self.windowed_size = (WINDOW_WIDTH, WINDOW_HEIGHT)
        else:
            self.windowed_size = (WINDOW_WIDTH, WINDOW_HEIGHT)

        self.fullscreen = FULLSCREEN

        if self.fullscreen:
            self.screen = pygame.display.set_mode(
                (0, 0),
                pygame.FULLSCREEN,
            )
        else:
            flags = pygame.RESIZABLE if RESIZABLE else 0

            self.screen = pygame.display.set_mode(
                self.windowed_size,
                flags,
            )

        pygame.display.set_caption(WINDOW_TITLE)

        self.clock = pygame.time.Clock()
        self.running = True

        self.theme_manager = ThemeManager(DEFAULT_THEME)
        self.window_manager = WindowManager(self)

        self.scene_manager = SceneManager(self)

    def run(self):
        """Ejecuta el bucle principal."""

        while self.running:
            dt = self.clock.tick(TARGET_FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    continue

                if self.window_manager.handle_event(event):
                    continue

                self.scene_manager.handle_event(event)

            self.scene_manager.update(dt)
            self.window_manager.update(dt)

            self.scene_manager.draw(self.screen)
            self.window_manager.draw(self.screen)

            pygame.display.flip()

        pygame.quit()

    def set_windowed_resolution(self, width, height):
        """Cambia la resolución del modo ventana."""

        if width <= 0 or height <= 0 or self.fullscreen:
            return

        self.windowed_size = (int(width), int(height))

        flags = pygame.RESIZABLE if RESIZABLE else 0

        window_position = pygame.display.get_window_position()

        self.screen = pygame.display.set_mode(
            self.windowed_size,
            flags,
        )

        pygame.display.set_window_position(window_position)
    def quit(self):
        """Solicita el cierre de la aplicación."""

        self.running = False


    def set_fullscreen(self, enabled):
        """Activa o desactiva la pantalla completa."""

        enabled = bool(enabled)

        if enabled == self.fullscreen:
            return

        if enabled:
            self.windowed_size = self.screen.get_size()

            self.screen = pygame.display.set_mode(
                (0, 0),
                pygame.FULLSCREEN,
            )
        else:
            flags = pygame.RESIZABLE if RESIZABLE else 0

            self.screen = pygame.display.set_mode(
                self.windowed_size,
                flags,
            )

        self.fullscreen = enabled
