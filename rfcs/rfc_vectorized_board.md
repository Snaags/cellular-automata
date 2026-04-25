# RFC: Vectorized Board with NumPy

## Summary

Redesign the board storage from OOP (objects per cell) to NumPy vectorized arrays for scalability to 10k+ cells per side (100M+ total).

## Motivation

Current OOP approach with individual Cell/Entity objects has:
- Per-object memory overhead (~56 bytes per object)
- Python iteration overhead for 100M+ cells
- Not viable at target scale (10k+ cells per side = 100M+ total)

## Proposal

### New Data Layout

```python
import numpy as np

class VectorBoard:
    width: int
    height: int
    
    team: np.ndarray         # shape (height, width), -1 = empty, 0+ = team ID
    population: np.ndarray   # shape (height, width), float32
    terrain: np.ndarray     # shape (height, width), int8: 0=flat, 1=mountain, ...
    resources: np.ndarray   # shape (height, width), float32
```

### Array Specifications

| Array | dtype | Shape | Default | Description |
|-------|-------|-------|---------|-------------|
| `team` | int8 | (h, w) | -1 | Team ID (-1 = empty) |
| `population` | float32 | (h, w) | 0.0 | Cell population |
| `terrain` | int8 | (h, w) | 0 | Terrain type |
| `resources` | float32 | (h, w) | 0.0 | Cell resources |

### Initialization

```python
class VectorBoard:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.team = np.full((height, width), -1, dtype=np.int8)
        self.population = np.zeros((height, width), dtype=np.float32)
        self.terrain = np.zeros((height, width), dtype=np.int8)
        self.resources = np.zeros((height, width), dtype=np.float32)
```

### API Design

```python
class VectorBoard:
    def get_team(self, x: int, y: int) -> int:
        """Get team at location"""
        if not self.in_bounds(x, y):
            raise IndexError(f"Location ({x},{y}) out of bounds")
        return self.team[y, x]
    
    def set_team(self, x: int, y: int, team_id: int) -> None:
        """Set team at location"""
        self.team[y, x] = team_id
    
    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height
    
    # --- Vectorized operations ---
    
    def count_team_cells(self, team_id: int) -> int:
        """Count cells belonging to team (vectorized)"""
        return int(np.sum(self.team == team_id))
    
    def get_team_population(self, team_id: int) -> float:
        """Get total population of team"""
        return float(np.sum(self.population[self.team == team_id]))
    
    def get_cells_neighboring(self, x: int, y: int) -> list[tuple[int, int]]:
        """Get valid neighbor coordinates"""
        neighbors = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if self.in_bounds(nx, ny):
                    neighbors.append((nx, ny))
        return neighbors
    
    def get_team_cells(self, team_id: int) -> list[tuple[int, int]]:
        """Get all cell coordinates for a team"""
        coords = np.where(self.team == team_id)
        return list(zip(coords[1], coords[0]))  # (x, y) pairs
    
    def get_cells_neighboring_empty(self, team_id: int) -> list[tuple[int, int]]:
        """Get cells of team that border empty cells"""
        result = []
        for x, y in self.get_team_cells(team_id):
            for nx, ny in self.get_cells_neighboring(x, y):
                if self.team[ny, nx] == -1:
                    result.append((nx, ny))
        return result
    
    def get_team_cells_border_enemy(self, team_id: int) -> list[tuple[int, int]]:
        """Get cells of team bordering enemy cells"""
        result = []
        for x, y in self.get_team_cells(team_id):
            for nx, ny in self.get_cells_neighboring(x, y):
                neighbor_team = self.team[ny, nx]
                if neighbor_team != -1 and neighbor_team != team_id:
                    result.append((x, y))
                    break
        return result
```

### Changes to CombatSimulation (High-Level)

```python
class CombatSimulation:
    def __init__(self, ...):
        self.board = VectorBoard(width, height)
        self.teams = {i: Team(id=i) for i in range(factions)}
    
    def _after_tick(self) -> None:
        for team_id, team in self.teams.items():
            cell_count = self.board.count_team_cells(team_id)
            if cell_count == 0:
                team.alive = False
                continue
            team.pop += cell_count * team.growth_rate
            # ... spawn + combat logic using vectorized ops
```

## Implementation Path

### Phase 1: Core VectorBoard
1. Create `cellular_automata/vector_board.py` with VectorBoard class
2. Implement basic get/set operations
3. Implement vectorized counting methods

### Phase 2: Integration
1. Update CombatSimulation to use VectorBoard
2. Update spawn/combat logic for new board API
3. Add team population tracking for VectorBoard

### Phase 3: TUI Update
1. Update render_board for VectorBoard access patterns
2. (Optional) Add terrain visualization

### Phase 4: Testing
1. Add tests for VectorBoard
2. Test integration with simulation
3. Benchmark at scale

## Decision Points (To Confirm)

| Decision | Proposed | Status |
|----------|----------|--------|
| Separate class | VectorBoard (new) | Need confirmation |
| Keep old Board | Keep for backward compat or replace? | Need confirmation |
| Entity handling | Keep entity objects (simplest), or full arrays? | Need confirmation |

## Memory Comparison

| Config | Current (OOP) | NumPy Vectorized |
|--------|-----------------|---------------|
| 100x100 (10k cells) | ~560 MB | ~16 MB |
| 1000x1000 (1M cells) | N/A | ~160 MB |
| 10000x10000 (100M cells) | N/A | ~16 GB |

## Open Questions

- [ ] Separate VectorBoard class or refactor existing?
- [ ] Keep old Board for compatibility?
- [ ] Store team health in arrays or entity objects?
- [ ] Terrain types: flat (0) or extensible?