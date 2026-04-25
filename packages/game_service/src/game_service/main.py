"""
game_service.py
────────────────
Ad-hoc “all-in-one” service layer that

• defines the immutable GameConfig dataclass
• builds a CombatSimulation instance from that config
• manages active game sessions, action submission, and snapshots

Dependencies
------------
gridcore            – common engine primitives
cellular_automata   – your CombatSimulation implementation
"""

from __future__ import annotations

import uuid
import random
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Optional

from gridcore.actions import OrderSequence
from cellular_automata.automata import CombatSimulation

# --------------------------------------------------------------------------- #
# 1.  Immutable game configuration                                            #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class GameConfig:
    """Everything required to reproduce a game deterministically."""

    width: int
    height: int
    factions: int
    max_ticks: int = 1_000
    seed: Optional[int] = None


# --------------------------------------------------------------------------- #
# 2.  Factory → GameConfig ➜ CombatSimulation                                 #
# --------------------------------------------------------------------------- #


def build_simulation(cfg: GameConfig) -> CombatSimulation:
    """
    Create a fresh CombatSimulation seeded for deterministic replays.
    The concrete `initialise_board_with_n_players` constructor lives
    inside `cellular_automata.automata.CombatSimulation`.
    """
    rng = random.Random(cfg.seed)
    return CombatSimulation.initialise_board_with_n_players(
        width=cfg.width,
        height=cfg.height,
        max_ticks=cfg.max_ticks,
        rng=rng,
        factions=cfg.factions,
    )


# --------------------------------------------------------------------------- #
# 3.  Game-service façade – session / action / snapshot                       #
# --------------------------------------------------------------------------- #


class GameService:
    """
    Minimal in-memory lobby that can:
      • create games
      • collect per-player OrderSequence objects
      • advance the underlying simulator when all orders arrive
      • return immutable snapshots to UIs / API endpoints
    """

    def __init__(self) -> None:
        self._sessions: Dict[str, CombatSimulation] = {}  # gid → sim
        self._pending: Dict[str, Dict[str, OrderSequence]] = defaultdict(dict)
        #            │             └── player_id → orders
        #            └── gid

    # ---- game-lifecycle -------------------------------------------------- #
    def create_game(self, cfg: GameConfig) -> str:
        gid = str(uuid.uuid4())
        self._sessions[gid] = build_simulation(cfg)
        return gid

    def join_game(self, gid: str, player_id: str) -> None:
        """
        Extend with authentication, quota checks, or snapshot return.
        Currently a stub because CombatSimulation already tracks `expected_players`.
        """
        if gid not in self._sessions:
            raise KeyError(f"Game ID {gid} not found")

    # ---- turn handling --------------------------------------------------- #
    def push_actions(self, gid: str, player_id: str, orders: OrderSequence) -> None:
        if gid not in self._sessions:
            raise KeyError(f"Game ID {gid} not found")

        self._pending[gid][player_id] = orders
        sim = self._sessions[gid]

        # Advance once *all* expected players have provided an OrderSequence.
        if len(self._pending[gid]) == sim.expected_players:
            sim.advance(self._pending[gid])
            self._pending[gid].clear()

    # ---- read-only view -------------------------------------------------- #
    def snapshot(self, gid: str):
        if gid not in self._sessions:
            raise KeyError(f"Game ID {gid} not found")
        return self._sessions[gid].snapshot()
