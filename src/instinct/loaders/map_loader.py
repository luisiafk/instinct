from copy import deepcopy
from pathlib import Path

from instinct.world.entities import Building, Terrain, WorldObject
from instinct.world.world_grid import WorldGrid


class MapLoader:
    """Carga mapas .map y sus capas complementarias de edificios."""

    def load_file(
        self,
        filepath: str | Path,
        terrains: list[Terrain],
        objects: list[WorldObject],
        buildings: list[Building] | None = None,
    ) -> tuple[str, WorldGrid]:
        path = Path(filepath)

        try:
            content = path.read_text(encoding="utf-8")
        except FileNotFoundError as error:
            raise ValueError(
                f"No se encontró el archivo de mapa: '{path}'."
            ) from error
        except UnicodeDecodeError as error:
            raise ValueError(
                f"El archivo de mapa '{path}' no contiene texto UTF-8 válido."
            ) from error
        except OSError as error:
            raise ValueError(
                f"No se pudo leer el archivo de mapa '{path}': {error}."
            ) from error

        building_path = path.with_suffix(".bmap")
        building_content = None

        if building_path.exists():
            try:
                building_content = building_path.read_text(encoding="utf-8")
            except UnicodeDecodeError as error:
                raise ValueError(
                    f"El archivo de edificios '{building_path}' "
                    "no contiene texto UTF-8 válido."
                ) from error
            except OSError as error:
                raise ValueError(
                    f"No se pudo leer el archivo de edificios "
                    f"'{building_path}': {error}."
                ) from error

        return self.load_string(
            content,
            terrains,
            objects,
            str(path),
            buildings,
            building_content,
            str(building_path),
        )

    def load_string(
        self,
        content: str,
        terrains: list[Terrain],
        objects: list[WorldObject],
        source: str = "<memoria>",
        buildings: list[Building] | None = None,
        building_content: str | None = None,
        building_source: str = "<capa de edificios>",
    ) -> tuple[str, WorldGrid]:

        if not isinstance(content, str):
            raise TypeError("El contenido del mapa debe ser texto.")

        if not terrains:
            raise ValueError(
                "No se puede cargar un mapa sin terrenos disponibles."
            )

        lines = content.splitlines()

        if len(lines) < 2:
            self._error(
                source, 1,
                "El mapa debe tener un nombre y al menos una fila."
            )

        map_name = lines[0].strip()

        if not map_name:
            self._error(source, 1, "El mapa debe tener un nombre.")

        rows = lines[1:]
        width = len(rows[0])

        if width == 0:
            self._error(
                source, 2,
                "Las filas del mapa no pueden estar vacías."
            )

        for line_number, row in enumerate(rows, start=2):
            if len(row) != width:
                self._error(
                    source,
                    line_number,
                    f"La fila tiene {len(row)} caracteres; "
                    f"se esperaban {width}.",
                )

        terrain_by_char = {}
        object_by_char = {}

        for terrain in terrains:
            if terrain.char in terrain_by_char:
                raise ValueError(
                    f"El carácter '{terrain.char}' está asignado "
                    "a más de un terreno."
                )
            terrain_by_char[terrain.char] = terrain

        for obj in objects:
            if obj.char in object_by_char:
                raise ValueError(
                    f"El carácter '{obj.char}' está asignado "
                    "a más de un objeto."
                )

            if obj.char in terrain_by_char:
                raise ValueError(
                    f"El carácter '{obj.char}' está asignado "
                    "a un terreno y a un objeto."
                )

            object_by_char[obj.char] = obj

        default_terrain = terrains[0]

        world = WorldGrid(
            width=width,
            height=len(rows),
            default_terrain=default_terrain,
        )

        for y, row in enumerate(rows):
            for x, char in enumerate(row):
                tile = world.get_tile(x, y)

                if char in terrain_by_char:
                    tile.terrain = deepcopy(terrain_by_char[char])

                elif char in object_by_char:
                    tile.terrain = deepcopy(default_terrain)
                    world.place_object(
                        deepcopy(object_by_char[char]), x, y
                    )

                else:
                    self._error(
                        source,
                        y + 2,
                        f"El carácter '{char}' no corresponde "
                        "a ningún terreno ni objeto cargado.",
                    )

        if building_content is not None:
            self._load_building_layer(
                building_content,
                building_source,
                buildings or [],
                world,
            )

        return map_name, world

    def _load_building_layer(
        self,
        content: str,
        source: str,
        buildings: list[Building],
        world: WorldGrid,
    ) -> None:
        if not buildings:
            self._error(
                source, 1,
                "La capa contiene edificios, pero no hay "
                "definiciones de edificios disponibles."
            )

        rows = content.splitlines()

        if len(rows) != world.height:
            self._error(
                source,
                len(rows) + 1,
                f"La capa tiene {len(rows)} filas; "
                f"el mapa tiene {world.height}.",
            )

        for line_number, row in enumerate(rows, start=1):
            if len(row) != world.width:
                self._error(
                    source,
                    line_number,
                    f"La fila tiene {len(row)} caracteres; "
                    f"se esperaban {world.width}.",
                )

        building_by_char = {}

        for building in buildings:
            if building.char in building_by_char:
                raise ValueError(
                    f"El carácter '{building.char}' está asignado "
                    "a más de un edificio."
                )

            building_by_char[building.char] = building

        visited = set()

        for y, row in enumerate(rows):
            for x, char in enumerate(row):

                if char == "." or (x, y) in visited:
                    continue

                building_template = building_by_char.get(char)

                if building_template is None:
                    self._error(
                        source,
                        y + 1,
                        f"El carácter '{char}' no corresponde "
                        "a ningún edificio cargado.",
                    )

                width = building_template.width
                height = building_template.height

                # Validar que toda la huella del edificio
                # esté representada por su carácter.
                for offset_y in range(height):
                    for offset_x in range(width):
                        target_x = x + offset_x
                        target_y = y + offset_y

                        if not world.in_bounds(target_x, target_y):
                            self._error(
                                source,
                                y + 1,
                                f"El edificio '{building_template.name}' "
                                "excede los límites del mapa.",
                            )

                        if rows[target_y][target_x] != char:
                            self._error(
                                source,
                                target_y + 1,
                                f"La huella del edificio "
                                f"'{building_template.name}' "
                                "está incompleta o es inválida.",
                            )

                        if (target_x, target_y) in visited:
                            self._error(
                                source,
                                target_y + 1,
                                "Dos edificios comparten una misma casilla.",
                            )

                # Registrar la huella para no procesar
                # sus caracteres como edificios independientes.
                for offset_y in range(height):
                    for offset_x in range(width):
                        visited.add((x + offset_x, y + offset_y))

                # Cada aparición crea una instancia independiente.
                building_instance = deepcopy(building_template)

                world.place_building(
                    building_instance,
                    x,
                    y,
                )

    @staticmethod
    def _error(source: str, line: int, message: str) -> None:
        raise ValueError(
            f"Error en '{source}', línea {line}: {message}"
        )
