# test_board.py
import pytest
import random
from gridcore.types import Location, BaseEntity
from gridcore.grid import Cell, Board


# ---------- helpers ---------------------------------------------------------
@pytest.fixture
def board3x3():
    return Board.empty(3, 3)


def an_entity():
    return BaseEntity(team=1, health=1)


# ----------------------------------------------------------------------------


# 1 ─ basic geometry ---------------------------------------------------------
def test_number_of_cells(board3x3):
    assert board3x3.number_of_cells == 9


@pytest.mark.parametrize(
    "loc, idx",
    [
        (Location(0, 0), 0),
        (Location(2, 0), 2),
        (Location(0, 2), 6),
        (Location(2, 2), 8),
    ],
)
def test_at_indexes_correct_cell(board3x3, loc, idx):
    assert board3x3.at(loc).location == loc
    assert board3x3.cells[idx].location == loc  # mirrors mapping


# 2 ─ adding entities --------------------------------------------------------
def test_add_entity_success(board3x3):
    loc = Location(1, 1)
    board3x3.add_entity_at_empty_location(an_entity(), loc)
    assert not board3x3.location_is_empty(loc)
    assert board3x3.at(loc).contents  # not empty list


def test_add_entity_fails_if_occupied(board3x3):
    loc = Location(0, 0)
    board3x3.add_entity_at_empty_location(an_entity(), loc)
    with pytest.raises(ValueError):
        board3x3.add_entity_at_empty_location(an_entity(), loc)


# 3 ─ empty-location pickers --------------------------------------------------
def test_random_empty_location_is_empty(board3x3, monkeypatch):
    # deterministic: force randint/choice to return index 0 first
    monkeypatch.setattr(random, "randint", lambda *_: 0)
    monkeypatch.setattr(random, "choice", lambda seq: seq[0])
    loc = board3x3.get_any_empty_location_on_board()
    assert board3x3.location_is_empty(loc)


def test_random_empty_location_raises_when_full(board3x3):
    # fill the board
    for cell in board3x3.cells:
        cell.contents.append(an_entity())
    with pytest.raises(ValueError):
        board3x3.get_any_empty_location_on_board()


# 4 ─ bounds validation ------------------------------------------------------
@pytest.mark.parametrize(
    "loc, expected",
    [
        (Location(0, 0), True),
        (Location(2, 2), True),
        (Location(-1, 0), False),
        (Location(3, 1), False),
    ],
)
def test_validate_position(board3x3, loc, expected):
    assert board3x3._validate_position(loc) is expected


# 5 ─ neighbours -------------------------------------------------------------
def test_get_valid_neighbours_corners(board3x3):
    loc = Location(0, 0)  # NW corner
    ns = board3x3.get_valid_neighbours(loc)
    assert list(ns) == [Location(1, 0), Location(0, 1)]  # east & south only


# 6 ─ cells bordering empty --------------------------------------------------
def test_cells_bordering_empty(board3x3):
    # put an entity in the centre; its 4 neighbours should now “border empty”
    centre = Location(1, 1)
    board3x3.add_entity_at_empty_location(an_entity(), centre)
    bordering = board3x3.get_cells_boardering_empty()
    locations = [c.location for c in bordering]
    expected = [Location(0, 1), Location(2, 1), Location(1, 0), Location(1, 2)]
    assert list(locations) == expected
