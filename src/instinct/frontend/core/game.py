
import pygame

from instinct.frontend.core.scene_manager import SceneManager
from instinct.frontend.interface.theme_manager import ThemeManager
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

        self.scene_manager = SceneManager(self)

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

    def set_windowed_resolution(self, width, height):
        """Cambia la resolución del modo ventana."""

        if width <= 0 or height <= 0:
            return

        self.windowed_size = (int(width), int(height))

        if not self.fullscreen:
            flags = pygame.RESIZABLE if RESIZABLE else 0

            self.screen = pygame.display.set_mode(
                self.windowed_size,
                flags,
            )

    def run(self):
        """Ejecuta el bucle principal."""

        while self.running:
            dt = self.clock.tick(TARGET_FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    continue

                self.scene_manager.handle_event(event)

            self.scene_manager.update(dt)
            self.scene_manager.draw(self.screen)

            pygame.display.flip()

        pygame.quit()

    def quit(self):
        """Solicita el cierre de la aplicación."""

        self.running = False
