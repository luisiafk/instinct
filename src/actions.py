class Action:
    """
    Clase base de las acciones.

    Las demás clases heredan de esta para mantener una estructura común.
    """

    def __init__(self):
        pass

    def init(self, *args):
        raise NotImplementedError
    
    def execute(self, creature, world):
        """
        Cada acción tiene que implementar su propio comportamiento.
        """
        raise NotImplementedError(
            "Esta acción todavía no tiene una implementación"
        )


def evaluate_expression(expression, creature):
    """
    Evalúa una expresión utilizando la memoria de la criatura.

    Las expresiones vienen del AST y pueden ser números, textos,
    variables u operaciones.
    """

    return expression.evaluate(creature.memory)


def is_integer(value):
    """
    Comprueba que un valor sea un número entero.

    Se excluyen los booleanos porque en Python True y False también
    se consideran enteros.
    """

    return isinstance(value, int) and not isinstance(value, bool)


def valid_direction(dx, dy):
    """
    Comprueba que el desplazamiento sea válido.

    Las criaturas solamente pueden desplazarse una casilla por eje
    en cada movimiento.
    """

    return (
        is_integer(dx)
        and is_integer(dy)
        and dx in (-1, 0, 1)
        and dy in (-1, 0, 1)
    )


def runtime_error(creature, world, message):
    """
    Gestiona los errores que aparecen durante la ejecucion

    Cuando una criatura comete un error, muere y su casilla
    queda libre inmediatamente
    """

    # Marcamos la criatura como muerta
    creature.alive = False

    # Buscamos la casilla que ocupa actualmente
    tile = world.get_tile(creature.x, creature.y)

    # Liberamos la casilla si todavía pertenece a esta criatura
    if tile is not None and tile.creature is creature:
        tile.creature = None

    # Mostramos el error por consola
    print(
        f"Error de ejecución en {creature.species_name}: {message}"
    )


class Move(Action):
    """
    Permite mover una criatura por el mapa.

    El movimiento puede avanzar varias casillas, pero se detiene
    cuando encuentra un obstáculo.
    """

    def __init__(self, dx_expr, dy_expr, speed_expr):
        self.dx_expr = dx_expr
        self.dy_expr = dy_expr
        self.speed_expr = speed_expr

    def execute(self, creature, world):

        # Primero evaluamos los valores recibidos desde el programa
        dx = evaluate_expression(self.dx_expr, creature)
        dy = evaluate_expression(self.dy_expr, creature)
        speed = evaluate_expression(self.speed_expr, creature)

        # Comprobamos que la dirección sea válida
        if not valid_direction(dx, dy):
            runtime_error(creature, world, "Dirección de movimiento inválida")
            return True

        if not is_integer(speed):
            runtime_error(creature, world, "La velocidad debe ser un entero")
            return True

        # Una velocidad menor que uno no permite avanzar
        if speed < 1:
            return True

        # Avanzamos una casilla cada vez para no atravesar obstáculos
        for _ in range(speed):

            new_x = creature.x + dx
            new_y = creature.y + dy

            # Comprobamos si la casilla está libre
            if not world.is_walkable(new_x, new_y):
                break

            old_tile = world.get_tile(creature.x, creature.y)
            new_tile = world.get_tile(new_x, new_y)

            if old_tile is None or new_tile is None:
                break

            # Quitamos la criatura de su posición anterior
            old_tile.creature = None

            # La colocamos en la nueva posición
            new_tile.creature = creature

            # Actualizamos sus coordenadas
            creature.x = new_x
            creature.y = new_y

        # El movimiento siempre consume el turno
        return True

class Attack(Action):
    """
    Permite atacar a una criatura, un objeto o el terreno.

    También se puede utilizar la dirección (0, 0) para atacar
    el terreno que se encuentra debajo de la propia criatura.
    """

    def __init__(self, dx_expr, dy_expr, damage_expr):
        self.dx_expr = dx_expr
        self.dy_expr = dy_expr
        self.damage_expr = damage_expr

    def execute(self, creature, world):

        dx = evaluate_expression(self.dx_expr, creature)
        dy = evaluate_expression(self.dy_expr, creature)
        damage = evaluate_expression(self.damage_expr, creature)

        if not valid_direction(dx, dy):
            runtime_error(creature, world, "Dirección de ataque inválida")
            return True

        if not is_integer(damage):
            runtime_error(creature, world, "El daño debe ser un entero")
            return True

        target_x = creature.x + dx
        target_y = creature.y + dy

        tile = world.get_tile(target_x, target_y)

        # Si la posición está fuera del mapa, el ataque no tiene efecto
        if tile is None:
            return True

        # Si hay una criatura en la casilla, le aplicamos el daño
        # La dirección (0, 0) no puede atacar a la propia criatura
        if tile.creature is not None and tile.creature is not creature:

            target = tile.creature
            target.health -= damage

            # Si muere, dejamos libre la casilla inmediatamente
            if target.health <= 0:
                target.alive = False
                tile.creature = None

        # Si hay un objeto, reducimos su reserva
        elif tile.game_object is not None:

            tile.game_object.reserve -= damage

            if tile.game_object.reserve <= 0:
                tile.game_object = None

        # Si no hay criatura ni objeto, atacamos el terreno
        elif tile.terrain is not None:

            tile.terrain.reserve -= damage

            if tile.terrain.reserve < 0:
                tile.terrain.reserve = 0

        return True


