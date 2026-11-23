from instinct.backend.ast_nodes import (
    ActionNode,
    AssignNode,
    GotoNode,
    IfGotoNode,
    LabelNode,
)
from instinct.runtime.execution_context import ExecutionContext

MAX_INSTRUCTIONS_PER_TURN = 100


def execute_turn(context: ExecutionContext, tick: int) -> None:
    """
    Ejecuta el turno de una criatura.

    Las asignaciones, los saltos, las etiquetas y say no terminan
    el turno. Las demás acciones sí lo terminan.
    """

    if not isinstance(context, ExecutionContext):
        raise TypeError(
            "El contexto debe ser una instancia de ExecutionContext."
        )

    if (
        not isinstance(tick, int)
        or isinstance(tick, bool)
        or tick < 0
    ):
        raise ValueError("El número de turno no es válido.")

    context.current_tick = tick

    if context.creature_obj.health <= 0:
        return

    try:
        # Las percepciones se actualizan al comienzo del turno
        # individual de cada criatura.
        context.perception_registry.update(context)

        # Los turnos pendientes de wait se consumen sin ejecutar
        # instrucciones del programa.
        if context.wait_turns > 0:
            context.wait_turns -= 1
            return

        executed_instructions = 0
        program = context.program

        while executed_instructions < MAX_INSTRUCTIONS_PER_TURN:

            # Al alcanzar el final del programa, se vuelve a start.
            if context.instruction_pointer >= len(program):
                context.instruction_pointer = program.start_position

            if context.instruction_pointer < 0:
                raise RuntimeError(
                    "Error de ejecución: la posición de instrucción "
                    "no es válida."
                )

            statement = program.statements[context.instruction_pointer]
            executed_instructions += 1
            context.last_executed_line = statement.lineno

            # Las etiquetas no producen efectos.
            if isinstance(statement, LabelNode):
                context.instruction_pointer += 1
                continue

            # Asignación de variables.
            if isinstance(statement, AssignNode):
                value = statement.value.evaluate(context)
                context.set_variable(statement.name, value)
                context.instruction_pointer += 1
                continue

            # Salto incondicional.
            if isinstance(statement, GotoNode):
                context.instruction_pointer = (
                    program.get_label_position(statement.target)
                )
                continue

            # Salto condicional.
            if isinstance(statement, IfGotoNode):
                condition = statement.condition.evaluate(context)

                if condition:
                    context.instruction_pointer = (
                        program.get_label_position(statement.target)
                    )
                else:
                    context.instruction_pointer += 1

                continue

            # Ejecución de acciones.
            if isinstance(statement, ActionNode):
                args = [
                    argument.evaluate(context)
                    for argument in statement.args
                ]

                context.execute_action(statement.name, args)

                context.instruction_pointer += 1

                # wait(n) consume el turno actual y reserva
                # los siguientes n-1 turnos.
                if statement.name == "wait":
                    if len(args) != 1 or type(args[0]) is not int:
                        raise RuntimeError(
                            "Error de ejecución: wait requiere "
                            "un argumento entero."
                        )

                    context.wait_turns = max(1, args[0]) - 1
                    return

                # say no consume el turno.
                if statement.name == "say":
                    continue

                # Las demás acciones terminan el turno.
                return

            raise RuntimeError(
                f"Error de ejecución en la línea {statement.lineno}: "
                f"instrucción no reconocida "
                f"'{type(statement).__name__}'."
            )

    except RuntimeError as error:
        _handle_runtime_error(context, tick, str(error))


def _handle_runtime_error(
    context: ExecutionContext,
    tick: int,
    message: str,
) -> None:
    """Registra el error y elimina a la criatura de la simulación."""

    creature = context.creature_obj
    world = context.world

    creature.health = 0

    if world.in_bounds(creature.x, creature.y):
        tile = world.get_tile(creature.x, creature.y)

        if tile.creature is creature:
            world.remove_creature(creature.x, creature.y)

    context.event_log.add(
        tick,
        message,
        category="error",
    )

    context.perception_registry.clear(context)