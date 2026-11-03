from pathlib import Path

from entities import Terrain, GameObject
from grid import WorldGrid


class LoaderError(ValueError):
    """Error que aparece cuando un archivo tiene un formato incorrecto"""


def _error(filepath: str, line_number: int, message: str) -> LoaderError:
    # Preparamos un mensaje que indique exactamente donde esta el problema
    return LoaderError(f"{filepath}:{line_number}: {message}")


def _read_lines(filepath: str):
    # Leemos el archivo manteniendo los espacios que puedan formar parte del mapa
    with open(filepath, "r", encoding="utf-8-sig") as file:
        return file.readlines()


def _parse_int(value: str, filepath: str, line_number: int, field: str) -> int:
    # Convertimos los valores a enteros y avisamos si estan mal escritos
    try:
        return int(value.strip())
    except (TypeError, ValueError):
        raise _error(
            filepath,
            line_number,
            f"el campo '{field}' debe ser un numero entero"
        )


def _store_char(items: dict, symbol: str, item, filepath: str, line_number: int):
    # Comprobamos que cada terreno u objeto tenga un unico caracter
    if len(symbol) != 1 or symbol in ("\n", "\r", "\t"):
        raise _error(
            filepath,
            line_number,
            "el campo 'char' debe contener un solo caracter"
        )

    # Evitamos que dos elementos del mismo archivo compartan simbolo
    if symbol in items:
        raise _error(
            filepath,
            line_number,
            f"el caracter '{symbol}' esta repetido en el archivo"
        )

    # Guardamos el caracter dentro del propio elemento
    item.char = symbol
    items[symbol] = item


