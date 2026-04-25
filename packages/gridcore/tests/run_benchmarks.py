#!/usr/bin/env python3
"""
Performance benchmark runner that logs results to a file.
"""
import random
import time
import cProfile
import pstats
import io
import json
from datetime import datetime
from cellular_automata.automata import CombatSimulation


def run_benchmark(factions, width, height, ticks, rng_seed=42, name=""):
    """Run a single benchmark."""
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

    s = io.StringIO()
    stats = pstats.Stats(profiler, stream=s)
    stats.sort_stats('cumulative')
    stats.print_stats(20)
    profile_output = s.getvalue()

    # Parse top functions
    top_functions = []
    for line in profile_output.split('\n')[5:25]:
        if line.strip():
            top_functions.append(line.strip())

    result = {
        "name": name,
        "timestamp": datetime.now().isoformat(),
        "config": {
            "factions": factions,
            "width": width,
            "height": height,
            "ticks": ticks,
            "rng_seed": rng_seed,
        },
        "results": {
            "total_time_ms": elapsed * 1000,
            "time_per_tick_ms": (elapsed / ticks) * 1000,
            "cells_occupied": int((sim.board._teams != -1).sum()),
            "total_cells": width * height,
            "density": float((sim.board._teams != -1).sum()) / (width * height),
        },
        "top_functions": top_functions,
    }

    return result


def run_all_benchmarks():
    """Run all benchmarks and log to file."""
    benchmarks = [
        # Name, factions, width, height, ticks
        ("small_50x20_full", 10, 50, 20, 200),
        ("medium_50x50", 5, 50, 50, 100),
        ("large_300x50", 5, 300, 50, 100),
        ("full_100x50", 5, 100, 50, 2000),
    ]

    results = []
    for name, factions, width, height, ticks in benchmarks:
        print(f"Running {name}...")
        result = run_benchmark(factions, width, height, ticks, name=name)
        results.append(result)
        print(f"  {result['results']['time_per_tick_ms']:.2f}ms/tick")

    return results


if __name__ == "__main__":
    results = run_all_benchmarks()
    
    # Save to JSON
    with open("benchmark_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\nResults saved to benchmark_results.json")
