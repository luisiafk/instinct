# Instinct 🧬

Instinct es un motor de simulación y un lenguaje de dominio específico (DSL) diseñado para programar el comportamiento autónomo de criaturas y entidades dentro de entornos cuadriculados. El proyecto integra un compilador completo desde cero (Lexer, Parser y Analizador Semántico) junto con un bucle de simulación visual en tiempo real.

## 🏗️ Arquitectura del Proyecto

El proyecto sigue una estructura limpia modularizada bajo la carpeta src/instinct, separando claramente el motor de compilación del núcleo de simulación y la interfaz gráfica:

```text
instinct/
├── src/
│   └── instinct/
│       ├── scripts/
|           ├── depredador.ins #Depredador en lenguaje instinct
|           └── recolector.ins #Recolector en lenguaje instinct
|       ├── maps/
|           ├── loaders.py     # Cargadores de archivos de configuración y escenarios
|            ....              # Algunos mapas genericos
|           └── bosque.map     # Mapa generico del bosque
|       ├── objects/
|           └── objetos.ob     # Objetos que pueden aparecer en el mapa
|       ├── terrains/
|            └── terrenos.te   # Tipos de terrenos
│       ├── backend/           # Componentes del compilador
│       │   ├── lexer.py       # Análisis léxico y manejo de tokens
│       │   ├── parser.py      # Generación del Árbol de Sintaxis Abstracta (AST)
│       │   └── semantic.py    # Analizador semántico y validación de tipos/entorno
│       ├── actions.py         # Acciones ejecutables por las entidades (move, consume, say, etc.)
│       ├── entities.py        # Definición, atributos y ciclo de vida de las criaturas
│       ├── grid.py            # Gestión espacial y coordenadas de la grilla

│       ├── perceptions.py     # Sensores del entorno (see, enemy_dist, aliados cercanos)
│       ├── simulation.py      # Orquestador del bucle principal de simulación
│       └── ui.py              # Interfaz gráfica y renderizado visual (Pygame)
├── tests/                     # Pruebas unitarias e integración del compilador
├── pyproject.toml             # Configuración del proyecto y dependencias (uv)
└── README.md
```

## Caracteristicas Principales

- **Lenguaje DSL propio (`Instinct`):** Sintaxis orientada a reglas de supervivencia con soporte para etiquetas(`labels`), saltos condicionales (`if ... got`), operadores unarios, llamadas de funciones de entorno y manejo de comentarios.
- **Analizador Semantico Robusto:** Valida variables globales de cabecera (`health`, `vision`, `faction`), sensores integrados del motor (`enemy_dist`, `enemy_dx`, `enemy_dy`, `x`, `y`) y previene el uso de variables no declaradas o etiquetas duplicadas.
- **Simulacion en Tiempo Real:** Visualizacion interactiva mediante `Pygame` donde las criaturas evaluan sus scripts de comportamiento iterativamente.

## Requisitos e Instalacion

Este proyecto utiliza `uv` como gestor de paquetes. Asegurate de tenerlo instalado en tu sistema.

1. Clona el repositorio en tu maquina local:

    ```bash
        git clone https://github.com/luisiafk/instinct.git
        cd instinct
    ```

2. Sincroniza y configura el entorno con las dependencias del proyecto:

    ```bash
        uv sync
    ```

### Ejecucion

Para poner en marcha la simulacion grafica e interactiva del entorno:

```bash
    uv run pyhton src/instinct/main.py
```
## Para agregar nuevas criaturas se deben agregar en `src/scripts/criatura.ins` siguiendo las reglasd del lenguaje instinct

### Tests

Para ejecutar la suite de pruebas automatizadas del analizador lexico, sintactico y semantico:

```bash
uv run pytest
```

## Contribucion y Flujo de Trabajo

- No se sube codigo directament a la rama `main`.

- Trabaja siempre en una rama de caracteristicas (ej. `feature/nombre-de-la-tarea`).

- Abre un **Pull Request** vinculado a su respectiva **Issue** (utilizando palabras claves como `Close #x`) para la revision de codigo por parte del equipo.

---

Made with instinct <3 xd.
