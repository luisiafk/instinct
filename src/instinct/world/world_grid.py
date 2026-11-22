
"""
Representación del mundo de Instinct mediante una grilla rectangular.

La grilla almacena las casillas utilizando la convención:
    tiles[y][x]

Cada casilla posee su propio terreno y puede contener
un objeto, una criatura o formar parte de un edificio.
"""

from copy import deepcopy

from instinct.world.entities import Building, Creature, Terrain, WorldObject
from instinct.world.tile import Tile


class WorldGrid:
    """Grilla rectangular que representa el mundo de la simulación."""

    def __init__(
        self,
        width: int,
        height: int,
        default_terrain: Terrain,
    ) -> None:
        if not isinstance(width, int) or isinstance(width, bool):
            raise TypeError("El ancho del mundo debe ser un número entero.")

        if not isinstance(height, int) or isinstance(height, bool):
            raise TypeError("El alto del mundo debe ser un número entero.")

        if width <= 0 or height <= 0:
            raise ValueError("Las dimensiones del mundo deben ser positivas.")

        if not isinstance(default_terrain, Terrain):
            raise TypeError("El terreno predeterminado no es válido.")

        self.width = width
        self.height = height

        self.tiles: list[list[Tile]] = [
            [
                Tile(terrain=deepcopy(default_terrain))
                for _ in range(width)
            ]
            for _ in range(height)
        ]

    def in_bounds(self, x: int, y: int) -> bool:
        """Comprueba si una coordenada pertenece al mundo."""
        return (
            isinstance(x, int)
            and not isinstance(x, bool)
            and isinstance(y, int)
            and not isinstance(y, bool)
            and 0 <= x < self.width
            and 0 <= y < self.height
        )

    def get_tile(self, x: int, y: int) -> Tile:
        """Devuelve la casilla situada en las coordenadas indicadas."""
        if not self.in_bounds(x, y):
            raise IndexError(
                f"La posición ({x}, {y}) está fuera de los límites del mundo."
            )

        return self.tiles[y][x]

    def place_creature(self, creature: Creature, x: int, y: int) -> None:
        """Coloca una criatura en una casilla libre y transitable."""
        tile = self.get_tile(x, y)
        tile.set_creature(creature)

        creature.x = x
        creature.y = y

    def place_object(self, obj: WorldObject, x: int, y: int) -> None:
        """Coloca un objeto en una casilla libre."""
        tile = self.get_tile(x, y)
        tile.set_object(obj)

    def place_building(
        self,
        building: Building,
        x: int,
        y: int,
    ) -> None:
        """
        Coloca un edificio completo en el mundo.

        (x, y) representa la esquina superior izquierda de su huella lógica.
        Todas las casillas comparten la misma instancia del edificio.
        """
        if not isinstance(building, Building):
            raise TypeError("Solo se pueden colocar edificios válidos.")

        if not self.in_bounds(x, y):
            raise IndexError(
                f"La posición ({x}, {y}) está fuera de los límites del mundo."
            )

        if x + building.width > self.width or y + building.height > self.height:
            raise ValueError(
                f"El edificio '{building.name}' queda fuera de los límites "
                "del mundo."
            )

        # Evitar colocar dos veces la misma instancia.
        for row in self.tiles:
            for tile in row:
                if tile.building is building:
                    raise ValueError(
                        f"El edificio '{building.name}' ya está colocado."
                    )

        # Primera pasada: validar toda la huella sin modificar el mundo.
        footprint: list[tuple[Tile, int, int]] = []

        for offset_y in range(building.height):
            for offset_x in range(building.width):
                tile = self.tiles[y + offset_y][x + offset_x]

                if tile.has_building:
                    raise ValueError(
                        f"La huella del edificio '{building.name}' "
                        "se superpone con otro edificio."
                    )

                if tile.object is not None or tile.creature is not None:
                    raise ValueError(
                        f"La huella del edificio '{building.name}' "
                        "contiene un objeto o una criatura."
                    )

                footprint.append((tile, offset_x, offset_y))

        # Segunda pasada: colocar el edificio después de validar todo.
        for tile, offset_x, offset_y in footprint:
            tile.set_building(building, offset_x, offset_y)

        building.x = x
        building.y = y

    def remove_creature(self, x: int, y: int) -> Creature | None:
        """Retira y devuelve la criatura de una casilla."""
        return self.get_tile(x, y).remove_creature()

    def remove_object(self, x: int, y: int) -> WorldObject | None:
        """Retira y devuelve el objeto de una casilla."""
        return self.get_tile(x, y).remove_object()
