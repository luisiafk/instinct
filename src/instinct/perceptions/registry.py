
"""Registro y actualización de percepciones de Instinct."""

from weakref import WeakKeyDictionary

from instinct.perceptions.base import PerceptionValue
from instinct.perceptions.nearby_perceptions import NearbyPerceptions
from instinct.perceptions.self_perceptions import SelfPerceptions
from instinct.perceptions.world_perceptions import WorldPerceptions
from instinct.runtime.execution_context import ExecutionContext
from instinct.world.constants import SeeResult


class PerceptionRegistry:
    """Administra las percepciones de las criaturas."""

    def __init__(self) -> None:
        self._groups = (
            SelfPerceptions(),
            WorldPerceptions(),
            NearbyPerceptions(),
        )

        # Cada contexto conserva su propio conjunto de percepciones.
        self._values: WeakKeyDictionary[
            ExecutionContext,
            dict[str, PerceptionValue],
        ] = WeakKeyDictionary()

        self._constants: dict[str, int] = {
            "NONE": SeeResult.NONE,
            "GROUND": SeeResult.GROUND,
            "OBJECT": SeeResult.OBJECT,
            "ALLY": SeeResult.ALLY,
            "ENEMY": SeeResult.ENEMY,
        }

    def update(self, context: ExecutionContext) -> None:
        """Actualiza las percepciones al comienzo de un turno."""

        if not isinstance(context, ExecutionContext):
            raise TypeError("El contexto de ejecución no es válido.")

        values: dict[str, PerceptionValue] = {}

        for group in self._groups:
            group_values = group.calculate(context)

            duplicated = values.keys() & group_values.keys()

            if duplicated:
                names = ", ".join(sorted(duplicated))
                raise RuntimeError(
                    f"Error de ejecución: hay percepciones duplicadas: {names}."
                )

            values.update(group_values)

        self._values[context] = values

    def get(
        self,
        context: ExecutionContext,
        name: str,
    ) -> PerceptionValue:
        """Obtiene una percepción o constante."""

        if name in self._constants:
            return self._constants[name]

        # random se calcula en cada lectura, no en update().
        if name == "random":
            return context.rng.randint(0, 99)

        if context not in self._values:
            raise RuntimeError(
                "Error de ejecución: las percepciones de la criatura "
                "todavía no han sido actualizadas."
            )

        values = self._values[context]

        if name not in values:
            raise RuntimeError(
                f"Error de ejecución: la percepción '{name}' no existe."
            )

        return values[name]

    def has_perception(self, name: str) -> bool:
        """Comprueba si el nombre pertenece al catálogo."""

        return name in {
            "NONE", "GROUND", "OBJECT", "ALLY", "ENEMY",
            "random",
            "health", "age", "lifespan", "vision",
            "species", "faction", "x", "y",
            "terrain_here", "reserve_here",
            "width", "height", "tick",
            "total_creatures", "total_allies", "total_enemies",
            "allies_near", "enemies_near", "objects_near", "consumables_near",
            "ally_dist", "ally_dx", "ally_dy",
            "enemy_dist", "enemy_dx", "enemy_dy",
            "object_dist", "object_dx", "object_dy",
            "consumable_dist", "consumable_dx", "consumable_dy",
            "roars_near", "last_roar",
        }

    def clear(self, context: ExecutionContext) -> None:
        """Elimina las percepciones almacenadas de un contexto."""
        self._values.pop(context, None)
