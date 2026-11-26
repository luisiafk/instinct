
"""Implementación de las siete acciones básicas de Instinct."""

from instinct.actions.base import Action
from instinct.runtime.execution_context import ExecutionContext
from instinct.world.entities import Creature


class WaitAction(Action):
    name = "wait"
    arity = 1

    def execute(
        self,
        context: ExecutionContext,
        args: list[int | str],
    ) -> None:
        self.validate_arguments(args)
        self.require_integer(args[0], "n", self.name)

        # El intérprete administra los turnos de espera.


class MoveAction(Action):
    name = "move"
    arity = 3

    def execute(
        self,
        context: ExecutionContext,
        args: list[int | str],
    ) -> None:
        self.validate_arguments(args)

        dx = self.require_integer(args[0], "dx", self.name)
        dy = self.require_integer(args[1], "dy", self.name)
        speed = self.require_integer(args[2], "speed", self.name)

        self.require_direction(dx, dy, self.name)

        creature = context.creature_obj
        world = context.world

        if dx == 0 and dy == 0:
            return

        start_x = creature.x
        start_y = creature.y

        for _ in range(max(0, speed)):
            next_x = creature.x + dx
            next_y = creature.y + dy

            if not world.in_bounds(next_x, next_y):
                break

            next_tile = world.get_tile(next_x, next_y)

            if not next_tile.terrain.walkable or next_tile.is_occupied:
                break

            current_x = creature.x
            current_y = creature.y

            world.remove_creature(current_x, current_y)
            world.place_creature(creature, next_x, next_y)

        distance = max(
            abs(creature.x - start_x),
            abs(creature.y - start_y),
        )

        if distance > 0:
            context.publish_action_event(
                "move",
                data={
                    "start": (start_x, start_y),
                    "end": (creature.x, creature.y),
                    "distance": distance,
                    "dx": dx,
                    "dy": dy,
                    "speed": speed,
                },
            )


class AttackAction(Action):
    name = "attack"
    arity = 3

    def execute(
        self,
        context: ExecutionContext,
        args: list[int | str],
    ) -> None:
        self.validate_arguments(args)

        dx = self.require_integer(args[0], "dx", self.name)
        dy = self.require_integer(args[1], "dy", self.name)
        damage = self.require_integer(args[2], "damage", self.name)

        self.require_direction(dx, dy, self.name)

        context.publish_action_event(
            "attack",
            data={
                "dx": dx,
                "dy": dy,
                "damage": damage,
            },
        )

        self._attack_target(context, dx, dy, damage)

    @staticmethod
    def _attack_target(
        context: ExecutionContext,
        dx: int,
        dy: int,
        damage: int,
    ) -> Creature | None:
        """Aplica daño al objetivo y registra sus consecuencias."""

        creature = context.creature_obj
        world = context.world

        target_x = creature.x + dx
        target_y = creature.y + dy

        if not world.in_bounds(target_x, target_y):
            return None

        tile = world.get_tile(target_x, target_y)

        if dx == 0 and dy == 0:
            reserve = tile.terrain.reserve or 0
            tile.terrain.reserve = max(0, reserve - damage)
            return None

        target_creature = tile.creature

        if target_creature is not None:
            target_creature.health -= damage

            context.publish_action_event(
                "damage",
                target=target_creature,
                data={
                    "damage": damage,
                    "remaining_health": target_creature.health,
                },
            )

            if target_creature.health <= 0:
                tile.remove_creature()

                context.event_log.add(
                    context.current_tick,
                    (
                        f"La criatura '{target_creature.name}' "
                        f"ha muerto por el ataque de '{creature.name}'."
                    ),
                    "muerte",
                )

                context.publish_action_event(
                    "death",
                    target=target_creature,
                    data={
                        "cause": "attack",
                        "damage": damage,
                    },
                )

            return target_creature

        target_object = tile.object

        if target_object is not None:
            # Los objetos indestructibles no reciben daño.
            if not target_object.destructible:
                return None

            reserve = target_object.reserve or 0
            target_object.reserve = max(0, reserve - damage)

            if target_object.reserve <= 0:
                tile.remove_object()

            return None

        reserve = tile.terrain.reserve or 0
        tile.terrain.reserve = max(0, reserve - damage)

        return None


