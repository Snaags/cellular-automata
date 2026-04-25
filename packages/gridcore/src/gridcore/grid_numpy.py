import numpy as np
from typing import Union
from gridcore.types import Location, BaseEntity


class Board:
    def __init__(
        self,
        width: int,
        height: int,
        teams: np.ndarray | None = None,
    ) -> None:
        self.width = width
        self.height = height
        if teams is None:
            self._teams = np.full((height, width), -1, dtype=np.int32)
        else:
            self._teams = teams

    @classmethod
    def empty(cls, width: int, height: int) -> "Board":
        return cls(width, height)

    @property
    def number_of_cells(self) -> int:
        return self.width * self.height

    def at(self, loc: Location) -> "Cell":
        return Cell(self, loc)

    def replace_contents_at_location(self, location: Location, contents: BaseEntity) -> None:
        self._teams[location.y, location.x] = contents.team

    def add_entity_at_empty_location(self, entity: BaseEntity, loc: Location) -> None:
        if self._teams[loc.y, loc.x] != -1:
            raise ValueError(f"cell at {loc} not empty and contains team {self._teams[loc.y, loc.x]}")
        self._teams[loc.y, loc.x] = entity.team

    def location_is_empty(self, loc: Location) -> bool:
        return self._teams[loc.y, loc.x] == -1

    def get_any_empty_location_on_board(self) -> Location:
        empty_y, empty_x = np.where(self._teams == -1)
        if len(empty_y) == 0:
            raise ValueError("No empty locations")
        idx = np.random.randint(len(empty_y))
        return Location(empty_x[idx], empty_y[idx])

    def _validate_position(self, loc: Location) -> bool:
        return 0 <= loc.x < self.width and 0 <= loc.y < self.height

    def _validate_positions(self, locs: list[Location]) -> list[Location]:
        return [l for l in locs if self._validate_position(l)]

    def get_valid_neighbours(self, loc: Location) -> list[Location]:
        neighbours = []
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = loc.x + dx, loc.y + dy
                if self._validate_position(Location(nx, ny)):
                    neighbours.append(Location(nx, ny))
        return neighbours

    def get_cells_boardering_empty(self) -> list["Cell"]:
        kernel = np.array([
            [1, 1, 1],
            [1, 0, 1],
            [1, 1, 1],
        ], dtype=np.uint8)

        occupied = (self._teams != -1).astype(np.uint8)
        padded = np.pad(occupied, pad_width=1, mode='constant', constant_values=0)

        neighbor_count = np.zeros((self.height, self.width), dtype=np.uint8)
        for dy in range(3):
            for dx in range(3):
                if dy == 1 and dx == 1:
                    continue
                neighbor_count += padded[dy:dy+self.height, dx:dx+self.width]

        has_empty = (neighbor_count == 0) & (occupied == 1)
        empty_y, empty_x = np.where(has_empty)

        return [Cell(self, Location(x, y)) for x, y in zip(empty_x, empty_y)]

    def get_cells_boardering_other(self, team: Union[str, int]) -> list["Cell"]:
        team_arr = np.array([team], dtype=np.int32)
        occupied = (self._teams != -1).astype(np.uint8)
        team_mask = (self._teams == team).astype(np.uint8)

        kernel = np.array([
            [1, 1, 1],
            [1, 0, 1],
            [1, 1, 1],
        ], dtype=np.uint8)

        padded = np.pad(team_mask, pad_width=1, mode='constant', constant_values=0)

        neighbor_count = np.zeros((self.height, self.width), dtype=np.uint8)
        for dy in range(3):
            for dx in range(3):
                if dy == 1 and dx == 1:
                    continue
                neighbor_count += padded[dy:dy+self.height, dx:dx+self.width]

        other_team_count = np.zeros((self.height, self.width), dtype=np.uint8)
        for t in np.unique(self._teams):
            if t == team or t == -1:
                continue
            other_mask = (self._teams == t).astype(np.uint8)
            padded_other = np.pad(other_mask, pad_width=1, mode='constant', constant_values=0)
            count = np.zeros((self.height, self.width), dtype=np.uint8)
            for dy in range(3):
                for dx in range(3):
                    if dy == 1 and dx == 1:
                        continue
                    count += padded_other[dy:dy+self.height, dx:dx+self.width]
            other_team_count = np.maximum(other_team_count, count)

        borders = (team_mask == 1) & (other_team_count > 0)
        borders_y, borders_x = np.where(borders)

        return [Cell(self, Location(x, y)) for x, y in zip(borders_x, borders_y)]


class Cell:
    def __init__(self, board: Board, location: Location):
        self._board = board
        self.location = location

    @property
    def is_empty(self) -> bool:
        return self._board._teams[self.location.y, self.location.x] == -1

    @property
    def controlled_by(self) -> Union[str, int]:
        team = self._board._teams[self.location.y, self.location.x]
        if team == -1:
            raise IndexError("Cell is empty")
        return team

    @property
    def contents(self) -> list[BaseEntity]:
        team = self._board._teams[self.location.y, self.location.x]
        if team == -1:
            return []
        return [BaseEntity(team=team, health=1)]