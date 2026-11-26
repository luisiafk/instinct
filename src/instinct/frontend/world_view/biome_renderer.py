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
        """Dibuja la transición del agua hacia los terrenos vecinos."""

        if self.asset_loader is None:
            return

        # Buscamos las casillas de tierra que rodean esta casilla de agua.
        neighbors = {
            "north": (x, y - 1),
            "south": (x, y + 1),
            "east": (x + 1, y),
            "west": (x - 1, y),
        }

        land_neighbors = []

        for direction, (nx, ny) in neighbors.items():
            if not world.in_bounds(nx, ny):
                continue

            neighbor = world.get_tile(nx, ny)

            if (
                neighbor is not None
                and neighbor.terrain.name.lower() != "water"
            ):
                land_neighbors.append(direction)

        # Por ahora aplicamos una pieza recta solo cuando hay un único
        # lado de tierra. Así evitamos superponer transiciones incompatibles.
        if len(land_neighbors) != 1:
            return

        # El nombre indica hacia dónde queda orientada la parte de agua.
        sprite_names = {
            "north": "shore_north_edge",
            "south": "shore_south_edge",
            "east": "shore_east_edge",
            "west": "shore_west_edge",
        }

        # La orilla se encuentra en el lado contrario al terreno vecino.
        opposite = {
            "north": "south",
            "south": "north",
            "east": "west",
            "west": "east",
        }

        sprite_name = sprite_names[opposite[land_neighbors[0]]]
        cache_key = (sprite_name, rect.size)

        if cache_key not in self.shore_images:
            image = self.asset_loader.load_image(
                f"biomes/{sprite_name}.png"
            )

            if image is None:
                return

            if image.get_size() != rect.size:
                image = pygame.transform.scale(image, rect.size)

            self.shore_images[cache_key] = image

        screen.blit(self.shore_images[cache_key], rect)