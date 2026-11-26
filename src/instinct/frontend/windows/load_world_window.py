import pygame

from instinct.frontend.windows.base_window import BaseWindow
from instinct.persistence import WorldSaveManager
from instinct.frontend.scenes.simulation_scene import SimulationScene


class LoadWorldWindow(BaseWindow):
    """Ventana para seleccionar y recuperar un mundo guardado."""

    ROW_HEIGHT = 46

    def __init__(self, game, recent_only=False):
        screen_width, screen_height = game.screen.get_size()

        width = min(620, screen_width - 40)
        height = min(480, screen_height - 40)

        rect = (
            (screen_width - width) // 2,
            (screen_height - height) // 2,
            width,
            height,
        )

        title = (
            "Mundos recientes"
            if recent_only
            else "Cargar mundo"
        )

        super().__init__(game, title, rect)

        self.saves = WorldSaveManager.list_saves()

        if recent_only:
            self.saves = self.saves[:5]

        self.scroll = 0
        self.message = ""

        self.info_font = pygame.font.Font(None, 25)
        self.small_font = pygame.font.Font(None, 21)

    @property
    def list_rect(self):
        return pygame.Rect(
            self.rect.x + 20,
            self.rect.y + 75,
            self.rect.width - 40,
            self.rect.height - 145,
        )

    def handle_content_event(self, event):
        """Procesa la selección de un guardado."""

        if event.type == pygame.MOUSEWHEEL:
            self.scroll -= event.y

            max_scroll = max(
                0,
                len(self.saves) - self._visible_rows(),
            )

            self.scroll = max(0, min(self.scroll, max_scroll))
            return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.list_rect.collidepoint(event.pos):
                return True

            relative_y = event.pos[1] - self.list_rect.y
            row_index = relative_y // self.ROW_HEIGHT
            save_index = self.scroll + row_index

            if save_index < len(self.saves):
                self._load_save(self.saves[save_index])

            return True

        return True

    def _visible_rows(self):
        return max(
            1,
            self.list_rect.height // self.ROW_HEIGHT,
        )

    def _load_save(self, filepath):
        """Lee el guardado y abre la simulación restaurada."""

        try:
            data = WorldSaveManager.load(filepath)

            new_scene = SimulationScene(
                self.game,
                map_name=data["map_name"],
                saved_data=data,
            )

            if new_scene.error_message is not None:
                raise ValueError(new_scene.error_message)

            self.close()

            self.game.scene_manager.change_scene(new_scene)

        except (OSError, ValueError, KeyError, TypeError) as error:
            self.message = str(error)

    def draw_content(self, screen):
        colors = self.game.theme_manager.colors

        if not self.saves:
            message = self.info_font.render(
                "No hay mundos guardados.",
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

        for visible_index, save_index in enumerate(
            range(self.scroll, min(
                len(self.saves),
                self.scroll + self._visible_rows(),
            ))
        ):
            filepath = self.saves[save_index]

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
                filepath.stem,
                True,
                colors["text"],
            )

            screen.blit(
                label,
                (row_rect.x + 12, row_rect.y + 10),
            )

        screen.set_clip(previous_clip)

        if self.message:
            message_surface = self.small_font.render(
                self.message,
                True,
                colors["gold"],
            )

            screen.blit(
                message_surface,
                (self.rect.x + 20, self.rect.bottom - 48),
            )