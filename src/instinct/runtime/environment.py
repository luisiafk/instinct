
"""
Entorno de ejecución de Instinct.

Almacena las variables de una criatura y conserva sus valores
durante toda la simulación.
"""

class Environment:
    """Administra las variables de una criatura."""

    def __init__(self) -> None:
        self._variables: dict[str, int | str] = {}

    @property
    def variables(self) -> dict[str, int | str]:
        """Devuelve una copia de las variables almacenadas."""
        return self._variables.copy()

    def set_variable(self, name: str, value: int | str) -> None:
        """Crea o actualiza una variable."""

        if not isinstance(name, str) or not name:
            raise ValueError("El nombre de la variable no es válido.")

        if isinstance(value, bool) or not isinstance(value, (int, str)):
            raise TypeError(
                "Una variable solo puede almacenar números enteros o textos."
            )

        self._variables[name] = value

    def get_variable(self, name: str) -> int | str:
        """Obtiene el valor de una variable."""

        if name not in self._variables:
            raise RuntimeError(
                f"Error de ejecución: la variable '{name}' no ha sido inicializada."
            )

        return self._variables[name]

    def has_variable(self, name: str) -> bool:
        """Comprueba si una variable ha sido inicializada."""
        return name in self._variables

    def clear(self) -> None:
        """Elimina todas las variables del entorno."""
        self._variables.clear()

    def __len__(self) -> int:
        """Devuelve la cantidad de variables almacenadas."""
        return len(self._variables)
