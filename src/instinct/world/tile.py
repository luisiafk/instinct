
"""
Representación de una casilla del mundo de Instinct.

Cada casilla contiene un terreno y puede contener un objeto,
una criatura o formar parte de un edificio.
"""

from dataclasses import dataclass, field

from instinct.world.entities import Building, Creature, Terrain, WorldObject


@dataclass
class Tile:
    """Casilla individual del mundo."""

    terrain: Terrain
    _object: WorldObject | None = field(default=None, repr=False)
    _creature: Creature | None = field(default=None, repr=False)
    building: Building | None = field(default=None, repr=False)
    building_offset: tuple[int, int] | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if not isinstance(self.terrain, Terrain):
            raise TypeError("Una casilla debe tener un terreno válido.")

        if self._object is not None and not isinstance(
            self._object, WorldObject
        ):
            raise TypeError("El contenido debe ser un objeto válido.")

        if self._creature is not None and not isinstance(
            self._creature, Creature
        ):
            raise TypeError("El contenido debe ser una criatura válida.")

        if self.building is not None and not isinstance(
            self.building, Building
        ):
            raise TypeError("El edificio de la casilla no es válido.")

        if self._object is not None and self._creature is not None:
            raise ValueError(
                "Una casilla no puede contener un objeto "
                "y una criatura a la vez."
            )

        if self.building is None and self.building_offset is not None:
            raise ValueError(
                "Una casilla sin edificio no puede tener un desplazamiento."
            )

        if self.building is not None:
            if self.building_offset is None:
                raise ValueError(
                    "Una casilla con edificio debe tener un desplazamiento."
                )

            self._validate_building_offset(
                self.building,
                *self.building_offset,
            )

            if self._object is not None or self._creature is not None:
                raise ValueError(
                    "No se puede colocar un edificio sobre "
                    "una casilla que ya contiene algo."
                )

    @property
    def object(self) -> WorldObject | None:
        """Devuelve el objeto de la casilla, si existe."""
        return self._object

    @property
    def creature(self) -> Creature | None:
        """Devuelve la criatura de la casilla, si existe."""
        return self._creature

    @property
    def has_building(self) -> bool:
        """Indica si la casilla forma parte de un edificio."""
        return self.building is not None

    @property
    def is_occupied(self) -> bool:
        """Indica si la casilla está bloqueada para el movimiento."""
        if self._object is not None or self._creature is not None:
            return True

        if self.building is None:
            return False

        offset_x, offset_y = self.building_offset
        return not self.building.is_walkable_at(offset_x, offset_y)

    @property
    def occupant(self) -> WorldObject | Creature | None:
        """Devuelve el objeto o criatura de la casilla."""
        if self._object is not None:
            return self._object

        return self._creature


    def _validate_building_offset(
        self,
        building: Building,
        offset_x: int,
        offset_y: int,
    ) -> None:
        if (
            not isinstance(offset_x, int)
            or isinstance(offset_x, bool)
            or not isinstance(offset_y, int)
            or isinstance(offset_y, bool)
        ):
            raise TypeError(
                "Los desplazamientos del edificio deben ser enteros."
            )

        if not (
            0 <= offset_x < building.width
            and 0 <= offset_y < building.height
        ):
            raise ValueError(
                "El desplazamiento está fuera de la huella del edificio."
            )

    def set_building(
        self,
        building: Building,
        offset_x: int,
        offset_y: int,
    ) -> None:
        """Asigna el edificio y su posición relativa dentro de la huella."""
        if not isinstance(building, Building):
            raise TypeError("Solo se pueden colocar edificios válidos.")

        if self.building is not None:
            raise ValueError("La casilla ya pertenece a un edificio.")

        if self._object is not None or self._creature is not None:
            raise ValueError(
                "No se puede colocar un edificio sobre una casilla ocupada."
            )

        self._validate_building_offset(
            building,
            offset_x,
            offset_y,
        )

        self.building = building
        self.building_offset = (offset_x, offset_y)

    def set_object(self, obj: WorldObject) -> None:
        """Coloca un objeto si la casilla está libre de edificios y ocupantes."""
        if not isinstance(obj, WorldObject):
            raise TypeError("Solo se pueden colocar objetos válidos.")

        if self.is_occupied or self.has_building:
            raise ValueError("La casilla ya está ocupada.")

        self._object = obj

    def set_creature(self, creature: Creature) -> None:
        """Coloca una criatura si la casilla permite el movimiento."""
        if not isinstance(creature, Creature):
            raise TypeError("Solo se pueden colocar criaturas válidas.")

        if self.is_occupied:
            raise ValueError("La casilla está ocupada o no es transitable.")

        self._creature = creature

    def remove_object(self) -> WorldObject | None:
        """Retira y devuelve el objeto de la casilla."""
        obj = self._object
        self._object = None
        return obj

    def remove_creature(self) -> Creature | None:
        """Retira y devuelve la criatura de la casilla."""
        creature = self._creature
        self._creature = None
        return creature
