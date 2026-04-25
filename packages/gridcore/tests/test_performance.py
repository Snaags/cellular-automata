import pytest
import random
import time
from gridcore.grid import Board
from gridcore.types import Location, BaseEntity
from cellular_automata.automata import CombatSimulation


def create_filled_board(width: int, height: int, density: float = 0.3, seed: int = 42) -> Board:
    """Create a board with entities filling ~density% of cells."""
    rng = random.Random(seed)
    board = Board.empty(width, height)

    target_filled = int(width * height * density)
    filled = 0

    while filled < target_filled:
        x = rng.randint(0, width - 1)
        y = rng.randint(0, height - 1)
        loc = Location(x, y)
        if board.location_is_empty(loc):
            team = rng.randint(0, 3)
            entity = BaseEntity(team=team, health=1)
            board.add_entity_at_empty_location(entity, loc)
            filled += 1

    return board


class TestBoardPerformance:
    @pytest.mark.parametrize("width,height,threshold", [
        (20, 20, 5.0),
        (50, 50, 50.0),
        (100, 100, 200.0),
    ])
    def test_get_cells_boardering_empty(self, width, height, threshold):
        board = create_filled_board(width, height, density=0.3)

        start = time.perf_counter()
        result = board.get_cells_boardering_empty()
        elapsed = (time.perf_counter() - start) * 1000

        assert elapsed < threshold, f"get_cells_boardering_empty ({width}x{height}) took {elapsed:.2f}ms, expected <{threshold}ms"

    def test_get_valid_neighbours(self):
        board = create_filled_board(50, 50, density=0.3)
        loc = Location(25, 25)

        start = time.perf_counter()
        for _ in range(1000):
            result = board.get_valid_neighbours(loc)
        elapsed = (time.perf_counter() - start) * 1000 / 1000

        assert elapsed < 0.5, f"get_valid_neighbours took {elapsed:.2f}ms, expected <0.5ms"

    def test_get_cells_boardering_other(self):
        board = create_filled_board(30, 30, density=0.4)

        start = time.perf_counter()
        for _ in range(100):
            result = board.get_cells_boardering_other(team=0)
        elapsed = (time.perf_counter() - start) * 1000 / 100

        assert elapsed < 10.0, f"get_cells_boardering_other took {elapsed:.2f}ms, expected <10ms"


class TestSimulationPerformance:
    @pytest.mark.parametrize("factions,width,height,ticks,threshold", [
        (2, 20, 20, 50, 20.0),
        (3, 50, 50, 20, 100.0),
        (5, 100, 100, 10, 500.0),
    ])
    def test_advance_tick(self, factions, width, height, ticks, threshold):
        sim = CombatSimulation.initialise_board_with_n_players(
            factions=factions,
            width=width,
            height=height,
            max_ticks=100,
            rng=random.Random(42),
        )

        start = time.perf_counter()
        for _ in range(ticks):
            sim.advance({})
        elapsed = (time.perf_counter() - start) * 1000 / ticks

        assert elapsed < threshold, f"advance ({width}x{height}, {factions} factions) took {elapsed:.2f}ms, expected <{threshold}ms"

    def test_full_simulation_100_ticks(self):
        sim = CombatSimulation.initialise_board_with_n_players(
            factions=5,
            width=30,
            height=30,
            max_ticks=100,
            rng=random.Random(42),
        )

        start = time.perf_counter()
        for tick in range(100):
            sim.advance({})
        total_elapsed = (time.perf_counter() - start) * 1000

        assert total_elapsed < 1000.0, f"100 ticks took {total_elapsed:.2f}ms, expected <1000ms"