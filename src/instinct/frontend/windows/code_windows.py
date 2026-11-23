
from pathlib import Path

import pygame

from instinct.frontend.windows.base_window import BaseWindow


class CodeWindows(BaseWindow):
    """Ventana que muestra el código de una criatura y su ejecución."""

    LINE_HEIGHT = 25
    FONT_SIZE = 21
    GUTTER_WIDTH = 48

    CURRENT_LINE_COLOR = (32, 78, 145)
    CURRENT_LINE_TEXT = (255, 255, 255)
    CODE_BACKGROUND = (21, 27, 43)

    def __init__(self, game, simulation_scene):
        screen_width, screen_height = game.screen.get_size()

        width = min(900, screen_width - 80)
        height = min(700, screen_height - 80)

        rect = (
            (screen_width - width) // 2,
            (screen_height - height) // 2,
            width,
            height,
        )

        super().__init__(
            game,
            "Código de criatura",
            rect,
            modal=False,
            draggable=True,
            closable=True,
        )

        self.simulation_scene = simulation_scene

        self.creature = None
        self.source_lines = []
        self.source_error = None

        self.scroll_offset = 0
        self.current_line = None

        self.code_font = pygame.font.SysFont(
            "consolas",
            self.FONT_SIZE,
        )

        self.line_font = pygame.font.SysFont(
            "consolas",
            self.FONT_SIZE - 1,
        )

        self.info_font = pygame.font.Font(None, 23)

        self.set_creature(self._get_selected_creature())

    def _get_selected_creature(self):
        """Obtiene la primera criatura seleccionada."""

        creatures = (
            self.simulation_scene.selection.get_selected_creatures()
        )

        return creatures[0] if creatures else None

    def set_creature(self, creature):
        """Carga el código de una criatura."""

        if creature is self.creature:
            return

        self.creature = creature
        self.source_lines = []
        self.source_error = None
        self.scroll_offset = 0
        self.current_line = None

        if creature is None:
            return

        resource_dir = self.simulation_scene.resource_manager.resource_dir

        filepath = (
            Path(resource_dir)
            / "creatures"
            / f"{creature.name.lower()}.ins"
        )

        try:
            source = filepath.read_text(encoding="utf-8")
            self.source_lines = source.splitlines()

        except OSError:
            self.source_error = (
                f"No se pudo leer el archivo: {filepath.name}"
            )

    def update(self, delta_time):
        """Sincroniza la ventana con la selección y ejecución."""

        selected = self._get_selected_creature()

        self.set_creature(selected)

        if self.creature is None:
            self.current_line = None
            return

        simulation = self.simulation_scene.simulation

        self.current_line = simulation.get_last_executed_line(
            self.creature
        )

        self._ensure_current_line_visible()

    def _get_visible_line_count(self, content_rect):
        code_height = content_rect.height - 30

        return max(
            1,
            code_height // self.LINE_HEIGHT,
        )

    def _ensure_current_line_visible(self):
        """Desplaza el código para mantener visible la línea activa."""

        if self.current_line is None:
            return

        line_index = self.current_line - 1

        visible_count = max(
            1,
            (self.rect.height - 125) // self.LINE_HEIGHT,
        )

        if line_index < self.scroll_offset:
            self.scroll_offset = line_index

        elif line_index >= self.scroll_offset + visible_count:
            self.scroll_offset = line_index - visible_count + 1

        self.scroll_offset = max(0, self.scroll_offset)

    def handle_event(self, event):
        """Gestiona el desplazamiento manual del código."""

        if event.type == pygame.MOUSEWHEEL:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                max_offset = max(
                    0,
                    len(self.source_lines) - 1,
                )

                self.scroll_offset = max(
                    0,
                    min(
                        max_offset,
                        self.scroll_offset - event.y * 3,
                    ),
                )

                return True

        return super().handle_event(event)

    def draw_content(self, screen):
        colors = self.game.theme_manager.colors

        content_rect = pygame.Rect(
            self.rect.x + 12,
            self.rect.y + self.HEADER_HEIGHT + 10,
            self.rect.width - 24,
            self.rect.height - self.HEADER_HEIGHT - 20,
        )

        pygame.draw.rect(
            screen,
            self.CODE_BACKGROUND,
            content_rect,
            border_radius=6,
        )

        previous_clip = screen.get_clip()
        screen.set_clip(content_rect)

        # Información de la criatura.
        if self.creature is None:
            info = "Selecciona una criatura para consultar su código."

        else:
            info = (
                f"{self.creature.name}  |  "
                f"Facción: {self.creature.faction}"
            )

            if self.current_line is not None:
                info += f"  |  Línea: {self.current_line}"
            else:
                info += "  |  Esperando ejecución"

        info_surface = self.info_font.render(
            info,
            True,
            colors["gold"],
        )

        screen.blit(
            info_surface,
            (content_rect.x + 12, content_rect.y + 8),
        )

        code_top = content_rect.y + 35

        visible_count = max(
            1,
            (content_rect.bottom - code_top) // self.LINE_HEIGHT,
        )

        if self.source_error:
            error_surface = self.code_font.render(
                self.source_error,
                True,
                (230, 110, 110),
            )

            screen.blit(
                error_surface,
                (content_rect.x + 12, code_top + 8),
            )

        elif not self.source_lines:
            message = (
                "No hay ninguna criatura seleccionada."
                if self.creature is None
                else "El archivo de código está vacío."
            )

            message_surface = self.code_font.render(
                message,
                True,
                colors["secondary_text"],
            )

            screen.blit(
                message_surface,
                (content_rect.x + 12, code_top + 8),
            )

        else:
            for visible_index in range(visible_count):
                line_index = self.scroll_offset + visible_index

                if line_index >= len(self.source_lines):
                    break

                line_number = line_index + 1

                y = code_top + visible_index * self.LINE_HEIGHT

                is_current = (
                    line_number == self.current_line
                )

                if is_current:
                    highlight_rect = pygame.Rect(
                        content_rect.x,
                        y,
                        content_rect.width,
                        self.LINE_HEIGHT,
                    )

                    pygame.draw.rect(
                        screen,
                        self.CURRENT_LINE_COLOR,
                        highlight_rect,
                    )

                number_color = (
                    self.CURRENT_LINE_TEXT
                    if is_current
                    else colors["secondary_text"]
                )

                text_color = (
                    self.CURRENT_LINE_TEXT
                    if is_current
                    else colors["text"]
                )

                number_surface = self.line_font.render(
                    str(line_number).rjust(3),
                    True,
                    number_color,
                )

                code_surface = self.code_font.render(
                    self.source_lines[line_index],
                    True,
                    text_color,
                )

                screen.blit(
                    number_surface,
                    (content_rect.x + 5, y + 2),
                )

                screen.blit(
                    code_surface,
                    (
                        content_rect.x + self.GUTTER_WIDTH,
                        y + 2,
                    ),
                )

        screen.set_clip(previous_clip)
