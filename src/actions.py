from abc import ABC, abstractmethod
from grid import WorldGrid
from entities import Creature, Tile


class Action(ABC):
    """
    Clase base abstracta para representar cualquier acción ejecutable por una criatura.
    Establecer la estructura común y obligar a las clases hijas a implementar el método execute.
    """
    
    @abstractmethod
    def execute(self, creature: Creature, world: WorldGrid) -> bool:
        """
        Ejecutar la acción sobre el mundo y la criatura actual.
        Retornar True si la acción consume el turno, o False en caso contrario.
        """
        pass


class Move(Action):
    """
    Acción para desplazar a la criatura en una dirección y velocidad determinadas.
    """
    
    def init(self, dx_expr, dy_expr, speed_expr):
        # Guardar los nodos del AST para su posterior evaluación dinámica mediante la memoria de la criatura.
        self.dx_expr = dx_expr
        self.dy_expr = dy_expr
        self.speed_expr = speed_expr

    def execute(self, creature: Creature, world: WorldGrid) -> bool:
        # Obtener el valor numérico de las expresiones usando la memoria interna de la criatura.
        dx = int(self.dx_expr.evaluate(creature.memory))
        dy = int(self.dy_expr.evaluate(creature.memory))
        speed = int(self.speed_expr.evaluate(creature.memory))
        
        # Acotar el desplazamiento entre -1 y 1 para asegurar que solo se mueva a casillas adyacentes por cada paso unitario.
        dx = max(-1, min(1, dx))
        dy = max(-1, min(1, dy))
        
        # Iterar según la velocidad indicada para avanzar casilla por casilla de forma secuencial.
        for _ in range(speed):
            new_x = creature.x + dx
            new_y = creature.y + dy
            
            # Validar mediante el grid si la casilla destino está libre y es transitable.
            if world.is_walkable(new_x, new_y):
                # Desocupar la casilla anterior para reflejar el movimiento en la matriz del mundo.
                old_tile = world.get_tile(creature.x, creature.y)
                if old_tile:
                    old_tile.creature = None
                
                # Actualizar las coordenadas espaciales de la criatura.
                creature.x = new_x
                creature.y = new_y
                
                # Ocupar la nueva casilla con la criatura en su nueva posición.
                new_tile = world.get_tile(new_x, new_y)
                if new_tile:
                    new_tile.creature = creature
            else:
                # Detener el ciclo si se encuentra un obstáculo o límite del mapa antes de completar toda la velocidad.
                break
                
        # Indicar que la acción de movimiento consume el turno de la criatura.
        return True


class Attack(Action):
    """
    Acción para golpear una casilla adyacente, reduciendo la salud de criaturas o dañando objetos destructibles.
    """
    
    def init(self, dx_expr, dy_expr, damage_expr):
        self.dx_expr = dx_expr
        self.dy_expr = dy_expr
        self.damage_expr = damage_expr

    def execute(self, creature: Creature, world: WorldGrid) -> bool:
        # Resolver las expresiones del AST para obtener las coordenadas relativas y el daño base.
        dx = int(self.dx_expr.evaluate(creature.memory))
        dy = int(self.dy_expr.evaluate(creature.memory))
        damage = int(self.damage_expr.evaluate(creature.memory))
        
        # Calcular la posición absoluta de la casilla objetivo en el grid.
        target_x = creature.x + dx
        target_y = creature.y + dy
        
        # Recuperar la casilla del mundo para inspeccionar su contenido.
        tile = world.get_tile(target_x, target_y)
        if tile:
            # Caso de ataque a otra criatura presente en la casilla.

            if tile.creature:
                tile.creature.health -= damage
                # Verificar si la criatura atacada muere por falta de salud para retirarla del mapa.
                if not tile.creature.is_alive():
                    tile.creature = None
            # Caso de ataque a un objeto destructible (como rocas u obstáculos con resistencia).
            elif tile.game_object and tile.game_object.destructible:
                tile.game_object.reserve -= damage
                # Eliminar el objeto del mapa si su reserva o durabilidad llega a cero o menos.
                if tile.game_object.reserve <= 0:
                    tile.game_object = None
            # Caso alternativo de daño directo al terreno si posee reservas alterables.
            elif tile.terrain:
                tile.terrain.reserve -= damage
                if tile.terrain.reserve < 0:
                    tile.terrain.reserve = 0
                    
        return True


