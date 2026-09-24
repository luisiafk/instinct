from .entities import Tile, Terrain, GameObject, Creature

class WorldGrid:
    """Matriz del mapa y las colisiones"""
    def init(self, width: int, height: int):
        self.width = width
        self.height = height
        # Crea una matriz vacía de ancho x alto rellena de casillas (Tile)
        self.matrix = [[Tile(terrain=Terrain(name="ground")) for _ in range(width)] for _ in range(height)]

    def in_bounds(self, x: int, y: int) -> bool:
        """Verifica si la coordenada (x, y) está dentro del mapa"""
        return 0 <= x < self.width and 0 <= y < self.height

    def get_tile(self, x: int, y: int) -> Tile:
        """Casilla en la posición (x, y)"""
        if self.in_bounds(x, y):
            return self.matrix[y][x]
        return None

    def is_walkable(self, x: int, y: int) -> bool:
        """Determina si una criatura puede dar un paso hacia la casilla (x, y)"""
        if not self.in_bounds(x, y):
            return False  # Los bordes del mapa funcionan como muros
            
        tile = self.matrix[y][x]
        
        # No se puede pisar si hay una criatura presente
        if tile.creature is not None:
            return False
            
        # No se puede pisar si hay un objeto no transitable (ej. roca)
        if tile.game_object is not None and not tile.game_object.walkable:
            return False
            
        # No se puede pisar si el suelo en sí es intransitable (ej. agua/lava)
        if tile.terrain is not None and not tile.terrain.walkable:
            return False
            
        return True