# Cellular Automata

Combat simulation using cellular automata with TUI viewer.

## Installation

```bash
pip install -e packages/cellular_automata/
```

## Usage

### TUI Viewer (interactive)

```bash
cellular-automata-tui --config config.json
```

Controls:
- `h` / `l` - scroll left / right
- `k` / `j` - scroll up / down

Options:
- `--config <path>` - Path to config JSON file
- `--headless`, `-n` - Run headless (no TUI, just simulation)
- `--ticks N` - Maximum ticks to simulate (default: 1000)

### Headless Mode

Run simulation without TUI for testing or benchmarking:

```bash
cellular-automata-tui --config config.json --headless --ticks 500
```

Output:
```
Outcome: ongoing (tick 500)
```

Use headless mode for:
- Quick simulation testing without TUI overhead
- Benchmarking simulation performance
- CI/CD automation

## Configuration

Create a `config.json` file:

```json
{
  "board": { "width": 50, "height": 50 },
  "factions": 5,
  "tick_rate_ms": 100
}
```

- `board.width` - Board width
- `board.height` - Board height
- `factions` - Number of factions/players
- `tick_rate_ms` - Tick rate in milliseconds (TUI only)

## Development

```bash
# Run tests
pytest packages/cellular_automata/

# Lint
ruff check packages/cellular_automata/

# Type check
mypy packages/cellular_automata/
```