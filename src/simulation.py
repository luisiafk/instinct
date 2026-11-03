import random

from grid import WorldGrid
from entities import Creature
from actions import Move, Attack, Consume, Wait, Say, Reproduce, Roar


class _ExpressionAdapter:
    """Adapta los nodos del AST a la interfaz evaluate(memory) de actions.py."""

    def __init__(self, simulation, expression, creature):
        self.simulation = simulation
        self.expression = expression
        self.creature = creature

    def evaluate(self, memory):
        return self.simulation._evaluate_expression(self.expression, self.creature)


class Simulation:
    """Gestiona el mundo, los ticks, los turnos y la ejecución de los programas."""

    READ_ONLY_PERCEPTIONS = {
        "health", "age", "lifespan", "vision", "species", "faction", "x", "y",
        "terrain_here", "reserve_here", "width", "height", "tick",
        "total_creatures", "total_allies", "total_enemies", "allies_near",
        "enemies_near", "objects_near", "enemy_dist", "enemy_dx", "enemy_dy",
        "ally_dist", "ally_dx", "ally_dy", "object_dist", "object_dx",
        "object_dy", "roars_near", "last_roar", "random",
    }

    CONSTANTS = {"NONE": -1, "GROUND": 0, "OBJECT": 1, "ALLY": 2, "ENEMY": 3}

    ACTIONS = {
        "MOVE": (Move, 3),
        "ATTACK": (Attack, 3),
        "CONSUME": (Consume, 4),
        "WAIT": (Wait, 1),
        "SAY": (Say, 1),
        "REPRODUCE": (Reproduce, 3),
        "ROAR": (Roar, 1),
    }

    def __init__(self, world: WorldGrid, seed: int = None):
        self.world = world
        self.creatures = []
        self.tick_count = 0
        self.rng = random.Random(seed)
        self.logs = []
        self.roar_events = []

    def _log(self, message):
        self.logs.append(str(message))

    @staticmethod
    def _is_integer(value):
        return isinstance(value, int) and not isinstance(value, bool)

    @staticmethod
    def _is_truthy(value):
        # En INSTINCT solo 0 y la cadena vacía son falsos.
        return value != 0 and value != ""

    @staticmethod
    def _direction(delta):
        return (delta > 0) - (delta < 0)

    def add_creature(self, creature: Creature, x: int, y: int) -> bool:
        tile = self.world.get_tile(x, y)
        if tile is None or tile.creature is not None or tile.game_object is not None:
            return False
        if tile.terrain is not None and not tile.terrain.walkable:
            return False
        if creature in self.creatures:
            return False

        creature.x = x
        creature.y = y
        creature.alive = True
        creature.simulation = self
        tile.creature = creature
        self.creatures.append(creature)
        return True

    def remove_dead_creatures(self):
        survivors = []
        for creature in self.creatures:
            if creature.is_alive():
                survivors.append(creature)
            else:
                tile = self.world.get_tile(creature.x, creature.y)
                if tile is not None and tile.creature is creature:
                    tile.creature = None
        self.creatures = survivors

    def update_environment_resources(self):
        for y in range(self.world.height):
            for x in range(self.world.width):
                tile = self.world.get_tile(x, y)
                if tile is None:
                    continue

                terrain = tile.terrain
                if terrain is not None:
                    maximum = getattr(terrain, "resource_max", terrain.reserve)
                    regeneration = getattr(terrain, "regen_rate", 0)
                    terrain.reserve = min(maximum, terrain.reserve + regeneration)

                if tile.game_object is not None and tile.game_object.reserve <= 0:
                    tile.game_object = None

    def apply_natural_laws(self):
        for creature in list(self.creatures):
            if creature.is_alive():
                creature.health -= 1
                creature.age += 1
                if creature.health <= 0 or creature.age >= creature.lifespan:
                    creature.alive = False
        self.remove_dead_creatures()

    def _visible_creatures(self, creature):
        """Devuelve criaturas vivas dentro del radio de vision"""
        result = []
        for other in self.creatures:
            if other is creature or not other.is_alive():
                continue
            distance = max(abs(other.x - creature.x), abs(other.y - creature.y))
            if distance <= creature.vision:
                result.append((distance, other))
        return result

    def _visible_objects(self, creature):
        """Devuelve objetos dentro del radio de visión"""
        result = []
        left = max(0, creature.x - creature.vision)
        right = min(self.world.width - 1, creature.x + creature.vision)
        top = max(0, creature.y - creature.vision)
        bottom = min(self.world.height - 1, creature.y + creature.vision)

        for y in range(top, bottom + 1):
            for x in range(left, right + 1):
                distance = max(abs(x - creature.x), abs(y - creature.y))
                if distance > creature.vision:
                    continue
                tile = self.world.get_tile(x, y)
                if tile is not None and tile.game_object is not None:
                    result.append((distance, tile.game_object, x, y))
        return result

    def _nearest_creature_perception(self, candidates, creature):
        if not candidates:
            return -1, 0, 0
        distance, target = min(candidates, key=lambda item: item[0])
        return (
            distance,
            self._direction(target.x - creature.x),
            self._direction(target.y - creature.y),
        )

    def update_creature_perceptions(self, creature: Creature):
        tile = self.world.get_tile(creature.x, creature.y)
        creature.memory.update({
            "health": creature.health,
            "age": creature.age,
            "lifespan": creature.lifespan,
            "vision": creature.vision,
            "species": creature.species_name,
            "faction": creature.faction,
            "x": creature.x,
            "y": creature.y,
            "terrain_here": tile.terrain.name if tile and tile.terrain else "",
            "reserve_here": tile.terrain.reserve if tile and tile.terrain else 0,
            "width": self.world.width,
            "height": self.world.height,
            "tick": self.tick_count,
        })

        others = [c for c in self.creatures if c is not creature and c.is_alive()]
        visible = self._visible_creatures(creature)
        allies = [(distance, c) for distance, c in visible if c.faction == creature.faction]
        enemies = [(distance, c) for distance, c in visible if c.faction != creature.faction]
        objects = self._visible_objects(creature)

        memory = creature.memory
        memory["total_creatures"] = len(others)
        memory["total_allies"] = sum(c.faction == creature.faction for c in others)
        memory["total_enemies"] = sum(c.faction != creature.faction for c in others)
        memory["allies_near"] = len(allies)
        memory["enemies_near"] = len(enemies)
        memory["objects_near"] = len(objects)

        memory["enemy_dist"], memory["enemy_dx"], memory["enemy_dy"] = (
            self._nearest_creature_perception(enemies, creature)
        )
        memory["ally_dist"], memory["ally_dx"], memory["ally_dy"] = (
            self._nearest_creature_perception(allies, creature)
        )

        if objects:
            distance, _, object_x, object_y = min(objects, key=lambda item: item[0])
            memory["object_dist"] = distance
            memory["object_dx"] = self._direction(object_x - creature.x)
            memory["object_dy"] = self._direction(object_y - creature.y)
        else:
            memory["object_dist"] = -1
            memory["object_dx"] = 0
            memory["object_dy"] = 0

        previous_tick_roars = [
            event for event in self.roar_events
            if event["tick"] == self.tick_count - 1
            and max(abs(event["x"] - creature.x), abs(event["y"] - creature.y)) <= creature.vision
        ]
        memory["roars_near"] = len(previous_tick_roars)
        memory["last_roar"] = previous_tick_roars[-1]["value"] if previous_tick_roars else ""

    def record_roar(self, creature: Creature, value):
        """Registra un rugido para que pueda percibirse durante el tick siguiente."""
        self.roar_events.append({
            "x": creature.x,
            "y": creature.y,
            "value": value,
            "tick": self.tick_count,
        })

    def _evaluate_expression(self, expression, creature):
        """Evalúa un nodo de expresión del AST sin modificar backend/ast_nodes.py."""
        node_type = expression.__class__.__name__

        if node_type == "NumberNode":
            return expression.value
        if node_type == "StringNode":
            return expression.value

        if node_type == "IdentifierNode":
            name = expression.name
            if name in self.CONSTANTS:
                return self.CONSTANTS[name]
            if name == "random":
                return self.rng.randint(0, 99)
            if name not in creature.memory:
                raise RuntimeError(f"Variable no definida: {name}")
            return creature.memory[name]

        if node_type == "FunctionCallNode":
            function = expression.name
            if function not in ("see", "name"):
                raise RuntimeError(f"Función desconocida: {function}")
            if len(expression.args) != 2:
                raise RuntimeError(f"La función {function} requiere exactamente 2 argumentos")

            dx = self._evaluate_expression(expression.args[0], creature)
            dy = self._evaluate_expression(expression.args[1], creature)
            if not self._is_integer(dx) or not self._is_integer(dy):
                raise RuntimeError(f"Los argumentos de {function} deben ser enteros")
            if max(abs(dx), abs(dy)) > creature.vision:
                return -1 if function == "see" else ""

            target = self.world.get_tile(creature.x + dx, creature.y + dy)
            if target is None:
                return 1 if function == "see" else ""

            if function == "name":
                if target.creature is not None:
                    return target.creature.species_name
                if target.game_object is not None:
                    return target.game_object.name
                return target.terrain.name if target.terrain is not None else ""

            # see(): la propia casilla también se clasifica como ALLY
            if target.creature is not None:
                return 2 if target.creature.faction == creature.faction else 3
            if target.game_object is not None:
                return 1
            return 0

        if node_type == "UnaryOpNode":
            value = self._evaluate_expression(expression.operand, creature)
            operator = str(expression.op).lower()
            if operator == "-":
                if not self._is_integer(value):
                    raise RuntimeError("El operador '-' requiere un entero")
                return -value
            if operator == "not":
                return 0 if self._is_truthy(value) else 1
            raise RuntimeError(f"Operador unario desconocido: {expression.op}")

        if node_type == "BinaryOpNode":
            operator = str(expression.op).lower()
            left = self._evaluate_expression(expression.left, creature)

            if operator == "and":
                if not self._is_truthy(left):
                    return 0
                right = self._evaluate_expression(expression.right, creature)
                return int(self._is_truthy(right))
            if operator == "or":
                if self._is_truthy(left):
                    return 1
                right = self._evaluate_expression(expression.right, creature)
                return int(self._is_truthy(right))

            right = self._evaluate_expression(expression.right, creature)
            if operator in ("+", "-", "*", "/", "%"):
                if not self._is_integer(left) or not self._is_integer(right):
                    raise RuntimeError(f"El operador '{operator}' solo admite enteros")
                if operator == "+":
                    return left + right
                if operator == "-":
                    return left - right
                if operator == "*":
                    return left * right
                if right == 0:
                    raise RuntimeError("División o módulo por cero")
                return left // right if operator == "/" else left % right

            if operator in ("==", "!="):
                if type(left) is not type(right):
                    raise RuntimeError("No se pueden comparar valores de tipos diferentes")
                equal = left == right
                return int(equal if operator == "==" else not equal)

            if operator in ("<", "<=", ">", ">="):
                if not self._is_integer(left) or not self._is_integer(right):
                    raise RuntimeError(f"El operador '{operator}' solo admite enteros")
                if operator == "<":
                    return int(left < right)
                if operator == "<=":
                    return int(left <= right)
                if operator == ">":
                    return int(left > right)
                return int(left >= right)

            raise RuntimeError(f"Operador binario desconocido: {expression.op}")

        raise RuntimeError(f"Nodo de expresión no reconocido: {node_type}")

    @staticmethod
    def _get_labels(statements):
        labels = {}
        for index, statement in enumerate(statements):
            if statement.__class__.__name__ == "LabelNode":
                if statement.name in labels:
                    raise RuntimeError(f"Etiqueta duplicada: {statement.name}")
                labels[statement.name] = index
        if "start" not in labels:
            raise RuntimeError("El programa no contiene la etiqueta obligatoria 'start:'")
        return labels

    def _make_action(self, statement, creature):
        # Obtenemos el nombre de la acción y lo convertimos a mayúsculas
        action_name = statement.name.upper()

        # Comprobamos que la acción exista
        if action_name not in self.ACTIONS:
            raise RuntimeError(f"Acción desconocida: {statement.name}")

        # Consultamos la clase y la cantidad de argumentos que necesita
        action_class, expected_arguments = self.ACTIONS[action_name]

        # Comprobamos que se haya indicado el número correcto de argumentos
        if len(statement.args) != expected_arguments:
            raise RuntimeError(
                f"La acción {statement.name} requiere {expected_arguments} argumentos; "
                f"recibió {len(statement.args)}"
            )

        # Adaptamos las expresiones del AST para que puedan evaluarse desde actions.py
        arguments = [
            _ExpressionAdapter(self, expression, creature)
            for expression in statement.args
        ]

        # Algunas acciones reciben sus argumentos directamente en el constructor
        if action_name in ("MOVE", "ATTACK", "CONSUME", "ROAR"):
            action = action_class(*arguments)

        # Las demás acciones se inicializan mediante el método init()
        else:
            action = action_class()
            action.init(*arguments)

        return action

    def _sync_creatures_from_world(self):
        """Registra las crías creadas por Reproduce sin darles turno en este tick."""
        known = set(self.creatures)
        for row in self.world.matrix:
            for tile in row:
                creature = tile.creature
                if creature is not None and creature not in known:
                    creature.simulation = self
                    self.creatures.append(creature)
                    known.add(creature)

    def run_creature_turn(self, creature: Creature, program_ast):
        if not creature.is_alive():
            return

        if getattr(creature, "sleep_turns", 0) > 0:
            creature.sleep_turns -= 1
            return

        self.update_creature_perceptions(creature)
        statements = program_ast.statements
        statement = None

        try:
            labels = self._get_labels(statements)
            pointer = creature.instruction_pointer
            if isinstance(pointer, str):
                if pointer not in labels:
                    raise RuntimeError(f"Etiqueta de inicio no definida: {pointer}")
                ip = labels[pointer]
            elif self._is_integer(pointer) and 0 <= pointer < len(statements):
                ip = pointer
            else:
                ip = labels["start"]

            executed = 0
            turn_consumed = False
            while executed < 100 and not turn_consumed and creature.is_alive():
                if ip < 0 or ip >= len(statements):
                    # El final del programa implica reiniciar en start en el próximo turno.
                    ip = labels["start"]
                    break

                statement = statements[ip]
                executed += 1
                node_type = statement.__class__.__name__

                if node_type == "LabelNode":
                    ip += 1
                elif node_type == "GotoNode":
                    if statement.target not in labels:
                        raise RuntimeError(f"Etiqueta no definida: {statement.target}")
                    ip = labels[statement.target]
                elif node_type == "IfGotoNode":
                    condition = self._evaluate_expression(statement.condition, creature)
                    if self._is_truthy(condition):
                        if statement.target not in labels:
                            raise RuntimeError(f"Etiqueta no definida: {statement.target}")
                        ip = labels[statement.target]
                    else:
                        ip += 1
                elif node_type == "AssignNode":
                    if statement.name in self.READ_ONLY_PERCEPTIONS or statement.name in self.CONSTANTS:
                        raise RuntimeError(
                            f"No se puede modificar la variable de solo lectura: {statement.name}"
                        )
                    creature.memory[statement.name] = self._evaluate_expression(
                        statement.value, creature
                    )
                    ip += 1
                elif node_type == "ActionNode":
                    action = self._make_action(statement, creature)
                    turn_consumed = bool(action.execute(creature, self.world))
                    ip += 1
                else:
                    raise RuntimeError(f"Instrucción AST no reconocida: {node_type}")

            if ip >= len(statements):
                ip = labels["start"]
            creature.instruction_pointer = ip

        except Exception as error:
            # Los nodos AST actuales no guardan números de línea; no se inventan.
            line = getattr(statement, "line", None) if statement is not None else None
            suffix = f" (línea {line})" if line is not None else ""
            self._log(f"Error de ejecución en {creature.species_name}{suffix}: {error}")
            creature.health = 0
            creature.alive = False
            self.remove_dead_creatures()

    def run_tick(self, programs_dict=None):
        self.tick_count += 1
        self.remove_dead_creatures()

        active_creatures = list(self.creatures)
        self.rng.shuffle(active_creatures)

        if programs_dict is not None:
            for creature in active_creatures:
                if not creature.is_alive():
                    continue
                program = programs_dict.get(creature.species_name)
                if program is not None:
                    self.run_creature_turn(creature, program)

        # Las crías nacen durante el tick, pero no participan en el orden de turnos ya creado.
        self._sync_creatures_from_world()
        self.apply_natural_laws()
        self.update_environment_resources()

        # Los rugidos solo se consultan durante el tick inmediatamente posterior.
        self.roar_events = [
            event for event in self.roar_events
            if event["tick"] >= self.tick_count - 1
        ]
