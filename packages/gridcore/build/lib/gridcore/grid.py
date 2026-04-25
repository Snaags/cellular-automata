# gridcore/grid.py
from dataclasses import dataclass, field
from typing import Generic, Iterable, List, Tuple, TypeVar, Union
from gridcore.types import Location, BaseEntity
import random


@dataclass
class Cell:
    location: Location
    contents: List[BaseEntity] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        return bool(self.contents)

    @property
    def controlled_by(self) -> Union[str, int]:
        if len(self.contents) > 1:
            raise IndexError(
                f"Only one entity per cell but here we have {len(self.contents)}"
            )
        return self.contents[0].team


@dataclass
class Board:
    width: int
    height: int
    cells: List[Cell]

    def __post_init__(self):
        self.number_of_cells = self.width * self.height

    @classmethod
    def empty(cls, width: int, height: int) -> "Board":
        return cls(
            width,
            height,
            [Cell(Location(x, y)) for x in range(width) for y in range(height)],
        )

    def at(self, loc: Location) -> Cell:
        if not self._validate_position(loc):
            raise IndexError(f"Location {loc} out of bounds.")
        idx = loc.x * self.height + loc.y
        return self.cells[idx]

    def add_entity_at_empty_location(self, entity: BaseEntity, loc: Location) -> None:
        cell = self.at(loc)
        if cell.is_empty:
            cell.contents.append(entity)
        else:
            raise ValueError(f"cell at {loc} not empty and contains {cell.contents}")

    def location_is_empty(self, loc: Location) -> bool:
        return self.at(loc).is_empty

    def get_any_empty_location_on_board(self):
        empty_cell_indices = [
            i for i in range(self.number_of_cells) if self.cells[i].is_empty
        ]

        index = random.choice(empty_cell_indices)

        x = index // self.width
        y = index % self.width

        return Location(x, y)

    def _validate_position(self, loc: Location) -> bool:
        if (loc.x >= self.width) or (loc.y >= self.height):
            return False
        if (loc.x < 0) or (loc.y < 0):
            return False
        return True

    def _validate_positions(self, loc: list[Location]) -> list[Location]:
        return [l for l in loc if self._validate_position(l)]

    def get_valid_neighbours(self, loc: Location) -> list[Location]:
        possible_neighbours: list[Location] = loc.possible_neighbours()
        return self._validate_positions(possible_neighbours)

    def get_cells_boardering_empty(self) -> list[Cell]:
        cells_boardering_empty = []
        for index in range(self.number_of_cells):
            cell = self.cells[index]
            if not cell.is_empty:
                possible_neighbours = self.cells[index].location.possible_neighbours()
                valid_neighbours = self._validate_positions(possible_neighbours)
                empty_neighbours = [
                    loc for loc in valid_neighbours if self.at(loc).is_empty
                ]
                if any(empty_neighbours):
                    cells_boardering_empty.append(cell)
        return cells_boardering_empty
