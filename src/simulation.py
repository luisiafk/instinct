import random
from grid import WorldGrid
from entities import Creature, Tile


class Simulation:
    """
    Clase encargada de controlar el motor principal de la simulación, 
    gestionando el avance por turnos (ticks), el orden aleatorio de las criaturas,
    la ejecución de sus comportamientos y la aplicación de las leyes naturales del mundo.
    """

    def init(self, world: WorldGrid, seed: int = None):
        # Inicializar el mundo simulado a partir de la grilla proporcionada.
        self.world = world
        # Almacenar la lista global de criaturas activas en la simulación.
        self.creatures = []
        # Inicializar el contador de ticks en cero.
        self.tick_count = 0
        
        # Configurar la semilla de aleatoriedad si se especifica para asegurar reproducibilidad.
        if seed is not None:
            random.seed(seed)

    def add_creature(self, creature: Creature, x: int, y: int) -> bool:
        """
        Colocar una criatura en una posición específica del mapa si la casilla está libre.
        Retornar True si se colocó con éxito, o False en caso contrario.
        """
        tile = self.world.get_tile(x, y)
        if tile and tile.creature is None and tile.game_object is None:
            creature.x = x
            creature.y = y
            tile.creature = creature
            self.creatures.append(creature)
            return True
        return False

    def remove_dead_creatures(self):
        """
        Eliminar del mapa y de la lista de activas a todas las criaturas que hayan muerto.
        """
        surviving_creatures = []
        for creature in self.creatures:
            if creature.is_alive():
                surviving_creatures.append(creature)
            else:
                # Desocupar la casilla correspondiente en el grid del mundo.
                tile = self.world.get_tile(creature.x, creature.y)
                if tile and tile.creature == creature:
                    tile.creature = None
        self.creatures = surviving_creatures

    def update_environment_resources(self):
        """
        Aplicar la regeneración natural de los terrenos y la desaparición de objetos agotados al final del tick.
        """
        for y in range(self.world.height):
            for x in range(self.world.width):
                tile = self.world.get_tile(x, y)
                if tile:
                    # Regenerar el terreno según su tasa establecida sin superar su valor máximo.
                    if tile.terrain:
                        max_res = getattr(tile.terrain, 'resource_max', 100)
                        regen = getattr(tile.terrain, 'regen_rate', 0)
                        tile.terrain.reserve = min(max_res, tile.terrain.reserve + regen)
                    
                    # Eliminar objetos cuya reserva haya llegado a cero o menos.
                    if tile.game_object and tile.game_object.reserve <= 0:
                        tile.game_object = None

    def apply_natural_laws(self):
        """
        Aplicar las leyes naturales al final de cada tick a todas las criaturas vivas:
        perder 1 punto de vida, aumentar 1 tick de edad y comprobar condiciones de muerte.
        """
        for creature in self.creatures:
            if creature.is_alive():
                # Reducir un punto de vida y sumar uno a la edad de forma obligatoria por turno.
                creature.health -= 1
                creature.age = max(0, creature.age + 1)
                
                # Comprobar si la criatura muere por falta de salud o por alcanzar su esperanza de vida.
                if creature.health <= 0 or creature.age >= creature.lifespan:
                    creature.alive = False

        # Limpiar del mundo a las criaturas que hayan perecido por causas naturales.
        self.remove_dead_creatures()

    def update_creature_perceptions(self, creature: Creature):
        """
        Actualizar las variables de solo lectura en la memoria de la criatura al comenzar su turno.
        """
        # Actualizar percepciones básicas sobre sí misma.
        creature.memory["health"] = creature.health
        creature.memory["age"] = creature.age
        creature.memory["lifespan"] = creature.lifespan
        creature.memory["vision"] = creature.vision
        creature.memory["species"] = creature.species_name
        creature.memory["faction"] = creature.faction
        creature.memory["x"] = creature.x
        creature.memory["y"] = creature.y
        
        # Consultar el terreno bajo los pies de la criatura.
        current_tile = self.world.get_tile(creature.x, creature.y)
        if current_tile and current_tile.terrain:
            creature.memory["terrain_here"] = current_tile.terrain.name
            creature.memory["reserve_here"] = current_tile.terrain.reserve
        else:
            creature.memory["terrain_here"] = ""
            creature.memory["reserve_here"] = 0

        # Actualizar percepciones globales del mundo.
        creature.memory["width"] = self.world.width
        creature.memory["height"] = self.world.height
        creature.memory["tick"] = self.tick_count
        
        # Calcular totales de criaturas, aliados y enemigos en todo el mapa (excluyéndose a sí misma).
        total_c = len(self.creatures) - 1
        total_a = 0
        total_e = 0
        for c in self.creatures:
            if c != creature:
                if c.faction == creature.faction:
                    total_a += 1
                else:
                    total_e += 1
        creature.memory["total_creatures"] = max(0, total_c)
        creature.memory["total_allies"] = total_a
        creature.memory["total_enemies"] = total_e

        # Proveer la fuente de aleatoriedad del lenguaje (entero entre 0 y 99).
        creature.memory["random"] = random.randint(0, 99)

    def run_creature_turn(self, creature: Creature):
        """
        Ejecutar el turno de una criatura individual, procesando sus instrucciones 
        hasta que realice una acción que consuma turno o alcance el límite de líneas.
        """
        # Verificar si la criatura se encuentra en estado de espera (dormida por un wait previo).
        if hasattr(creature, "sleep_turns") and creature.sleep_turns > 0:
            creature.sleep_turns -= 1
            return

        # Actualizar las percepciones obligatorias al inicio del turno.
        self.update_creature_perceptions(creature)

        # Ejecutar instrucciones del script de forma iterativa (respetando el límite de 100 líneas por turno).
        lines_executed = 0
        turn_consumed = False

        while lines_executed < 100 and not turn_consumed and creature.is_alive():
            lines_executed += 1
            
            # Nota de integración: Aquí se conecta con el intérprete del compañero
            # para obtener la instrucción actual a partir del instruction_pointer de la criatura.
            # Si el script ejecuta una acción que retorna True (move, attack, consume, reproduce, roar, wait),
            # se marca el turno como consumido. Si ejecuta say, retorna False y continúa evaluando.
            
            break

    def run_tick(self):
        """
        Avanzar la simulación un turno completo (tick), ordenando aleatoriamente a las criaturas,
        ejecutando sus turnos y aplicando posteriormente las leyes naturales y la regeneración del entorno.
        """
        # Incrementar el contador global de ticks de la simulación.
        self.tick_count += 1

        # Limpiar criaturas muertas antes de iniciar el nuevo turno.
        self.remove_dead_creatures()

        # Crear una copia de la lista de criaturas vivas y sortear su orden al azar en cada tick.
        active_creatures = list(self.creatures)
        random.shuffle(active_creatures)