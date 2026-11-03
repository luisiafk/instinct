from entities import Tile, Terrain, GameObject, Creature
from grid import WorldGrid


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
                    
                    objects[symbol] = GameObject(name=name, walkable=False, reserve=value, destructible=True)
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

def load_map(filepath: str, terrains_dict: dict, objects_dict: dict) -> WorldGrid:
    """
    Lee un archivo .map en formato de cuadrícula de caracteres (ej. #...#),
    calcula sus dimensiones automáticamente y asigna Terrain y GameObject a cada Tile.
    Cumple con la Sección 3.3 de la especificación oficial.
    """
    lines = []
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            clean_line = line.strip()
            # Guardar únicamente líneas que contengan contenido relevante para el mapa
            if clean_line and not clean_line.startswith('//'):
                lines.append(clean_line)

    # Comprobación de líneas vacías fuera del bucle (Corrección del bug de indentación)
    if not lines:
        return WorldGrid(width=10, height=10)

    # Filtrar filas que contengan caracteres válidos de mapa
    map_rows = []
    for line in lines:
        if any(char in line for char in ['.', '#', 'T', 'A', 'B', 'W', 'L', ' ']):
            map_rows.append(line)

    if not map_rows:
        map_rows = lines

    height = len(map_rows)
    width = max(len(row) for row in map_rows) if height > 0 else 10

    grid = WorldGrid(width=width, height=height)

    for y, row in enumerate(map_rows):
        for x, char in enumerate(row):
            if x >= width:
                break
            
            # Obtener terreno base por defecto (punto o ground)
            terrain = terrains_dict.get('.', terrains_dict.get('ground', Terrain(name="ground")))
            game_object = None

            # Evaluar el carácter del mapa frente a los diccionarios cargados
            if char in terrains_dict:
                terrain = terrains_dict[char]
            elif char in objects_dict:
                game_object = objects_dict[char]
            elif char == 'T':
                terrain = terrains_dict.get('T', Terrain(name="resource_terrain", regen_rate=10))
            elif char == '#':
                game_object = objects_dict.get('#', GameObject(name="Rock", walkable=False))
            elif char in ('A', 'B'):
                # Son puntos de inicio de criaturas, se deja el terreno base debajo
                terrain = terrains_dict.get('.', Terrain(name="ground"))

            grid.set_tile_terrain(x, y, terrain)
            if game_object:
                grid.set_tile_object(x, y, game_object)

    return grid