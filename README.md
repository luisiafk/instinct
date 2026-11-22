# Instinct

**Instinct** es un entorno de simulación de criaturas autónomas controladas mediante un lenguaje de dominio específico (DSL) propio. Cada criatura ejecuta un programa que determina cómo percibe el entorno y cómo actúa dentro de un mundo organizado en una cuadrícula.

El proyecto combina un compilador desarrollado desde cero, un entorno de ejecución, un motor de simulación por turnos y una interfaz gráfica construida con **Python y Pygame CE**.

> **Estado del proyecto:** en desarrollo activo. El compilador, el runtime y el motor de simulación están implementados. La aplicación gráfica ya integra mundo, criaturas, animaciones, cámara y HUD; la auditoría de integración visual está identificando los últimos ajustes pendientes.

## Contenido

- [Instinct](#instinct)
  - [Contenido](#contenido)
  - [Características](#características)
    - [Lenguaje Instinct](#lenguaje-instinct)
    - [Motor de simulación](#motor-de-simulación)
    - [Interfaz gráfica](#interfaz-gráfica)
  - [Arquitectura](#arquitectura)
    - [Responsabilidades principales](#responsabilidades-principales)
  - [Tecnologías](#tecnologías)
  - [Instalación](#instalación)
  - [Ejecución](#ejecución)
  - [Recursos del mundo](#recursos-del-mundo)
    - [Ejemplo de terreno](#ejemplo-de-terreno)
    - [Ejemplo de objeto](#ejemplo-de-objeto)
    - [Mapas](#mapas)
  - [Pruebas y calidad](#pruebas-y-calidad)
  - [Documentación y seguimiento](#documentación-y-seguimiento)

## Características

### Lenguaje Instinct

- Lenguaje DSL propio para definir el comportamiento de las criaturas.
- Análisis léxico, sintáctico y semántico.
- Construcción y evaluación de un árbol de sintaxis abstracta (AST).
- Ejecución de instrucciones, condiciones, funciones y acciones mediante el runtime.

### Motor de simulación

- Mundo basado en una cuadrícula de casillas.
- Entidades diferenciadas: criaturas, terrenos y objetos.
- Sistema de acciones y percepciones para interactuar con el entorno.
- Simulación organizada en ticks y orden de ejecución administrado por turnos.
- Registro de eventos y aplicación de reglas naturales del mundo.

### Interfaz gráfica

- Aplicación gráfica desarrollada con Pygame CE.
- Menú principal y escena de simulación.
- Renderizado de terrenos, objetos y criaturas.
- Cámara con zoom, desplazamiento y seguimiento de criatura seleccionada.
- Interpolación visual de movimiento vinculada a eventos del motor.
- Máquina de estados de animación independiente por criatura.
- Paneles de información, controles de simulación y registro de eventos.

La interfaz representa visualmente el estado del motor; la lógica de comportamiento y las reglas de simulación pertenecen al núcleo del proyecto.

## Arquitectura

El código fuente se organiza como un paquete Python dentro de `src/instinct/`.

```text
instinct/
├── resources/
│   ├── creatures/       # Programas de criaturas (.ins)
│   ├── maps/            # Definiciones de mapas (.map)
│   ├── objects/         # Definiciones de objetos (.ob)
│   └── terrains/        # Definiciones de terrenos (.te)
├── docs/
│   ├── instinct.pdf     # Documento de orientación del proyecto
│   └── PROGRESS.md      # Seguimiento del desarrollo
├── src/
│   └── instinct/
│       ├── actions/     # Acciones disponibles para las criaturas
│       ├── backend/     # Lexer, parser, AST y análisis semántico
│       ├── engine/      # Simulación, turnos, leyes y eventos
│       ├── frontend/    # Interfaz gráfica, escenas y renderizado
│       ├── functions/   # Funciones y operaciones registradas
│       ├── loaders/     # Carga y validación de recursos
│       ├── perceptions/ # Sensores y percepciones del entorno
│       ├── runtime/     # Entorno de ejecución e intérprete
│       ├── world/       # Entidades, casillas y cuadrícula
│       └── main.py      # Punto de entrada compatible
├── tests/               # Pruebas automatizadas
├── pyproject.toml       # Configuración y dependencias
├── uv.lock
└── README.md
```

### Responsabilidades principales

| Módulo | Responsabilidad |

|---|---|
| `backend` | Convierte el código Instinct en una representación ejecutable y valida su estructura y semántica. |
| `runtime` | Ejecuta los programas y administra su contexto de ejecución. |
| `actions` | Define las acciones que las criaturas pueden realizar. |
| `perceptions` | Proporciona información del entorno y de la propia criatura. |
| `world` | Modela las entidades y la estructura espacial del mundo. |
| `engine` | Coordina los ticks, el orden de ejecución, las reglas naturales y los eventos. |
| `loaders` | Lee y valida las definiciones externas de criaturas, terrenos, objetos y mapas. |
| `frontend` | Presenta el mundo y sus estados mediante la interfaz gráfica. |

## Tecnologías

- **Python 3.13 o superior**
- **Pygame CE** para la interfaz gráfica.
- **uv** para la gestión del entorno y las dependencias.
- **pytest** para las pruebas automatizadas.
- **Ruff** para linting.
- **Mypy** para comprobación estática de tipos.

## Instalación

Instala Python 3.13 o una versión compatible y [uv](https://docs.astral.sh/uv/).

Clona el repositorio:

```bash
git clone https://github.com/luisiafk/instinct.git
cd instinct
```

Crea y sincroniza el entorno:

```bash
uv sync
```

## Ejecución

Desde la raíz del repositorio, cualquiera de estos comandos inicia la aplicación:

```bash
uv run python -m instinct.frontend.app
```

También está disponible el comando instalado por el proyecto:

```bash
uv run instinct
```

Ambas formas de arranque fueron comprobadas y conducen al menú principal de la aplicación.

## Recursos del mundo

Los recursos de la simulación se definen mediante archivos de texto ubicados en `resources/`.

| Extensión | Recurso | Ubicación |

|---|---|---|
| `.ins` | Programa y comportamiento de una criatura | `resources/creatures/` |
| `.te` | Definición de un terreno | `resources/terrains/` |
| `.ob` | Definición de un objeto | `resources/objects/` |
| `.map` | Distribución de casillas del mapa | `resources/maps/` |

### Ejemplo de terreno

Archivo `resources/terrains/grass.te`:

```text
terrain Grass
char .
resource_max 100
regen 2
```

### Ejemplo de objeto

Archivo `resources/objects/rock.ob`:

```text
object Rock
char #
resource_max 100
consumable false
destructible false
```

### Mapas

Un archivo `.map` utiliza caracteres para referenciar los terrenos y objetos registrados. La primera línea identifica el mapa y las siguientes representan sus filas. Las filas deben mantener el mismo ancho.

Las criaturas se incorporan a la simulación por separado; no forman parte de la matriz de caracteres del mapa.

Los nombres, campos y caracteres de los recursos deben respetar las definiciones y validaciones del cargador correspondiente.

## Pruebas y calidad

Ejecuta la suite completa:

```bash
uv run pytest -q
```

Ejecuta Ruff:

```bash
uv run ruff check src tests
```

Ejecuta Mypy:

```bash
uv run mypy src
```

**Última verificación comunicada:** 30 pruebas aprobadas, Ruff sin errores y Mypy sin errores en 107 archivos fuente. Estos resultados corresponden a la última ejecución reportada durante el desarrollo; conviene repetir los tres comandos después de nuevos cambios.

## Documentación y seguimiento

- **[Seguimiento del desarrollo](docs/PROGRESS.md):** funcionalidades completadas, auditorías, hallazgos y tareas pendientes.
- **[Documento de orientación](docs/instinct.pdf):** referencia general del proyecto.

El tracker es el documento de referencia para el estado técnico y el orden de trabajo. Este README se centra en explicar el proyecto, su arquitectura y cómo ejecutarlo.

---

Desarrollado con Python, curiosidad y mucho Instinct.
