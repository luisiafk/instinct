from entities import Tile, Terrain, GameObject, Creature
from grid import WorldGrid


def load_terrains(filepath: str) -> dict:
    """
    Lee un archivo de terrenos (.te) y devuelve un diccionario 
    donde la clave es el nombre del terreno y el valor es el objeto Terrain.
    """
    terrains = {}
    
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            # 1. Limpiar espacios en blanco al inicio y al final
            clean_line = line.strip()
            
            # 2. Ignorar líneas vacías o comentarios
            if not clean_line or line.startswith('#'):
                continue
            
            # 3. Separar los valores por coma
            parts = [p.strip() for p in line.split(',')]
            
            # Formato esperado: nombre, walkable, regen_rate
            name = parts[0]
            walkable = parts[1].lower() == 'true'  # Convierte el texto "true" a Booleano True
            regen_rate = float(parts[2])            # Convierte el texto a número float
            
            # 4. Crear la instancia de Terrain y guardarla en el diccionario
            terrains[name] = Terrain(name=name, walkable=walkable, regen_rate=regen_rate)
            
    return terrains

def load_objects(filepath: str) -> dict:

    """
    Lee un archivo .ob y devuelve un diccionario con las instancias de GameObject.
    Ejemplo de línea en el archivo: roca, false, true
    (Nombre, Walkable, Destructible)
    """
    objects = {}

    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
             # 1. Limpiar espacios en blanco al inicio y al final
            clean_line = line.strip()
                             
            # 2. Ignorar líneas vacías o comentarios
            if not clean_line or line.startswith('#'):
                continue
            #3. Separar los valores por coma
            parts = [part.strip() for part in clean_line.split(',')]
            
            name = parts[0]
            walkable = parts[1].lower() == 'true'
            destructible = parts[2].lower() == 'true'
                    
            # Crear la instancia de GameObject y guardarla en el diccionario
            objects[name] = GameObject(
                name=name, 
                walkable=walkable, 
                destructible=destructible
                    )
            
    return objects

def load_map(filepath: str, terrains_dict: dict, objects_dict: dict) -> WorldGrid:
    """
    Lee un archivo .map, crea la matriz WorldGrid y asigna a cada Tile
    su correspondiente Terrain y GameObject.
    """
    grid = None
    y = 0  # Control de la fila actual en el mapa

    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            clean_line = line.strip()

            # 1. Tu parte: Ignorar líneas vacías o comentarios
            if not clean_line or clean_line.startswith('#'):
                continue

            # 2. Encabezados de tamaño (WIDTH y HEIGHT)
            if clean_line.startswith('WIDTH'):
                width = int(clean_line.split()[1])
                continue
            
            if clean_line.startswith('HEIGHT'):
                height = int(clean_line.split()[1])
                # Una vez que tenemos ancho y alto, instanciamos la grilla
                grid = WorldGrid(width=width, height=height)
                continue

            # 3. Leer las filas del mapa (coordenadas Y)
            
            elements = [elem.strip() for elem in clean_line.split(',')]

            for x, item_name in enumerate(elements):
                # Averiguar si el elemento es un terreno o un objeto
                terrain = terrains_dict.get(item_name, None)
                game_object = objects_dict.get(item_name, None)

                # Si es un terreno, se lo asignamos a Tile
                if terrain:
                    grid.set_tile_terrain(x, y, terrain)
                
                # Si es un objeto (ej. roca, árbol), se lo colocamos encima al Tile
                if game_object:
                    grid.set_tile_object(x, y, game_object)

            # Avanzamos a la siguiente fila del tablero
            y += 1

    return grid