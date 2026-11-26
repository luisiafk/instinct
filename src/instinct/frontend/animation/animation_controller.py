
from collections import deque
from dataclasses import dataclass, field

from instinct.frontend.animation.animation_state import AnimationState
from instinct.frontend.animation.animation_state_machine import (
    AnimationStateMachine,
)
from instinct.frontend.animation.animations_config import AnimationConfig


@dataclass(slots=True)
class CreatureAnimation:
    creature: object
    state_machine: AnimationStateMachine
    frame_index: int = 0
    elapsed_ms: float = 0.0
    finished: bool = False

    # Recorridos pendientes: (inicio, destino, duración).
    movement_queue: deque = field(default_factory=deque)
    visual_position: tuple[float, float] | None = None
    movement_elapsed_ms: float = 0.0


class AnimationController:
    """Administra una FSM, un reproductor y un movimiento visual por criatura."""

    WALK_MS_PER_TILE = 400
    RUN_MS_PER_TILE = 250

    def __init__(self, config=AnimationConfig):
        self.config = config
        self._creatures = {}

    @staticmethod
    def _key(creature):
        return id(creature)

    def _get_or_create(self, creature):
        key = self._key(creature)
        record = self._creatures.get(key)

        if record is None or record.creature is not creature:
            record = CreatureAnimation(
                creature=creature,
                state_machine=AnimationStateMachine(),
            )
            self._creatures[key] = record

        return record

    def set_state(self, creature, state, force=False):
        """Activa un estado y reinicia su reproducción si corresponde."""

        if isinstance(state, str):
            state = AnimationState(state.lower())

        record = self._get_or_create(creature)

        changed = record.state_machine.transition(
            state,
            force=force,
        )

        if changed:
            record.frame_index = 0
            record.elapsed_ms = 0.0
            record.finished = False

        return changed

    def start_movement(self, creature, start, end, state):
        """Registra un desplazamiento visual sin modificar el mundo real."""

        if isinstance(state, str):
            state = AnimationState(state.lower())

        if state not in (AnimationState.WALK, AnimationState.RUN):
            raise ValueError("El estado de movimiento no es válido.")

        start = tuple(start)
        end = tuple(end)

        if len(start) != 2 or len(end) != 2:
            raise ValueError("Las posiciones deben tener dos coordenadas.")

        distance = max(
            abs(end[0] - start[0]),
            abs(end[1] - start[1]),
        )

        if distance == 0:
            return

        record = self._get_or_create(creature)

        duration_per_tile = (
            self.RUN_MS_PER_TILE
            if state is AnimationState.RUN
            else self.WALK_MS_PER_TILE
        )

        duration = duration_per_tile * distance

        record.movement_queue.append(
            (start, end, duration, state)
        )

        if record.visual_position is None:
            record.visual_position = (
                float(start[0]),
                float(start[1]),
            )
            record.movement_elapsed_ms = 0.0

        self.set_state(creature, state)

    def get_visual_position(self, creature):
        """Devuelve la posición interpolada o la posición real de la criatura."""

        record = self._get_or_create(creature)

        if record.visual_position is not None:
            return record.visual_position

        return float(creature.x), float(creature.y)

    def get_state(self, creature):
        return self._get_or_create(creature).state_machine.current_state

    def get_frame(self, creature):
        return self._get_or_create(creature).frame_index

    def get_definition(self, creature, state=None):
        record = self._get_or_create(creature)
        state = state or record.state_machine.current_state

        return self.config.get(creature.name, state)

    def _update_movement(self, record, delta_ms):
        """Avanza el recorrido visual, incluyendo varios segmentos pendientes."""

        remaining_ms = delta_ms

        while record.movement_queue and remaining_ms > 0:
            start, end, duration, _ = record.movement_queue[0]

            available_ms = duration - record.movement_elapsed_ms
            consumed_ms = min(remaining_ms, available_ms)

            record.movement_elapsed_ms += consumed_ms
            remaining_ms -= consumed_ms

            progress = min(
                1.0,
                record.movement_elapsed_ms / duration,
            )

            x = start[0] + (end[0] - start[0]) * progress
            y = start[1] + (end[1] - start[1]) * progress

            record.visual_position = (x, y)

            if progress >= 1.0:
                record.visual_position = (
                    float(end[0]),
                    float(end[1]),
                )
                record.movement_queue.popleft()
                record.movement_elapsed_ms = 0.0

        if not record.movement_queue:
            record.visual_position = None
            record.movement_elapsed_ms = 0.0

            current_state = record.state_machine.current_state

            if current_state in (
                AnimationState.WALK,
                AnimationState.RUN,
            ):
                self.set_state(
                    record.creature,
                    AnimationState.IDLE,
                    force=True,
                )

    def update(self, delta_time):
        """Actualiza desplazamientos y fotogramas usando delta_time en segundos."""

        if delta_time < 0:
            raise ValueError(
                "El tiempo transcurrido no puede ser negativo."
            )

        delta_ms = delta_time * 1000.0

        for record in tuple(self._creatures.values()):
            self._update_movement(record, delta_ms)

            state = record.state_machine.current_state
            definition = self.config.get(record.creature.name, state)

            if record.finished:
                continue

            record.elapsed_ms += delta_ms

            while record.elapsed_ms >= definition.frame_duration:
                record.elapsed_ms -= definition.frame_duration

                if record.frame_index + 1 < definition.frame_count:
                    record.frame_index += 1
                    continue

                if definition.loop:
                    record.frame_index = 0
                    continue

                if state is AnimationState.DEATH:
                    record.frame_index = definition.frame_count - 1
                    record.finished = True
                else:
                    # Si termina el daño y todavía hay un desplazamiento
                    # pendiente, recuperamos su estado visual.
                    if (
                        state is AnimationState.HURT
                        and record.movement_queue
                    ):
                        movement_state = (
                            record.movement_queue[0][3]
                        )

                        self.set_state(
                            record.creature,
                            movement_state,
                            force=True,
                        )
                    else:
                        record.state_machine.finish_animation()

                    record.frame_index = 0
                    record.elapsed_ms = 0.0

                break

    def iter_death_animations(self):
        """Devuelve criaturas retiradas del mundo cuya muerte sigue pendiente."""

        for record in tuple(self._creatures.values()):
            if record.state_machine.is_dead:
                yield (
                    record.creature,
                    record.frame_index,
                    record.finished,
                )

    def remove_creature(self, creature):
        self._creatures.pop(self._key(creature), None)

    def prune(self, living_creatures):
        """Libera registros de criaturas ausentes que no estén muriendo."""

        living_ids = {
            id(creature)
            for creature in living_creatures
        }

        for key, record in tuple(self._creatures.items()):
            if (
                key not in living_ids
                and not record.state_machine.is_dead
            ):
                self._creatures.pop(key, None)
