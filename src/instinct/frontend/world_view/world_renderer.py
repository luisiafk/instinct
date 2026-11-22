import pygame

from instinct.frontend.world_view.biome_renderer import BiomeRenderer
from instinct.frontend.world_view.grid_renderer import GridRenderer
from instinct.frontend.world_view.object_renderer import ObjectRenderer
from instinct.frontend.world_view.building_renderer import BuildingRenderer

class WorldRenderer:
    """Coordina la representación visual del mundo."""

    BACKGROUND_COLOR = (17, 22, 41)

    def __init__(
        self,
        asset_loader=None,
        show_grid=True,
    ):
        self.biome_renderer = BiomeRenderer(asset_loader)
        self.object_renderer = ObjectRenderer(asset_loader)
        self.building_renderer = BuildingRenderer(asset_loader)
        self.grid_renderer = GridRenderer(enabled=show_grid)
        self.world = None
        self.camera = None

    def set_world(self, world):
        """Asigna el mundo que se va a representar."""

        self.world = world
        self.building_renderer.clear_cache()

    def set_camera(self, camera):
        """Asigna la cámara utilizada para visualizar el mundo."""

        self.camera = camera

    def draw(self, screen):
        """Dibuja el mundo dentro del área visible de la cámara."""

        if self.world is None or self.camera is None:
            return

        viewport = self.camera.viewport

        previous_clip = screen.get_clip()
        screen.set_clip(viewport)

        pygame.draw.rect(
            screen,
            self.BACKGROUND_COLOR,
            viewport,
        )

        start_x, start_y, end_x, end_y = (
            self.camera.get_visible_tiles()
        )

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile = self.world.get_tile(x, y)

                if tile is None:
                    continue

                rect = self.camera.get_tile_rect(x, y)

                self.biome_renderer.draw_tile(
                    screen,
                    tile,
                    rect,
                )

                self.object_renderer.draw_object(
                    screen,
                    tile.object,
                    rect,
                )

        self.building_renderer.draw_world(
            screen,
            self.world,
            self.camera,
        )

        self.grid_renderer.draw(screen, self.camera)

        screen.set_clip(previous_clip)

    def toggle_grid(self):
        """Activa o desactiva la cuadrícula."""

        self.grid_renderer.toggle()

    def set_grid_visible(self, visible: bool):
        self.grid_renderer.set_enabled(visible)

    def set_asset_loader(self, asset_loader):
        """Actualiza el cargador de recursos gráficos."""

        self.biome_renderer.asset_loader = asset_loader
        self.biome_renderer.terrain_images.clear()

        self.object_renderer.asset_loader = asset_loader
        self.object_renderer.object_images.clear()

        self.building_renderer.asset_loader = asset_loader
        self.building_renderer.clear_cache()
