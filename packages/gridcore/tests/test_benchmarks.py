import pytest
import random
import time
import cProfile
import pstats
import io
from gridcore.grid_numpy import Board
from gridcore.types import Location, BaseEntity
from cellular_automata.automata import CombatSimulation


def run_and_profile(factions, width, height, ticks, rng_seed=42):
    """Run simulation and return profiling stats."""
    profiler = cProfile.Profile()
    profiler.enable()

    sim = CombatSimulation.initialise_board_with_n_players(
        factions=factions,
        width=width,
        height=height,
        max_ticks=ticks,
        rng=random.Random(rng_seed),
    )

    start = time.perf_counter()
    for _ in range(ticks):
        sim.advance({})
    elapsed = time.perf_counter() - start

    profiler.disable()

    # Get stats
    s = io.StringIO()
    stats = pstats.Stats(profiler, stream=s)
    stats.sort_stats('cumulative')
    stats.print_stats(20)

    return {
        'factions': factions,
        'width': width,
        'height': height,
        'ticks': ticks,
        'total_time': elapsed,
        'time_per_tick': elapsed / ticks,
        'cells_occupied': (sim.board._teams != -1).sum(),
        'max_cells': width * height,
        'profile_output': s.getvalue(),
    }


def print_results(results):
    """Print benchmark results nicely."""
    r = results
    print(f"\n{'='*60}")
    print(f"Benchmark: {r['width']}x{r['height']} board, {r['factions']} factions, {r['ticks']} ticks")
    print(f"{'='*60}")
    print(f"Total runtime:     {r['total_time']*1000:.1f}ms")
    print(f"Time per tick:      {r['time_per_tick']*1000:.2f}ms")
    print(f"Cells occupied:    {r['cells_occupied']}/{r['max_cells']} ({r['cells_occupied']/r['max_cells']*100:.1f}%)")
    print(f"\nTop functions by cumulative time:")
    print(r['profile_output'])


class TestLargeBoard:
    """Tests for large boards to find bottlenecks."""

    def test_large_board_300x50_100ticks(self):
        """300x50 board with 100 ticks - tests large board performance."""
        results = run_and_profile(
            factions=5,
            width=300,
            height=50,
            ticks=100,
        )
        print_results(results)
        # Should complete in reasonable time
        assert results['total_time'] < 10.0, f"Too slow: {results['total_time']}s"

    def test_large_board_100x100_50ticks(self):
        """100x100 board with 50 ticks."""
        results = run_and_profile(
            factions=5,
            width=100,
            height=100,
            ticks=50,
        )
        print_results(results)
        assert results['total_time'] < 5.0

    def test_medium_board_50x50_200ticks(self):
        """50x50 board over longer period."""
        results = run_and_profile(
            factions=3,
            width=50,
            height=50,
            ticks=200,
        )
        print_results(results)
        assert results['total_time'] < 5.0


class TestSmallBoardFull:
    """Tests for small boards to test when board fills up."""

    def test_small_board_50x20_full(self):
        """50x20 board - tests behavior as board fills."""
        results = run_and_profile(
            factions=10,
            width=50,
            height=20,
            ticks=200,
        )
        print_results(results)
        # Board is nearly full
        density = results['cells_occupied'] / results['max_cells']
        print(f"\nFinal density: {density*100:.1f}%")

    def test_very_small_board_20x10_many_teams(self):
        """20x10 with many teams - fills quickly."""
        results = run_and_profile(
            factions=20,
            width=20,
            height=10,
            ticks=100,
        )
        print_results(results)
        density = results['cells_occupied'] / results['max_cells']
        print(f"\nFinal density: {density*100:.1f}%")

    def test_tiny_board_10x10_slow_fill(self):
        """10x10 board - very constrained."""
        results = run_and_profile(
            factions=5,
            width=10,
            height=10,
            ticks=50,
        )
        print_results(results)
        density = results['cells_occupied'] / results['max_cells']
        print(f"\nFinal density: {density*100:.1f}%")


class TestScaling:
    """Tests to understand scaling behavior."""

    def test_width_scaling(self):
        """Test scaling with width (fixed height)."""
        for width in [50, 100, 200, 300]:
            results = run_and_profile(
                factions=3,
                width=width,
                height=50,
                ticks=50,
            )
            print(f"{width}x50: {results['time_per_tick']*1000:.2f}ms/tick, {results['cells_occupied']} cells")

    def test_height_scaling(self):
        """Test scaling with height (fixed width)."""
        for height in [20, 50, 100]:
            results = run_and_profile(
                factions=3,
                width=50,
                height=height,
                ticks=50,
            )
            print(f"50x{height}: {results['time_per_tick']*1000:.2f}ms/tick, {results['cells_occupied']} cells")

    def test_factions_scaling(self):
        """Test scaling with factions."""
        for factions in [2, 5, 10, 20]:
            results = run_and_profile(
                factions=factions,
                width=50,
                height=50,
                ticks=50,
            )
            print(f"{factions} factions: {results['time_per_tick']*1000:.2f}ms/tick, {results['cells_occupied']} cells")


class TestEdgeCases:
    """Edge case tests."""

    def test_single_faction(self):
        """Minimal simulation with just 1 faction."""
        results = run_and_profile(
            factions=1,
            width=50,
            height=50,
            ticks=50,
        )
        print_results(results)

    def test_max_factions_small_board(self):
        """Many factions on small board."""
        results = run_and_profile(
            factions=50,
            width=30,
            height=30,
            ticks=30,
        )
        print_results(results)
        # Should fill quickly
        assert results['cells_occupied'] / results['max_cells'] > 0.9


if __name__ == "__main__":
    # Run specific tests manually
    print("Running large board test...")
    TestLargeBoard().test_large_board_300x50_100ticks()