class ConsumeAction(Action):
    name = "consume"
    arity = 4

    def execute(
        self,
        context: ExecutionContext,
        args: list[int | str],
    ) -> None:
        self.validate_arguments(args)

        dx = self.require_integer(args[0], "dx", self.name)
        dy = self.require_integer(args[1], "dy", self.name)
        damage = self.require_integer(args[2], "damage", self.name)
        heal = self.require_integer(args[3], "heal", self.name)

        self.require_direction(dx, dy, self.name)

        creature = context.creature_obj
        world = context.world

        target_x = creature.x + dx
        target_y = creature.y + dy

        if not world.in_bounds(target_x, target_y):
            return

        target_tile = world.get_tile(target_x, target_y)

        if damage <= 0:
            return

        # Consumir una criatura enemiga.
        target_creature = target_tile.creature

        if target_creature is not None and target_creature is not creature:
            target_creature.health -= damage
            creature.health += heal

            context.publish_action_event(
                "consume",
                data={
                    "dx": dx,
                    "dy": dy,
                    "damage": damage,
                    "heal": heal,
                    "target": target_creature.name,
                },
            )

            context.publish_action_event(
                "damage",
                target=target_creature,
                data={
                    "damage": damage,
                    "remaining_health": target_creature.health,
                },
            )

            if target_creature.health <= 0:
                target_tile.remove_creature()

                context.event_log.add(
                    context.current_tick,
                    (
                        f"La criatura '{target_creature.name}' "
                        f"ha muerto al ser consumida por "
                        f"'{creature.name}'."
                    ),
                    "muerte",
                )

                context.publish_action_event(
                    "death",
                    target=target_creature,
                    data={
                        "cause": "consume",
                        "damage": damage,
                    },
                )

            return

        # Mantener el consumo de objetos.
        target_object = target_tile.object

        if target_object is None:
            return

        reserve = target_object.reserve or 0
        target_object = target_tile.object

        if target_object is None:
            return

        # Los objetos no consumibles no pueden ser ingeridos.
        if not target_object.consumable:
            return

        reserve = target_object.reserve or 0

        if reserve <= 0:
            return

        consumed = min(damage, reserve)
        target_object.reserve = reserve - consumed

        if target_object.reserve <= 0:
            target_tile.remove_object()

        # La curación nunca puede superar la vida máxima de la criatura.
        creature.health += heal

        context.publish_action_event(
            "consume",
            data={
                "dx": dx,
                "dy": dy,
                "damage": consumed,
                "heal": heal,
                "object": target_object.name,
                "remaining_reserve": target_object.reserve,
            },
        )


class ReproduceAction(Action):
    name = "reproduce"
    arity = 3

    def execute(
        self,
        context: ExecutionContext,
        args: list[int | str],
    ) -> None:
        self.validate_arguments(args)

        dx = self.require_integer(args[0], "dx", self.name)
        dy = self.require_integer(args[1], "dy", self.name)
        child_health = self.require_integer(args[2], "health", self.name)

        self.require_direction(dx, dy, self.name)

        if dx == 0 and dy == 0:
            return
        
        if child_health <= 0:
            return

        mother = context.creature_obj
        world = context.world

        if not mother.can_reproduce: 
            return

        target_x = mother.x + dx
        target_y = mother.y + dy

        if not world.in_bounds(target_x, target_y):
            return

        target_tile = world.get_tile(target_x, target_y)

        if target_tile.is_occupied:
            return

        if mother.health <= child_health:
            return

        child = Creature(
            name=mother.name,
            faction=mother.faction,
            health=child_health,
            vision=mother.vision,
            lifespan=mother.lifespan,
            x=target_x,
            y=target_y,
            age=0,
            program=context.program,
            can_reproduce=False
        )

        world.place_creature(child, target_x, target_y)

        # La madre pierde la vida correspondiente y agota su única reproducción.
        mother.health -= child_health
        mother.can_reproduce = False

        context.publish_action_event(
            "reproduce",
            target=child,
            data={
                "child_health": child_health,
                "position": (target_x, target_y),
            },
        )


class RoarAction(Action):
    name = "roar"
    arity = 1

    def execute(
        self,
        context: ExecutionContext,
        args: list[int | str],
    ) -> None:
        self.validate_arguments(args)

        value = str(args[0])
        creature = context.creature_obj

        context.event_log.add(
            context.current_tick,
            f"{creature.name}: {value}",
            "rugido",
            x=creature.x,
            y=creature.y,
        )

        context.publish_action_event(
            "roar",
            data={"message": value},
        )


class SayAction(Action):
    name = "say"
    arity = 1

    def execute(
        self,
        context: ExecutionContext,
        args: list[int | str],
    ) -> None:
        self.validate_arguments(args)

        value = str(args[0])
        creature = context.creature_obj

        context.event_log.add(
            context.current_tick,
            f"{creature.name}: {value}",
            "mensaje",
        )