def load_terrains(filepath: str) -> dict:
    """
    Carga los terrenos oficiales y mantiene la compatibilidad
    con los formatos antiguos utilizados en INSTINCT
    """

    terrains = {}
    lines = _read_lines(filepath)

    # Aqui guardamos los terrenos escritos mediante el formato oficial
    official_blocks = []
    current_block = None

    for line_number, raw_line in enumerate(lines, start=1):
        clean_line = raw_line.strip()

        # Ignoramos las lineas vacias y los comentarios habituales
        if not clean_line or clean_line.startswith("//"):
            continue

        # Primero comprobamos el formato antiguo separado por dos puntos
        # Esto es importante porque un terreno antiguo puede usar el simbolo #
        if ":" in clean_line:
            parts = [part.strip() for part in clean_line.split(":")]

            if len(parts) != 4:
                raise _error(
                    filepath,
                    line_number,
                    "la fila antigua de terreno debe tener 4 campos"
                )

            symbol, cost_text, obstacle_text, health_text = parts

            cost = _parse_int(
                cost_text, filepath, line_number, "movement_cost"
            )
            obstacle = _parse_int(
                obstacle_text, filepath, line_number, "obstacle"
            )
            health_modifier = _parse_int(
                health_text, filepath, line_number, "health_modifier"
            )

            if len(symbol) != 1:
                raise _error(
                    filepath,
                    line_number,
                    "el simbolo del terreno debe tener un solo caracter"
                )

            if cost < 1:
                raise _error(
                    filepath,
                    line_number,
                    "el costo de movimiento debe ser mayor que cero"
                )

            if obstacle not in (0, 1):
                raise _error(
                    filepath,
                    line_number,
                    "el campo de obstaculo solo puede ser 0 o 1"
                )



            # Creamos el terreno respetando los datos del archivo antiguo
            terrain = Terrain(
                name=f"Terrain_{symbol}",
                walkable=(obstacle == 0),
                reserve=100,
                regen_rate=1 if symbol == "T" else 0,
                health_modifier=health_modifier,
                movement_cost=cost
            )

            _store_char(
                terrains,
                symbol,
                terrain,
                filepath,
                line_number
            )
            continue

        # Ignoramos los comentarios que empiezan por #
        if clean_line.startswith("#"):
            continue

        # Detectamos el comienzo de un bloque oficial de terreno
        if clean_line.lower().startswith("terrain "):

            if current_block is not None:
                official_blocks.append(current_block)

            name = clean_line.split(None, 1)[1].strip()

            if not name:
                raise _error(
                    filepath,
                    line_number,
                    "falta el nombre del terreno"
                )

            current_block = {
                "name": name,
                "line": line_number,
                "fields": {}
            }
            continue

        # Leemos los campos que pertenecen al terreno actual
        if current_block is not None:
            parts = clean_line.split(None, 1)

            if len(parts) != 2:
                raise _error(
                    filepath,
                    line_number,
                    "campo de terreno invalido"
                )

            key, value = parts

            if key not in ("char", "resource_max", "regen"):
                raise _error(
                    filepath,
                    line_number,
                    f"campo de terreno desconocido: '{key}'"
                )

            if key in current_block["fields"]:
                raise _error(
                    filepath,
                    line_number,
                    f"campo '{key}' repetido"
                )

            current_block["fields"][key] = (value.strip(), line_number)
            continue

        # Mantenemos el formato antiguo separado por comas
        if "," in clean_line:
            parts = [part.strip() for part in clean_line.split(",")]

            if len(parts) != 3:
                raise _error(
                    filepath,
                    line_number,
                    "la fila de terreno por comas debe tener 3 campos"
                )

            name, walkable_text, regen_text = parts

            if walkable_text.lower() not in ("true", "false"):
                raise _error(
                    filepath,
                    line_number,
                    "el valor de transitable debe ser true o false"
                )

            regen = _parse_int(
                regen_text, filepath, line_number, "regen"
            )

            if regen < 0:
                raise _error(
                    filepath,
                    line_number,
                    "la regeneracion no puede ser negativa"
                )

            terrain = Terrain(
                name=name,
                walkable=walkable_text.lower() == "true",
                regen_rate=regen
            )

            terrain.char = None
            terrains[name] = terrain
            continue

        # Tambien aceptamos nombres simples del formato antiguo
        terrain = Terrain(name=clean_line)
        terrain.char = None
        terrains[clean_line] = terrain

    # Guardamos el ultimo bloque si el archivo termina con un terreno
    if current_block is not None:
        official_blocks.append(current_block)

    # Ahora creamos los terrenos que utilizan el formato oficial
    for block in official_blocks:
        fields = block["fields"]


        # Comprobamos que no falte ninguno de los campos obligatorios
        for required in ("char", "resource_max", "regen"):
            if required not in fields:
                raise _error(
                    filepath,
                    block["line"],
                    f"al terreno '{block['name']}' le falta '{required}'"
                )

        symbol, symbol_line = fields["char"]
        resource_max, reserve_line = fields["resource_max"]
        regen, regen_line = fields["regen"]

        reserve = _parse_int(
            resource_max, filepath, reserve_line, "resource_max"
        )
        regen_value = _parse_int(
            regen, filepath, regen_line, "regen"
        )

        if reserve <= 0:
            raise _error(
                filepath,
                reserve_line,
                "resource_max debe ser mayor que cero"
            )

        if regen_value < 0:
            raise _error(
                filepath,
                regen_line,
                "regen no puede ser negativo"
            )

        # Creamos el terreno con su reserva y regeneracion correspondientes
        terrain = Terrain(
            name=block["name"],
            walkable=True,
            reserve=reserve,
            regen_rate=regen_value
        )

        _store_char(
            terrains,
            symbol,
            terrain,
            filepath,
            symbol_line
        )

    return terrains


