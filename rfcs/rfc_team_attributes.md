# RFC: Team Attributes System

## Summary

Add a structured `Team` dataclass to track per-team attributes including population, with cell-based population that grows over time.

## Motivation

Currently teams are represented only by integer IDs (`team=0`, `team=1`, etc.) with no persistent state. This limits:
- Ability to track "population" or resource totals
- Win conditions beyond "last team standing"
- Strategic depth (resources, growth rates, bonuses)

## Proposal

### New Team Dataclass

```python
from dataclasses import dataclass

@dataclass
class Team:
    id: int
    population: float = 0.0
    population_per_cell: float = 1.0
    growth_rate: float = 0.005
    alive: bool = True
    eliminated: bool = False
```

#### Attributes

| Attribute | Type | Default | Description |
|----------|------|---------|-------------|
| `id` | int | required | Team identifier |
| `population` | float | 0.0 | Total team population |
| `population_per_cell` | float | 1.0 | "Population value" of each cell |
| `growth_rate` | float | 0.005 | Population added per cell per tick (fixed) |
| `alive` | bool | True | Team still has cells |
| `eliminated` | bool | False | Team has been eliminated |

### Population System (Decision: 1000 start, 0.005 rate, no victory)

- Each cell has `population_per_cell` base value (default 1.0)
- Starting population per team: **1000**
- Each tick: `population += population_per_cell * cell_count * growth_rate`
- Cell gained in combat: `population += population_per_cell`
- Cell lost in combat: `population -= population_per_cell`

**Equation per tick:**
```python
cell_count = count_cells(team)
team.population += cell_count * team.population_per_cell * team.growth_rate
```

#### Example (starting 1000, rate 0.005)

| Tick | Cells | Population |
|------|-------|------------|
| 0 | 1 | 1000.0 |
| 1 | 1 | 1000.005 |
| 10 | 1 | 1000.05 |
| 50 | 3 | 1015.0 |

### Changes Required

#### 1. New file: `packages/cellular_automata/src/cellular_automata/team.py`

```python
from dataclasses import dataclass

@dataclass
class Team:
    id: int
    population: float = 1000.0  # Starting population
    population_per_cell: float = 1.0
    growth_rate: float = 0.005
    alive: bool = True
    eliminated: bool = False

    def is_alive(self) -> bool:
        return self.alive and not self.eliminated
```

#### 2. Modify `automata.py`

- Change `self.teams: list[int|str]` to `self.teams: dict[int, Team]`
- Update `_after_tick()` to track population
- Update initialization to create Team objects

```python
def __init__(self, ...):
    super().__init__(...)
    self.teams = {i: Team(id=i) for i in range(factions)}

def _after_tick(self) -> None:
    for team_id, team in self.teams.items():
        if not team.is_alive():
            continue
        cell_count = self.board.count_cells(team_id)
        if cell_count == 0:
            team.alive = False
            team.eliminated = True
            continue
        team.population += cell_count * team.population_per_cell * team.growth_rate
        # ... spawn + combat logic
```

#### 3. Update `Snapshot`

```python
@dataclass(frozen=True, slots=True)
class Snapshot:
    tick: int
    board: Board
    outcome: str = 'ongoing'
    combats: tuple = ()
    teams: tuple = ()  # Add team states
```

#### 4. Add helper methods to CombatSimulation

```python
def get_team_population(self, team_id: int) -> float:
    return self.teams[team_id].population

def get_team(self, team_id: int) -> Team:
    return self.teams[team_id]

def get_active_teams(self) -> list[Team]:
    return [t for t in self.teams.values() if t.is_alive()]
```

## Test Plan

```python
def test_team_starts_with_1000_population():
    team = Team(id=0)
    assert team.population == 1000.0

def test_population_grows_over_time():
    team = Team(id=0, population=1000.0, growth_rate=0.005)
    team.population += 1 * 1.0 * 0.005  # 1 cell
    assert team.population == 1000.005

def test_team_eliminated_when_no_cells():
    team = Team(id=0, population=0, alive=False, eliminated=True)
    assert not team.is_alive()
```

## Backward Compatibility

- Existing integer team IDs still work (Team.id)
- Default values for new attributes
- No changes to board/cell structure
- Headless mode continues to work

## Timeline

1. Add `Team` dataclass to new file
2. Modify `CombatSimulation` to use teams dict
3. Add population updates in `_after_tick()`
4. Add teams to Snapshot
5. Tests

## Open Questions

- [x] Starting population: 1000
- [x] Growth rate: fixed 0.005
- [x] Victory condition: none for now