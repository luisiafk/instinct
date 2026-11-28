
import pygame

from instinct.frontend.interface.widgets.button import Button
from instinct.frontend.scenes.base_scene import BaseScene


class SettingsScene(BaseScene):
    """Pantalla de configuración general de Instinct."""

    RESOLUTIONS = (
        (1280, 720),
        (1600, 900),
        (1920, 1080),
    )

    def __init__(self, game):
        super().__init__(game)

        self.theme_manager = game.theme_manager

        self.title_font = pygame.font.Font(None, 64)
        self.info_font = pygame.font.Font(None, 27)

        self.panel_rect = pygame.Rect(0, 0, 0, 0)
        self.buttons = []

        current_resolution = self.game.windowed_size

        resolutions = list(self.RESOLUTIONS)

        if current_resolution not in resolutions:
            resolutions.append(current_resolution)

        self.resolutions = resolutions
        self.resolution_index = self.resolutions.index(
            current_resolution
        )

        self._create_buttons()
        self._update_layout()
        self._refresh_labels()

    def _create_buttons(self):
        """Crea los controles de configuración."""

        self.buttons = [
            Button(
                (0, 0, 100, 55),
                "",
                callback=self._toggle_theme,
                font_size=30,
            ),
            Button(
                (0, 0, 100, 55),
                "",
                callback=self._toggle_fullscreen,
                font_size=30,
            ),
            Button(
                (0, 0, 100, 55),
                "",
                callback=self._cycle_resolution,
                font_size=30,
            ),
            Button(
                (0, 0, 100, 55),
                "Volver",
                callback=self._return_to_menu,
                font_size=30,
            ),
        ]

    def _update_layout(self):
        """Adapta los controles al tamaño de pantalla."""

        width, height = self.game.screen.get_size()

        panel_width = min(680, width - 40)
        panel_height = min(650, height - 40)

        self.panel_rect = pygame.Rect(
            0,
            0,
            panel_width,
            panel_height,
        )

        self.panel_rect.center = (
            width // 2,
            height // 2,
        )

        button_width = min(460, panel_width - 80)
        button_height = 58
        spacing = 22

        start_y = self.panel_rect.y + 230

        for index, button in enumerate(self.buttons):
            button.rect = pygame.Rect(
                0,
                0,
                button_width,
                button_height,
            )

            button.rect.centerx = self.panel_rect.centerx
            button.rect.y = start_y + index * (
                button_height + spacing
            )

    def _refresh_labels(self):
        """Actualiza los textos y estados de los controles."""

        theme_name = (
            "Claro"
            if self.theme_manager.current_theme == "light"
            else "Oscuro"
        )

        self.buttons[0].text = f"Tema: {theme_name}"

        display_mode = (
            "Pantalla completa"
            if self.game.fullscreen
            else "Ventana"
        )

        self.buttons[1].text = f"Modo: {display_mode}"

        width, height = self.game.windowed_size

        self.buttons[2].text = (
            f"Resolución: {width} × {height}"
        )

        self.buttons[2].enabled = not self.game.fullscreen

    def _toggle_theme(self):
        """Alterna entre tema oscuro y claro."""

        self.theme_manager.toggle_theme()
        self._refresh_labels()

    def _toggle_fullscreen(self):
        """Alterna entre ventana y pantalla completa."""

        self.game.set_fullscreen(
            not self.game.fullscreen
        )

        self._update_layout()
        self._refresh_labels()

    def _cycle_resolution(self):
        """Selecciona la siguiente resolución disponible."""

        if self.game.fullscreen:
            return

        self.resolution_index = (
            self.resolution_index + 1
        ) % len(self.resolutions)

        width, height = self.resolutions[
            self.resolution_index
        ]

        self.game.set_windowed_resolution(
            width,
            height,
        )

        self._update_layout()
        self._refresh_labels()

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

        if event.type == pygame.VIDEORESIZE:
            self._update_layout()

        for button in self.buttons:
            button.handle_event(event)

    def draw(self, screen):
        colors = self.theme_manager.colors

        screen.fill(colors["background"])

        pygame.draw.rect(
            screen,
            colors["panel"],
            self.panel_rect,
            border_radius=18,
        )

        pygame.draw.rect(
            screen,
            colors["accent"],
            self.panel_rect,
            width=3,
            border_radius=18,
        )

        title = self.title_font.render(
            "CONFIGURACIÓN",
            True,
            colors["gold"],
        )

        screen.blit(
            title,
            title.get_rect(
                center=(
                    self.panel_rect.centerx,
                    self.panel_rect.y + 95,
                )
            ),
        )

        description = self.info_font.render(
            "Personaliza la apariencia y la pantalla",
            True,
            colors["secondary_text"],
        )

        screen.blit(
            description,
            description.get_rect(
                center=(
                    self.panel_rect.centerx,
                    self.panel_rect.y + 150,
                )
            ),
        )

        for button in self.buttons:
            button.background = colors["panel"]
            button.hover_color = colors["accent"]
            button.text_color = colors["text"]
            button.border_color = colors["accent"]

            button.draw(screen)
