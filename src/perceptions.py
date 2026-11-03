from grid import WorldGrid
from entities import Creature, Tile


def get_visible_tiles(grid: WorldGrid, creature: Creature, vision_range: int) -> list[Tile]:
    """
    Devuelve las casillas dentro del campo de visión Chebyshev.

    La distancia Chebyshev entre dos posiciones es max(abs(dx), abs(dy)).
    Por tanto, las diagonales cuentan igual que los desplazamientos
    horizontales y verticales. Los límites del mapa se recortan porque
    fuera de la grilla no existen objetos Tile que devolver.
    """
    if vision_range < 0:
        return []

    visible_tiles = []
    cx, cy = creature.x, creature.y

    min_x = max(0, cx - vision_range)
    max_x = min(grid.width - 1, cx + vision_range)
    min_y = max(0, cy - vision_range)
    max_y = min(grid.height - 1, cy + vision_range)

    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            if max(abs(x - cx), abs(y - cy)) <= vision_range:
                tile = grid.get_tile(x, y)
                if tile is not None:
                    visible_tiles.append(tile)

    return visible_tiles


def get_visible_entities(grid: WorldGrid, creature: Creature, vision_range: int) -> list:
    """
    Devuelve criaturas y objetos ubicados en casillas visibles.
    """
    entities = []

    for tile in get_visible_tiles(grid, creature, vision_range):
        if tile.game_object is not None:
            entities.append(tile.game_object)

        if tile.creature is not None and tile.creature is not creature:
            entities.append(tile.creature)

    return entities