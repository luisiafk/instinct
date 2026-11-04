import random
from grid import WorldGrid
from entities import Creature, Tile


class Simulation:
    """
    Clase encargada de controlar el motor principal de la simulación,
    gestionando el avance por turnos (ticks), el orden aleatorio de las criaturas,
    la ejecución de sus comportamientos y la aplicación de las leyes naturales del mundo.
    """

    def __init__(self, world: WorldGrid, seed: int = None):
        # Inicializar el mundo simulado a partir de la grilla proporcionada[span_4](start_span)[span_4](end_span).
        self.world = world
        # Almacenar la lista global de criaturas activas en la simulación[span_5](start_span)[span_5](end_span).
        self.creatures = []
        # Inicializar el contador de ticks en cero[span_6](start_span)[span_6](end_span).
        self.tick_count = 0

        # Configurar la semilla de aleatoriedad si se especifica para asegurar reproducibilidad[span_7](start_span)[span_7](end_span).
        if seed is not None:
            random.seed(seed)

    def add_creature(self, creature: Creature, x: int, y: int) -> bool:
        """
        Colocar una criatura en una posición específica del mapa si la casilla está libre.
        Retornar True si se colocó con éxito, o False en caso contrario[span_8](start_span)[span_8](end_span).
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
        Eliminar del mapa y de la lista de activas a todas las criaturas que hayan muerto[span_9](start_span)[span_9](end_span).
        """
        surviving_creatures = []
        for creature in self.creatures:
            if creature.is_alive():
                surviving_creatures.append(creature)
            else:
                # Desocupar la casilla correspondiente en el grid del mundo[span_10](start_span)[span_10](end_span).
                tile = self.world.get_tile(creature.x, creature.y)
                if tile and tile.creature == creature:
                    tile.creature = None
        self.creatures = surviving_creatures

    def update_environment_resources(self):
        """
        Aplicar la regeneración natural de los terrenos y la desaparición de objetos agotados al final del tick[span_11](start_span)[span_11](end_span).
        """
        for y in range(self.world.height):
            for x in range(self.world.width):
                tile = self.world.get_tile(x, y)
                if tile:
                    # Regenerar el terreno según su tasa establecida sin superar su valor máximo[span_12](start_span)[span_12](end_span).
                    if tile.terrain:
                        max_res = getattr(tile.terrain, 'resource_max', 100)
                        regen = getattr(tile.terrain, 'regen_rate', 0)
                        tile.terrain.reserve = min(max_res, tile.terrain.reserve + regen)

                    # Eliminar objetos cuya reserva haya llegado a cero o menos[span_13](start_span)[span_13](end_span).
                    if tile.game_object and tile.game_object.reserve <= 0:
                        tile.game_object = None

    def apply_natural_laws(self):
        """
        Aplicar las leyes naturales al final de cada tick a todas las criaturas vivas:
        perder 1 punto de vida, aumentar 1 tick de edad y comprobar condiciones de muerte.
        """
        # Iteramos sobre una copia de la lista para evitar alterar el iterador en pleno ciclo
        for creature in list(self.creatures):
            if creature.is_alive():
                # Reducir un punto de vida y sumar uno a la edad de forma obligatoria por turno
                creature.health -= 1
                creature.age = max(0, creature.age + 1)

                # Comprobar si la criatura muere por falta de salud o por alcanzar su esperanza de vida
                if creature.health <= 0 or creature.age >= creature.lifespan:
                    creature.alive = False

        # Limpiar del mundo a las criaturas que hayan perecido una vez finalizada la revisión
        self.remove_dead_creatures()

    def update_creature_perceptions(self, creature: Creature):
        """
        Actualizar las variables de solo lectura en la memoria de la criatura al comenzar su turno[span_18](start_span)[span_18](end_span).
        """
        # Actualizar percepciones básicas sobre sí misma[span_19](start_span)[span_19](end_span).
        creature.memory["health"] = creature.health
        creature.memory["age"] = creature.age
        creature.memory["lifespan"] = creature.lifespan
        creature.memory["vision"] = creature.vision
        creature.memory["species"] = creature.species_name
        creature.memory["faction"] = creature.faction
        creature.memory["x"] = creature.x
        creature.memory["y"] = creature.y

        min_dist = 9999
        closest_enemy = None

        for c in self.creatures:
            if c != creature and c.faction != creature.faction and c.is_alive():
                dist = abs(c.x - creature.x) + abs(c.y - creature.y)
                if dist <= creature.vision and dist < min_dist:
                    min_dist = dist
                    closest_enemy = c

        if closest_enemy:
            creature.memory["enemy_dist"] = min_dist
            creature.memory["enemy_dx"] = closest_enemy.x - creature.x
            creature.memory["enemy_dy"] = closest_enemy.y - creature.y
        else:
            creature.memory["enemy_dist"] = 0
            creature.memory["enemy_dx"] = 0
            creature.memory["enemy_dy"] = 0




        # Consultar el terreno bajo los pies de la criatura[span_20](start_span)[span_20](end_span).
        current_tile = self.world.get_tile(creature.x, creature.y)
        if current_tile and current_tile.terrain:
            creature.memory["terrain_here"] = current_tile.terrain.name
            creature.memory["reserve_here"] = current_tile.terrain.reserve
        else:
            creature.memory["terrain_here"] = ""
            creature.memory["reserve_here"] = 0

        # Actualizar percepciones globales del mundo[span_21](start_span)[span_21](end_span).
        creature.memory["width"] = self.world.width
        creature.memory["height"] = self.world.height
        creature.memory["tick"] = self.tick_count

        # Calcular totales de criaturas, aliados y enemigos en todo el mapa (excluyéndose a sí misma)[span_22](start_span)[span_22](end_span).
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

    def run_creature_turn(self, creature: Creature, program_ast):
        """
        Ejecutar el turno de una criatura individual, interpretando su AST
        a partir de su instruction_pointer actual y procesando las instrucciones.
        """
        if hasattr(creature, "sleep_turns") and creature.sleep_turns > 0:
            creature.sleep_turns -= 1
            return

        # Actualizar las percepciones obligatorias al inicio del turno.
        self.update_creature_perceptions(creature)

        if isinstance(program_ast, list):
            statements = program_ast
        else:
            statements = getattr(program_ast, 'statements', [])


        # Encontrar el índice de inicio basado en el instruction_pointer de la criatura (ej. "start")
        ip = 0
        if isinstance(creature.instruction_pointer, str):
            for idx, stmt in enumerate(statements):
                if hasattr(stmt, "name") and stmt.name == creature.instruction_pointer:
                    ip = idx
                    break
        elif isinstance(creature.instruction_pointer, int):
            ip = creature.instruction_pointer

        lines_executed = 0
        turn_consumed = False


        while lines_executed < 100 and not turn_consumed and creature.is_alive() and ip < len(statements):
            lines_executed += 1
            stmt = statements[ip]

            node_type = stmt.__class__.__name__

            # 1. Etiquetas (LabelNode): solo avanzamos el puntero
            if node_type == "LabelNode":
                ip += 1
                continue

            # 2. Salto incondicional (GotoNode)
            elif node_type == "GotoNode":
                target_label = stmt.target
                found = False
                for idx, s in enumerate(statements):
                    if hasattr(s, "name") and s.name == target_label:
                        ip = idx
                        found = True
                        break
                if not found:
                    break
                continue

            # 3. Salto condicional (IfGotoNode)
            elif node_type == "IfGotoNode":
                condition_val = stmt.condition.evaluate(creature.memory)
                if condition_val:
                    target_label = stmt.target
                    found = False
                    for idx, s in enumerate(statements):
                        if hasattr(s, "name") and s.name == target_label:
                            ip = idx
                            found = True
                            break
                    if not found:
                        break
                    continue
                else:
                    ip += 1
                    continue

            # 4. Asignación (AssignNode)
            elif node_type == "AssignNode":
                val = stmt.value.evaluate(creature.memory)
                creature.memory[stmt.name] = val
                ip += 1
                continue

            # 5. Ejecución de Acción (ActionNode)
            elif node_type == "ActionNode":
                action_name = stmt.name.upper()
                action_obj = None

                if action_name == "MOVE" and len(stmt.args) >= 3:
                    from actions import Move
                    action_obj = Move()
                    action_obj.init(stmt.args[0], stmt.args[1], stmt.args[2])
                elif action_name == "ATTACK" and len(stmt.args) >= 3:
                    from actions import Attack
                    action_obj = Attack()
                    action_obj.init(stmt.args[0], stmt.args[1], stmt.args[2])
                elif action_name == "CONSUME" and len(stmt.args) >= 4:
                    from actions import Consume
                    action_obj = Consume()
                    action_obj.init(stmt.args[0], stmt.args[1], stmt.args[2], stmt.args[3])
                elif action_name == "WAIT" and len(stmt.args) >= 1:
                    from actions import Wait
                    action_obj = Wait()
                    action_obj.init(stmt.args[0])
                elif action_name == "SAY" and len(stmt.args) >= 1:
                    from actions import Say
                    action_obj = Say()
                    action_obj.init(stmt.args[0])
                elif action_name == "REPRODUCE" and len(stmt.args) >= 3:
                    from actions import Reproduce
                    action_obj = Reproduce()
                    action_obj.init(stmt.args[0], stmt.args[1], stmt.args[2])
                elif action_name == "ROAR" and len(stmt.args) >= 1:
                    from actions import Roar
                    action_obj = Roar()
                    action_obj.init(stmt.args[0])

                if action_obj:
                    # Ejecuta la acción y devuelve True si consume turno, o False si continúa (ej. say)[span_33](start_span)[span_33](end_span)
                    turn_consumed = action_obj.execute(creature, self.world)

                ip += 1

            else:
                ip += 1

        # Guardar el puntero para el siguiente turno[span_34](start_span)[span_34](end_span)
        creature.instruction_pointer = ip

    def run_tick(self, programs_dict=None):
        """
        Avanzar la simulación un turno completo (tick), ordenando aleatoriamente a las criaturas,
        ejecutando sus turnos y aplicando posteriormente las leyes naturales y la regeneración del entorno[span_35](start_span)[span_35](end_span).
        """
        self.tick_count += 1
        self.remove_dead_creatures()

        existing_creatures = set(self.creatures)
        for y in range(self.world.height):
            for x in range(self.world.width):
                tile = self.world.get_tile(x, y)
                if tile and tile.creature and tile.creature not in existing_creatures:
                    self.creatures.append(tile.creature)
                    existing_creatures.add(tile.creature)

        active_creatures = list(self.creatures)
        random.shuffle(active_creatures)

        # Ejecutar el turno de cada criatura activa utilizando su respectivo programa AST cargado
        if programs_dict:
            for creature in active_creatures:
                prog = programs_dict.get(creature.species_name)
                if prog:
                    self.run_creature_turn(creature, prog)

        # Aplicar leyes naturales y regeneración al final del tick[span_36](start_span)[span_36](end_span)
        self.apply_natural_laws()
        self.update_environment_resources()