
from instinct.frontend.animation.animation_state import AnimationState


class EventAdapter:
    """Convierte ActionEventLog en cambios de estado y movimiento visual."""

    def __init__(self, action_event_log, animation_controller):
        if action_event_log is None:
            raise ValueError(
                "Se necesita un registro de eventos de acciones."
            )

        if animation_controller is None:
            raise ValueError(
                "Se necesita un controlador de animaciones."
            )

        self.action_event_log = action_event_log
        self.animation_controller = animation_controller
        self.cursor = 0

    def process_new_events(self):
        """Consume exactamente una vez todos los eventos nuevos."""

        events = self.action_event_log.get_since(self.cursor)

        for event in events:
            self._process_event(event)

        self.cursor += len(events)

        return len(events)

    def _set(self, creature, state, force=False):
        if creature is not None:
            self.animation_controller.set_state(
                creature,
                state,
                force=force,
            )

    def _process_event(self, event):
        event_type = event.event_type.lower()

        actor = event.actor_ref
        target = event.target_ref
        data = event.data or {}

        if event_type == "move":
            if actor is None:
                return

            start = data.get("start")
            end = data.get("end")

            distance = data.get("distance", 1)

            state = (
                AnimationState.RUN
                if distance > 1
                else AnimationState.WALK
            )

            if start is not None and end is not None:
                self.animation_controller.start_movement(
                    actor,
                    start,
                    end,
                    state,
                )
            else:
                self._set(actor, state)

            return

        if event_type == "attack":
            self._set(actor, AnimationState.ATTACK)
            return

        if event_type == "damage":
            self._set(target, AnimationState.HURT)
            return

        if event_type == "death":
            # En combate muere el objetivo; por causas naturales, el actor.
            deceased = target if target is not None else actor

            self._set(
                deceased,
                AnimationState.DEATH,
                force=True,
            )
            return
           

        if event_type == "consume":
            self._set(actor, AnimationState.CONSUME)
            return

        if event_type == "reproduce":
            self._set(actor, AnimationState.REPRODUCE)
            return

        if event_type == "roar":
            self._set(actor, AnimationState.ROAR)