def load_objects(filepath: str) -> dict:
    """
    Carga objetos oficiales y conserva los datos del formato
    antiguo utilizado por los objetos y recursos de INSTINCT
    """

    objects = {}
    lines = _read_lines(filepath)

    official_blocks = []
    current_block = None

    for line_number, raw_line in enumerate(lines, start=1):
        clean_line = raw_line.strip()

       # Ignoramos las lineas vacias y los comentarios
        if (
            not clean_line
            or clean_line.startswith("//")
            or clean_line.startswith("#")
        ):
            continue

        # Primero comprobamos los registros antiguos separados por plecas
        if "|" in clean_line:
            parts = [part.strip() for part in clean_line.split("|")]

            if len(parts) != 6:
                raise _error(
                    filepath,
                    line_number,
                    "el objeto antiguo debe tener 6 campos"
                )

            object_id, name, symbol, effect_type, value_text, consumable_text = parts

            if not object_id or not name or not effect_type:
                raise _error(
                    filepath,
                    line_number,
                    "el ID, nombre y tipo de efecto son obligatorios"
                )

            if consumable_text not in ("0", "1"):
                raise _error(
                    filepath,
                    line_number,
                    "el campo consumible solo puede ser 0 o 1"
                )

            value = _parse_int(
                value_text, filepath, line_number, "valor"
            )

            if value < 0:
                raise _error(
                    filepath,
                    line_number,
                    "el valor del objeto no puede ser negativo"
                )

            if len(symbol) != 1:
                raise _error(
                    filepath,
                    line_number,
                    "el simbolo del objeto debe tener un solo caracter"
                )

            if symbol in objects or object_id in objects:
                raise _error(
                    filepath,
                    line_number,
                    "el ID o simbolo del objeto esta repetido"
                )

            # Creamos el objeto con la reserva indicada en el archivo
            game_object = GameObject(
                name=name,
                walkable=False,
                reserve=value,
                destructible=True
            )


        # Conservamos los datos especiales de los objetos del proyecto
            game_object.object_id = object_id
            game_object.char = symbol
            game_object.effect_type = effect_type
            game_object.effect_value = value
            game_object.consumable = (consumable_text == "1")

            # Permitimos buscar el objeto tanto por su simbolo como por su ID
            objects[symbol] = game_object
            objects[object_id] = game_object
            continue

        # Ignoramos los comentarios que empiezan por #
        if clean_line.startswith("#"):
            continue

        # Detectamos el comienzo de un bloque oficial de objeto
        if clean_line.lower().startswith("object "):

            if current_block is not None:
                official_blocks.append(current_block)

            name = clean_line.split(None, 1)[1].strip()

            if not name:
                raise _error(
                    filepath,
                    line_number,
                    "falta el nombre del objeto"
                )

            current_block = {
                "name": name,
                "line": line_number,
                "fields": {}
            }
            continue

        # Leemos los campos del objeto actual
        if current_block is not None:
            parts = clean_line.split(None, 1)

            if len(parts) != 2:
                raise _error(
                    filepath,
                    line_number,
                    "campo de objeto invalido"
                )

            key, value = parts

            if key not in ("char", "resource_max"):
                raise _error(
                    filepath,
                    line_number,
                    f"campo de objeto desconocido: '{key}'"
                )

            if key in current_block["fields"]:
                raise _error(
                    filepath,
                    line_number,
                    f"campo '{key}' repetido"
                )

            current_block["fields"][key] = (value.strip(), line_number)
            continue

        # Mantenemos tambien el formato antiguo separado por comas
        if "," in clean_line:
            parts = [part.strip() for part in clean_line.split(",")]

            if len(parts) != 3:
                raise _error(
                    filepath,
                    line_number,
                    "la fila de objeto por comas debe tener 3 campos"
                )

            name, walkable_text, destructible_text = parts

            if walkable_text.lower() not in ("true", "false"):
                raise _error(
                    filepath,
                    line_number,
                    "el campo transitable debe ser true o false"
                )

            if destructible_text.lower() not in ("true", "false"):
                raise _error(
                    filepath,
                    line_number,
                    "el campo destructible debe ser true o false"
                )

            game_object = GameObject(
                name=name,
                walkable=walkable_text.lower() == "true",
                destructible=destructible_text.lower() == "true"
            )

            game_object.char = None
            objects[name] = game_object
            continue

        # Aceptamos tambien nombres simples del formato antiguo
        game_object = GameObject(name=clean_line)
        game_object.char = None
        objects[clean_line] = game_object

    # Guardamos el ultimo bloque del archivo
    if current_block is not None:
        official_blocks.append(current_block)

    # Creamos los objetos escritos mediante el formato oficial
    for block in official_blocks:
        fields = block["fields"]

        # Estos dos campos son obligatorios para cada objeto

        for required in ("char", "resource_max"):
            if required not in fields:
                raise _error(
                    filepath,
                    block["line"],
                    f"al objeto '{block['name']}' le falta '{required}'"
                )

        symbol, symbol_line = fields["char"]
        resource_max, reserve_line = fields["resource_max"]

        reserve = _parse_int(
            resource_max, filepath, reserve_line, "resource_max"
        )

        if reserve <= 0:
            raise _error(
                filepath,
                reserve_line,
                "resource_max debe ser mayor que cero"
            )

        # Creamos el objeto con la reserva inicial indicada
        game_object = GameObject(
            name=block["name"],
            walkable=False,
            reserve=reserve,
            destructible=True
        )

        game_object.object_id = block["name"]
        game_object.char = symbol
        game_object.effect_type = None
        game_object.effect_value = None
        game_object.consumable = True

        _store_char(
            objects,
            symbol,
            game_object,
            filepath,
            symbol_line
        )

    return objects


def _get_char_items(items: dict) -> dict:
    # Creamos un diccionario que contiene solamente los caracteres del mapa
    result = {}

    for key, item in items.items():
        symbol = getattr(item, "char", None)

        if symbol is not None:
            result[symbol] = item

        elif isinstance(key, str) and len(key) == 1:
            result[key] = item

    return result


