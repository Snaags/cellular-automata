# test_grid.py
import random
import pytest

from gridcore.grid import Cell, Board
from gridcore.types import Location, BaseEntity


# -------------------------------------------------------------------------
#  helpers
# -------------------------------------------------------------------------
class DummyEntity(BaseEntity):
    """Minimal stub with just the `team` field used by Cell.controlled_by."""

    def __init__(self, team: int):
        self.team = team


def mk_board(w=4, h=4) -> Board:
    return Board.empty(w, h)


# -------------------------------------------------------------------------
#  Cell behaviour
# -------------------------------------------------------------------------
def test_is_empty_flag():
    c = Cell(Location(0, 0))
    assert c.is_empty  # no contents
    c.contents.append(DummyEntity(1))
    assert not c.is_empty  # now occupied


def test_controlled_by_single():
    ent = DummyEntity(team=7)
    c = Cell(Location(1, 1), contents=[ent])
    assert c.controlled_by == 7


def test_controlled_by_multiple():
    c = Cell(Location(2, 2), contents=[DummyEntity(1), DummyEntity(2)])
    with pytest.raises(IndexError):
        _ = c.controlled_by


# -------------------------------------------------------------------------
#  Board construction & indexing
# -------------------------------------------------------------------------
def test_board_empty_shape_and_cells():
    w, h = 3, 5
    b = mk_board(w, h)
    assert b.width == w and b.height == h
    assert len(b.cells) == w * h
    # all cells start empty
    assert all(cell.is_empty for cell in b.cells)


def test_board_at_row_major():
    b = mk_board(3, 3)
    loc = Location(2, 1)  # row 2, col 1
    idx = loc.x * b.height + loc.y
    assert b.at(loc) is b.cells[idx]


# -------------------------------------------------------------------------
#  Mutating helpers
# -------------------------------------------------------------------------
def test_add_entity_at_empty_location_success():
    b = mk_board(2, 2)
    loc = Location(0, 1)
    ent = DummyEntity(team=0)

    b.add_entity_at_empty_location(ent, loc)
    assert not b.at(loc).is_empty
    assert b.at(loc).contents[0] is ent


def test_add_entity_at_empty_location_failure():
    b = mk_board(2, 2)
    loc = Location(1, 1)
    b.at(loc).contents.append(DummyEntity(1))
    with pytest.raises(ValueError):
        b.add_entity_at_empty_location(DummyEntity(2), loc)


# -------------------------------------------------------------------------
#  Empty-cell search helpers


def test_get_any_empty_location(monkeypatch):
    b = mk_board(2, 2)
    # occupy three cells, leave (1,1) empty
    for loc in [Location(0, 0), Location(0, 1), Location(1, 0)]:
        b.at(loc).contents.append(DummyEntity(1))

    # force choice to pick the first element in list for determinism
    monkeypatch.setattr(random, "choice", lambda seq: seq[0])

    loc = b.get_any_empty_location_on_board()
    assert loc == Location(1, 1)
    assert b.location_is_empty(loc)


# -------------------------------------------------------------------------
#  Neighbour helpers
# -------------------------------------------------------------------------
def test_validate_position_bounds():
    b = mk_board(3, 3)
    assert b._validate_position(Location(2, 2))
    assert not b._validate_position(Location(3, 0))
    assert not b._validate_position(Location(0, 3))


def test_get_valid_neighbours():
    b = mk_board(3, 3)
    loc = Location(1, 1)
    neighbours = b.get_valid_neighbours(loc)
    # centre cell on 3×3 board has 8 neighbours
    assert len(neighbours) == 8
    assert all(b._validate_position(n) for n in neighbours)


def test_get_cells_boardering_empty():
    b = mk_board(3, 3)
    # occupy centre cell, leave east neighbour empty
    centre = Location(1, 1)
    b.at(centre).contents.append(DummyEntity(0))

    edge_cells = b.get_cells_boardering_empty()
    assert b.at(centre) in edge_cells
