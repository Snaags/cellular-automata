from typing import Sequence, Union
from gridcore.simulation import SimulationBase
from gridcore.actions import OrderSequence
from gridcore.grid_numpy import Board, Cell
from gridcore.types import BaseEntity, Location
import random
from dataclasses import dataclass


def construct_empty_board(width: int, height: int) -> Board:
    return Board.empty(width, height)


@dataclass
class PlayerCell(BaseEntity):
    player: bool = False


class CombatSimulation(SimulationBase):
    @dataclass
    class Config:
        width: int
        height: int
        factions: int

    def __init__(
        self,
        board: Board,
        entities: Sequence[BaseEntity],
        teams: list[Union[str, int]],
        max_ticks: int,
        rng,
    ):
        super().__init__(board, entities, max_ticks, rng)
        self.teams = teams

    @classmethod
    def initialise_board_with_n_players(
        cls, factions: int, width: int, height: int, max_ticks: int, rng = None
    ):
        board = construct_empty_board(width, height)

        player_cells: Sequence[PlayerCell] = [
            PlayerCell(team=i, health=1) for i in range(factions)
        ]

        board: Board = CombatSimulation.add_player_entities_to_random_cell(
            board, player_cells
        )

        return cls(
            board=board,
            entities=player_cells,
            teams=[i for i in range(factions)],
            max_ticks=max_ticks,
            rng=rng,
        )

    @staticmethod
    def add_player_entities_to_random_cell(
        board: Board, players: list[PlayerCell]
    ) -> Board:
        for player_entity in players:
            loc: Location = board.get_any_empty_location_on_board()
            board.add_entity_at_empty_location(entity=player_entity, loc=loc)

        return board

    def _ingest_actions(self, actions: dict[str, OrderSequence]) -> None:
        # existing combat _apply_actions logic
        ...

    def _after_tick(self) -> None:
        for team in self.teams:
            success = self.spawn_adjacent(team)
            if not success:
                border_cells = self.board.get_cells_boardering_other(team)
                if border_cells:
                    cell_ = random.choice(border_cells)
                    cell_out = self._next_cell_state(cell_.location)
                    self.board.replace_contents_at_location(cell_.location, cell_out.contents[-1])

    def spawn_adjacent(self, team: Union[int, str]) -> bool:
        cells_bordering_empty = self.board.get_cells_boardering_empty()
        if not cells_bordering_empty:
            return False
            
        team_cells = [cell for cell in cells_bordering_empty if cell.controlled_by == team]
        if not team_cells:
            return False
            
        cell_to_spawn_from = random.choice(team_cells)
        valid_neighbours = self.board.get_valid_neighbours(cell_to_spawn_from.location)
        empty_neighbours = [
            neighbour
            for neighbour in valid_neighbours
            if self.board.location_is_empty(neighbour)
        ]
        if not empty_neighbours:
            return False
            
        self.board.add_entity_at_empty_location(
            entity=PlayerCell(team=team, health=1), loc=random.choice(empty_neighbours)
        )
        return True

    def _next_cell_state(self, location: Location) -> Cell:
        """Pure; derives the cell’s next state from current world."""
        cell = self.board.at(location)
        team = cell.contents[-1].team
        neighbours: list[Location] = self.board.get_valid_neighbours(location)
        allies = 0
        enemies = 0
        enemy_cells = []
        for loc_ in neighbours:
            cell_ = self.board.at(loc_)
            if cell_.is_empty:
                continue
            neighbour_team = cell_.contents[-1].team
            if team == neighbour_team:
                allies += 1
            else:
                enemies += 1
                enemy_cells.append(cell_)

        win_rate = (allies**2 + 1.5) / (enemies**2 + allies**2 + 1.5)

        if win_rate != 1:
            print(f'battle between: {allies} allies and {enemies} enemies for {cell} at {location} with winrate of: {win_rate}')
        if random.random() < win_rate:
            return cell
        else:
            return random.choice(enemy_cells)
