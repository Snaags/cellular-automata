from textual.app import App, ComposeResult
from textual.widgets import Static
from textual.binding import Binding

from gridcore.types import Location
from cellular_automata.automata import CombatSimulation
from gridcore.simulation import Snapshot
import json


TEAM_COLORS = {
    0: "gray",
    1: "green",
    2: "red",
    3: "blue",
    4: "lightgreen",
    5: "cyan",
    6: "yellow",
}


class CellularAutomataApp(App):
    CSS = """
    Screen {
        background: black;
    }
    #board {
        width: 100%;
        height: 100%;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self, config_path: str):
        super().__init__()
        self.config = self.load_config(config_path)
        self.engine = CombatSimulation.initialise_board_with_n_players(
            factions=self.config["factions"],
            width=self.config["board"]["width"],
            height=self.config["board"]["height"],
            max_ticks=10000,
            rng=None,
        )
        self.tick_rate = self.config.get("tick_rate_ms", 100) / 1000.0

    def load_config(self, path: str) -> dict:
        with open(path) as f:
            return json.load(f)

    def compose(self) -> ComposeResult:
        yield Static(id="board")

    def render_board(self, state: Snapshot) -> str:
        board = state.board
        board_width = board.width
        board_height = board.height

        display = self.size

        if display.width == 0 or display.height == 0:
            display = (80, 24)

        render_width = display.width
        render_height = display.height - 1

        board_aspect = board_width / board_height

        if board_aspect >= 1:
            render_width = display.width
            if board_aspect > 1:
                render_height = int(render_width / board_aspect)
        else:
            render_height = display.height - 1
            render_width = int(render_height * board_aspect)

        pad_left = 0
        pad_top = 0

        scale_x = board_width / render_width
        scale_y = board_height / render_height

        lines = []
        for _ in range(pad_top):
            lines.append(" " * display.width)

        for dy in range(render_height):
            line = " " * pad_left
            for dx in range(render_width):
                bx = int(dx * scale_x)
                by = int(dy * scale_y)
                cell = board.at(Location(bx, by))

                if cell.contents:
                    team = int(cell.contents[-1].team) + 1
                    color = TEAM_COLORS.get(team, "white")
                    line += f"[{color}]■[/]"
                else:
                    line += "[gray]·[/]"
            lines.append(line + " " * (display.width - len(line)))

        for _ in range(display.height - 1 - render_height - pad_top):
            lines.append(" " * display.width)

        return "\n".join(lines)

    def on_mount(self) -> None:
        self.timer = self.set_interval(self.tick_rate, self.tick)

    def tick(self):
        state = self.engine.advance({})
        board_text = self.render_board(state)
        status = f" Tick: {state.tick} | Outcome: {state.outcome} "
        self.query_one("#board", Static).update(board_text + "\n" + status)

    def action_quit(self) -> None:
        self.exit()


def main():
    import sys
    config_path = None
    for i, arg in enumerate(sys.argv[1:]):
        if arg == "--config" and i + 1 < len(sys.argv):
            config_path = sys.argv[i + 2]
            break

    if not config_path:
        print("Usage: cellular-automata-textual --config <path/to/config.json>")
        sys.exit(1)

    app = CellularAutomataApp(config_path)
    app.run()


if __name__ == "__main__":
    main()