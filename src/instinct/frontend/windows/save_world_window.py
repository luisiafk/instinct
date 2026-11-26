
import pygame

from instinct.frontend.windows.base_window import BaseWindow
from instinct.persistence import WorldSaveManager


class SaveWorldWindow(BaseWindow):
    """Ventana para guardar el estado de la simulación actual."""

    def __init__(self, game, simulation_scene):

        # Colocamos la ventana en el centro de la pantalla.
        window_rect = pygame.Rect(0, 0, 500, 300)
        window_rect.center = game.screen.get_rect().center

        super().__init__(
            game,
            "Guardar mundo",
            window_rect,
        )

        self.simulation_scene = simulation_scene

        self.name = ""
        self.input_active = True
        self.message = ""

        self.info_font = pygame.font.Font(None, 25)
        self.input_font = pygame.font.Font(None, 29)
        self.message_font = pygame.font.Font(None, 22)

    @property
    def input_rect(self):
        return pygame.Rect(
            self.rect.x + 24,
            self.rect.y + 105,
            self.rect.width - 48,
            42,
        )

    @property
    def save_rect(self):
        return pygame.Rect(
            self.rect.centerx - 85,
            self.rect.y + 175,
            170,
            42,
        )

    def on_open(self):
        pygame.key.start_text_input()

    def on_close(self):
        pygame.key.stop_text_input()

    def handle_event(self, event):
        """Gestiona la escritura del nombre y el botón de guardado."""

        if event.type == pygame.TEXTINPUT and self.input_active:
            self.name = (self.name + event.text)[:40]
            return True

        if event.type == pygame.KEYDOWN and self.input_active:
            if event.key == pygame.K_BACKSPACE:
                self.name = self.name[:-1]
                return True

            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._save_world()
                return True

        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
        ):
            if self.input_rect.collidepoint(event.pos):
                self.input_active = True
                return True

            if self.save_rect.collidepoint(event.pos):
                self._save_world()
                return True

        return super().handle_event(event)

    def _save_world(self):
        """Guarda la simulación y muestra el resultado."""

        try:
            filepath = WorldSaveManager.save(
                simulation=self.simulation_scene.simulation,
                map_name=self.simulation_scene.map_name,
                save_name=self.name,
                controller=self.simulation_scene.controller,
            )

            self.message = f"Mundo guardado: {filepath.name}"

        except (ValueError, OSError) as error:
            self.message = str(error)

    def draw_content(self, screen):
        colors = self.game.theme_manager.colors

        label = self.info_font.render(
            "Nombre del guardado",
            True,
            colors["text"],
        )

        screen.blit(
            label,
            (self.rect.x + 24, self.rect.y + 75),
        )

        # Campo donde se escribe el nombre.
        pygame.draw.rect(
            screen,
            (20, 24, 39),
            self.input_rect,
            border_radius=6,
        )

        pygame.draw.rect(
            screen,
            colors["accent"],
            self.input_rect,
            width=2,
            border_radius=6,
        )

        displayed_name = self.name or "Escribe un nombre..."

        input_color = (
            colors["text"]
            if self.name
            else colors["secondary_text"]
        )

        input_surface = self.input_font.render(
            displayed_name,
            True,
            input_color,
        )

        screen.blit(
            input_surface,
            (self.input_rect.x + 10, self.input_rect.y + 8),
        )

        # Botón para confirmar el guardado.
        pygame.draw.rect(
            screen,
            colors["accent"],
            self.save_rect,
            border_radius=7,
        )

        button_surface = self.info_font.render(
            "Guardar",
            True,
            colors["text"],
        )

        screen.blit(
            button_surface,
            button_surface.get_rect(
                center=self.save_rect.center,
            ),
        )

        if self.message:
            message_surface = self.message_font.render(
                self.message,
                True,
                colors["gold"],
            )

            screen.blit(
                message_surface,
                (
                    self.rect.x + 24,
                    self.rect.bottom - 27,
                ),
            )