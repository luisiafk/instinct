from pathlib import Path
from copy import deepcopy
import random

import pygame

from instinct.frontend.scenes.base_scene import BaseScene
from instinct.frontend.settings import DEFAULT_TILE_SIZE

from instinct.loaders.resource_manager import ResourceManager
from instinct.engine.simulation import Simulation

from instinct.frontend.core.simulation_controller import (
    SimulationController,
)

from instinct.frontend.menu.asset_loader import AssetLoader

from instinct.frontend.world_view.camera import Camera
from instinct.frontend.world_view.world_renderer import WorldRenderer
from instinct.frontend.world_view.creature_renderer import CreatureRenderer
from instinct.frontend.animation.animation_controller import AnimationController
from instinct.frontend.adapters.event_adapter import EventAdapter
from instinct.frontend.world_view.selection import Selection

from instinct.frontend.interface.theme_manager import ThemeManager
from instinct.frontend.interface.top_bar import TopBar
from instinct.frontend.interface.creature_panel import CreaturePanel
from instinct.frontend.interface.event_panel import EventPanel
from instinct.frontend.interface.simulation_controls import SimulationControls
from instinct.frontend.interface.tile_info_panel import TileInfoPanel

class SimulationScene(BaseScene):
    """Escena principal de visualización y control del mundo."""

    def __init__(self, game, resource_manager=None, map_name=None, creature_counts=None):
        super().__init__(game)

        self.resource_manager = resource_manager
        self.selected_map_name = map_name
        self.creature_counts = creature_counts or {}

        self.resource_manager = None
        self.simulation = None
        self.controller = None

        self.asset_loader = AssetLoader()

        self.world_renderer = WorldRenderer(
            asset_loader=self.asset_loader,
            show_grid=True,
        )

        self.animation_controller = AnimationController()
        self.event_adapter = None

        self.creature_renderer = CreatureRenderer(
            self.asset_loader,
            animation_controller=self.animation_controller,
        )

        self.selection = Selection()

        self.camera = None
        self.world = None

        self.map_name = None
        self.error_message = None

        self.dragging = False
        self.last_mouse_position = None

        # Componentes del HUD.
        self.theme_manager = ThemeManager()
        self.top_bar = TopBar(self.theme_manager)
        self.creature_panel = CreaturePanel()
        self.event_panel = None
        self.simulation_controls = None
        self.tile_info_panel = TileInfoPanel()

        self._load_resources()
        self._update_layout()

    def _load_resources(self):
        """Carga recursos si es necesario y prepara el mapa seleccionado."""

        if self.resource_manager is None:
            project_root = Path(__file__).resolve().parents[4]
            resources_path = project_root / "resources"

            self.resource_manager = ResourceManager(
                resource_dir=resources_path,
            )

            self.resource_manager.load_all()

        if not self.resource_manager.maps:
            self.error_message = (
                "No hay mapas disponibles para iniciar la simulación."
            )
            return

        map_name = self.selected_map_name

        if map_name not in self.resource_manager.maps:
            self.error_message = (
                f"No se encontró el mapa '{map_name}'."
            )
            return

        self.map_name = map_name
        self._load_map(map_name)

    def _load_map(self, map_name):
        """Inicializa una simulación utilizando un mapa existente."""

        world = self.resource_manager.get_map(map_name)

        if world is None:
            self.error_message = (
                f"No se encontró el mapa '{map_name}'."
            )
            return

        self.world = deepcopy(world)

        # Colocar las criaturas antes de iniciar la simulación.
        self._place_initial_creatures()

        self.simulation = Simulation(self.world)

        self.controller = SimulationController(
            simulation=self.simulation,
        )

        self.event_adapter = EventAdapter(
            self.simulation.action_event_log,
            self.animation_controller,
        )

        screen_width, screen_height = self.game.screen.get_size()

        self.camera = Camera(
            viewport=pygame.Rect(0, 0, screen_width, screen_height),
            world_width=self.world.width,
            world_height=self.world.height,
            tile_size=DEFAULT_TILE_SIZE,
        )

        self.world_renderer.set_world(self.world)
        self.world_renderer.set_camera(self.camera)

        self.selection.clear()
        self.error_message = None

    def _place_initial_creatures(self):
        """Coloca la población configurada por el usuario."""

        for creature_name, count in self.creature_counts.items():
            for _ in range(count):
                self._place_creature_randomly(creature_name)

    def _place_creature_randomly(self, creature_name):
        """Crea una criatura y la coloca en una casilla libre aleatoria."""

        creature = self.resource_manager.create_creature(creature_name)

        if creature is None:
            print(
                f"No se encontró la plantilla de {creature_name}."
            )
            return

        available_positions = [
            (x, y)
            for y in range(self.world.height)
            for x in range(self.world.width)
            if not self.world.get_tile(x, y).is_occupied
        ]

        if not available_positions:
            print(
                f"No hay casillas libres para colocar a {creature_name}."
            )
            return

        x, y = random.choice(available_positions)

        self.world.place_creature(creature, x, y)

        print(
            f"{creature_name} colocado aleatoriamente en ({x}, {y})."
        )

    def _update_layout(self):
        """Calcula las áreas del mapa y los paneles del HUD."""

        screen_width, screen_height = self.game.screen.get_size()

        margin = 20
        gap = 14

        left_width = min(
            250,
            max(150, int(screen_width * 0.16)),
        )

        right_width = min(
            310,
            max(190, int(screen_width * 0.20)),
        )

        panel_top = 92
        bottom_height = 94

        panel_height = screen_height - panel_top - margin

        left_rect = pygame.Rect(
            margin,
            panel_top,
            left_width,
            panel_height,
        )

        right_rect = pygame.Rect(
            screen_width - margin - right_width,
            panel_top,
            right_width,
            panel_height,
        )

        viewport_x = left_rect.right + gap
        viewport_y = panel_top

        viewport_right = right_rect.left - gap
        viewport_bottom = screen_height - bottom_height - margin

        viewport_width = max(120, viewport_right - viewport_x)
        viewport_height = max(120, viewport_bottom - viewport_y)

        viewport = pygame.Rect(
            viewport_x,
            viewport_y,
            viewport_width,
            viewport_height,
        )

        self.left_panel_rect = left_rect
        self.right_panel_rect = right_rect

        if self.camera is not None:
            self.camera.set_viewport(viewport)

        if self.event_panel is None:
            self.event_panel = EventPanel(
                right_rect,
                self.theme_manager,
            )
        else:
            self.event_panel.set_rect(right_rect)

        controls_rect = pygame.Rect(
            viewport.x,
            screen_height - bottom_height + 5,
            viewport.width,
            bottom_height - 5,
        )

        if self.controller is not None:
            if self.simulation_controls is None:
                self.simulation_controls = SimulationControls(
                    controls_rect,
                    self.controller,
                    self.theme_manager,
                )
            else:
                self.simulation_controls.set_rect(controls_rect)

    def handle_event(self, event):

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                from instinct.frontend.scenes.main_menu import MainMenu

                self.game.scene_manager.change_scene(
                    MainMenu(self.game)
                )
                return

            if self.controller is None:
                return

            if event.key == pygame.K_SPACE:
                self.controller.toggle_pause()

            elif event.key == pygame.K_PERIOD:
                self.controller.step()
                self._process_action_events()

            elif event.key == pygame.K_RIGHTBRACKET:
                self.controller.increase_speed()

            elif event.key == pygame.K_LEFTBRACKET:
                self.controller.decrease_speed()

            elif event.key == pygame.K_g:
                self.world_renderer.toggle_grid()

            return

        if self.simulation_controls is not None:
            if self.simulation_controls.handle_event(event):
                return

        if self.event_panel is not None:
            self.event_panel.handle_event(event)

        if self.camera is None:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:
                if self.camera.viewport.collidepoint(event.pos):
                    self.selection.handle_click(
                        world=self.world,
                        camera=self.camera,
                        mouse_position=event.pos,
                        shift=bool(
                            getattr(event, "mod", 0) & pygame.KMOD_SHIFT
                        ),
                    )

            elif event.button == 2:
                if self.camera.viewport.collidepoint(event.pos):
                    self.dragging = True
                    self.last_mouse_position = event.pos

            elif event.button == 4:
                if self.camera.viewport.collidepoint(event.pos):
                    self.camera.zoom_in(event.pos)

            elif event.button == 5:
                if self.camera.viewport.collidepoint(event.pos):
                    self.camera.zoom_out(event.pos)

        elif event.type == pygame.MOUSEBUTTONUP:

            if event.button == 2:
                self.dragging = False
                self.last_mouse_position = None

        elif event.type == pygame.MOUSEMOTION:

            if self.dragging and self.camera is not None:
                current_position = event.pos

                dx = (
                    current_position[0]
                    - self.last_mouse_position[0]
                )

                dy = (
                    current_position[1]
                    - self.last_mouse_position[1]
                )

                self.camera.pan(dx, dy)
                self.last_mouse_position = current_position

        elif event.type == pygame.MOUSEWHEEL:

            mouse_position = getattr(
                event,
                "pos",
                pygame.mouse.get_pos(),
            )

            if self.camera.viewport.collidepoint(mouse_position):
                if event.y > 0:
                    self.camera.zoom_in(mouse_position)

                elif event.y < 0:
                    self.camera.zoom_out(mouse_position)

        elif event.type == pygame.VIDEORESIZE:
            self._update_layout()

    def _process_action_events(self):
        """Procesa los eventos nuevos del motor para las animaciones."""

        if self.event_adapter is not None:
            self.event_adapter.process_new_events()

    def _update_camera_follow(self):
        """Centra la cámara en la última criatura seleccionada que siga viva."""

        if self.camera is None or self.world is None:
            return

        selected = self.selection.get_selected_creatures()

        if not selected:
            return

        living_creatures = {
            id(tile.creature)
            for row in self.world.tiles
            for tile in row
            if tile.creature is not None
        }

        target = next(
            (
                creature
                for creature in reversed(selected)
                if id(creature) in living_creatures
            ),
            None,
        )

        if target is None:
            return

        visual_x, visual_y = (
            self.animation_controller.get_visual_position(target)
        )

        self.camera.x = (
            visual_x + 0.5
        ) * self.camera.tile_size

        self.camera.y = (
            visual_y + 0.5
        ) * self.camera.tile_size

    def update(self, delta_time):
        """Actualiza simulación, acontecimientos, animaciones y cámara."""

        if self.controller is not None:
            self.controller.update(delta_time)

        self._process_action_events()

        self.creature_renderer.update(delta_time)

        self._update_camera_follow()

        if self.event_panel is not None and self.simulation is not None:
            self.event_panel.set_events(
                self.simulation.event_log.events
            )

    def draw(self, screen):

        colors = self.theme_manager.colors
        screen.fill(colors["background"])

        if self.error_message is not None:
            self._draw_error(screen)
            return

        if self.world is None:
            return

        self.world_renderer.draw(screen)
        self._draw_creatures(screen)

        self.selection.draw(
            screen,
            self.camera,
        )

        self._draw_interface(screen)

    def _draw_creatures(self, screen):
        """Dibuja criaturas vivas y animaciones de muerte."""

        start_x, start_y, end_x, end_y = (
            self.camera.get_visible_tiles()
        )

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):

                tile = self.world.get_tile(x, y)

                if tile is None or tile.creature is None:
                    continue

                self.creature_renderer.draw_creature(
                    screen,
                    tile.creature,
                    self.camera,
                )

        self.creature_renderer.draw_death_animations(
            screen,
            self.camera,
        )

    def _draw_interface(self, screen):
        """Dibuja todos los componentes del HUD."""

        colors = self.theme_manager.colors

        if self.controller is not None:
            self.top_bar.draw(
                screen,
                self.map_name,
                self.controller.tick,
                self.controller.paused,
                self.controller.speed,
            )

        selected_creatures = (
            self.selection.get_selected_creatures()
        )

        if selected_creatures:
            self.creature_panel.draw(
                screen,
                self.left_panel_rect,
                selected_creatures,
                colors,
            )
        else:
            selected_tile = self.selection.get_selected_tile()
            tile = None

            if selected_tile is not None:
                tile_x, tile_y = selected_tile
                tile = self.world.get_tile(tile_x, tile_y)

            self.tile_info_panel.draw(
                screen,
                self.left_panel_rect,
                tile,
                selected_tile,
                colors,
            )

        if self.event_panel is not None:
            self.event_panel.draw(screen)

        if self.simulation_controls is not None:
            self.simulation_controls.draw(screen)

    def _draw_error(self, screen):

        colors = self.theme_manager.colors

        title_font = pygame.font.Font(None, 42)
        info_font = pygame.font.Font(None, 28)

        title = title_font.render(
            "No se pudo iniciar el mundo",
            True,
            colors["gold"],
        )

        message = info_font.render(
            self.error_message,
            True,
            colors["text"],
        )

        screen.blit(
            title,
            title.get_rect(
                center=(screen.get_width() // 2, 450)
            ),
        )

        screen.blit(
            message,
            message.get_rect(
                center=(screen.get_width() // 2, 510)
            ),
        )

        hint = info_font.render(
            "Pulsa ESC para volver al menú",
            True,
            colors["secondary_text"],
        )

        screen.blit(
            hint,
            hint.get_rect(
                center=(screen.get_width() // 2, 580)
            ),
        )
