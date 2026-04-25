import random
import pytest
from cellular_automata.automata import CombatSimulation, PlayerCell
from gridcore.grid import Board


@pytest.fixture
def fixed_rng():
    return random.Random(42)


@pytest.fixture
def empty_board():
    return Board.empty(10, 10)


@pytest.fixture
def sim_2_players(fixed_rng):
    return CombatSimulation.initialise_board_with_n_players(
        factions=2,
        width=10,
        height=10,
        max_ticks=100,
        rng=fixed_rng,
    )


@pytest.fixture
def sim_3_players(fixed_rng):
    return CombatSimulation.initialise_board_with_n_players(
        factions=3,
        width=10,
        height=10,
        max_ticks=100,
        rng=fixed_rng,
    )


@pytest.fixture
def sim_small_board(fixed_rng):
    return CombatSimulation.initialise_board_with_n_players(
        factions=3,
        width=5,
        height=5,
        max_ticks=50,
        rng=fixed_rng,
    )