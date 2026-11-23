# Instinct

**Instinct** es un simulador de ecosistemas de criaturas autónomas programadas mediante un lenguaje de dominio específico (DSL) propio. Cada criatura ejecuta un programa que determina su comportamiento, percepción del entorno e interacción con otras entidades dentro de un mundo dinámico basado en cuadrículas.

El proyecto integra un compilador, un entorno de ejecución, un motor de simulación y una interfaz gráfica interactiva desarrollados con Python.

---

## Características principales

### Lenguaje de programación Instinct

Instinct incorpora un lenguaje propio diseñado para definir comportamientos autónomos.

- Análisis léxico y sintáctico.
- Construcción de árboles de sintaxis abstracta (AST).
- Análisis semántico.
- Compilación y ejecución de programas.
- Variables, expresiones y estructuras de control.
- Instrucciones condicionales y saltos mediante etiquetas.
- Acciones y percepciones integradas con el mundo.
- Contexto de ejecución independiente para cada criatura.

Los comportamientos se definen mediante archivos `.ins`, lo que permite crear y modificar especies sin implementar su lógica directamente en Python.

### Simulación de ecosistemas

El motor administra un mundo en el que las criaturas interactúan de forma autónoma.

- Mundo organizado en una cuadrícula.
- Sistema de turnos y ticks.
- Ejecución independiente de programas.
- Movimiento y exploración.
- Combate y daño.
- Consumo de recursos.
- Reproducción.
- Interacción entre aliados y enemigos.
- Percepciones locales y globales.
- Regeneración de recursos y leyes naturales.
- Registro de eventos de simulación.

### Mundo y recursos configurables

El mundo se construye mediante archivos externos que permiten incorporar nuevos elementos sin modificar el motor.

- Terrenos con propiedades de regeneración y transitabilidad.
- Objetos con propiedades independientes de consumo y destrucción.
- Edificios con huellas lógicas y dimensiones visuales.
- Mapas configurables mediante archivos de texto.
- Capas complementarias para edificios.
- Cargadores y validación de recursos.

### Interfaz gráfica

La aplicación utiliza **Pygame CE** para visualizar y controlar las simulaciones.

Incluye:

- Menú principal.
- Configuración de nuevas simulaciones.
- Selección de mapas y especies.
- Configuración de cantidades iniciales por especie.
- Renderizado del mundo y sus entidades.
- Cámara con desplazamiento, zoom y seguimiento.
- Movimiento visual interpolado.
- Sistema de animaciones por criatura.
- Panel de información y estadísticas.
- Registro de eventos.
- Controles de velocidad, pausa y avance manual.
- Sistema de ventanas superpuestas y herramientas de inspección.
- Sistema de temas visuales.

La interfaz mantiene separada la representación gráfica de la lógica del motor de simulación.

---

## Arquitectura

El proyecto utiliza una arquitectura modular en la que cada componente tiene responsabilidades específicas.

```text
instinct/
├── resources/
│   ├── creatures/          # Programas de criaturas (.ins)
│   ├── terrains/           # Definiciones de terrenos (.te)
│   ├── objects/            # Definiciones de objetos (.ob)
│   ├── buildings/          # Definiciones de edificios (.bld)
│   └── maps/               # Mapas y capas de edificios
│
├── docs/
│   ├── instinct.pdf        # Documento de orientación
│   └── PROGRESS.md         # Seguimiento del desarrollo
│
├── src/
│   └── instinct/
│       ├── actions/        # Acciones de las criaturas
│       ├── backend/        # Lexer, parser, AST y compilador
│       ├── engine/         # Motor de simulación y turnos
│       ├── frontend/       # Interfaz gráfica
│       ├── functions/      # Funciones del lenguaje
│       ├── loaders/        # Cargadores de recursos
│       ├── perceptions/    # Sistema de percepciones
│       ├── runtime/        # Intérprete y ejecución
│       ├── world/          # Entidades y cuadrícula
│       └── main.py
│
├── tests/                  # Pruebas automatizadas
├── pyproject.toml
├── uv.lock
└── README.md
```

### Responsabilidades de los módulos

| Módulo | Responsabilidad |
|---|---|
| `backend` | Analiza, valida y compila los programas Instinct. |
| `runtime` | Ejecuta los programas y administra sus contextos. |
| `actions` | Implementa las acciones disponibles para las criaturas. |
| `functions` | Registra las funciones utilizadas por el lenguaje. |
| `perceptions` | Proporciona información del mundo y de las criaturas. |
| `world` | Define las entidades y la estructura espacial. |
| `engine` | Coordina los turnos, ticks, eventos y leyes naturales. |
| `loaders` | Carga y valida las definiciones externas. |
| `frontend` | Gestiona la interfaz, escenas, cámara, animaciones y renderizado. |

---

## Tecnologías

| Tecnología | Uso |
|---|---|
| Python 3.13+ | Lenguaje principal. |
| Pygame CE | Interfaz gráfica y renderizado. |
| uv | Gestión de dependencias y entorno. |
| pytest | Pruebas automatizadas. |
| Ruff | Análisis y calidad del código. |
| Mypy | Comprobación estática de tipos. |

---

## Instalación

### Requisitos