def load_map(filepath: str, terrains_dict: dict, objects_dict: dict) -> WorldGrid:
    """
    Carga mapas oficiales y mapas antiguos de INSTINCT

    El formato oficial utiliza el nombre del mapa en la primera linea
    y todas las filas deben tener exactamente la misma longitud
    """

    raw_lines = _read_lines(filepath)
    map_lines = []

    # Guardamos las filas sin eliminar espacios que puedan ser casillas
    for line_number, raw_line in enumerate(raw_lines, start=1):
        row = raw_line.rstrip("\r\n")

        # Ignoramos las filas vacias y los comentarios de varias lineas
        if not row.strip() or row.lstrip().startswith("//"):
            continue

        map_lines.append((line_number, row))

    if not map_lines:
        raise _error(filepath, 1, "el mapa esta vacio")

    # Obtenemos los caracteres declarados en los archivos de terrenos y objetos
    terrain_chars = _get_char_items(terrains_dict)
    object_chars = _get_char_items(objects_dict)

    # Un mismo caracter no puede representar un terreno y un objeto
    duplicated = set(terrain_chars).intersection(object_chars)

    if duplicated:
        symbol = sorted(duplicated)[0]

        raise _error(
            filepath,
            map_lines[0][0],
            f"el caracter '{symbol}' esta declarado como terreno y objeto"
        )

    # Preparamos los caracteres permitidos en los mapas antiguos
    legacy_chars = set(terrain_chars) | set(object_chars) | {"A"}

    first_line_number, first_line = map_lines[0]
    remaining_rows = map_lines[1:]

    # Comprobamos si la primera fila es realmente una fila del mapa antiguo
    first_is_row = (
        len(map_lines) > 1
        and all(char in legacy_chars for char in first_line)
        and all(
            len(row) == len(first_line)
            and all(char in legacy_chars for char in row)
            for _, row in remaining_rows
        )
    )

    if first_is_row:
        # Los mapas antiguos no tienen una linea inicial con su nombre
        rows = map_lines
        legacy_format = True
        map_name = Path(filepath).stem

    else:
        # En el formato oficial la primera linea contiene el nombre del mapa
        map_name = first_line.strip()

        if not map_name:
            raise _error(
                filepath,
                first_line_number,
                "falta el nombre del mapa"
            )

        rows = remaining_rows
        legacy_format = False


        if not rows:
            raise _error(
                filepath,
                first_line_number,
                "el mapa no contiene filas"
            )

    # Todas las filas deben tener el mismo ancho
    expected_width = len(rows[0][1])

    if expected_width == 0:
        raise _error(
            filepath,
            rows[0][0],
            "la fila del mapa esta vacia"
        )

    for line_number, row in rows:
        if len(row) != expected_width:
            raise _error(
                filepath,
                line_number,
                f"la fila tiene {len(row)} caracteres y se esperaban {expected_width}"
            )

    # El primer terreno declarado sera la base que quede debajo de los objetos
    if not terrains_dict:
        raise _error(
            filepath,
            rows[0][0],
            "no hay terrenos cargados para construir el mapa"
        )

    first_terrain = next(iter(terrains_dict.values()))

    # Creamos la matriz con las dimensiones reales del archivo
    grid = WorldGrid(
        width=expected_width,
        height=len(rows)
    )

    for y, (line_number, row) in enumerate(rows):

        for x, symbol in enumerate(row):

            # Por defecto cada casilla empieza con el primer terreno declarado
            terrain = first_terrain
            game_object = None

            # Si el caracter es un terreno usamos ese terreno
            if symbol in terrain_chars:
                terrain = terrain_chars[symbol]

            # Si es un objeto lo colocamos sobre el primer terreno
            elif symbol in object_chars:
                game_object = object_chars[symbol]

            # A era una marca de inicio en los mapas antiguos
            elif legacy_format and symbol == "A":
                terrain = first_terrain

            else:
                # No sustituimos caracteres desconocidos por terreno normal
                raise _error(
                    filepath,
                    line_number,
                    f"el caracter '{symbol}' no esta declarado"
                )

            # Asignamos el terreno correspondiente a la casilla
            grid.set_tile_terrain(x, y, terrain)

            # Colocamos el objeto si la casilla contiene uno
            if game_object is not None:
                grid.set_tile_object(x, y, game_object)

                # Guardamos el nombre del mapa para que pueda utilizarlo la interfaz
    grid.name = map_name

    return grid

        