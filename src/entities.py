class Entity:
    def __init__(self, name: str, regen_rate: int=0):
        self.name = name
        self.regen_rate = regen_rate

class Terrain(Entity):
    """Representa el terreno de una casilla """
    def __init__(self, name: str, walkable: bool = True, reserve: int = 100, regen_rate: int = 1):
        super().__init__(name = name)
        self.walkable = walkable
        self.reserve = reserve
        self.regen_rate = regen_rate

    def __repr__(self):
        return f"Terrain({self.name})"


class GameObject(Entity):
    """Representa obstáculos o recursos en el mapa"""
    def __init__(self, name: str, walkable: bool = False, reserve: int = 50, destructible: bool = True, regen_rate: int=0):
        super().__init__(name = name, regen_rate = regen_rate)
        self.walkable = walkable
        self.reserve = reserve
        self.destructible = destructible

    def __repr__(self):
        return f"GameObject({self.name})"


class Creature(Entity):
    """Representa a un monstruo/criatura en ejecución"""
    def __init__(self, species_name: str, faction: str, health: int, vision: int, lifespan: int, x: int = 0, y: int = 0):
        super().__init__(name = species_name)
        # Atributos
        self.species_name = species_name
        self.faction = faction
        self.health = health
        self.max_health = health  
        self.vision = vision
        self.lifespan = lifespan

        # Estado en tiempo de ejecución
        self.x = x
        self.y = y
        self.age = 0
        self.alive = True

        # Memoria interna (variables que la criatura asigna en su script)
        self.memory = {}

        self.instruction_pointer = "start"

    def is_alive(self) -> bool:
        """Una criatura muere si su vida llega a 0 o supera su esperanza de vida"""
        if self.health <= 0 or self.age >= self.lifespan:
            self.alive = False
        return self.alive

    def __repr__(self):
        return f"Creature({self.species_name}, Faction:{self.faction}, HP:{self.health}, Pos:({self.x},{self.y}))"

class Tile:
    """Una casilla en la matriz que guarda el terreno, objeto y criatura si la hay"""
    def __init__(self, terrain: Terrain, game_object: GameObject = None, creature: Creature = None):
        self.terrain = terrain
        self.game_object = game_object
        self.creature = creature