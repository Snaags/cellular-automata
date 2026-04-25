import numpy as np
import random
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
        idx = random.choice(range(len(empty_y)))
        return Location(int(empty_x[idx]), int(empty_y[idx]))

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
        occupied = (self._teams != -1)
        padded = np.pad(occupied, pad_width=1, mode='constant', constant_values=False)
        borders_empty = np.zeros((self.height, self.width), dtype=bool)
        
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if dy == 0 and dx == 0:
                    continue
                slice_y = slice(1 + dy, 1 + dy + self.height)
                slice_x = slice(1 + dx, 1 + dx + self.width)
                shifted_empty = ~padded[slice_y, slice_x]
                borders_empty |= (occupied & shifted_empty)
        
        empty_y, empty_x = np.where(borders_empty)
        return [Cell(self, Location(x, y)) for x, y in zip(empty_x, empty_y)]

    def get_cells_boardering_other(self, team: Union[str, int]) -> list["Cell"]:
        occupied = (self._teams != -1)
        team_mask = (self._teams == team)
        
        padded_occupied = np.pad(occupied, pad_width=1, mode='constant', constant_values=False)
        padded_team = np.pad(team_mask, pad_width=1, mode='constant', constant_values=False)
        
        borders_other = np.zeros((self.height, self.width), dtype=bool)
        
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if dy == 0 and dx == 0:
                    continue
                slice_y = slice(1 + dy, 1 + dy + self.height)
                slice_x = slice(1 + dx, 1 + dx + self.width)
                
                shifted_occupied = padded_occupied[slice_y, slice_x]
                shifted_team = padded_team[slice_y, slice_x]
                
                borders_other |= (team_mask & shifted_occupied & ~shifted_team)
        
        borders_y, borders_x = np.where(borders_other)
        return [Cell(self, Location(x, y)) for x, y in zip(borders_x, borders_y)]

    def get_cells_bordering_empty_for_team(self, team: Union[str, int]) -> list[Location]:
        occupied = (self._teams != -1)
        padded = np.pad(occupied, pad_width=1, mode='constant', constant_values=False)
        borders_empty = np.zeros((self.height, self.width), dtype=bool)
        
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if dy == 0 and dx == 0:
                    continue
                slice_y = slice(1 + dy, 1 + dy + self.height)
                slice_x = slice(1 + dx, 1 + dx + self.width)
                shifted_empty = ~padded[slice_y, slice_x]
                borders_empty |= (occupied & shifted_empty)
        
        team_mask = (self._teams == team)
        team_bordering_empty = borders_empty & team_mask
        
        y_coords, x_coords = np.where(team_bordering_empty)
        return [Location(x, y) for x, y in zip(x_coords, y_coords)]

    def get_empty_spawn_locations_for_team(self, team: Union[str, int]) -> list[Location]:
        team_mask = (self._teams == team)
        team_occupied = team_mask
        
        padded = np.pad(team_occupied, pad_width=1, mode='constant', constant_values=False)
        
        borders_team = np.zeros((self.height, self.width), dtype=bool)
        
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if dy == 0 and dx == 0:
                    continue
                slice_y = slice(1 + dy, 1 + dy + self.height)
                slice_x = slice(1 + dx, 1 + dx + self.width)
                borders_team |= padded[slice_y, slice_x]
        
        empty = (self._teams == -1)
        spawn_locations = borders_team & empty
        
        y_coords, x_coords = np.where(spawn_locations)
        return [Location(x, y) for x, y in zip(x_coords, y_coords)]


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