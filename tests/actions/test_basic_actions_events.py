import random

import pytest

from instinct.actions.basic import (
    AttackAction,
    ConsumeAction,
    MoveAction,
    ReproduceAction,
    RoarAction,
)
from instinct.backend.ast_nodes import (
    HeaderNode,
    LabelNode,
    ProgramNode,
)
from instinct.engine.action_event import ActionEventLog
from instinct.engine.event_log import EventLog
from instinct.runtime.execution_context import ExecutionContext
from instinct.runtime.program import Program
from instinct.world.entities import Creature, Terrain
from instinct.world.world_grid import WorldGrid


@pytest.fixture
def simulation_context():
    """Construye un contexto real de ejecución para probar acciones."""

    header = HeaderNode(
        lineno=1,
        creature="Naruto",
        faction="Konoha",
        health=100,
        vision=5,
        lifespan=500,
    )

    ast = ProgramNode(
        lineno=1,
        header=header,
        statements=[
            LabelNode(lineno=7, name="start"),
        ],
    )

    program = Program(ast)

    terrain = Terrain(
        name="Grass",
        char=".",
        resource_max=100,
        regen=2,
    )

    world = WorldGrid(
        width=5,
        height=5,
        default_terrain=terrain,
    )

    creature = Creature(
        name="Naruto",
        faction="Konoha",
        health=100,
        vision=5,
        lifespan=500,
    )

    world.place_creature(creature, 1, 1)

    action_event_log = ActionEventLog()
    event_log = EventLog()

    context = ExecutionContext(
        program=program,
        creature=creature,
        world=world,
        rng=random.Random(0),
        event_log=event_log,
        action_event_log=action_event_log,
    )

    return {
        "context": context,
        "world": world,
        "creature": creature,
        "action_events": action_event_log,
        "event_log": event_log,
    }


def test_move_publishes_event_with_real_displacement(simulation_context):
    data = simulation_context

    MoveAction().execute(
        data["context"],
        [1, 0, 2],
    )

    creature = data["creature"]
    events = data["action_events"].events

    assert (creature.x, creature.y) == (3, 1)
    assert len(events) == 1

    event = events[0]

    assert event.event_type == "move"
    assert event.actor_ref is creature
    assert event.data["start"] == (1, 1)
    assert event.data["end"] == (3, 1)
    assert event.data["distance"] == 2


def test_move_does_not_publish_event_when_blocked(simulation_context):
    data = simulation_context

    obstacle = Creature(
        name="Sasuke",
        faction="Konoha",
        health=100,
        vision=5,
        lifespan=500,
    )

    data["world"].place_creature(obstacle, 2, 1)

    MoveAction().execute(
        data["context"],
        [1, 0, 2],
    )

    assert (data["creature"].x, data["creature"].y) == (1, 1)
    assert len(data["action_events"].events) == 0


def test_attack_publishes_attack_and_damage_events(simulation_context):
    data = simulation_context

    target = Creature(
        name="Sasuke",
        faction="Uchiha",
        health=50,
        vision=5,
        lifespan=500,
    )

    data["world"].place_creature(target, 2, 1)

    AttackAction().execute(
        data["context"],
        [1, 0, 15],
    )

    events = data["action_events"].events

    assert target.health == 35
    assert [event.event_type for event in events] == [
        "attack",
        "damage",
    ]

    assert events[0].actor_ref is data["creature"]
    assert events[1].target_ref is target
    assert events[1].data["damage"] == 15
    assert events[1].data["remaining_health"] == 35


def test_lethal_attack_publishes_death_and_preserves_target_reference(
    simulation_context,
):
    data = simulation_context

    target = Creature(
        name="Sasuke",
        faction="Uchiha",
        health=10,
        vision=5,
        lifespan=500,
    )

    data["world"].place_creature(target, 2, 1)

    AttackAction().execute(
        data["context"],
        [1, 0, 20],
    )

    events = data["action_events"].events

    assert [event.event_type for event in events] == [
        "attack",
        "damage",
        "death",
    ]

    death_event = events[-1]

    assert death_event.target_ref is target
    assert death_event.target_name == "Sasuke"
    assert death_event.target_x == 2
    assert death_event.target_y == 1

    assert target.health <= 0
    assert data["world"].get_tile(2, 1).creature is None


def test_consume_publishes_event_and_heals_actor(simulation_context):
    data = simulation_context
    actor = data["creature"]
    actor.health = 40

    target = Creature(
        name="Enemy",
        faction="Enemy",
        health=50,
        vision=5,
        lifespan=500,
    )

    data["world"].place_creature(target, 2, 1)

    ConsumeAction().execute(
        data["context"],
        [1, 0, 10, 15],
    )

    events = data["action_events"].events

    assert actor.health == 55
    assert target.health == 40

    assert [event.event_type for event in events] == [
        "consume",
        "damage",
    ]

    assert events[0].actor_ref is actor
    assert events[1].target_ref is target

def test_consume_cannot_exceed_maximum_health(simulation_context):
    data = simulation_context
    actor = data["creature"]

    actor.health = 90

    target = Creature(
        name="Enemy",
        faction="Enemy",
        health=50,
        vision=5,
        lifespan=500,
    )
    data["world"].place_creature(target, 2, 1)

    ConsumeAction().execute(
        data["context"],
        [1, 0, 10, 22],
    )

    assert actor.health == 100


def test_consume_preserves_health_below_maximum(simulation_context):
    data = simulation_context
    actor = data["creature"]

    actor.health = 40

    target = Creature(
        name="Enemy",
        faction="Enemy",
        health=50,
        vision=5,
        lifespan=500,
    )
    data["world"].place_creature(target, 2, 1)

    ConsumeAction().execute(
        data["context"],
        [1, 0, 10, 15],
    )

    assert actor.health == 55


def test_reproduce_publishes_event_and_creates_child(simulation_context):
    data = simulation_context
    mother = data["creature"]

    ReproduceAction().execute(
        data["context"],
        [0, 1, 30],
    )

    child = data["world"].get_tile(1, 2).creature
    events = data["action_events"].events

    assert child is not None
    assert child is not mother
    assert child.name == mother.name
    assert child.health == 30
    assert child.program is data["context"].program

    assert mother.health == 70

    assert len(events) == 1
    assert events[0].event_type == "reproduce"
    assert events[0].actor_ref is mother
    assert events[0].target_ref is child


def test_roar_publishes_structured_event(simulation_context):
    data = simulation_context

    RoarAction().execute(
        data["context"],
        ["¡Rasengan!"],
    )

    events = data["action_events"].events

    assert len(events) == 1
    assert events[0].event_type == "roar"
    assert events[0].actor_ref is data["creature"]
    assert events[0].data["message"] == "¡Rasengan!"


def test_action_events_keep_the_correct_tick(simulation_context):
    data = simulation_context
    context = data["context"]

    context.current_tick = 42

    RoarAction().execute(
        context,
        ["¡Vamos!"],
    )

    event = data["action_events"].events[0]

    assert event.tick == 42


def test_failed_reproduction_does_not_publish_event(simulation_context):
    data = simulation_context

    # La criatura no puede reproducirse sobre una casilla ocupada.
    obstacle = Creature(
        name="Sasuke",
        faction="Uchiha",
        health=100,
        vision=5,
        lifespan=500,
    )

    data["world"].place_creature(obstacle, 1, 2)

    ReproduceAction().execute(
        data["context"],
        [0, 1, 30],
    )

    assert data["creature"].health == 100
    assert len(data["action_events"].events) == 0