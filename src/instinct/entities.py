class Entity:
    def __init__(self, name: str, regen_rate: int = 0):
        self.name = name
        self.regen_rate = regen_rate

class Terrain(Entity):
    """Representa el terreno de una casilla con soporte para biomas y modificadores"""
    def __init__(self, name: str, walkable: bool = True, reserve: int = 100, regen_rate: int = 1, health_modifier: int = 0, movement_cost: int = 1):
        super().__init__(name = name)

        self.walkable = walkable
        self.reserve = reserve
        self.resource_max = reserve
        self.regen_rate = regen_rate
        self.health_modifier = health_modifier  # Daño o curacion al pisarlo
        self.movement_cost = movement_cost      # Costo de movimiento

    def repr(self):
        return f"Terrain({self.name})"


class GameObject(Entity):
    """Representa obstáculos o recursos en el mapa"""
    def __init__(self, name: str, symbol: str = '.',walkable: bool = False, reserve: int = 50, destructible: bool = True, regen_rate: int = 0):
        super().__init__(name = name)
        self.walkable = walkable
        self.symbol = symbol
        self.reserve = reserve
        self.resource_max = reserve
        self.regen_rate = regen_rate
        self.destructible = destructible

    def repr(self):
        return f"GameObject({self.name})"


class Creature(Entity):
    """Representa a un monstruo/criatura en ejecucion"""
    def __init__(self, species_name: str, faction: str, health: int, vision: int, lifespan: int, x: int = 0, y: int = 0):
        super().__init__(name = species_name)

        self.species_name = species_name
        self.faction = faction
        self.health = health
        self.max_health = health
        self.vision = vision
        self.lifespan = lifespan

        # Estado en tiempo de ejecucion
        self.x = x
        self.y = y
        self.age = 0
        self.alive = True

        # Memoria interna (variables que la criatura asigna en su script)
        self.memory = {}

        # Puntero de instrucciones
        self.instruction_pointer = "start"

    def is_alive(self) -> bool:
        """Una criatura muere si su vida llega a 0 o supera su esperanza de vida"""
        if self.health <= 0 or self.age >= self.lifespan:
            self.alive = False
        return self.alive

    def repr(self):
        return f"Creature({self.species_name}, Faction:{self.faction}, HP:{self.health}, Pos:({self.x},{self.y}))"


class Tile:
    """Una casilla en la matriz que guarda el terreno, objeto y criatura si la hay"""
    def __init__(self, terrain: Terrain, game_object: GameObject = None, creature: Creature = None):
        self.terrain = terrain
        self.game_object = game_object
        self.creature = creature