- Python 3.13 o superior.
- [uv](https://docs.astral.sh/uv/).
- Git.

### Clonar el repositorio

```bash
git clone https://github.com/luisiafk/instinct.git
cd instinct
```

### Instalar dependencias

```bash
uv sync
```

---

## Ejecución

Para iniciar la aplicación gráfica:

```bash
uv run python -m instinct.frontend.app
```

También se puede utilizar el punto de entrada del proyecto:

```bash
uv run instinct
```

Ambos comandos permiten iniciar Instinct desde el entorno administrado por uv.

---

## Recursos del mundo

Los recursos se definen mediante archivos de texto que se cargan al iniciar la aplicación o preparar una simulación.

| Extensión | Tipo | Directorio |
|---|---|---|
| `.ins` | Programa de criatura | `resources/creatures/` |
| `.te` | Terreno | `resources/terrains/` |
| `.ob` | Objeto | `resources/objects/` |
| `.bld` | Edificio | `resources/buildings/` |
| `.map` | Mapa | `resources/maps/` |
| `.bmap` | Capa de edificios | `resources/maps/` |

### Programas de criaturas

Los archivos `.ins` contienen las características y el comportamiento de cada criatura.

Cada criatura tiene su propio programa y contexto de ejecución, lo que permite que múltiples individuos de una misma especie ejecuten comportamientos independientes.

### Terrenos

Los archivos `.te` definen las características de los terrenos, incluyendo:

- Carácter identificador.
- Reserva máxima.
- Regeneración.
- Transitabilidad.

Ejemplo:

```text
terrain Grass
char .
resource_max 100
regen 2
walkable true
```

### Objetos

Los archivos `.ob` definen los objetos que pueden aparecer en el mundo.

Entre sus propiedades se encuentran:

- Carácter identificador.
- Reserva máxima.
- Consumibilidad.
- Destructibilidad.

Ejemplo:

```text
object Rock
char #
resource_max 100
consumable false
destructible false
```

### Edificios

Los archivos `.bld` permiten definir estructuras que ocupan una o varias casillas.

Admiten:

- Dimensiones lógicas.
- Matriz de transitabilidad.
- Recursos gráficos.
- Dimensiones visuales independientes de la huella lógica.

Esto permite representar edificios grandes sin alterar innecesariamente la distribución lógica del mundo.

### Mapas

Los archivos `.map` definen la distribución del terreno y los objetos mediante caracteres.

Los archivos `.bmap` permiten añadir una capa independiente de edificios, conservando intacto el mapa original.

---

## Sistema de animaciones

Las criaturas disponen de un sistema de estados visuales independiente de la lógica de simulación.

Los estados contemplados incluyen:

- `IDLE`
- `WALK`
- `RUN`
- `ATTACK`
- `HURT`
- `DEATH`
- `ROAR`
- `CONSUME`
- `REPRODUCE`

El sistema utiliza eventos del motor para actualizar las animaciones y mantiene una máquina de estados por instancia de criatura.

Las animaciones se configuran por especie y utilizan spritesheets independientes.

### Organización de recursos gráficos

Los recursos se organizan dentro de la carpeta correspondiente a cada criatura, separando las animaciones cuando sea necesario.

Los tiles del mundo utilizan imágenes PNG RGBA de 32×32 píxeles y las spritesheets utilizan frames de 64×64 píxeles.

---

## Interfaz de simulación

La interfaz permite controlar y observar el comportamiento del ecosistema.

Entre sus herramientas se encuentran:

- Selección e inspección de criaturas.
- Visualización de estadísticas.
- Información contextual de casillas y entidades.
- Registro de eventos.
- Control de velocidad de simulación.
- Pausa y reanudación.
- Avance manual por ticks.
- Cámara con zoom y seguimiento.
- Ventanas de inspección y visualización de código.

La simulación y el renderizado funcionan de forma independiente: los ticks controlan la lógica del mundo, mientras que el frontend actualiza su representación visual.

---

## Pruebas y calidad

Instinct incorpora pruebas automatizadas para validar sus componentes y reducir regresiones durante el desarrollo.

Ejecutar la suite completa:

```bash
uv run pytest -q
```

Ejecutar Ruff:

```bash
uv run ruff check src tests
```

Ejecutar Mypy:

```bash
uv run mypy src
```

---

## Documentación

La documentación del proyecto se divide según su propósito:

- **README.md:** descripción general, arquitectura, tecnologías e instrucciones de instalación y ejecución.
- **docs/PROGRESS.md:** seguimiento del desarrollo, funcionalidades implementadas, tareas pendientes y prioridades.
- **docs/instinct.pdf:** documento de orientación y referencia del proyecto.

El seguimiento técnico debe mantenerse actualizado en `docs/PROGRESS.md`, sin convertir el README en una lista de tareas.

---

## Objetivo del proyecto

Instinct busca proporcionar un entorno extensible de simulación de vida artificial en el que los comportamientos de las criaturas puedan definirse mediante un lenguaje propio.

La arquitectura modular permite incorporar nuevas especies, comportamientos, acciones, percepciones, terrenos, objetos, edificios y mapas, manteniendo separadas la lógica de simulación y su representación gráfica.

---

**Instinct — Un mundo. Múltiples criaturas. Comportamientos autónomos.**