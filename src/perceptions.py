from grid import WorldGrid
from entities import Creature, Tile


def has_line_of_sight(grid: WorldGrid, cx: int, cy: int, tx: int, ty: int) -> bool:
    """
    Verifica si existe línea de visión directa entre (cx, cy) y (tx, ty)
    Algoritmo de trazado de linea de grilla
    """
    if cx == tx and cy == ty:
        return True

    dx = abs(tx - cx)
    dy = abs(ty - cy)
    x, y = cx, cy

    sx = 1 if tx > cx else -1
    sy = 1 if ty > cy else -1

    err = dx - dy

    while True:
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy

        # Si alcanzamos la casilla destino, la línea de visión está despejada
        if x == tx and y == ty:
            return True

        # Inspeccionar la casilla intermedia en la trayectoria
        tile = grid.get_tile(x, y)
        if tile:
            # Un objeto (ej. árbol/roca)
            # interrumpe la línea de visión hacia las casillas posteriores.
            
            is_object_blocking = tile.game_object and not tile.game_object.walkable

            if is_object_blocking:
                return False


def get_visible_tiles(grid: WorldGrid, creature: Creature, vision_range: int) -> list[Tile]:
    """
    Devuelve la lista de casillas (Tile) dentro del radio de visión de la criatura
    que no se encuentren bloqueadas por ningún obstáculo.
    """
    visible_tiles = []
    cx, cy = creature.x, creature.y

    # Delimitar el área de búsqueda dentro de los bordes reales del mapa
    min_x = max(0, cx - vision_range)
    max_x = min(grid.width - 1, cx + vision_range)
    min_y = max(0, cy - vision_range)
    max_y = min(grid.height - 1, cy + vision_range)

    for x in range(min_x, max_x + 1):
        for y in range(min_y, max_y + 1):
            # Omitir la casilla ocupada por la propia criatura
            if x == cx and y == cy:
                continue

            # Verificar la línea de visión hasta la casilla objetivo
            if has_line_of_sight(grid, cx, cy, x, y):
                tile = grid.get_tile(x, y)
                if tile:
                    visible_tiles.append(tile)

    return visible_tiles


def get_visible_entities(grid: WorldGrid, creature: Creature, vision_range: int) -> list:
    """
    Devuelve la lista de entidades (GameObjects y Creatures) situadas en las
    casillas que la criatura puede ver actualmente.
    """
    visible_tiles = get_visible_tiles(grid, creature, vision_range)
    entities = []

    for tile in visible_tiles:
        if tile.object_on_tile:
            entities.append(tile.object_on_tile)
        if tile.creature_on_tile:
            entities.append(tile.creature_on_tile)

    return entities
    