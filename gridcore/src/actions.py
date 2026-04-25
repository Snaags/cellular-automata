# gridcore/actions.py
from dataclasses import dataclass
from .types import Location

@dataclass
class BaseAction:
    actor_id: str      # depends on the game’s entity-tracking method
    target: Location

    @property
    def is_projectile(self) -> bool:
        return False


@dataclass
class ProjectileMixin:
    width: float = 0.0
    max_range: int | None = None

    @property
    def is_projectile(self) -> bool:
        return True


@dataclass
class OrderSequence:
    actions: list[BaseAction]
    idx: int = 0

    def next_action(self, turn: int) -> BaseAction:
        assert turn == self.idx, "Turn desync"
        action = self.actions[self.idx]
        self.idx += 1
        return action
