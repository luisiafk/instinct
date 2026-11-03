from entities import Tile, Terrain, GameObject, Creature


class WorldGrid:
    """Matriz del mapa y control de las casillas"""

    def __init__(self, width: int, height: int):
        # Comprobamos que el mapa tenga un tamaño valido
        if not isinstance(width, int) or isinstance(width, bool):
            raise TypeError("El ancho del mapa debe ser un numero entero")
        if not isinstance(height, int) or isinstance(height, bool):
            raise TypeError("El alto del mapa debe ser un numero entero")
        if width < 1 or height < 1:
            raise ValueError("El ancho y el alto deben ser mayores que cero")

        self.width = width
        self.height = height

        # Creamos una casilla para cada posicion del mapa
        # Cada casilla empieza con su propio terreno base
        self.matrix = [
            [Tile(terrain=Terrain(name="ground")) for _ in range(width)]
            for _ in range(height)
        ]

    def in_bounds(self, x: int, y: int) -> bool:
        """Comprueba si una posicion esta dentro del mapa"""
        # Revisamos que las coordenadas sean numeros enteros
        if not isinstance(x, int) or isinstance(x, bool):
            return False
        if not isinstance(y, int) or isinstance(y, bool):
            return False

        # Comprobamos que la posicion no salga de los bordes
        return 0 <= x < self.width and 0 <= y < self.height

    def get_tile(self, x: int, y: int) -> Tile:
        """Devuelve la casilla que se encuentra en esa posicion"""
        # Si la posicion existe, devolvemos su casilla
        if self.in_bounds(x, y):
            return self.matrix[y][x]

        # Si la posicion no existe, no hay ninguna casilla que devolver
        return None

    def set_tile_terrain(self, x: int, y: int, terrain):
        """Asigna un terreno a una casilla del mapa"""
        # Solo cambiamos el terreno si la posicion y el terreno son validos
        if not self.in_bounds(x, y):
            return
        if not isinstance(terrain, Terrain):
            return

        self.matrix[y][x].terrain = terrain

    def set_tile_object(self, x: int, y: int, game_object):
        """Coloca o retira un objeto de una casilla"""
        # Primero comprobamos que la posicion exista
        if not self.in_bounds(x, y):
            return

        # Permitimos retirar un objeto usando None
        if game_object is None:
            self.matrix[y][x].game_object = None
            return

        # Solo aceptamos objetos del tipo correcto
        if not isinstance(game_object, GameObject):
            return

        tile = self.matrix[y][x]

        # No colocamos un objeto donde ya hay una criatura
        if tile.creature is not None:
            return

        # Si la casilla esta libre, colocamos el objeto
        tile.game_object = game_object

    def is_walkable(self, x: int, y: int) -> bool:
        """Indica si una criatura puede entrar en una casilla"""
        # Los bordes del mapa funcionan como paredes
        if not self.in_bounds(x, y):
            return False

        tile = self.matrix[y][x]

        # No se puede entrar donde ya hay otra criatura
        if tile.creature is not None:
            return False

        # Los objetos siempre bloquean el paso
        if tile.game_object is not None:
            return False

        # Algunos terrenos tampoco permiten caminar sobre ellos
        if tile.terrain is None or not tile.terrain.walkable:
            return False

        # Si no hay ningun obstaculo, la casilla esta libre
        return True