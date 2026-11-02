class Entity:
    def init(self, name: str, regen_rate: int = 0):
        self.name = name
        self.regen_rate = regen_rate

class Terrain(Entity):
    """Representa el terreno de una casilla con soporte para biomas y modificadores."""
    def init(self, name: str, walkable: bool = True, reserve: int = 100, regen_rate: int = 1, health_modifier: int = 0, movement_cost: int = 1):
        super().init(name = name, regen_rate = regen_rate)
        self.walkable = walkable
        self.reserve = reserve
        self.resource_max = reserve  # Alias compatible con la guía oficial[span_4](start_span)[span_4](end_span)
        self.regen = regen_rate      # Alias compatible con la guía oficial[span_5](start_span)[span_5](end_span)
        self.health_modifier = health_modifier  # Daño o curación al pisarlo (ej. Lava L)
        self.movement_cost = movement_cost      # Costo de movimiento (ej. Pantano W)

    def repr(self):
        return f"Terrain({self.name})"


class GameObject(Entity):
    """Representa obstáculos o recursos en el mapa"""
    def init(self, name: str, walkable: bool = False, reserve: int = 50, destructible: bool = True, regen_rate: int = 0):
        super().init(name = name, regen_rate = regen_rate)
        self.walkable = walkable
        self.reserve = reserve
        self.resource_max = reserve  # Alias compatible con la guía oficial[span_6](start_span)[span_6](end_span)
        self.destructible = destructible

    def repr(self):
        return f"GameObject({self.name})"


class Creature(Entity):
    """Representa a un monstruo/criatura en ejecución"""
    def init(self, species_name: str, faction: str, health: int, vision: int, lifespan: int, x: int = 0, y: int = 0):
        super().init(name = species_name)
        # Atributos obligatorios de la cabecera
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

        # Puntero de instrucciones inicializado en la etiqueta obligatoria 'start[span_7](start_span)[span_8](start_span)'[span_7](end_span)[span_8](end_span)
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