from abc import ABC, abstractmethod
from grid import WorldGrid
from entities import Creature, Tile


class Action(ABC):
    """Clase base abstracta para todas las acciones"""
    
    @abstractmethod 
    def execute(self, creature: Creature, world: WorldGrid) -> bool:
        """
        Ejecuta la acción.
        Retorna True si la acción consume el turno de la criatura, 
        False si no consume turno (como Say).
        """
        pass 


class Move(Action):
    """Acción para mover a la criatura en una dirección"""
    
    def init(self, direction_expr):
        #guardar el nodo AST de la expresion que indica la direccion 
        self.direction_expr = direction_expr

    def execute(self, creature: Creature, world: WorldGrid) -> bool:
        # 1. Evaluar la dirección usando el entorno de la criatura
        target_direction = str(self.direction_expr.evaluate(creature.memory)).lower()

        #traducir la direccion a coordenadas
        # Mapeo de direcciones a vectores de desplazamiento (dx, dy)
        directions = {
            "north": (0, -1),
            "south": (0, 1),
            "west": (-1, 0),
            "east": (1, 0)
        }

        #obtener el cambio en x e y, si la direccion no existe no se mueve
        dx, dy = directions.get(target_direction, (0, 0))

        #posición actual de la criatura (usando creature.x y creature.y de entities.py)
        current_x = creature.x
        current_y = creature.y

        #calcular nueva posición
        new_x = current_x + dx
        new_y = current_y + dy

        #verificar si la casilla destino está libre y realizar el movimiento
        if world.is_walkable(new_x, new_y):
            #Liberar la casilla anterior en el mundo
            old_tile = world.get_tile(current_x, current_y)
            if old_tile:
                old_tile.creature = None

            #actualizar las coordenadas de la criatura
            creature.x = new_x
            creature.y = new_y

            #ocupar la nueva casilla en el mundo
            new_tile = world.get_tile(new_x, new_y)
            if new_tile:
                new_tile.creature = creature

        return True  # Consume el turno


class Say(Action):
    """Acción para emitir un mensaje"""
    
    def init(self, message):
        #guarda el nodo AST de la expresion del mensaje 
        self.message = message

    def execute(self, creature: Creature, world: WorldGrid) -> bool:
        # Evaluar la expresión del mensaje con la memoria interna
        message_text = self.message.evaluate(creature.memory)
        
        print(f"{creature.species_name} dice: {message_text}")
        
        return False  # No consume el turno


class Attack(Action):
    """Acción para atacar a una criatura o destruir un objeto en una casilla"""
    
    def init(self, target):
        self.target = target

    def execute(self, creature: Creature, world: WorldGrid) -> bool:
        # 1. Evaluar el objetivo/dirección usando la memoria de la criatura
        target_direction = str(self.target.evaluate(creature.memory)).lower()

        directions = {
            "north": (0, -1),
            "south": (0, 1),
            "west": (-1, 0),
            "east": (1, 0)
        }

        dx, dy = directions.get(target_direction, (0, 0))
        target_x = creature.x + dx
        target_y = creature.y + dy

        tile = world.get_tile(target_x, target_y)
        if tile:
            # CASO A: Hay una criatura en la casilla
            if tile.creature:
                tile.creature.health -= 10  # Daño base
                if not tile.creature.is_alive():
                    tile.creature = None  # Se remueve al morir

            # CASO B: Hay un objeto destructible (ej. una roca)
            elif tile.game_object and tile.game_object.destructible:
                tile.game_object.reserve -= 10  # Se reduce la resistencia/reserva del objeto
                if tile.game_object.reserve <= 0:
                    tile.game_object = None  # Se destruye el objeto y la casilla queda libre

        return True  # Consume el turno
    
class Wait(Action):
    """Accion que representa cuando la criaturano realiza ninguna accion activa"""
    def __init__(self):
        pass

    def execute(self, creature: Creature, world: WorldGrid) -> bool:
        print (f"{creature.species_name}decide ceder el turno")

        return True #esta vez si consume el turno

class Interact(Action):
    """
    Acción para interactuar con el entorno:
    - Si es un objeto destructible lo rompe y elimina del mapa.
    - Si es un recurso consumible, consume su reserva para curar a la criatura.
    """
    
    def init(self, target_expr):
        self.target_expr = target_expr

    def execute(self, creature: Creature, world: WorldGrid) -> bool:
        #evaluar dirección objetivo desde la memoria de la criatura
        direction = str(self.target_expr.evaluate(creature.memory)).lower()
        
        directions = {
            "north": (0, -1),
            "south": (0, 1),
            "west": (-1, 0),
            "east": (1, 0)
        }
        
        dx, dy = directions.get(direction, (0, 0))
        target_x = creature.x + dx
        target_y = creature.y + dy

        #obtener la casilla objetivo
        tile = world.get_tile(target_x, target_y)
        if not tile or not tile.game_object:
            return True  # No hay objeto con el cual interactuar

        obj = tile.game_object

        # Caso A: Objeto destructible (ej. una roca / obstáculo)
        if obj.destructible:
            obj.reserve -= 25
            if obj.reserve <= 0:
                # libera el paso y la visión
                tile.game_object = None

        # Caso B: Recurso consumible/regenerable
        if obj.regen_rate and obj.reserve > 0:
            cant_curada = 15
            
            # Subir salud a la criatura sin pasar su máximo
            creature.health = min(creature.max_health, creature.health + cant_curada)
            
            # Consumir la reserva del objeto (sin borrar el objeto del Tile)
            obj.reserve = max(0, obj.reserve - cant_curada)
            
            print(f"{creature.species_name} comió {obj.name}. Salud: {creature.health}/{creature.max_health}. Reserva restante del objeto: {obj.reserve}")

        return True  # Consume el turno