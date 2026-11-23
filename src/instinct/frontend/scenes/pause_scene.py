
import pygame

from instinct.frontend.scenes.base_scene import BaseScene
from instinct.frontend.interface.widgets.button import Button


class PauseScene(BaseScene):
    """Menú de pausa superpuesto a la simulación actual."""

    PANEL_COLOR = (30, 30, 51)
    BORDER_COLOR = (118, 84, 168)
    GOLD = (212, 174, 98)
    TEXT = (242, 239, 250)
    MUTED = (155, 150, 174)

    def __init__(self, game, simulation_scene):
        super().__init__(game)

        self.simulation_scene = simulation_scene

        self.title_font = pygame.font.Font(None, 64)
        self.info_font = pygame.font.Font(None, 28)

        self.panel_rect = pygame.Rect(0, 0, 0, 0)
        self.buttons = []

        self._create_buttons()
        self._update_layout()

    def _create_buttons(self):
        """Crea las opciones del menú de pausa."""

        self.buttons = [
            Button(
                (0, 0, 100, 50),
                "Reanudar",
                callback=self._resume,
                font_size=34,
            ),
            Button(
                (0, 0, 100, 50),
                "Avanzar un tick",
                callback=self._step,
                font_size=32,
            ),
            Button(
                (0, 0, 100, 50),
                "Reiniciar",
                callback=self._restart,
                font_size=32,
            ),
            Button(
                (0, 0, 100, 50),
                "Volver al menú",
                callback=self._return_to_menu,
                font_size=32,
            ),
            Button(
                (0, 0, 100, 50),
                "Salir",
                callback=self._quit,
                font_size=32,
            ),
        ]

    def _update_layout(self):
        """Adapta el menú al tamaño actual de la ventana."""

        width, height = self.game.screen.get_size()

        panel_width = min(520, width - 40)
        panel_height = min(620, height - 40)

        self.panel_rect = pygame.Rect(
            0,
            0,
            panel_width,
            panel_height,
        )

        self.panel_rect.center = (width // 2, height // 2)

        button_width = min(360, panel_width - 80)
        button_height = 58
        spacing = 16

        total_height = (
            len(self.buttons) * button_height
            + (len(self.buttons) - 1) * spacing
        )

        start_y = (
            self.panel_rect.centery
            + 15
            - total_height // 2
        )

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

    def _resume(self):
        """Reanuda la misma simulación."""

        controller = self.simulation_scene.controller

        if controller is not None:
            controller.play()

        self.game.scene_manager.change_scene(
            self.simulation_scene
        )

    def _step(self):
        """Ejecuta un único tick y regresa a la simulación pausada."""

        controller = self.simulation_scene.controller

        if controller is not None:
            controller.pause()
            controller.step()

            self.simulation_scene._process_action_events()

        self.game.scene_manager.change_scene(
            self.simulation_scene
        )

    def _restart(self):
        """Crea una simulación nueva con la configuración original."""

        from instinct.frontend.scenes.simulation_scene import (
            SimulationScene,
        )

        new_scene = SimulationScene(
            self.game,
            resource_manager=self.simulation_scene.resource_manager,
            map_name=self.simulation_scene.map_name,
            creature_counts=dict(
                self.simulation_scene.creature_counts
            ),
        )

        self.game.scene_manager.change_scene(new_scene)

    def _return_to_menu(self):
        """Regresa al menú principal."""

        from instinct.frontend.scenes.main_menu import MainMenu

        self.game.scene_manager.change_scene(
            MainMenu(self.game)
        )

    def _quit(self):
        """Cierra la aplicación."""

        self.game.quit()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._resume()
                return

        if event.type == pygame.VIDEORESIZE:
            self._update_layout()

        for button in self.buttons:
            button.handle_event(event)

    def draw(self, screen):
        # Dibujar la simulación conservando su estado visual.
        self.simulation_scene.draw(screen)

        # Oscurecer el fondo.
        overlay = pygame.Surface(
            screen.get_size(),
            pygame.SRCALPHA,
        )
        overlay.fill((5, 5, 15, 190))
        screen.blit(overlay, (0, 0))

        # Panel central.
        pygame.draw.rect(
            screen,
            self.PANEL_COLOR,
            self.panel_rect,
            border_radius=18,
        )

        pygame.draw.rect(
            screen,
            self.BORDER_COLOR,
            self.panel_rect,
            width=3,
            border_radius=18,
        )

        # Título.
        title = self.title_font.render(
            "PAUSA",
            True,
            self.GOLD,
        )

        screen.blit(
            title,
            title.get_rect(
                center=(
                    self.panel_rect.centerx,
                    self.panel_rect.y + 85,
                )
            ),
        )

        # Información del tick.
        controller = self.simulation_scene.controller
        tick = controller.tick if controller is not None else 0

        info = self.info_font.render(
            f"Simulación detenida · Tick {tick}",
            True,
            self.MUTED,
        )

        screen.blit(
            info,
            info.get_rect(
                center=(
                    self.panel_rect.centerx,
                    self.panel_rect.y + 135,
                )
            ),
        )

        # Botones.
        for button in self.buttons:
            button.draw(screen)