class Consume(Action):
    """
    Acción para interactuar con los recursos del entorno, permitiendo dañar o consumir elementos mientras se cura la criatura.
    """
    
    def init(self, dx_expr, dy_expr, damage_expr, heal_expr):
        self.dx_expr = dx_expr
        self.dy_expr = dy_expr
        self.damage_expr = damage_expr
        self.heal_expr = heal_expr

    def execute(self, creature: Creature, world: WorldGrid) -> bool:
        # Evaluar los componentes de daño y curación a partir de las expresiones del script.
        dx = int(self.dx_expr.evaluate(creature.memory))
        dy = int(self.dy_expr.evaluate(creature.memory))
        damage = int(self.damage_expr.evaluate(creature.memory))
        heal = int(self.heal_expr.evaluate(creature.memory))
        
        target_x = creature.x + dx
        target_y = creature.y + dy
        
        tile = world.get_tile(target_x, target_y)
        if tile:
            # Aplicar la lógica de daño e interacción sobre el objetivo de la misma forma que en el ataque.
            if tile.creature:
                tile.creature.health -= damage
                if not tile.creature.is_alive():
                    tile.creature = None
            elif tile.game_object and tile.game_object.destructible:
                tile.game_object.reserve -= damage
                if tile.game_object.reserve <= 0:
                    tile.game_object = None
            elif tile.terrain:
                tile.terrain.reserve -= damage
                if tile.terrain.reserve < 0:
                    tile.terrain.reserve = 0
            
            # Incrementar la salud de la criatura utilizando la función min para evitar superar el límite máximo permitido.
            creature.health = min(creature.max_health, creature.health + heal)
            
        return True


class Wait(Action):
    """
    Acción para que la criatura ceda su turno de ejecución durante un número determinado de ciclos.
    """
    
    def init(self, n_expr):
        self.n_expr = n_expr

    def execute(self, creature: Creature, world: WorldGrid) -> bool:
        # Obtener la cantidad de turnos a esperar evaluando la expresión correspondiente.
        n = int(self.n_expr.evaluate(creature.memory))
        # Retornar True para consumir el turno actual de la simulación.
        return True


class Say(Action):
    """
    Acción para emitir un mensaje de texto por consola. Constituye la única acción que no consume el turno de la criatura.
    """
    
    def init(self, message_expr):
        self.message_expr = message_expr

    def execute(self, creature: Creature, world: WorldGrid) -> bool:
        # Resolver el texto del mensaje evaluando la expresión asociada en la memoria.
        message = self.message_expr.evaluate(creature.memory)
        print(f"{creature.species_name} dice: {message}")
        # Retornar False para permitir que la criatura ejecute otra acción en el mismo tick sin perder el turno.
        return False

class Reproduce(Action):
    """
    Acción para generar una nueva criatura descendiente en una casilla adyacente vacía a cambio de sacrificar parte de la salud propia.
    """
    
    def init(self, dx_expr, dy_expr, health_expr):
        self.dx_expr = dx_expr
        self.dy_expr = dy_expr
        self.health_expr = health_expr

    def execute(self, creature: Creature, world: WorldGrid) -> bool:
        # Obtener las coordenadas relativas y el costo de vida necesario para la reproducción.
        dx = int(self.dx_expr.evaluate(creature.memory))
        dy = int(self.dy_expr.evaluate(creature.memory))
        health_cost = int(self.health_expr.evaluate(creature.memory))
        
        target_x = creature.x + dx
        target_y = creature.y + dy
        
        tile = world.get_tile(target_x, target_y)
        
        # Comprobar condiciones estrictas: la casilla debe existir, estar totalmente vacía y la madre poseer vida superior al costo.
        if tile and creature.health > health_cost and tile.creature is None and tile.game_object is None:
            # Descontar el coste de salud de la criatura madre.
            creature.health -= health_cost
            
            # Instanciar el nuevo objeto Creature heredando las propiedades base de la especie.
            baby = Creature(
                species_name=creature.species_name,
                faction=creature.faction,
                health=health_cost,
                vision=creature.vision,
                lifespan=creature.lifespan,
                x=target_x,
                y=target_y
            )
            
            # Inicializar los valores de estado propios de la cría de forma independiente.
            baby.age = 0
            baby.instruction_pointer = "start"
            baby.memory = {}
            
            # Asignar la cría recién nacida a la casilla correspondiente en la matriz del mundo.
            tile.creature = baby
            
        return True

class Roar(Action):
    """
    Acción para emitir un rugido con un valor específico que se almacena temporalmente para ser detectado por el entorno o criaturas vecinas.
    """
    
    def init(self, value_expr):
        self.value_expr = value_expr

    def execute(self, creature: Creature, world: WorldGrid) -> bool:
        # Evaluar la expresión numérica o de texto vinculada al rugido.
        value = self.value_expr.evaluate(creature.memory)
        # Registrar el rugido en un atributo dinámico de la criatura para que las percepciones puedan consultarlo.
        creature.last_roar = str(value)
        print(f"{creature.species_name} ruge: {value}")
        return True