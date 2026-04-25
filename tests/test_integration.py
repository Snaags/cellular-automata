import pytest
from cellular_automata.automata import CombatSimulation
from helpers import count_team_cells


class TestSimulation:
    """Integration tests using headless simulation"""

    def test_simulation_runs_without_error(self, sim_2_players):
        """Simulation should advance without crashing"""
        state = sim_2_players.snapshot()
        for _ in range(10):
            state = sim_2_players.advance({})
        assert state.tick == 10

    def test_tick_increments(self, sim_small_board):
        """Tick should increment each advance"""
        state = sim_small_board.snapshot()
        assert state.tick == 0
        for _ in range(5):
            state = sim_small_board.advance({})
        assert state.tick == 5

    def test_teams_can_spawn(self, sim_2_players):
        """Teams should be able to spawn new cells"""
        state = sim_2_players.snapshot()
        initial_team0 = count_team_cells(state.board, 0)
        initial_team1 = count_team_cells(state.board, 1)

        for _ in range(50):
            state = sim_2_players.advance({})

        final_team0 = count_team_cells(state.board, 0)
        final_team1 = count_team_cells(state.board, 1)

        assert final_team0 >= initial_team0
        assert final_team1 >= initial_team1

    def test_combats_tracked(self, sim_2_players):
        """Combats should be tracked in snapshot"""
        for _ in range(100):
            state = sim_2_players.advance({})

        assert hasattr(state, 'combats')
        assert isinstance(state.combats, tuple)

    def test_no_crash_on_small_board(self, sim_small_board):
        """Small board should not crash (regression test)"""
        state = sim_small_board.snapshot()
        for _ in range(20):
            state = sim_small_board.advance({})
        assert state.tick == 20

    def test_outcome_ongoing_initially(self, sim_2_players):
        """Outcome should be ongoing at start"""
        state = sim_2_players.snapshot()
        assert state.outcome == "ongoing"