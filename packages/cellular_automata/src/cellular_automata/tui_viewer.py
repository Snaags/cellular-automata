import sys
import json
import time
import select
from pathlib import Path
from dataclasses import dataclass

import blessed
from gridcore.types import Location
from cellular_automata.automata import CombatSimulation
from gridcore.simulation import Snapshot


@dataclass
class Viewport:
    x: int = 0
    y: int = 0


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
    return "■"


def render_board(state: Snapshot, term: blessed.Terminal, vp: Viewport) -> None:
    display_width = term.width or 80
    display_height = (term.height or 24) - 1
    board = state.board

    for dy in range(display_height):
        line = ""
        for dx in range(display_width):
            bx = vp.x + dx
            by = vp.y + dy
            if bx < board.width and by < board.height:
                cell = board.at(Location(bx, by))
                if cell.contents:
                    team = int(cell.contents[-1].team) + 1
                    color = TEAM_COLORS.get(team, "white")
                    line += getattr(term, color)(get_team_display(team))
                else:
                    line += term.gray("·")
            else:
                line += " "
        sys.stdout.write(term.move_xy(0, dy) + line)

    status = f" Tick: {state.tick} | Outcome: {state.outcome} | Pos: {vp.x},{vp.y} "
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

    engine = CombatSimulation.initialise_board_with_n_players(
        factions=config.factions,
        width=config.board_width,
        height=config.board_height,
        max_ticks=1000,
        rng=None,
    )

    vp = Viewport()
    term = blessed.Terminal()

    try:
        with term.fullscreen(), term.cbreak(), term.hidden_cursor():
            gstate = engine.snapshot()
            render_board(gstate, term, vp)

            while gstate.outcome == "ongoing":
                time.sleep(config.tick_rate_ms / 1000.0)
                gstate = engine.advance({})

                if select.select([sys.stdin], [], [], 0)[0]:
                    key = sys.stdin.read(1)
                    dw = term.width or 80
                    dh = (term.height or 24) - 1
                    if key == 'h' and vp.x > 0:
                        vp.x -= 1
                    elif key == 'l' and vp.x + dw < config.board_width:
                        vp.x += 1
                    elif key == 'k' and vp.y > 0:
                        vp.y -= 1
                    elif key == 'j' and vp.y + dh < config.board_height:
                        vp.y += 1

                render_board(gstate, term, vp)
    finally:
        print(term.normal)


if __name__ == "__main__":
    main()