
import pytest

from instinct.world.entities import Building, Creature, Terrain, WorldObject
from instinct.world.world_grid import WorldGrid


@pytest.fixture
def terrain():
    return Terrain(
        name="Grass",
        char=".",
        resource_max=100,
        regen=1,
    )


@pytest.fixture
def world(terrain):
    return WorldGrid(10, 10, terrain)


@pytest.fixture
def gate():
    return Building(
        name="Gate",
        char="G",
        width=3,
        height=1,
        asset="special/gate.png",
        walkable=((False, True, False),),
        visual_width=3,
        visual_height=3,
    )


def test_place_building_occupies_complete_footprint(world, gate):
    world.place_building(gate, 2, 3)

    left = world.get_tile(2, 3)
    center = world.get_tile(3, 3)
    right = world.get_tile(4, 3)

    assert left.building is gate
    assert center.building is gate
    assert right.building is gate

    assert left.building_offset == (0, 0)
    assert center.building_offset == (1, 0)
    assert right.building_offset == (2, 0)

    assert gate.x == 2
    assert gate.y == 3


def test_creature_can_enter_walkable_building_cell(world, gate):
    world.place_building(gate, 2, 3)

    creature = Creature(
        name="Naruto",
        faction="Konoha",
        health=100,
        vision=6,
        lifespan=500,
    )

    world.place_creature(creature, 3, 3)

    assert world.get_tile(3, 3).creature is creature
    assert creature.x == 3
    assert creature.y == 3


@pytest.mark.parametrize("x", [2, 4])
def test_creature_cannot_enter_blocked_building_cells(world, gate, x):
    world.place_building(gate, 2, 3)

    creature = Creature(
        name="Naruto",
        faction="Konoha",
        health=100,
        vision=6,
        lifespan=500,
    )

    with pytest.raises(ValueError):
        world.place_creature(creature, x, 3)


def test_building_cannot_be_placed_over_object(world, gate):
    obj = WorldObject(
        name="Rock",
        char="#",
        resource_max=100,
        consumable=False,
        destructible=False,
    )

    world.place_object(obj, 3, 3)

    with pytest.raises(ValueError):
        world.place_building(gate, 2, 3)

    assert all(
        not tile.has_building
        for row in world.tiles
        for tile in row
    )

    assert world.get_tile(3, 3).object is obj


def test_building_cannot_exceed_world_bounds(world, gate):
    with pytest.raises(ValueError):
        world.place_building(gate, 9, 3)

    assert all(
        not tile.has_building
        for row in world.tiles
        for tile in row
    )


def test_building_cannot_overlap_another_building(world, gate):
    world.place_building(gate, 2, 3)

    another_gate = Building(
        name="Gate",
        char="G",
        width=3,
        height=1,
        asset="special/gate.png",
        walkable=((False, True, False),),
        visual_width=3,
        visual_height=3,
    )

    with pytest.raises(ValueError):
        world.place_building(another_gate, 4, 3)
