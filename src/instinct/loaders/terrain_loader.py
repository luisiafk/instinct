from pathlib import Path
from typing import ClassVar, NoReturn

from instinct.world.entities import Terrain


class TerrainLoader:
    """Carga y valida definiciones de terrenos desde archivos .te."""

    REQUIRED_FIELDS: ClassVar[set[str]] = {"char", "resource_max", "regen", "walkable"}

    def load_file(self, filepath: str | Path) -> Terrain:
        """Lee un archivo .te y devuelve el terreno definido en él."""
        path = Path(filepath)

        try:
            content = path.read_text(encoding="utf-8")
        except FileNotFoundError as error:
            raise ValueError(
                f"No se encontró el archivo de terreno: '{path}'."
            ) from error
        except UnicodeDecodeError as error:
            raise ValueError(
                f"El archivo de terreno '{path}' no contiene texto UTF-8 válido."
            ) from error
        except OSError as error:
            raise ValueError(
                f"No se pudo leer el archivo de terreno '{path}': {error}."
            ) from error

        return self.load_string(content, source=str(path))

    def load_string(
        self,
        content: str,
        source: str = "<memoria>",
    ) -> Terrain:
        """Analiza el contenido de un archivo .te."""

        if not isinstance(content, str):
            raise TypeError("El contenido del terreno debe ser texto.")

        lines = content.splitlines()
        declaration = None
        declaration_line = 0
        fields: dict[str, tuple[str, int]] = {}

        for line_number, raw_line in enumerate(lines, start=1):
            line = raw_line.strip()

            # Ignorar líneas vacías y comentarios completos.
            if not line or line.startswith("#"):
                continue

            parts = line.split(maxsplit=1)
            key = parts[0]

            if declaration is None:
                if key != "terrain" or len(parts) != 2:
                    self._error(
                        source,
                        line_number,
                        "Se esperaba una declaración 'terrain Nombre'.",
                    )

                name = parts[1].strip()

                if not name or len(name.split()) != 1:
                    self._error(
                        source,
                        line_number,
                        "El nombre del terreno debe ser una sola palabra.",
                    )

                declaration = name
                declaration_line = line_number
                continue

            if key not in self.REQUIRED_FIELDS:
                self._error(
                    source,
                    line_number,
                    f"Propiedad desconocida '{key}' en el terreno.",
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
            self._error(source, 1, "El archivo no declara ningún terreno.")

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
                "El carácter del terreno debe tener exactamente un símbolo.",
            )

        resource_max = self._parse_integer(
            fields["resource_max"][0],
            "resource_max",
            source,
            fields["resource_max"][1],
        )

        regen = self._parse_integer(
            fields["regen"][0],
            "regen",
            source,
            fields["regen"][1],
        )

        if resource_max < 0:
            self._error(
                source,
                fields["resource_max"][1],
                "'resource_max' no puede ser negativo.",
            )

        if regen < 0:
            self._error(
                source,
                fields["regen"][1],
                "'regen' no puede ser negativo.",
            )

        walkable = True

        if "walkable" in fields:
            value, line_number = fields["walkable"]

            if value.lower() not in {"true", "false"}:
                self._error(
                    source,
                    line_number,
                    "'walkable' debe ser true o false.",
                )

            walkable = value.lower() == "true"

        return Terrain(
            name=declaration,
            char=char,
            resource_max=resource_max,
            regen=regen,
            walkable=walkable,
        )

    @staticmethod
    def _parse_integer(
        value: str,
        field: str,
        source: str,
        line_number: int,
    ) -> int:
        try:
            return int(value)
        except ValueError:
            raise ValueError(
                f"Error en '{source}', línea {line_number}: "
                f"'{field}' debe ser un número entero."
            ) from None

    @staticmethod
    def _error(source: str, line: int, message: str) -> NoReturn:
        raise ValueError(
            f"Error en '{source}', línea {line}: {message}"
        )
