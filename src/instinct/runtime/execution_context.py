from collections.abc import Callable
from random import Random
from typing import Any, ClassVar

from instinct.engine.action_event import ActionEventLog
from instinct.engine.event_log import EventLog
from instinct.runtime.environment import Environment
from instinct.runtime.program import Program
from instinct.world.entities import Creature
from instinct.world.world_grid import WorldGrid

Value = int | str

ActionExecutor = Callable[
    ["ExecutionContext", str, list[Value]],
    None,
]

FunctionExecutor = Callable[
    ["ExecutionContext", str, list[Value]],
    Value,
]


class ExecutionContext:
    """Mantiene el estado de ejecución de una criatura."""

    READ_ONLY_NAMES: ClassVar[set[str]] = {
        "GROUND", "OBJECT", "ALLY", "ENEMY", "NONE",
        "creature", "faction", "species",
        "health", "vision", "lifespan", "age",
        "orientation", "x", "y",
        "allies_near", "enemies_near", "objects_near",
        "consumables_near",
        "enemy_dist", "enemy_dx", "enemy_dy",
        "ally_dist", "ally_dx", "ally_dy",
        "object_dist", "object_dx", "object_dy",
        "consumable_dist", "consumable_dx", "consumable_dy",
        "roars_near", "last_roar",
        "terrain_here", "reserve_here",
        "width", "height", "tick",
        "total_creatures", "total_allies",
        "total_enemies", "random",
    }

    def __init__(
        self,
        program: Program,
        creature: Creature,
        world: WorldGrid,
        rng: Random,
        event_log: EventLog,
        action_event_log: ActionEventLog | None = None,
        action_registry: Any = None,
        function_registry: Any = None,
    ) -> None:
        if not isinstance(program, Program):
            raise TypeError("El programa debe ser una instancia de Program.")

        if not isinstance(creature, Creature):
            raise TypeError("La criatura debe ser una instancia de Creature.")

        if not isinstance(world, WorldGrid):
            raise TypeError("El mundo debe ser una instancia de WorldGrid.")

        if not isinstance(rng, Random):
            raise TypeError(
                "El generador aleatorio debe ser una instancia de Random."
            )

        if not isinstance(event_log, EventLog):
            raise TypeError("El registro debe ser una instancia de EventLog.")

        if action_event_log is not None and not isinstance(
            action_event_log, ActionEventLog
        ):
            raise TypeError(
                "El registro de acontecimientos debe ser una instancia "
                "de ActionEventLog."
            )

        self.program = program
        self.creature_obj = creature
        self.world = world
        self.rng = rng
        self.event_log = event_log

        self.action_event_log = (
            action_event_log
            if action_event_log is not None
            else ActionEventLog()
        )

        from instinct.perceptions.registry import PerceptionRegistry

        self.perception_registry = PerceptionRegistry()
        self.environment = Environment()

        self.instruction_pointer = program.start_position
        self.wait_turns = 0
        self.current_tick = 0

        self.action_executor: ActionExecutor | None = None
        self.function_executor: FunctionExecutor | None = None

        if action_registry is not None:
            self.set_action_registry(action_registry)

        if function_registry is not None:
            self.set_function_registry(function_registry)

    def set_action_registry(self, registry: Any) -> None:
        """Conecta el registro central de acciones."""

        execute = getattr(registry, "execute", None)

        if not callable(execute):
            raise TypeError(
                "El registro de acciones debe proporcionar el método execute."
            )

        self.action_executor = execute

    def set_function_registry(self, registry: Any) -> None:
        """Conecta el registro central de funciones."""

        execute = getattr(registry, "execute", None)

        if not callable(execute):
            raise TypeError(
                "El registro de funciones debe proporcionar el método execute."
            )

        self.function_executor = execute

    def get_variable(self, name: str) -> Value:
        """Obtiene una variable, percepción o propiedad de la criatura."""

        if not isinstance(name, str) or not name:
            raise RuntimeError(
                "Error de ejecución: el nombre de la variable no es válido."
            )

        creature = self.creature_obj

        creature_values: dict[str, Value] = {
            "creature": creature.name,
            "species": creature.name,
            "faction": creature.faction,
            "health": creature.health,
            "vision": creature.vision,
            "lifespan": creature.lifespan,
            "age": creature.age,
            "x": creature.x,
            "y": creature.y,
            "width": self.world.width,
            "height": self.world.height,
            "tick": self.current_tick,
        }

        if name in creature_values:
            return creature_values[name]

        if self.perception_registry.has_perception(name):
            return self.perception_registry.get(self, name)

        if self.environment.has_variable(name):
            return self.environment.get_variable(name)

        raise RuntimeError(
            f"Error de ejecución: la variable '{name}' no ha sido inicializada."
        )

    def set_variable(self, name: str, value: Value) -> None:
        """Asigna una variable del programa."""

        if not isinstance(name, str) or not name:
            raise RuntimeError(
                "Error de ejecución: el nombre de la variable no es válido."
            )

        if name in self.READ_ONLY_NAMES:
            raise RuntimeError(
                f"Error de ejecución: no se puede modificar "
                f"la variable '{name}' porque es de solo lectura."
            )

        if self.perception_registry.has_perception(name):
            raise RuntimeError(
                f"Error de ejecución: no se puede modificar "
                f"la percepción '{name}'."
            )

        self.environment.set_variable(name, value)

    def call_function(self, name: str, args: list[Value]) -> Value:
        """Ejecuta una función del lenguaje."""

        if self.function_executor is None:
            raise RuntimeError(
                f"Error de ejecución: no hay un registro conectado "
                f"para la función '{name}'."
            )

        return self.function_executor(self, name, args)

    def publish_action_event(
        self,
        event_type: str,
        target: Creature | None = None,
        data: dict[str, Any] | None = None,
    ) -> None:
        """Publica un acontecimiento de la criatura en ejecución."""

        self.action_event_log.publish(
            tick=self.current_tick,
            event_type=event_type,
            actor=self.creature_obj,
            target=target,
            data=data,
        )

    def execute_action(self, name: str, args: list[Value]) -> None:
        """Ejecuta una acción del lenguaje."""

        if self.action_executor is None:
            raise RuntimeError(
                f"Error de ejecución: no hay un registro conectado "
                f"para la acción '{name}'."
            )

        self.action_executor(self, name, args)

    def __getattr__(self, name: str) -> Value:
        """Permite que IdentifierNode consulte variables como atributos."""

        try:
            return self.get_variable(name)
        except RuntimeError as error:
            raise AttributeError(name) from error
