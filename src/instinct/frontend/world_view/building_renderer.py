
from pathlib import Path
import random

import pygame


class BuildingRenderer:
    """Representa visualmente los edificios del mundo."""

    def __init__(self, asset_loader=None):
        self.asset_loader = asset_loader

        # Una imagen seleccionada por cada instancia de edificio.
        self.building_images = {}

    def clear_cache(self):
        """Limpia las imágenes asociadas a las instancias anteriores."""
        self.building_images.clear()

    def _get_building_image(self, building):
        """Obtiene la imagen correspondiente a una instancia."""

        key = id(building)

        if key in self.building_images:
            return self.building_images[key]

        if self.asset_loader is None:
            return None

        asset_path = (
            self.asset_loader.assets_path
            / "buildings"
            / building.asset
        )

        if asset_path.is_dir():
            candidates = sorted(
                path
                for path in asset_path.iterdir()
                if path.is_file()
                and path.suffix.lower() == ".png"
            )

            if not candidates:
                print(
                    "No se encontraron imágenes PNG para el edificio "
                    f"'{building.name}' en '{asset_path}'."
                )
                self.building_images[key] = None
                return None

            selected_path = random.choice(candidates)

            relative_path = selected_path.relative_to(
                self.asset_loader.assets_path
            )

        else:
            relative_path = asset_path.relative_to(
                self.asset_loader.assets_path
            )

        image = self.asset_loader.load_image(relative_path)

        if image is None:
            self.building_images[key] = None
            return None

        self.building_images[key] = image

        return image

    def draw_building(self, screen, building, camera):
        """Dibuja un edificio respetando sus dimensiones visuales."""

        if building is None:
            return

        image = self._get_building_image(building)

        if image is None:
            return

        tile_size = camera.tile_size
        zoom = camera.zoom

        visual_width = building.visual_width
        visual_height = building.visual_height

        width = max(
            1,
            round(visual_width * tile_size * zoom),
        )

        height = max(
            1,
            round(visual_height * tile_size * zoom),
        )

        # Posición de la casilla de origen.
        origin_rect = camera.get_tile_rect(
            building.x,
            building.y,
        )

        # Alinear la imagen con la parte inferior de la huella lógica.
        logical_bottom = camera.get_tile_rect(
            building.x,
            building.y + building.height,
        ).bottom

        draw_rect = pygame.Rect(
            origin_rect.left,
            logical_bottom - height,
            width,
            height,
        )

        # Evitar escalar y dibujar imágenes fuera del viewport.
        if not draw_rect.colliderect(camera.viewport):
            return

        if image.get_size() != draw_rect.size:
            scaled_image = pygame.transform.scale(
                image,
                draw_rect.size,
            )
        else:
            scaled_image = image

        screen.blit(scaled_image, draw_rect)

    def draw_world(self, screen, world, camera):
        """Dibuja cada edificio una sola vez."""

        if world is None or camera is None:
            return

        for row in world.tiles:
            for tile in row:
                building = tile.building

                if building is None:
                    continue

                # Las demás casillas de la huella comparten
                # la instancia, pero no deben dibujarla otra vez.
                if tile.building_offset != (0, 0):
                    continue

                self.draw_building(
                    screen,
                    building,
                    camera,
                )
