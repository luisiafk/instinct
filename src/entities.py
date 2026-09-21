class Terrain:
    """Representa el terreno de una casilla """
    def init(self, name: str, walkable: bool = True, reserve: int = 100, regen_rate: int = 1):
        self.name = name
        self.walkable = walkable
        self.reserve = reserve
        self.regen_rate = regen_rate

    def repr(self):
        return f"Terrain({self.name})"


class GameObject:
    """Representa obstáculos o recursos en el mapa"""
    def init(self, name: str, walkable: bool = False, reserve: int = 50, destructible: bool = True):
        self.name = name
        self.walkable = walkable
        self.reserve = reserve
        self.destructible = destructible

    def repr(self):
        return f"GameObject({self.name})"


class Creature:
    """Representa a un monstruo/criatura en ejecución"""
    def init(self, species_name: str, faction: str, health: int, vision: int, lifespan: int, x: int = 0, y: int = 0):
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

    def repr(self):
        return f"Creature({self.species_name}, Faction:{self.faction}, HP:{self.health}, Pos:({self.x},{self.y}))"

class Tile:
    """Una casilla en la matriz que guarda el terreno, objeto y criatura si la hay"""
    def init(self, terrain: Terrain, game_object: GameObject = None, creature: Creature = None):
        self.terrain = terrain
        self.game_object = game_object
        self.creature = creature