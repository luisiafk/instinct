"""
Registro de acontecimientos de la simulación de Instinct.

Centraliza los mensajes producidos durante la ejecución
para que puedan consultarse desde el frontend.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Event:
    """Representa un acontecimiento de la simulación."""

    tick: int
    message: str
    category: str
    timestamp: datetime
    x: int | None = None
    y: int | None = None


class EventLog:
    """Almacena los acontecimientos de la simulación."""

    def __init__(self) -> None:
        self._events: list[Event] = []

    def add(
        self,
        tick: int,
        message: str,
        category: str = "general",
        x: int | None = None,
        y: int | None = None,
    ) -> Event:
        """Registra un nuevo acontecimiento."""

        if not isinstance(tick, int) or isinstance(tick, bool):
            raise TypeError("El número de tick debe ser un entero.")

        if tick < 0:
            raise ValueError("El número de tick no puede ser negativo.")

        if not isinstance(message, str):
            raise TypeError("El mensaje del acontecimiento debe ser texto.")

        if not isinstance(category, str):
            raise TypeError("La categoría del acontecimiento debe ser texto.")

        if (x is None) != (y is None):
            raise ValueError(
                "Las coordenadas del acontecimiento deben proporcionarse juntas."
            )

        if x is not None:
            if not isinstance(x, int) or isinstance(x, bool):
                raise TypeError("La coordenada x debe ser un entero.")

            if not isinstance(y, int) or isinstance(y, bool):
                raise TypeError("La coordenada y debe ser un entero.")

        event = Event(
            tick=tick,
            message=message,
            category=category,
            timestamp=datetime.now(),
            x=x,
            y=y,
        )

        self._events.append(event)
        return event

    @property
    def events(self) -> tuple[Event, ...]:
        """Devuelve una vista inmutable de los acontecimientos."""
        return tuple(self._events)

    def get_by_tick(self, tick: int) -> list[Event]:
        """Obtiene los acontecimientos correspondientes a un tick."""
        return [
            event
            for event in self._events
            if event.tick == tick
        ]

    def get_by_category(self, category: str) -> list[Event]:
        """Obtiene los acontecimientos de una categoría."""
        return [
            event
            for event in self._events
            if event.category == category
        ]

    def clear(self) -> None:
        """Elimina todos los acontecimientos registrados."""
        self._events.clear()

    def __len__(self) -> int:
        return len(self._events)
