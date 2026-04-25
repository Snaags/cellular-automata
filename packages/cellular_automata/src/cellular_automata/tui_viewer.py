import sys
import json
import time
from pathlib import Path
from typing import Union
from dataclasses import dataclass

import blessed
from gridcore.types import Location
from cellular_automata.automata import CombatSimulation
from gridcore.simulation import Snapshot


@dataclass
class Config:
    board_width: int
    board_height: int
    factions: int
    tick_rate_ms: int


def load_config(path: Path) -> Config:
    with open(path) as f:
        data = json.load(f)
    board = data.get("board", {})
    return Config(
        board_width=board.get("width", 50),
        board_height=board.get("height", 50),
        factions=data.get("factions", 5),
        tick_rate_ms=data.get("tick_rate_ms", 100),
    )


TEAM_COLORS = {
    0: "gray",
    1: "green",
    2: "red",
    3: "blue",
    4: "lightgreen",
    5: "cyan",
    6: "yellow",
}


def get_team_display(team: int) -> str:
    return "▮"


def render_board(state: Snapshot, term: blessed.Terminal) -> None:
    display_width = term.width or 80
    display_height = (term.height or 24) - 1
    board = state.board

    render_width = display_width
    render_height = display_height

    pad_left = 0
    pad_top = 0

    scale_x = board.width / render_width
    scale_y = board.height / render_height

    for dy in range(render_height):
        line = " " * pad_left
        for dx in range(render_width):
            bx = int(dx * scale_x)
            by = int(dy * scale_y)
            cell = board.at(Location(bx, by))

            if cell.contents:
                team = int(cell.contents[-1].team) + 1
                color = TEAM_COLORS.get(team, "white")
                line += getattr(term, color)(get_team_display(team))
            else:
                line += term.gray("·")
        line += " " * (display_width - len(line))
        sys.stdout.write(term.move_xy(0, dy + pad_top) + line)

    status = f" Tick: {state.tick} | Outcome: {state.outcome} "
    sys.stdout.write(term.move_xy(0, display_height) + term.black_on_white(status.ljust(display_width)))
    sys.stdout.flush()


def main() -> None:
    config_path = None
    for i, arg in enumerate(sys.argv[1:]):
        if arg == "--config" and i + 1 < len(sys.argv):
            config_path = Path(sys.argv[i + 2])
            break

    if not config_path:
        print("Usage: cellular-automata-tui --config <path/to/config.json>")
        sys.exit(1)

    config = load_config(config_path)

    term = blessed.Terminal()
    engine = CombatSimulation.initialise_board_with_n_players(
        factions=config.factions,
        width=config.board_width,
        height=config.board_height,
        max_ticks=1000,
        rng=None,
    )

    try:
        with term.fullscreen(), term.cbreak(), term.hidden_cursor():
            gstate = engine.snapshot()
            render_board(gstate, term)

            while gstate.outcome == "ongoing":
                time.sleep(config.tick_rate_ms / 1000.0)
                gstate = engine.advance({})
                render_board(gstate, term)
    finally:
        print(term.normal)


if __name__ == "__main__":
    main()

