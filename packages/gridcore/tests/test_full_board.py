import pytest
import random
import time
import cProfile
import pstats
import io
from cellular_automata.automata import CombatSimulation


def run_until_full(factions, width, height, max_ticks=5000, rng_seed=42):
    """Run simulation until board is full (or max ticks)."""
    profiler = cProfile.Profile()
    profiler.enable()

    sim = CombatSimulation.initialise_board_with_n_players(
        factions=factions,
        width=width,
        height=height,
        max_ticks=max_ticks,
        rng=random.Random(rng_seed),
    )

    total_cells = width * height
    ticks = 0
    start = time.perf_counter()
    
    while ticks < max_ticks:
        sim.advance({})
        ticks += 1
        occupied = (sim.board._teams != -1).sum()
        if occupied >= total_cells:
            break
            
    elapsed = time.perf_counter() - start

    profiler.disable()

    s = io.StringIO()
    stats = pstats.Stats(profiler, stream=s)
    stats.sort_stats('cumulative')
    stats.print_stats(30)

    return {
        'factions': factions,
        'width': width,
        'height': height,
        'ticks_to_fill': ticks,
        'total_time': elapsed,
        'time_per_tick': elapsed / ticks,
        'cells_occupied': occupied,
        'total_cells': total_cells,
        'density': occupied / total_cells,
        'profile_output': s.getvalue(),
    }


def print_full_results(results):
    """Print results for full board test."""
    r = results
    print(f"\n{'='*70}")
    print(f"FULL BOARD TEST: {r['width']}x{r['height']} board, {r['factions']} factions")
    print(f"{'='*70}")
    print(f"Ticks to fill:     {r['ticks_to_fill']}")
    print(f"Total runtime:    {r['total_time']*1000:.1f}ms")
    print(f"Avg time per tick: {r['time_per_tick']*1000:.2f}ms")
    print(f"Cells filled:      {r['cells_occupied']}/{r['total_cells']} ({r['density']*100:.1f}%)")
    print(f"\nFunction profile:")
    print(r['profile_output'])


class TestFullBoard:
    """Tests for when board is completely full."""

    def test_50x20_full(self):
        """50x20 board - small, fills quickly."""
        results = run_until_full(
            factions=10,
            width=50,
            height=20,
        )
        print_full_results(results)
        assert results['ticks_to_fill'] < 500
        assert results['density'] >= 0.95

    def test_30x30_full(self):
        """30x30 board."""
        results = run_until_full(
            factions=10,
            width=30,
            height=30,
        )
        print_full_results(results)
        assert results['ticks_to_fill'] < 500

    def test_100x50_full(self):
        """100x50 board - larger."""
        results = run_until_full(
            factions=5,
            width=100,
            height=50,
        )
        print_full_results(results)
        assert results['ticks_to_fill'] < 2000

    def test_many_factions_full(self):
        """Many factions on small board."""
        results = run_until_full(
            factions=30,
            width=20,
            height=20,
        )
        print_full_results(results)
        assert results['ticks_to_fill'] < 200


class TestFullBoardScaling:
    """Scaling tests for full boards."""

    def test_fill_time_scaling_width(self):
        """How does time to fill scale with width?"""
        for width in [20, 50, 100]:
            results = run_until_full(
                factions=10,
                width=width,
                height=20,
                max_ticks=5000,
            )
            print(f"{width}x20: {results['ticks_to_fill']} ticks, {results['total_time']*1000:.1f}ms total")

    def test_fill_time_scaling_factions(self):
        """How does time to fill scale with factions?"""
        for factions in [5, 10, 20, 50]:
            results = run_until_full(
                factions=factions,
                width=30,
                height=30,
                max_ticks=5000,
            )
            print(f"{factions} factions: {results['ticks_to_fill']} ticks, {results['total_time']*1000:.1f}ms total")


class TestFullBoardPerf:
    """Performance characteristics of full boards vs not-full."""

    def test_time_per_tick_before_and_after_full(self):
        """Compare time per tick before vs after board fills."""
        results = run_until_full(
            factions=10,
            width=30,
            height=30,
        )
        
        pre_fill = results['total_time'] / max(results['ticks_to_fill'] // 2, 1)
        post_fill = (results['total_time'] * 0.5) / (results['ticks_to_fill'] // 2)
        
        print(f"\n30x30 board, 10 factions:")
        print(f"  First half avg: {pre_fill*1000:.2f}ms/tick")
        print(f"  Second half avg: {post_fill*1000:.2f}ms/tick")
        print(f"  Slowdown factor: {post_fill/pre_fill:.1f}x")


if __name__ == "__main__":
    print("Running full board test...")
    TestFullBoard().test_50x20_full()