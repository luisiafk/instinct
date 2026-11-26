
import json
import re

from datetime import datetime
from pathlib import Path


class WorldSaveManager:
    """Gestiona los archivos de guardado de las simulaciones."""

    SAVE_DIRECTORY = Path(__file__).resolve().parents[2] / "saves"

    @classmethod
    def save(
        cls,
        simulation,
        map_name: str,
        save_name: str,
        controller=None,
    ) -> Path:
        """Guarda el estado actual de una simulación."""

        if simulation is None or simulation.world is None:
            raise ValueError("No existe una simulación que guardar.")

        # Limpiamos el nombre para evitar rutas o caracteres inválidos.
        filename = re.sub(
            r"[^\w-]+",
            "_",
            save_name.strip(),
        ).strip("_")[:40]

        if not filename:
            raise ValueError("Introduce un nombre válido para el guardado.")

        cls.SAVE_DIRECTORY.mkdir(
            parents=True,
            exist_ok=True,
        )

        filepath = cls.SAVE_DIRECTORY / f"{filename}.json"

        if filepath.exists():
            raise FileExistsError(
                f"Ya existe un guardado llamado '{filename}'."
            )

        world = simulation.world
        buildings = []
        saved_buildings = set()
        tiles = []

        # Guardamos cada casilla y sus recursos actuales.
        for row in world.tiles:
            saved_row = []

            for tile in row:
                terrain_data = {
                    "name": tile.terrain.name,
                    "reserve": tile.terrain.reserve,
                }

                object_data = None

                if tile.object is not None:
                    object_data = {
                        "name": tile.object.name,
                        "reserve": tile.object.reserve,
                    }

                # Cada edificio se registra una sola vez, aunque ocupe
                # varias casillas de la cuadrícula.
                if (
                    tile.building is not None
                    and id(tile.building) not in saved_buildings
                ):
                    building = tile.building

                    buildings.append({
                        "name": building.name,
                        "x": building.x,
                        "y": building.y,
                    })

                    saved_buildings.add(id(building))

                saved_row.append({
                    "terrain": terrain_data,
                    "object": object_data,
                })

            tiles.append(saved_row)

        creatures = []

        # Guardamos las propiedades de cada criatura viva.
        for row in world.tiles:
            for tile in row:
                creature = tile.creature

                if creature is None:
                    continue

                creatures.append({
                    "name": creature.name,
                    "faction": creature.faction,
                    "health": creature.health,
                    "vision": creature.vision,
                    "lifespan": creature.lifespan,
                    "x": creature.x,
                    "y": creature.y,
                    "age": creature.age,
                    "max_health": creature.max_health,
                    "can_reproduce": creature.can_reproduce,
                    "execution": simulation.get_execution_state(
                        creature
                    ),
                })

        # El estado aleatorio también se conserva para poder mantener
        # la secuencia de decisiones de la simulación al restaurarla.
        data = {
            "format_version": 1,
            "name": filename,
            "map_name": map_name,
            "saved_at": datetime.now().astimezone().isoformat(),
            "tick": simulation.tick,
            "speed": (
                controller.speed
                if controller is not None
                else 1
            ),
            "rng_state": simulation.rng.getstate(),
            "world": {
                "width": world.width,
                "height": world.height,
                "tiles": tiles,
                "buildings": buildings,
                "creatures": creatures,
            },
        }

        # Escribimos primero en un temporal para no dejar un JSON
        # incompleto si la escritura se interrumpe.
        temporary_path = filepath.with_suffix(".tmp")

        try:
            temporary_path.write_text(
                json.dumps(
                    data,
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            temporary_path.replace(filepath)

        except OSError:
            temporary_path.unlink(missing_ok=True)
            raise

        return filepath

    @classmethod
    def list_saves(cls):
        """Devuelve los guardados ordenados del más reciente al más antiguo."""

        cls.SAVE_DIRECTORY.mkdir(parents=True, exist_ok=True)

        return sorted(
            cls.SAVE_DIRECTORY.glob("*.json"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )

    @classmethod
    def load(cls, filepath):
        """Lee un guardado y comprueba que pertenece a una versión compatible."""

        path = Path(filepath).resolve()

        if path.parent != cls.SAVE_DIRECTORY.resolve():
            raise ValueError("La ruta del guardado no es válida.")

        if not path.is_file() or path.suffix.lower() != ".json":
            raise ValueError("El archivo de guardado no existe.")

        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if data.get("format_version") != 1:
            raise ValueError(
                "La versión del archivo de guardado no es compatible."
            )

        required_fields = (
            "map_name",
            "tick",
            "rng_state",
            "world",
        )

        if any(field not in data for field in required_fields):
            raise ValueError("El archivo de guardado está incompleto.")

        return data