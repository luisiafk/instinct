
"""
Leyes naturales del mundo de Instinct.

Se aplican al finalizar cada tick de la simulación:
- Regeneración de recursos de los terrenos.
- Desgaste de vida de las criaturas.
- Envejecimiento de las criaturas.
- Muerte por agotamiento de vida o esperanza de vida alcanzada.
"""

from instinct.engine.event_log import EventLog
from instinct.world.world_grid import WorldGrid
from instinct.engine.action_event import ActionEventLog

class NaturalLaws:
    """Aplica las leyes naturales al mundo de la simulación."""

    @staticmethod
    def apply(
        world: WorldGrid,
        tick: int,
        event_log: EventLog,
        action_event_log: ActionEventLog,
    ) -> None:
        NaturalLaws._regenerate_terrains(world)
        NaturalLaws._update_creatures(
            world,
            tick,
            event_log,
            action_event_log,
        )

    @staticmethod
    def _regenerate_terrains(world: WorldGrid) -> None:
        """Regenera los recursos de todos los terrenos."""

        for row in world.tiles:
            for tile in row:
                terrain = tile.terrain

                current_reserve = terrain.reserve or 0

                terrain.reserve = min(
                    terrain.resource_max,
                    current_reserve + terrain.regen,
                )

    @staticmethod
    def _update_creatures(
        world: WorldGrid,
        tick: int,
        event_log: EventLog,
        action_event_log: ActionEventLog,
    ) -> None:

        for y in range(world.height):
            for x in range(world.width):
                tile = world.get_tile(x, y)
                creature = tile.creature

                if creature is None:
                    continue

                creature.health -= 1
                creature.age += 1

                if creature.health <= 0:
                    tile.remove_creature()

                    event_log.add(
                        tick,
                        f"La criatura '{creature.name}' ha muerto por agotamiento de vida.",
                        "muerte",
                    )

                elif creature.age >= creature.lifespan:
                    tile.remove_creature()

                    event_log.add(
                        tick,
                        f"La criatura '{creature.name}' ha alcanzado su esperanza de vida.",
                        "muerte",
                    )
