# Performance Optimization Changelog

## v0.1.4 - Direct Empty Spawn Locations

### Changes
- Added `get_empty_spawn_locations_for_team()` method in grid_numpy.py that directly finds empty cells adjacent to team cells
- Simplified `spawn_adjacent()` to use the new method (no separate neighbor lookup + filtering)

### Benchmark Results
| Benchmark | v0.1.3 | v0.1.4 | Improvement |
|-----------|--------|--------|-------------|
| small_50x20_full | 1.91ms/tick | 1.71ms/tick | 10% faster |
| medium_50x50 | 0.59ms/tick | 0.46ms/tick | 22% faster |
| large_300x50 | 0.78ms/tick | 0.66ms/tick | 15% faster |
| full_100x50 | 1.30ms/tick | 1.26ms/tick | 3% faster |

### Total improvement from baseline (v0.1.2)
| Benchmark | Baseline | Current | Improvement |
|-----------|----------|---------|--------------|
| small_50x20_full | 3.97ms/tick | 1.71ms/tick | **57% faster** |
| medium_50x50 | 1.36ms/tick | 0.46ms/tick | **66% faster** |
| large_300x50 | 1.58ms/tick | 0.66ms/tick | **58% faster** |
| full_100x50 | 2.95ms/tick | 1.26ms/tick | **57% faster** |

---

## v0.1.3 - Spawn Adjacent Optimization

### Changes
- Added `get_cells_bordering_empty_for_team()` method in grid_numpy.py that directly returns Location objects instead of Cell objects
- Updated `spawn_adjacent()` in automata.py to use the new method, eliminating controlled_by property calls

### Benchmark Results
| Benchmark | Before | After | Improvement |
|-----------|--------|-------|--------------|
| small_50x20_full | 3.97ms/tick | 1.91ms/tick | **52% faster** |
| medium_50x50 | 1.36ms/tick | 0.59ms/tick | **57% faster** |
| large_300x50 | 1.58ms/tick | 0.78ms/tick | **51% faster** |
| full_100x50 | 2.95ms/tick | 1.30ms/tick | **56% faster** |

### Key Insight
The `controlled_by` property was being called tens of thousands of times per tick. By computing team membership directly in numpy, we avoid creating Cell objects and property calls.

---

## v0.1.2 - Baseline (Before Optimization)

### Benchmark Results
| Benchmark | Time per tick |
|-----------|---------------|
| small_50x20_full | 3.97ms/tick |
| medium_50x50 | 1.36ms/tick |
| large_300x50 | 1.58ms/tick |
| full_100x50 | 2.95ms/tick |

### Key Bottlenecks (50x20 full board)
- `get_cells_boardering_empty`: 362ms total (2,910 calls)
- `controlled_by` property: 99ms total (436,305 calls!)