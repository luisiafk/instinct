import random

from instinct.entities import Tile, Terrain, GameObject, Creature
from instinct.grid import WorldGrid

def generate_random_map_lines(width: int, height: int):
    map_rows = []
    for y in range(height):
        row = []
        for x in range(width):
            if x == 0 or x == width - 1 or y == 0 or y == height - 1:
                row.append('#')
            else:
                r = random.random()
                if r < 0.12:
                    row.append('#')
                elif r < 0.25:
                    row.append('T')
                else:
                    row.append('.')

        map_rows.append("".join(row))

    return map_rows


def parse_maps_rows_to_grid(map_rows: list[str], terrains_dict: dict, objects_dict: dict):
    height = len(map_rows)
    width = max(len(row) for row in map_rows)
    grid = WorldGrid(width=width, height=height)

    for y, row in enumerate(map_rows):
        for x, char in enumerate(row):
            if x >= width:
                break

            terrain = terrains_dict.get('.', terrains_dict.get('ground', Terrain(name="ground")))
            game_object = None

            if char in terrains_dict:
                terrain = terrains_dict[char]
            elif char in objects_dict:
                game_object = objects_dict[char]
            elif char == 'T':
                terrain = terrains_dict.get('T', Terrain(name="resource_terrain", regen_rate=10))
            elif char == '#':
                game_object = objects_dict.get('#', GameObject(name="Rock", walkable=False))

            grid.set_tile_terrain(x, y, terrain)
            if game_object:
                grid.set_tile_object(x, y, game_object)
    return grid

def populate_map_with_object(grid: WorldGrid, object_dict: dict, item_prob : float = 0.88):
    avialable_items = [
        obj for symbol, obj in object_dict.items()
        if len(symbol) == 1 and symbol not in ('#', '.', 'T', 'A', 'B')
    ]

    if not avialable_items:
        return

    for y in range(grid.height):
        for x in range(grid.width):
            tile = grid.get_tile(x, y)
            if tile and tile.creature is None and tile.game_object is None and tile.terrain.walkable:
                if random.random() < item_prob:
                    template_obj = random.choice(avialable_items)
                    new_object = GameObject(
                        name=template_obj.name,
                        symbol=template_obj.symbol,
                        walkable=template_obj.walkable,
                        reserve=template_obj.reserve,
                        destructible=template_obj.destructible
                    )
                    grid.set_tile_object(x, y, new_object)

def load_terrains(filepath: str) -> dict:
    """
    Lee un archivo de terrenos (.te) y devuelve un diccionario
    donde la clave es el símbolo o nombre y el valor es el objeto Terrain.
    Soporta formato por comas, dos puntos (:) o nombres simples.
    """
    terrains = {}

    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            clean_line = line.strip()

            # Ignorar líneas vacías o comentarios
            if not clean_line or clean_line.startswith('#') or clean_line.startswith('//'):
                continue

            # Soporte para formato separado por dos puntos (ej. . : 1 : 0 : 0)
            if ':' in clean_line:
                parts = [p.strip() for p in clean_line.split(':')]
                if len(parts) >= 4:
                    symbol = parts[0]
                    cost = int(parts[1])
                    walkable = int(parts[2]) == 0
                    health_mod = int(parts[3])  # Captura correcta del modificador de salud/daño

                    terrains[symbol] = Terrain(
                        name=f"Terrain_{symbol}",
                        walkable=walkable,
                        regen_rate=1 if symbol == 'T' else 0,
                        health_modifier=health_mod,
                        movement_cost=cost
                    )
            # Soporte para formato separado por comas
            elif ',' in clean_line:
                parts = [p.strip() for p in line.split(',')]
                name = parts[0]
                walkable = parts[1].lower() == 'true'
                regen_rate = float(parts[2])
                terrains[name] = Terrain(name=name, walkable=walkable, regen_rate=regen_rate)
            else:
                terrains[clean_line] = Terrain(name=clean_line)

    # Asegurar un terreno por defecto
    if '.' not in terrains and 'ground' not in terrains:
        terrains['.'] = Terrain(name="ground", walkable=True, regen_rate=1)

    return terrains


def load_objects(filepath: str) -> dict:
    """
    Lee un archivo .ob y devuelve un diccionario con las instancias de GameObject.
    Soporta formato por plecas (|), comas o nombres simples.
    """
    objects = {}

    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            clean_line = line.strip()

            # Ignorar líneas vacías o comentarios
            if not clean_line or clean_line.startswith('#') or clean_line.startswith('//'):
                continue

            # Soporte para formato separado por plecas (|)
            if '|' in clean_line:
                parts = [part.strip() for part in clean_line.split('|')]
                if len(parts) >= 6:
                    obj_id = parts[0]
                    name = parts[1]
                    symbol = parts[2]
                    value = int(parts[4])  # Capturar el valor numérico del recurso

                    objects[symbol] = GameObject(
                        name=name,
                        symbol=symbol,
                        walkable=True,
                        reserve=value,
                        destructible=True
                    )

                    objects[obj_id] = objects[symbol]
            # Soporte para formato separado por comas
            elif ',' in clean_line:
                parts = [p.strip() for p in clean_line.split(',')]
                name = parts[0]
                walkable = parts[1].lower() == 'true'
                destructible = parts[2].lower() == 'true'
                objects[name] = GameObject(name=name, walkable=walkable, destructible=destructible)
            else:
                objects[clean_line] = GameObject(name=clean_line)

    return objects

def load_map(width: int, height: int, terrains_dict: dict, objects_dict: dict) -> WorldGrid:
    """
    Lee un archivo .map en formato de cuadrícula de caracteres (ej. #...#),
    calcula sus dimensiones automáticamente y asigna Terrain y GameObject a cada Tile.
    Cumple con la Sección 3.3 de la especificación oficial.
    """
    map_rows = generate_random_map_lines(width, height)

    grid = parse_maps_rows_to_grid(map_rows, terrains_dict, objects_dict)

    populate_map_with_object(grid, objects_dict, item_prob=0.08)

    return grid