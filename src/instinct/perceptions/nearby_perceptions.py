from instinct.perceptions.base import PerceptionGroup
from instinct.runtime.execution_context import ExecutionContext


class NearbyPerceptions(PerceptionGroup):
    """Calcula las percepciones relacionadas con el entorno cercano."""

    def calculate(self, context: ExecutionContext) -> dict[str, int | str]:
        creature = context.creature_obj
        world = context.world

        allies = []
        enemies = []
        objects = []
        consumables = []

        vision = creature.vision

        min_x = max(0, creature.x - vision)
        max_x = min(world.width - 1, creature.x + vision)
        min_y = max(0, creature.y - vision)
        max_y = min(world.height - 1, creature.y + vision)

        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                tile = world.get_tile(x, y)

                distance = max(
                    abs(x - creature.x),
                    abs(y - creature.y),
                )

                if distance > vision:
                    continue

                other_creature = tile.creature

                if other_creature is not None and other_creature is not creature:
                    if other_creature.faction == creature.faction:
                        allies.append((other_creature.x, other_creature.y))
                    else:
                        enemies.append((other_creature.x, other_creature.y))

                if tile.object is not None:
                    objects.append((x, y))

                    if tile.object.consumable:
                        consumables.append((x, y))

        ally_dist, ally_dx, ally_dy = self._nearest_target(
            creature.x,
            creature.y,
            allies,
        )

        enemy_dist, enemy_dx, enemy_dy = self._nearest_target(
            creature.x,
            creature.y,
            enemies,
        )

        object_dist, object_dx, object_dy = self._nearest_target(
            creature.x,
            creature.y,
            objects,
        )

        consumable_dist, consumable_dx, consumable_dy = self._nearest_target(
            creature.x,
            creature.y,
            consumables,
        )

        roars_near, last_roar = self._calculate_roars(context)

        return {
            "allies_near": len(allies),
            "enemies_near": len(enemies),
            "objects_near": len(objects),
            "consumables_near": len(consumables),
            "enemy_dist": enemy_dist,
            "enemy_dx": enemy_dx,
            "enemy_dy": enemy_dy,
            "ally_dist": ally_dist,
            "ally_dx": ally_dx,
            "ally_dy": ally_dy,
            "object_dist": object_dist,
            "object_dx": object_dx,
            "object_dy": object_dy,
            "consumable_dist": consumable_dist,
            "consumable_dx": consumable_dx,
            "consumable_dy": consumable_dy,
            "roars_near": roars_near,
            "last_roar": last_roar,
        }

    @staticmethod
    def _nearest_target(
        origin_x: int,
        origin_y: int,
        targets: list[tuple[int, int]],
    ) -> tuple[int, int, int]:
        """Obtiene la distancia y dirección hacia el objetivo más cercano."""

        if not targets:
            return -1, 0, 0

        nearest_x, nearest_y = min(
            targets,
            key=lambda target: (
                max(
                    abs(target[0] - origin_x),
                    abs(target[1] - origin_y),
                ),
                target[1],
                target[0],
            ),
        )

        dx = nearest_x - origin_x
        dy = nearest_y - origin_y

        distance = max(abs(dx), abs(dy))

        return (
            distance,
            (dx > 0) - (dx < 0),
            (dy > 0) - (dy < 0),
        )

    @staticmethod
    def _calculate_roars(
        context: ExecutionContext,
    ) -> tuple[int, str]:
        """Cuenta los rugidos del tick anterior que siguen dentro de visión."""

        creature = context.creature_obj
        previous_tick = context.current_tick - 1

        roars_near = 0
        last_roar = ""

        for event in context.event_log.get_by_tick(previous_tick):
            if event.category != "rugido":
                continue

            if event.x is None or event.y is None:
                continue

            distance = max(
                abs(event.x - creature.x),
                abs(event.y - creature.y),
            )

            if distance <= creature.vision:
                roars_near += 1
                _, _, roar_text = event.message.partition(": ")
                last_roar = roar_text

        return roars_near, last_roar
