
from pathlib import Path

import pygame

from instinct.frontend.scenes.base_scene import BaseScene
from instinct.frontend.scenes.simulation_scene import SimulationScene
from instinct.loaders.resource_manager import ResourceManager


class NewSimulationScene(BaseScene):
    """Pantalla para configurar una nueva simulación."""

    MAX_CREATURES = 10

    BACKGROUND = (17, 19, 34)
    PANEL = (30, 30, 51)
    CARD = (41, 39, 71)
    BORDER = (92, 76, 125)
    ACCENT = (118, 84, 168)
    GOLD = (212, 174, 98)
    TEXT = (242, 239, 250)
    MUTED = (155, 150, 174)
    DISABLED = (75, 72, 91)

    def __init__(self, game):
        super().__init__(game)

        self.resource_manager = None

        self.maps = []
        self.map_index = 0

        # Cantidad inicial de cada especie.
        self.creature_counts = {}

        self.error_message = None

        self.title_font = pygame.font.Font(None, 58)
        self.subtitle_font = pygame.font.Font(None, 27)
        self.section_font = pygame.font.Font(None, 34)
        self.text_font = pygame.font.Font(None, 29)
        self.small_font = pygame.font.Font(None, 23)

        self._load_resources()

    def _load_resources(self):
        """Carga los recursos disponibles para configurar la partida."""

        project_root = Path(__file__).resolve().parents[4]
        resources_path = project_root / "resources"

        self.resource_manager = ResourceManager(resources_path)
        self.resource_manager.load_all()

        self.maps = sorted(self.resource_manager.maps.keys())
        creature_names = sorted(self.resource_manager.creatures.keys())

        self.creature_counts = {
            name: 1
            for name in creature_names
        }

        if not self.maps:
            self.error_message = (
                "No hay mapas disponibles. Revisa los recursos."
            )

        if not creature_names:
            self.error_message = (
                "No hay criaturas disponibles. Revisa los archivos .ins."
            )

    @property
    def selected_map(self):
        if not self.maps:
            return None

        return self.maps[self.map_index]

    def _change_map(self, direction):
        """Cambia el mapa seleccionado."""

        if not self.maps:
            return

        self.map_index = (
            self.map_index + direction
        ) % len(self.maps)

    def _change_creature_count(self, name, amount):
        """Modifica la cantidad de una especie."""

        current = self.creature_counts[name]

        self.creature_counts[name] = max(
            0,
            min(self.MAX_CREATURES, current + amount),
        )

    def _start_simulation(self):
        """Inicia la simulación con la configuración seleccionada."""

        if self.selected_map is None:
            return

        selected_creatures = {
            name: count
            for name, count in self.creature_counts.items()
            if count > 0
        }

        if not selected_creatures:
            self.error_message = (
                "Selecciona al menos una criatura para iniciar."
            )
            return

        self.game.scene_manager.change_scene(
            SimulationScene(
                self.game,
                resource_manager=self.resource_manager,
                map_name=self.selected_map,
                creature_counts=selected_creatures,
            )
        )

    def _return_to_menu(self):
        """Regresa al menú principal."""

        from instinct.frontend.scenes.main_menu import MainMenu

        self.game.scene_manager.change_scene(
            MainMenu(self.game)
        )

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._return_to_menu()
                return

            if event.key == pygame.K_LEFT:
                self._change_map(-1)

            elif event.key == pygame.K_RIGHT:
                self._change_map(1)

        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return

        width, height = self.game.screen.get_size()

        # Selector de mapa.
        map_rect = pygame.Rect(
            width // 2 - 230,
            245,
            460,
            58,
        )

        previous_rect = pygame.Rect(
            map_rect.left - 65,
            map_rect.y,
            52,
            58,
        )

        next_rect = pygame.Rect(
            map_rect.right + 13,
            map_rect.y,
            52,
            58,
        )

        if previous_rect.collidepoint(event.pos):
            self._change_map(-1)
            return

        if next_rect.collidepoint(event.pos):
            self._change_map(1)
            return

        # Controles de cantidad de criaturas.
        names = list(self.creature_counts.keys())

        row_height = 76
        start_y = 435

        for index, name in enumerate(names):
            row_y = start_y + index * row_height

            minus_rect = pygame.Rect(
                width // 2 + 185,
                row_y + 12,
                42,
                42,
            )

            plus_rect = pygame.Rect(
                width // 2 + 285,
                row_y + 12,
                42,
                42,
            )

            if minus_rect.collidepoint(event.pos):
                self._change_creature_count(name, -1)
                return

            if plus_rect.collidepoint(event.pos):
                self._change_creature_count(name, 1)
                return

        # Botones inferiores.
        back_rect = pygame.Rect(
            width // 2 - 245,
            height - 105,
            210,
            58,
        )

        start_rect = pygame.Rect(
            width // 2 + 35,
            height - 105,
            210,
            58,
        )

        if back_rect.collidepoint(event.pos):
            self._return_to_menu()

        elif start_rect.collidepoint(event.pos):
            self._start_simulation()

    def _draw_text(
        self,
        surface,
        text,
        font,
        color,
        position,
        center=False,
    ):
        rendered = font.render(str(text), True, color)

        rect = rendered.get_rect()

        if center:
            rect.center = position
        else:
            rect.topleft = position

        surface.blit(rendered, rect)

    def _draw_button(
        self,
        surface,
        rect,
        text,
        enabled=True,
        accent=False,
    ):
        background = self.ACCENT if accent else self.CARD
        border = self.GOLD if accent else self.BORDER

        if not enabled:
            background = self.DISABLED
            border = self.DISABLED

        pygame.draw.rect(
            surface,
            background,
            rect,
            border_radius=8,
        )

        pygame.draw.rect(
            surface,
            border,
            rect,
            width=2,
            border_radius=8,
        )

        self._draw_text(
            surface,
            text,
            self.text_font,
            self.TEXT if enabled else self.MUTED,
            rect.center,
            center=True,
        )

    def _draw_map_selector(self, screen):
        width = screen.get_width()

        self._draw_text(
            screen,
            "SELECCIONA EL MAPA",
            self.section_font,
            self.GOLD,
            (width // 2, 205),
            center=True,
        )

        map_rect = pygame.Rect(
            width // 2 - 230,
            245,
            460,
            58,
        )

        previous_rect = pygame.Rect(
            map_rect.left - 65,
            map_rect.y,
            52,
            58,
        )

        next_rect = pygame.Rect(
            map_rect.right + 13,
            map_rect.y,
            52,
            58,
        )

        self._draw_button(
            screen,
            previous_rect,
            "<",
            enabled=bool(self.maps),
        )

        self._draw_button(
            screen,
            next_rect,
            ">",
            enabled=bool(self.maps),
        )

        self._draw_button(
            screen,
            map_rect,
            self.selected_map or "Sin mapas disponibles",
            enabled=bool(self.maps),
        )

        if self.selected_map:
            world = self.resource_manager.get_map(self.selected_map)

            description = (
                f"Dimensiones: {world.width} × {world.height}"
            )

            self._draw_text(
                screen,
                description,
                self.small_font,
                self.MUTED,
                (width // 2, 322),
                center=True,
            )

    def _draw_creature_selector(self, screen):
        width = screen.get_width()

        self._draw_text(
            screen,
            "POBLACIÓN INICIAL",
            self.section_font,
            self.GOLD,
            (width // 2, 390),
            center=True,
        )

        names = list(self.creature_counts.keys())

        row_height = 76
        start_y = 435

        for index, name in enumerate(names):
            row_y = start_y + index * row_height

            row_rect = pygame.Rect(
                width // 2 - 350,
                row_y,
                700,
                66,
            )

            pygame.draw.rect(
                screen,
                self.CARD,
                row_rect,
                border_radius=8,
            )

            pygame.draw.rect(
                screen,
                self.BORDER,
                row_rect,
                width=1,
                border_radius=8,
            )

            count = self.creature_counts[name]
            enabled = count > 0

            self._draw_text(
                screen,
                name,
                self.text_font,
                self.TEXT if enabled else self.MUTED,
                (row_rect.x + 22, row_rect.centery),
                center=False,
            )

            self._draw_button(
                screen,
                pygame.Rect(
                    width // 2 + 185,
                    row_y + 12,
                    42,
                    42,
                ),
                "-",
                enabled=count > 0,
            )

            self._draw_text(
                screen,
                count,
                self.text_font,
                self.GOLD if enabled else self.MUTED,
                (width // 2 + 256, row_rect.centery),
                center=True,
            )

            self._draw_button(
                screen,
                pygame.Rect(
                    width // 2 + 285,
                    row_y + 12,
                    42,
                    42,
                ),
                "+",
                enabled=count < self.MAX_CREATURES,
            )

        total = sum(self.creature_counts.values())

        self._draw_text(
            screen,
            f"Total de criaturas: {total}",
            self.subtitle_font,
            self.MUTED,
            (width // 2, start_y + len(names) * row_height + 8),
            center=True,
        )

    def draw(self, screen):
        screen.fill(self.BACKGROUND)

        width, height = screen.get_size()

        # Panel principal.
        panel_rect = pygame.Rect(
            width // 2 - 460,
            35,
            920,
            height - 70,
        )

        pygame.draw.rect(
            screen,
            self.PANEL,
            panel_rect,
            border_radius=16,
        )

        pygame.draw.rect(
            screen,
            self.BORDER,
            panel_rect,
            width=2,
            border_radius=16,
        )

        self._draw_text(
            screen,
            "NUEVA SIMULACIÓN",
            self.title_font,
            self.GOLD,
            (width // 2, 105),
            center=True,
        )

        self._draw_text(
            screen,
            "Configura el mundo y la población inicial",
            self.subtitle_font,
            self.MUTED,
            (width // 2, 155),
            center=True,
        )

        self._draw_map_selector(screen)
        self._draw_creature_selector(screen)

        if self.error_message:
            self._draw_text(
                screen,
                self.error_message,
                self.small_font,
                (230, 105, 105),
                (width // 2, height - 145),
                center=True,
            )

        back_rect = pygame.Rect(
            width // 2 - 245,
            height - 105,
            210,
            58,
        )

        start_rect = pygame.Rect(
            width // 2 + 35,
            height - 105,
            210,
            58,
        )

        self._draw_button(
            screen,
            back_rect,
            "Volver",
        )

        can_start = (
            bool(self.maps)
            and any(count > 0 for count in self.creature_counts.values())
        )

        self._draw_button(
            screen,
            start_rect,
            "Iniciar",
            enabled=can_start,
            accent=True,
        )
