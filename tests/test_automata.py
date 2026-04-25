import random
import pytest
from cellular_automata.automata import CombatSimulation, PlayerCell
from gridcore.types import Location

from helpers import (
    board_with_two_teams_separated,
    board_with_two_teams_at_corners,
    board_with_team_surrounded,
    board_with_team_in_cell,
    count_team_cells,
)


class TestNextCellState:
    """Unit tests for _next_cell_state() combat resolution"""

    def test_lone_team_survives_with_no_neighbors(self):
        """Isolated team should survive"""
        board = board_with_team_in_cell(5, 5, team=0)
        sim = CombatSimulation(
            board=board,
            entities=[],
            teams=[0],
            max_ticks=10,
            rng=random.Random(42),
        )

        result = sim._next_cell_state(Location(5, 5))
        assert result.contents[-1].team == 0

    def test_team_with_more_allies_wins_probabilistically(self):
        """Team with more allies should have higher win rate (run multiple times)"""
        wins = 0
        trials = 100
        rng = random.Random(123)
        
        for _ in range(trials):
            board = board_with_two_teams_separated()
            sim = CombatSimulation(
                board=board,
                entities=[],
                teams=[0, 1],
                max_ticks=10,
                rng=rng,
            )
            result = sim._next_cell_state(Location(4, 5))
            if result.contents[-1].team == 0:
                wins += 1
        
        assert wins > trials * 0.3


class TestSpawnAdjacent:
    """Unit tests for spawn_adjacent()"""

    def test_spawns_into_empty_adjacent_cell(self):
        """Team should spawn into adjacent empty cell"""
        board = board_with_two_teams_at_corners()
        initial_count = count_team_cells(board, 0)
        sim = CombatSimulation(
            board=board,
            entities=[],
            teams=[0, 1],
            max_ticks=10,
            rng=random.Random(42),
        )

        success = sim.spawn_adjacent(0)
        assert success is True

    def test_fails_when_no_empty_cells(self):
        """Should fail when all adjacent cells are occupied"""
        board = board_with_two_teams_separated()
        sim = CombatSimulation(
            board=board,
            entities=[],
            teams=[0, 1],
            max_ticks=10,
            rng=random.Random(42),
        )

        success = sim.spawn_adjacent(0)
        assert success is False


class TestInitialisation:
    """Tests for board initialization"""

    def test_creates_correct_number_of_players(self, sim_2_players, sim_3_players):
        assert len(sim_2_players.teams) == 2
        assert len(sim_3_players.teams) == 3

    def test_all_players_start_on_board(self, sim_2_players):
        state = sim_2_players.snapshot()
        total_cells = count_team_cells(state.board, 0) + count_team_cells(state.board, 1)
        assert total_cells == 2

    def test_players_in_unique_locations(self, sim_2_players):
        state = sim_2_players.snapshot()
        team0_cells = []
        team1_cells = []
        for cell in state.board.cells:
            if cell.contents:
                if cell.contents[-1].team == 0:
                    team0_cells.append(cell.location)
                elif cell.contents[-1].team == 1:
                    team1_cells.append(cell.location)
        assert len(team0_cells) == 1
        assert len(team1_cells) == 1
        assert team0_cells[0] != team1_cells[0]