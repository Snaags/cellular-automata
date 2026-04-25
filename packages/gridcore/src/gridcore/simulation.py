# gridcore/simulation.py
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple, Sequence

from .grid import Board
from .types import BaseEntity, Location
from .actions import BaseAction, OrderSequence


@dataclass(frozen=True, slots=True)
class Snapshot:
    tick: int
    board: Board
    outcome: str = 'ongoing'




class SimulationBase(ABC):
    """
    • Keeps authoritative state
    • Provides `advance(actions)` + `snapshot()` so renderers/tests stay identical.
    Child classes override *only* the three protected hooks.
    """

    def __init__(
        self, board: Board, entities: Sequence[BaseEntity], max_ticks: int, rng
    ) -> None:
        self.board = board
        self.entities = entities
        self._tick = 0

    # ---------------- public ----------------
    def advance(self, actions: Dict[str, OrderSequence]) -> Snapshot:
        self._ingest_actions(actions)
        self._tick += 1
        self._after_tick()
        return self.snapshot()

    def snapshot(self) -> Snapshot:
        return Snapshot(self._tick, self.board)

    # ---------------- hooks for child games ----------------
    @abstractmethod
    def _ingest_actions(self, actions: Dict[str, OrderSequence]) -> None: ...

    @abstractmethod
    def _after_tick(self) -> None: ...
