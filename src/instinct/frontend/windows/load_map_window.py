from pathlib import Path

import pygame

from instinct.frontend.windows.base_window import BaseWindow
from instinct.frontend.scenes.new_simulation import NewSimulationScene
from instinct.loaders.resource_manager import ResourceManager


class LoadMapWindow(BaseWindow):
    """Permite elegir un mapa para preparar una nueva simulación."""

    ROW_HEIGHT = 44

    def __init__(self, game):
        screen_width, screen_height = game.screen.get_size()

        width = min(620, screen_width - 40)
        height = min(480, screen_height - 40)

        rect = (
            (screen_width - width) // 2,
            (screen_height - height) // 2,
            width,
            height,
        )

        super().__init__(game, "Cargar mundo", rect)

        # Utilizamos el mismo cargador de recursos que el resto
        # de la aplicación, sin crear otro sistema para los mapas.
        project_root = Path(__file__).resolve().parents[4]
        resources_path = project_root / "resources"

        self.resource_manager = ResourceManager(resources_path)
        self.resource_manager.load_all()

        self.maps = sorted(self.resource_manager.maps.keys())
        self.scroll = 0

        self.info_font = pygame.font.Font(None, 26)
        self.small_font = pygame.font.Font(None, 21)

    @property
    def list_rect(self):
        return pygame.Rect(
            self.rect.x + 20,
            self.rect.y + 62,
            self.rect.width - 40,
            self.rect.height - 110,
        )

    def _visible_rows(self):
        return max(1, self.list_rect.height // self.ROW_HEIGHT)

    def handle_event(self, event):
        # BaseWindow no recibe siempre la posición del ratón
        # en los eventos de rueda, por eso los tratamos aquí.
        if event.type == pygame.MOUSEWHEEL:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.handle_content_event(event)
                return True

        return super().handle_event(event)

    def handle_content_event(self, event):
        """Gestiona el desplazamiento y la selección de mapas."""

        if event.type == pygame.MOUSEWHEEL:
            max_scroll = max(
                0,
                len(self.maps) - self._visible_rows(),
            )

            self.scroll = max(
                0,
                min(self.scroll - event.y, max_scroll),
            )
            return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.list_rect.collidepoint(event.pos):
                return True

            relative_y = event.pos[1] - self.list_rect.y
            row_index = relative_y // self.ROW_HEIGHT
            map_index = self.scroll + row_index

            if map_index < len(self.maps):
                self._select_map(self.maps[map_index])

            return True

        return True

    def _select_map(self, map_name):
        """Abre la configuración con el mapa que acaba de elegir el usuario."""

        new_scene = NewSimulationScene(
            self.game,
            selected_map=map_name,
            resource_manager=self.resource_manager,
        )

        if new_scene.error_message is not None:
            return

        self.close()
        self.game.scene_manager.change_scene(new_scene)

    def draw_content(self, screen):
        colors = self.game.theme_manager.colors

        if not self.maps:
            message = self.info_font.render(
                "No hay mapas disponibles.",
                True,
                colors["secondary_text"],
            )

            screen.blit(
                message,
                message.get_rect(center=self.list_rect.center),
            )
            return

        previous_clip = screen.get_clip()
        screen.set_clip(self.list_rect)

        end_index = min(
            len(self.maps),
            self.scroll + self._visible_rows(),
        )

        for visible_index, map_index in enumerate(
            range(self.scroll, end_index)
        ):
            map_name = self.maps[map_index]
            row_rect = pygame.Rect(
                self.list_rect.x,
                self.list_rect.y + visible_index * self.ROW_HEIGHT,
                self.list_rect.width,
                self.ROW_HEIGHT - 4,
            )

            pygame.draw.rect(
                screen,
                (41, 39, 71),
                row_rect,
                border_radius=6,
            )

            pygame.draw.rect(
                screen,
                colors["accent"],
                row_rect,
                width=1,
                border_radius=6,
            )

            label = self.info_font.render(
                map_name,
                True,
                colors["text"],
            )

            screen.blit(
                label,
                (row_rect.x + 12, row_rect.y + 10),
            )

        screen.set_clip(previous_clip)

        if len(self.maps) > self._visible_rows():
            hint = self.small_font.render(
                "Usa la rueda del ratón para ver más mapas",
                True,
                colors["secondary_text"],
            )

            screen.blit(
                hint,
                (self.rect.x + 20, self.rect.bottom - 20),
            )

        