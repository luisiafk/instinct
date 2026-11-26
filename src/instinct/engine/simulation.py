
"""
Motor principal de la simulación de Instinct.

Coordina la ejecución de los turnos, la gestión de los contextos
de ejecución de las criaturas y la aplicación de las leyes
naturales del mundo.
"""

import random

from instinct.actions.registry import ActionRegistry
from instinct.engine.action_event import ActionEventLog
from instinct.engine.event_log import EventLog
from instinct.engine.natural_laws import NaturalLaws
from instinct.engine.turn_manager import TurnExecutor, TurnManager
from instinct.functions.registry import FunctionRegistry
from instinct.runtime.execution_context import ExecutionContext
from instinct.runtime.interpreter import execute_turn
from instinct.runtime.program import Program
from instinct.world.entities import Creature
from instinct.world.world_grid import WorldGrid


class Simulation:
    """Coordina el avance de la simulación por ticks."""

    def __init__(
        self,
        world: WorldGrid,
        seed: int | None = None,
    ) -> None:
        if not isinstance(world, WorldGrid):
            raise TypeError("El mundo proporcionado no es válido.")

        if seed is not None and (
            not isinstance(seed, int) or isinstance(seed, bool)
        ):
            raise TypeError(
                "La semilla aleatoria debe ser un número entero."
            )

        self.world = world
        self.tick = 0

        self.rng = random.Random(seed)

        self.event_log = EventLog()
        self.action_event_log = ActionEventLog()

        self.turn_manager = TurnManager(self.rng)

        self.action_registry = ActionRegistry()
        self.function_registry = FunctionRegistry()

        self._contexts: dict[int, ExecutionContext] = {}
        self._last_executed_lines: dict[int, int] = {}

    @property
    def is_finished(self) -> bool:
        """Indica si ya no quedan criaturas en el mundo."""

        return not any(
            tile.creature is not None
            for row in self.world.tiles
            for tile in row
        )

    def _get_execution_context(
        self,
        creature: Creature,
    ) -> ExecutionContext:
        """Obtiene o crea el contexto persistente de una criatura."""

        program = creature.program

        if not isinstance(program, Program):
            raise TypeError(
                f"La criatura '{creature.name}' no tiene un programa válido."
            )

        creature_id = id(creature)

        context = self._contexts.get(creature_id)

        if context is not None:
            return context

        context = ExecutionContext(
            program=program,
            creature=creature,
            world=self.world,
            rng=self.rng,
            event_log=self.event_log,
            action_event_log=self.action_event_log,
            action_registry=self.action_registry,
            function_registry=self.function_registry,
        )

        self._contexts[creature_id] = context

        return context

    def _execute_program_turn(
        self,
        creature: Creature,
        tick: int,
    ) -> None:
        """Ejecuta un turno utilizando el programa de una criatura."""

        if creature.program is None:
            return

        context = self._get_execution_context(creature)

        execute_turn(
            context=context,
            tick=tick,
        )

        self._last_executed_lines[id(creature)] = (
            context.last_executed_line
        )

    def get_last_executed_line(self, creature: Creature) -> int | None:
        """Devuelve la última línea ejecutada por una criatura."""

        return self._last_executed_lines.get(id(creature))

    def restore_execution_state(
        self,
        creature: Creature,
        state: dict,
    ) -> None:
        """Recupera el punto de ejecución y las variables de una criatura."""

        if not isinstance(state, dict):
            raise TypeError("El estado de ejecución no es válido.")

        context = self._get_execution_context(creature)

        instruction_pointer = state["instruction_pointer"]
        last_line = state.get("last_executed_line")
        wait_turns = state["wait_turns"]
        current_tick = state["current_tick"]
        variables = state.get("variables", {})

        if (
            not isinstance(instruction_pointer, int)
            or isinstance(instruction_pointer, bool)
            or not 0 <= instruction_pointer <= len(context.program)
        ):
            raise ValueError("La posición de ejecución guardada no es válida.")

        if (
            not isinstance(wait_turns, int)
            or isinstance(wait_turns, bool)
            or wait_turns < 0
        ):
            raise ValueError("El estado de espera guardado no es válido.")

        if (
            not isinstance(current_tick, int)
            or isinstance(current_tick, bool)
            or current_tick < 0
        ):
            raise ValueError("El tick del contexto no es válido.")

        if not isinstance(variables, dict):
            raise ValueError("Las variables guardadas no son válidas.")

        context.instruction_pointer = instruction_pointer
        context.last_executed_line = last_line
        context.wait_turns = wait_turns
        context.current_tick = current_tick

        for name, value in variables.items():
            context.environment.set_variable(name, value)

        if last_line is not None:
            self._last_executed_lines[id(creature)] = last_line

    def get_execution_state(
        self,
        creature: Creature,
    ) -> dict | None:
        """Obtiene el estado necesario para continuar el programa de una criatura."""

        context = self._contexts.get(id(creature))

        if context is None:
            return None

        return {
            "instruction_pointer": context.instruction_pointer,
            "last_executed_line": context.last_executed_line,
            "wait_turns": context.wait_turns,
            "current_tick": context.current_tick,
            "variables": context.environment.variables,
        }
    
    def _cleanup_contexts(self) -> None:
        """Elimina los contextos de criaturas que ya no están en el mundo."""

        active_ids = {
            id(tile.creature)
            for row in self.world.tiles
            for tile in row
            if tile.creature is not None
        }

        self._contexts = {
            creature_id: context
            for creature_id, context in self._contexts.items()
            if creature_id in active_ids
        }

    def run_tick(
        self,
        execute_turn: TurnExecutor | None = None,
    ) -> None:
        """
        Ejecuta un tick completo de la simulación.

        Si no quedan criaturas, no se ejecuta ningún tick.
        """

        if execute_turn is not None and not callable(execute_turn):
            raise TypeError(
                "El ejecutor de turnos debe ser una función válida."
            )

        if self.is_finished:
            return

        self.tick += 1

        turn_executor = (
            execute_turn
            if execute_turn is not None
            else self._execute_program_turn
        )

        self.turn_manager.execute_turns(
            world=self.world,
            tick=self.tick,
            execute_turn=turn_executor,
        )

        NaturalLaws.apply(
            world=self.world,
            tick=self.tick,
            event_log=self.event_log,
            action_event_log=self.action_event_log,  # También registramos los eventos de acciones
        )
        self._cleanup_contexts()

    def run(
        self,
        ticks: int,
        execute_turn: TurnExecutor | None = None,
    ) -> None:
        """Ejecuta una cantidad determinada de ticks."""

        if not isinstance(ticks, int) or isinstance(ticks, bool):
            raise TypeError(
                "La cantidad de ticks debe ser un número entero."
            )

        if ticks < 0:
            raise ValueError(
                "La cantidad de ticks no puede ser negativa."
            )

        for _ in range(ticks):
            if self.is_finished:
                break

            self.run_tick(execute_turn)