class Consume(Action):
    """
    Permite consumir recursos de una casilla.

    La acción puede producir daño sobre el objetivo y además
    recuperar salud para la criatura que realiza el consumo.

    La curación no tiene un límite máximo.
    """

    def __init__(self, dx_expr, dy_expr, damage_expr, heal_expr):
        self.dx_expr = dx_expr
        self.dy_expr = dy_expr
        self.damage_expr = damage_expr
        self.heal_expr = heal_expr

    def execute(self, creature, world):

        dx = evaluate_expression(self.dx_expr, creature)
        dy = evaluate_expression(self.dy_expr, creature)
        damage = evaluate_expression(self.damage_expr, creature)
        heal = evaluate_expression(self.heal_expr, creature)

        if not valid_direction(dx, dy):
            runtime_error(creature, world, "Dirección de consumo inválida")
            return True

        if not is_integer(damage) or not is_integer(heal):
            runtime_error(
                creature, world,
                "El daño y la curación deben ser valores enteros"
            )
            return True

        target_x = creature.x + dx
        target_y = creature.y + dy

        tile = world.get_tile(target_x, target_y)

        # Si el objetivo está fuera del mapa, no hacemos nada
        if tile is None:
            return True

        # Si hay otra criatura, le aplicamos el daño
        if tile.creature is not None and tile.creature is not creature:

            target = tile.creature
            target.health -= damage

            if target.health <= 0:
                target.alive = False
                tile.creature = None

        # Si hay un objeto, reducimos su reserva
        elif tile.game_object is not None:

            tile.game_object.reserve -= damage

            if tile.game_object.reserve <= 0:
                tile.game_object = None

        # Si no hay criatura ni objeto, actuamos sobre el terreno
        elif tile.terrain is not None:

            tile.terrain.reserve -= damage

            if tile.terrain.reserve < 0:
                    tile.terrain.reserve = 0

        # La criatura que consume recupera la cantidad indicada
        # No se utiliza max_health porque la orientación no establece
        # un límite para la curación
        creature.health += heal

        return True


class Wait(Action):
    """
    Hace que una criatura espere varios turnos.

    wait(1) solamente consume el turno actual.
    wait(3) consume el turno actual y hace que se salte los dos siguientes.
    """

    def init(self, n_expr):
        self.n_expr = n_expr

    def execute(self, creature, world):

        n = evaluate_expression(self.n_expr, creature)

        if not is_integer(n):
            runtime_error(creature, world, "El tiempo de espera debe ser un entero")
            return True

        # Según la orientación, los valores menores que uno cuentan como uno
        if n < 1:
            n = 1

        # Guardamos los turnos que debe saltarse después del actual
        creature.sleep_turns = n - 1

        return True


class Say(Action):
    """
    Permite que una criatura muestre un mensaje.

    Esta es la única acción que no consume el turno.
    """

    def init(self, message_expr):
        self.message_expr = message_expr

    def execute(self, creature, world):

        message = evaluate_expression(self.message_expr, creature)

        # Mostramos quién ha enviado el mensaje
        print(f"{creature.species_name}: {message}")

        # False indica que la criatura puede seguir ejecutando instrucciones
        return False


class Reproduce(Action):
    """
    Permite crear una nueva criatura de la misma especie.

    La criatura madre pierde la cantidad de salud indicada
    y la cría nace con esa misma cantidad de salud.
    """

    def init(self, dx_expr, dy_expr, health_expr):
        self.dx_expr = dx_expr
        self.dy_expr = dy_expr
        self.health_expr = health_expr

    def execute(self, creature, world):

        dx = evaluate_expression(self.dx_expr, creature)
        dy = evaluate_expression(self.dy_expr, creature)
        health_cost = evaluate_expression(self.health_expr, creature)

        if not valid_direction(dx, dy):
            runtime_error(creature, world, "Dirección de reproducción inválida")
            return True

        if not is_integer(health_cost):
            runtime_error(
                creature, world, 
                "El coste de reproducción debe ser un entero"
            )
            return True

        target_x = creature.x + dx
        target_y = creature.y + dy

        tile = world.get_tile(target_x, target_y)

        # No se puede reproducir fuera del mapa ni en la propia casilla
        if tile is None or (dx == 0 and dy == 0):
            return True

        # La casilla debe tener solamente terreno
        if tile.creature is not None or tile.game_object is not None:
            return True

        # La madre debe tener más salud que el coste de reproducción
        if creature.health <= health_cost:
            return True

        # Importamos Creature aquí para mantener la dependencia localizada
        from entities import Creature

        # La madre pierde la salud necesaria para reproducirse
        creature.health -= health_cost

        # Creamos una nueva criatura de la misma especie y facción
        child = Creature(
            species_name=creature.species_name,
            faction=creature.faction,
            health=health_cost,
            vision=creature.vision,
            lifespan=creature.lifespan,
            x=target_x,
            y=target_y
        )

        # La cría empieza desde cero y no hereda las variables de la madre
        child.age = 0
        child.memory = {}
        child.instruction_pointer = "start"

        # La colocamos en el mapa
        tile.creature = child

        # La simulación incorporará la cría a su lista de criaturas
        # para que pueda actuar a partir del siguiente tick

        return True

class Roar(Action):
    """
    Permite emitir un rugido que otras criaturas podrán escuchar
    durante el siguiente tick.
    """

    def __init__(self, value_expr):
        self.value_expr = value_expr

    def execute(self, creature, world):

        value = evaluate_expression(self.value_expr, creature)

        # Guardamos el último rugido de la criatura
        creature.last_roar = value

        # Si la criatura está conectada a una simulación
        # registramos el rugido para que pueda ser percibido después
        simulation = getattr(creature, "simulation", None)

        if simulation is not None:
            simulation.record_roar(creature, value)

        print(f"{creature.species_name} ha emitido un rugido: {value}")

        return True