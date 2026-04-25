from cellular_automata.automata import PlayerCell
from gridcore.grid import Board
from gridcore.types import Location


def board_with_team_in_cell(x: int, y: int, team: int) -> Board:
    """Create a board with a single team cell at given position"""
    board = Board.empty(10, 10)
    board.add_entity_at_empty_location(PlayerCell(team=team, health=1), Location(x, y))
    return board


def board_with_two_teams_separated() -> Board:
    """10x10 board: team 0 on left half, team 1 on right half"""
    board = Board.empty(10, 10)

    for x in range(5):
        for y in range(10):
            board.add_entity_at_empty_location(PlayerCell(team=0, health=1), Location(x, y))

    for x in range(5, 10):
        for y in range(10):
            board.add_entity_at_empty_location(PlayerCell(team=1, health=1), Location(x, y))

    return board


def board_with_two_teams_at_corners() -> Board:
    """10x10 board: team 0 at (0,0), team 1 at (9,9)"""
    board = Board.empty(10, 10)
    board.add_entity_at_empty_location(PlayerCell(team=0, health=1), Location(0, 0))
    board.add_entity_at_empty_location(PlayerCell(team=1, health=1), Location(9, 9))
    return board


def board_with_team_surrounded(team: int, center_x: int, center_y: int) -> Board:
    """Create board with team at center, different team surrounding it (3x3)"""
    board = Board.empty(10, 10)

    board.add_entity_at_empty_location(PlayerCell(team=team, health=1), Location(center_x, center_y))

    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            nx, ny = center_x + dx, center_y + dy
            other_team = (team + 1) % 2
            board.add_entity_at_empty_location(PlayerCell(team=other_team, health=1), Location(nx, ny))

    return board


def count_team_cells(board: Board, team: int) -> int:
    """Count cells belonging to a team"""
    count = 0
    for cell in board.cells:
        if cell.contents and cell.contents[-1].team == team:
            count += 1
    return count


def get_team_cells(board: Board, team: int) -> list[Location]:
    """Get all locations belonging to a team"""
    return [cell.location for cell in board.cells if cell.contents and cell.contents[-1].team == team]