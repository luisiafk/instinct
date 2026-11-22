from pathlib import Path
from typing import ClassVar, NoReturn

from instinct.world.entities import Building


class BuildingLoader:
    """Carga y valida definiciones de estructuras desde archivos .bld."""

    REQUIRED_FIELDS: ClassVar[set[str]] = {
        "char",
        "width",
        "height",
        "asset",
        "walkable",
    }

    OPTIONAL_FIELDS: ClassVar[set[str]] = {
        "visual_width",
        "visual_height",
    }

    def load_file(self, filepath: str | Path) -> Building:
        """Lee un archivo .bld y devuelve el edificio definido en él."""

        path = Path(filepath)

        try:
            content = path.read_text(encoding="utf-8")
        except FileNotFoundError as error:
            raise ValueError(
                f"No se encontró el archivo de edificio: '{path}'."
            ) from error
        except UnicodeDecodeError as error:
            raise ValueError(
                f"El archivo de edificio '{path}' no contiene texto UTF-8 válido."
            ) from error
        except OSError as error:
            raise ValueError(
                f"No se pudo leer el archivo de edificio '{path}': {error}."
            ) from error

        return self.load_string(content, source=str(path))

    def load_string(
        self,
        content: str,
        source: str = "<memoria>",
    ) -> Building:
        """Analiza el contenido de una definición .bld."""

        if not isinstance(content, str):
            raise TypeError("El contenido del edificio debe ser texto.")

        lines = content.splitlines()
        declaration = None
        declaration_line = 0
        fields: dict[str, tuple[str, int]] = {}

        allowed_fields = self.REQUIRED_FIELDS | self.OPTIONAL_FIELDS

        for line_number, raw_line in enumerate(lines, start=1):
            line = raw_line.strip()

            if not line or line.startswith("#"):
                continue

            parts = line.split(maxsplit=1)
            key = parts[0]

            if declaration is None:
                if key != "building" or len(parts) != 2:
                    self._error(
                        source,
                        line_number,
                        "Se esperaba una declaración 'building Nombre'.",
                    )

                name = parts[1].strip()

                if not name or len(name.split()) != 1:
                    self._error(
                        source,
                        line_number,
                        "El nombre del edificio debe ser una sola palabra.",
                    )

                declaration = name
                declaration_line = line_number
                continue

            if key not in allowed_fields:
                self._error(
                    source,
                    line_number,
                    f"Propiedad desconocida '{key}' en el edificio.",
                )

            if key in fields:
                self._error(
                    source,
                    line_number,
                    f"La propiedad '{key}' está duplicada.",
                )

            if len(parts) != 2 or not parts[1].strip():
                self._error(
                    source,
                    line_number,
                    f"Falta el valor de la propiedad '{key}'.",
                )

            fields[key] = (parts[1].strip(), line_number)

        if declaration is None:
            self._error(
                source,
                1,
                "El archivo no declara ningún edificio.",
            )

        for field in self.REQUIRED_FIELDS:
            if field not in fields:
                self._error(
                    source,
                    declaration_line,
                    f"Falta la propiedad obligatoria '{field}'.",
                )

        char = fields["char"][0]

        if len(char) != 1:
            self._error(
                source,
                fields["char"][1],
                "El carácter del edificio debe tener exactamente un símbolo.",
            )

        width = self._parse_integer(
            fields["width"],
            "width",
            source,
        )

        height = self._parse_integer(
            fields["height"],
            "height",
            source,
        )

        if width <= 0:
            self._error(
                source,
                fields["width"][1],
                "'width' debe ser mayor que cero.",
            )

        if height <= 0:
            self._error(
                source,
                fields["height"][1],
                "'height' debe ser mayor que cero.",
            )

        asset = fields["asset"][0]

        walkable = self._parse_walkable(
            fields["walkable"],
            width,
            height,
            source,
        )

        visual_width = self._parse_optional_dimension(
            fields,
            "visual_width",
            width,
            source,
        )

        visual_height = self._parse_optional_dimension(
            fields,
            "visual_height",
            height,
            source,
        )

        return Building(
            name=declaration,
            char=char,
            width=width,
            height=height,
            asset=asset,
            walkable=walkable,
            visual_width=visual_width,
            visual_height=visual_height,
        )

    @staticmethod
    def _parse_integer(
        field_data: tuple[str, int],
        field: str,
        source: str,
    ) -> int:
        value, line_number = field_data

        try:
            return int(value)
        except ValueError:
            raise ValueError(
                f"Error en '{source}', línea {line_number}: "
                f"'{field}' debe ser un número entero."
            ) from None

    @staticmethod
    def _parse_optional_dimension(
        fields: dict[str, tuple[str, int]],
        field: str,
        default: int,
        source: str,
    ) -> int:
        if field not in fields:
            return default

        value = BuildingLoader._parse_integer(
            fields[field],
            field,
            source,
        )

        if value <= 0:
            BuildingLoader._error(
                source,
                fields[field][1],
                f"'{field}' debe ser mayor que cero.",
            )

        return value

    @staticmethod
    def _parse_walkable(
        field_data: tuple[str, int],
        width: int,
        height: int,
        source: str,
    ) -> tuple[tuple[bool, ...], ...]:
        value, line_number = field_data

        rows = value.split(";")

        if len(rows) != height:
            BuildingLoader._error(
                source,
                line_number,
                "'walkable' debe tener tantas filas como indique 'height'.",
            )

        matrix = []

        for row_number, row in enumerate(rows, start=1):
            values = row.split()

            if len(values) != width:
                BuildingLoader._error(
                    source,
                    line_number,
                    f"La fila {row_number} de 'walkable' debe tener "
                    f"{width} valores.",
                )

            parsed_row = []

            for item in values:
                normalized = item.lower()

                if normalized == "true":
                    parsed_row.append(True)
                elif normalized == "false":
                    parsed_row.append(False)
                else:
                    BuildingLoader._error(
                        source,
                        line_number,
                        "'walkable' solo admite los valores "
                        "'true' y 'false'.",
                    )

            matrix.append(tuple(parsed_row))

        return tuple(matrix)

    @staticmethod
    def _error(source: str, line: int, message: str) -> NoReturn:
        raise ValueError(
            f"Error en '{source}', línea {line}: {message}"
        )
