
"""
Entidades que pueden existir en el mundo de Instinct.

Terrain: terreno que recupera sus recursos con el paso de los ticks.
WorldObject: objeto con propiedades de consumo y destrucción.
Creature: criatura que participa en la simulación.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from instinct.runtime.program import Program


@dataclass
class ResourceEntity:
    """Entidad que posee una reserva limitada de recursos."""

    name: str
    char: str
    resource_max: int
    reserve: int | None = None

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("El nombre de la entidad no puede estar vacío.")

        if len(self.char) != 1:
            raise ValueError(
                "El símbolo de la entidad debe ser exactamente un carácter."
            )

        if not isinstance(self.resource_max, int) or isinstance(
            self.resource_max, bool
        ):
            raise TypeError("La reserva máxima debe ser un número entero.")

        if self.resource_max < 0:
            raise ValueError("La reserva máxima no puede ser negativa.")

        if self.reserve is None:
            self.reserve = self.resource_max

        if not isinstance(self.reserve, int) or isinstance(self.reserve, bool):
            raise TypeError("La reserva debe ser un número entero.")

        if not 0 <= self.reserve <= self.resource_max:
            raise ValueError(
                "La reserva debe estar entre cero y la reserva máxima."
            )


@dataclass
class Terrain(ResourceEntity):
    """Terreno que regenera sus recursos durante la simulación."""

    regen: int = 0
    walkable: bool = True

    def __post_init__(self) -> None:
        super().__post_init__()

        if not isinstance(self.regen, int) or isinstance(self.regen, bool):
            raise TypeError("La regeneración debe ser un número entero.")

        if self.regen < 0:
            raise ValueError("La regeneración no puede ser negativa.")

        if not isinstance(self.walkable, bool):
            raise TypeError("La propiedad 'walkable' debe ser booleana.")


@dataclass
class WorldObject(ResourceEntity):
    """Objeto del mundo con propiedades independientes de consumo y daño."""

    description: str = ""
    consumable: bool = True
    destructible: bool = True

    def __post_init__(self) -> None:
        super().__post_init__()

        if not isinstance(self.description, str):
            raise TypeError("La descripción del objeto debe ser texto.")

        if not isinstance(self.consumable, bool):
            raise TypeError(
                "La propiedad 'consumable' debe ser booleana."
            )

        if not isinstance(self.destructible, bool):
            raise TypeError(
                "La propiedad 'destructible' debe ser booleana."
            )


@dataclass
class Building:
    """Estructura del mundo con huella lógica y dimensiones visuales."""

    name: str
    char: str
    width: int
    height: int
    asset: str
    walkable: tuple[tuple[bool, ...], ...]

    # Dimensiones visuales expresadas en tiles.
    visual_width: int | None = None
    visual_height: int | None = None

    # Coordenadas de origen dentro del mapa.
    x: int = 0
    y: int = 0

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("El nombre del edificio no puede estar vacío.")

        if not isinstance(self.char, str) or len(self.char) != 1:
            raise ValueError(
                "El símbolo del edificio debe ser exactamente un carácter."
            )

        integer_fields = {
            "El ancho": self.width,
            "El alto": self.height,
            "La coordenada x": self.x,
            "La coordenada y": self.y,
        }

        for field_name, value in integer_fields.items():
            if not isinstance(value, int) or isinstance(value, bool):
                raise TypeError(f"{field_name} debe ser un número entero.")

        if self.width <= 0 or self.height <= 0:
            raise ValueError(
                "Las dimensiones del edificio deben ser mayores que cero."
            )

        if not isinstance(self.asset, str) or not self.asset.strip():
            raise ValueError("El recurso gráfico del edificio es obligatorio.")

        if not isinstance(self.walkable, (tuple, list)):
            raise TypeError("La matriz de transitabilidad debe ser una matriz.")

        if len(self.walkable) != self.height:
            raise ValueError(
                "La matriz de transitabilidad debe tener tantas filas "
                "como indique el alto del edificio."
            )

        normalized_walkable = []

        for row in self.walkable:
            if not isinstance(row, (tuple, list)):
                raise TypeError(
                    "Cada fila de transitabilidad debe ser una secuencia."
                )

            if len(row) != self.width:
                raise ValueError(
                    "Cada fila de transitabilidad debe tener tantos valores "
                    "como indique el ancho del edificio."
                )

            if not all(isinstance(value, bool) for value in row):
                raise TypeError(
                    "Los valores de transitabilidad deben ser booleanos."
                )

            normalized_walkable.append(tuple(row))

        self.walkable = tuple(normalized_walkable)

        if self.visual_width is None:
            self.visual_width = self.width

        if self.visual_height is None:
            self.visual_height = self.height

        for field_name, value in {
            "El ancho visual": self.visual_width,
            "El alto visual": self.visual_height,
        }.items():
            if not isinstance(value, int) or isinstance(value, bool):
                raise TypeError(f"{field_name} debe ser un número entero.")

            if value <= 0:
                raise ValueError(
                    f"{field_name} debe ser mayor que cero."
                )


    def is_walkable_at(self, x: int, y: int) -> bool:
        """Indica si una posición local de la estructura es transitable."""

        if not (0 <= x < self.width and 0 <= y < self.height):
            raise IndexError(
                "La posición está fuera de la huella del edificio."
            )

        return self.walkable[y][x]



@dataclass
class Creature:
    """Criatura individual que participa en la simulación."""

    name: str
    faction: str
    health: int
    vision: int
    lifespan: int
    x: int = 0
    y: int = 0
    age: int = 0
    program: "Program | None" = None
    max_health: int = 0
    can_reproduce: bool = True

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("El nombre de la criatura no puede estar vacío.")

        if not self.faction:
            raise ValueError("La facción de la criatura no puede estar vacía.")

        integer_fields = {
            "La vida": self.health,
            "La visión": self.vision,
            "La esperanza de vida": self.lifespan,
            "La coordenada x": self.x,
            "La coordenada y": self.y,
            "La edad": self.age,
        }

        for field_name, value in integer_fields.items():
            if not isinstance(value, int) or isinstance(value, bool):
                raise TypeError(f"{field_name} debe ser un número entero.")

        if self.health <= 0:
            raise ValueError("La vida inicial debe ser mayor que cero.")

        if self.vision < 1:
            raise ValueError("La visión debe ser como mínimo uno.")

        if self.lifespan <= 0:
            raise ValueError("La esperanza de vida debe ser mayor que cero.")

        if self.age < 0:
            raise ValueError("La edad no puede ser negativa.")

        # Guardamos la vida inicial como límite de recuperación.
        if self.max_health == 0:
            self.max_health = self.health
        elif (
            not isinstance(self.max_health, int)
            or isinstance(self.max_health, bool)
        ):
            raise TypeError("La vida máxima debe ser un número entero.")

        if self.max_health < self.health or self.max_health <= 0:
            raise ValueError(
                "La vida máxima debe ser positiva y no inferior "
                "a la vida inicial."
            )

        # La capacidad de reproducción debe ser un valor booleano.
        if not isinstance(self.can_reproduce, bool):
            raise TypeError(
                "La disponibilidad de reproducción debe ser booleana."
            )