
import pytest

from instinct.loaders.map_loader import MapLoader
from instinct.world.entities import Building, Terrain
from instinct.world.world_grid import WorldGrid


@pytest.fixture
def terrain():
    return Terrain(
        name="Grass",
        char=".",
        resource_max=100,
        regen=2,
    )


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


@pytest.fixture
def loader():
    return MapLoader()


@pytest.fixture
def map_content():
    return (
        "TestMap\n"
        "..........\n"
        "..........\n"
        "..........\n"
    )


def test_load_building_layer(loader, terrain, gate, map_content):
    building_content = (
        "..........\n"
        ".GGG......\n"
        "..........\n"
    )

    _, world = loader.load_string(
        map_content,
        [terrain],
        [],
        buildings=[gate],
        building_content=building_content,
    )

    first_tile = world.get_tile(1, 1)
    middle_tile = world.get_tile(2, 1)
    last_tile = world.get_tile(3, 1)

    assert first_tile.building is middle_tile.building
    assert middle_tile.building is last_tile.building
    assert first_tile.building.name == "Gate"


def test_reject_building_layer_with_wrong_height(
    loader, terrain, gate, map_content
):
    building_content = (
        "..........\n"
        ".GGG......\n"
    )

    with pytest.raises(ValueError, match="filas"):
        loader.load_string(
            map_content,
            [terrain],
            [],
            buildings=[gate],
            building_content=building_content,
        )


def test_reject_unknown_building_character(
    loader, terrain, gate, map_content
):
    building_content = (
        "..........\n"
        ".XXX......\n"
        "..........\n"
    )

    with pytest.raises(ValueError, match="no corresponde"):
        loader.load_string(
            map_content,
            [terrain],
            [],
            buildings=[gate],
            building_content=building_content,
        )


def test_reject_incomplete_building_footprint(
    loader, terrain, gate, map_content
):
    building_content = (
        "..........\n"
        ".GG.......\n"
        "..........\n"
    )

    with pytest.raises(ValueError, match="incompleta"):
        loader.load_string(
            map_content,
            [terrain],
            [],
            buildings=[gate],
            building_content=building_content,
        )


def test_building_instances_are_independent(
    loader, terrain, gate, map_content
):
    building_content = (
        ".GGG.GGG..\n"
        "..........\n"
        "..........\n"
    )

    _, world = loader.load_string(
        map_content,
        [terrain],
        [],
        buildings=[gate],
        building_content=building_content,
    )

    first = world.get_tile(1, 0).building
    second = world.get_tile(5, 0).building

    assert first is not second

    first.x = 99

    assert second.x == 5
