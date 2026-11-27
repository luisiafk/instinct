from typing import ClassVar

import pygame


class BiomeRenderer:
    """Representa visualmente los terrenos del mundo."""

    # Colores provisionales mientras no estén disponibles los tiles.
    TERRAIN_COLORS: ClassVar[dict[str, tuple[int, int, int]]] = {
        "grass": (83, 142, 76),
        "desert": (211, 178, 112),
        "sand": (211, 178, 112),
        "water": (55, 112, 166),
        "mountain": (112, 112, 120),
        "rock": (112, 112, 120),
        "swamp": (83, 112, 83),
        "plains": (148, 166, 91),
        "forest": (48, 105, 63),
        "snow": (220, 225, 230),
    }

    DEFAULT_COLOR = (105, 105, 105)

    def __init__(self, asset_loader=None):
        self.asset_loader = asset_loader
        self.terrain_images = {}
        self.shore_images = {}

    def get_terrain_color(self, terrain):
        """Obtiene el color provisional correspondiente al terreno."""

        name = terrain.name.lower()
        return self.TERRAIN_COLORS.get(name, self.DEFAULT_COLOR)

    def get_terrain_image(self, terrain):
        """Obtiene la imagen del terreno, si está disponible."""

        if self.asset_loader is None:
            return None

        name = terrain.name

        if name not in self.terrain_images:
            image = self.asset_loader.load_terrain(name)
            self.terrain_images[name] = image

        return self.terrain_images[name]

    def draw_tile(self, screen, tile, rect):
        """Dibuja el terreno de una casilla."""

        terrain = tile.terrain
        image = self.get_terrain_image(terrain)

        if image is not None:
            if image.get_size() != rect.size:
                image = pygame.transform.scale(image, rect.size)

            screen.blit(image, rect)
        else:
            pygame.draw.rect(
                screen,
                self.get_terrain_color(terrain),
                rect,
            )

    def draw_shore(self, screen, world, x, y, rect):
        """Dibuja una franja de orilla dentro de los límites del agua."""

        # Cada dirección indica dónde está la tierra y qué sprite
        # contiene la transición correcta entre tierra y agua.
        neighbors = {
            "north": ((x, y - 1), "shore_south_edge"),
            "south": ((x, y + 1), "shore_north_edge"),
            "east": ((x + 1, y), "shore_east_edge"),
            "west": ((x - 1, y), "shore_west_edge"),
        }

        if self.asset_loader is None:
            return

        # La franja ocupa aproximadamente una quinta parte del tile.
        # Así conserva el detalle de la orilla sin tapar demasiado agua.
        band_size = max(2, min(rect.width, rect.height) // 5)

        for direction, (position, sprite_name) in neighbors.items():
            nx, ny = position

            if not world.in_bounds(nx, ny):
                continue

            neighbor = world.get_tile(nx, ny)

            # Solo necesitamos una transición cuando al otro lado hay tierra.
            if (
                neighbor is None
                or neighbor.terrain.name.lower() == "water"
            ):
                continue

            cache_key = (sprite_name, rect.size, direction)

            if cache_key not in self.shore_images:
                image = self.asset_loader.load_image(
                    f"biomes/{sprite_name}.png"
                )

                if image is None:
                    continue

                # Adaptamos el sprite al tamaño actual de la casilla.
                if image.get_size() != rect.size:
                    image = pygame.transform.scale(image, rect.size)

                # Recortamos solo la parte central, donde está dibujada
                # la transición irregular entre el agua y la tierra.
                if direction in ("north", "south"):
                    source_rect = pygame.Rect(
                        0,
                        (rect.height - band_size) // 2,
                        rect.width,
                        band_size,
                    )
                else:
                    source_rect = pygame.Rect(
                        (rect.width - band_size) // 2,
                        0,
                        band_size,
                        rect.height,
                    )

                self.shore_images[cache_key] = (
                    image.subsurface(source_rect).copy()
                )

            shore = self.shore_images[cache_key]

            # Colocamos la franja justo en el borde que toca la tierra.
            if direction == "north":
                destination = (rect.left, rect.top)
            elif direction == "south":
                destination = (
                    rect.left,
                    rect.bottom - band_size,
                )
            elif direction == "east":
                destination = (
                    rect.right - band_size,
                    rect.top,
                )
            else:
                destination = (rect.left, rect.top)

            screen.blit(shore, destination)