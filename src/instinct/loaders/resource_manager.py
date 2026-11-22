from pathlib import Path

from instinct.loaders.creature_loader import CreatureLoader
from instinct.loaders.map_loader import MapLoader
from instinct.loaders.object_loader import ObjectLoader
from instinct.loaders.terrain_loader import TerrainLoader
from instinct.loaders.building_loader import BuildingLoader
from instinct.world.entities import Creature, Terrain, WorldObject, Building
from instinct.world.world_grid import WorldGrid


class ResourceManager:
    """Coordina la carga de todos los recursos de Instinct."""

    def __init__(self, resource_dir: str | Path = "resources"):
        self.resource_dir = Path(resource_dir)

        self.terrains: dict[str, Terrain] = {}
        self.objects: dict[str, WorldObject] = {}
        self.buildings: dict[str, Building] = {}
        self.maps: dict[str, WorldGrid] = {}
        self.creatures: dict[str, Creature] = {}

        self.errors: list[str] = []

        self.terrain_loader = TerrainLoader()
        self.object_loader = ObjectLoader()
        self.building_loader = BuildingLoader()
        self.map_loader = MapLoader()
        self.creature_loader = CreatureLoader()


    def load_all(self) -> None:
        """Carga todos los recursos en el orden establecido."""

        self.errors.clear()

        self.terrains.clear()
        self.objects.clear()
        self.buildings.clear()
        self.maps.clear()
        self.creatures.clear()

        self._load_terrains()
        self._load_objects()
        self._load_buildings()
        self._validate_base_resources()
        self._load_maps()
        self._load_creatures()

    def _load_terrains(self) -> None:
        directory = self.resource_dir / "terrains"

        for filepath in self._get_files(directory, "*.te"):
            try:
                terrain = self.terrain_loader.load_file(filepath)
                self._register_terrain(terrain, filepath)
            except (ValueError, TypeError) as error:
                self._record_error(error)

    def _load_objects(self) -> None:
        directory = self.resource_dir / "objects"

        for filepath in self._get_files(directory, "*.ob"):
            try:
                obj = self.object_loader.load_file(filepath)
                self._register_object(obj, filepath)
            except (ValueError, TypeError) as error:
                self._record_error(error)

    def _load_buildings(self) -> None:
        directory = self.resource_dir / "buildings"

        for filepath in self._get_files(directory, "*.bld"):
            try:
                building = self.building_loader.load_file(filepath)

                if building.name in self.buildings:
                    raise ValueError(
                        f"El edificio '{building.name}' está duplicado "
                        f"en '{filepath}'."
                    )

                self._validate_unique_char(building.char, filepath)

                self.buildings[building.name] = building

            except (ValueError, TypeError) as error:
                self._record_error(error)

    def _load_maps(self) -> None:
        directory = self.resource_dir / "maps"

        if not self.terrains:
            self._record_error(
                "No se pueden cargar mapas porque no hay terrenos disponibles."
            )
            return

        terrains = list(self.terrains.values())
        objects = list(self.objects.values())

        for filepath in self._get_files(directory, "*.map"):
            try:
                map_name, world = self.map_loader.load_file(
                    filepath,
                    terrains,
                    objects,
                    list(self.buildings.values()),
                )

                if map_name in self.maps:
                    raise ValueError(
                        f"Ya existe un mapa registrado con el nombre '{map_name}'."
                    )

                self.maps[map_name] = world

            except (ValueError, TypeError, IndexError) as error:
                self._record_error(error)

    def _load_creatures(self) -> None:
        directory = self.resource_dir / "creatures"

        for filepath in self._get_files(directory, "*.ins"):
            try:
                creature = self.creature_loader.load_file(filepath)

                if creature.name in self.creatures:
                    raise ValueError(
                        f"Ya existe una criatura registrada "
                        f"con el nombre '{creature.name}'."
                    )

                self.creatures[creature.name] = creature

            except (ValueError, TypeError) as error:
                self._record_error(error)

    def _register_terrain(self, terrain, filepath: Path) -> None:
        if terrain.name in self.terrains:
            raise ValueError(
                f"El terreno '{terrain.name}' está duplicado en '{filepath}'."
            )

        self._validate_unique_char(terrain.char, filepath)

        self.terrains[terrain.name] = terrain

    def _register_object(self, obj, filepath: Path) -> None:
        if obj.name in self.objects:
            raise ValueError(
                f"El objeto '{obj.name}' está duplicado en '{filepath}'."
            )

        if obj.char in {
            terrain.char for terrain in self.terrains.values()
        }:
            raise ValueError(
                f"El carácter '{obj.char}' del objeto '{obj.name}' "
                "ya está asignado a un terreno."
            )

        self._validate_unique_char(obj.char, filepath)

        self.objects[obj.name] = obj

    def _validate_unique_char(self, char: str, filepath: Path) -> None:
        for terrain in self.terrains.values():
            if terrain.char == char:
                raise ValueError(
                    f"El carácter '{char}' ya pertenece "
                    f"al terreno '{terrain.name}'. Archivo: '{filepath}'."
                )

        for obj in self.objects.values():
            if obj.char == char:
                raise ValueError(
                    f"El carácter '{char}' ya pertenece "
                    f"al objeto '{obj.name}'. Archivo: '{filepath}'."
                )

        for building in self.buildings.values():
            if building.char == char:
                raise ValueError(
                    f"El carácter '{char}' ya pertenece "
                    f"al edificio '{building.name}'. Archivo: '{filepath}'."
                )

    def _validate_base_resources(self) -> None:
        grass = self.terrains.get("Grass")

        if grass is None:
            self._record_error(
                "Falta el terreno obligatorio 'Grass'."
            )
        elif (
            grass.char != "."
            or grass.resource_max != 100
            or grass.regen != 2
        ):
            self._record_error(
                "El terreno obligatorio 'Grass' debe tener "
                "char '.', resource_max 100 y regen 2."
            )

        rock = self.objects.get("Rock")

        if rock is None:
            self._record_error(
                "Falta el objeto obligatorio 'Rock'."
            )
        elif rock.char != "#" or rock.resource_max != 100:
            self._record_error(
                "El objeto obligatorio 'Rock' debe tener "
                "char '#' y resource_max 100."
            )

    def _get_files(self, directory: Path, pattern: str) -> list[Path]:
        if not directory.is_dir():
            self._record_error(
                f"No existe el directorio de recursos '{directory}'."
            )
            return []

        return sorted(directory.glob(pattern))

    def _record_error(self, error: Exception | str) -> None:
        self.errors.append(str(error))

    def get_terrain(self, name: str):
        return self.terrains.get(name)

    def get_object(self, name: str):
        return self.objects.get(name)

    def get_building(self, name: str):
        return self.buildings.get(name)

    def get_map(self, name: str):
        return self.maps.get(name)

    def get_creature(self, name: str):
        return self.creatures.get(name)

    def create_creature(self, name: str):
        """Crea una instancia independiente de una criatura registrada."""

        creature_template = self.get_creature(name)

        if creature_template is None:
            return None

        filepath = (
            self.resource_dir
            / "creatures"
            / f"{name.lower()}.ins"
        )

        return self.creature_loader.load_file(filepath)
