# factories.py
from gridcore.grid import Board, Location
from cellular_automata.automata import CombatSimulation, BaseEntity
from .main import GameConfig
import random


def build_simulation(cfg: GameConfig) -> CombatSimulation:
    rng = random.Random(cfg.seed)

    return CombatSimulation.initialise_board_with_n_players(
        height=cfg.height, width=cfg.width, max_ticks=cfg.max_ticks, rng=rng
    )
