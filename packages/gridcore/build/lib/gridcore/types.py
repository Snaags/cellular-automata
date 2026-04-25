from typing import Self
from dataclasses import dataclass, field
from typing import Union


@dataclass
class Location:
    x: int
    y: int

    def possible_neighbours(self) -> list[Self]:
        neighbours = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == dy == 0:
                    continue
                nx, ny = self.x + dx, self.y + dy
                neighbours.append(Location(x=nx, y=ny))

        return neighbours

    @property
    def centre(self) -> tuple[float, float]:
        return self.x + 0.5, self.y + 0.5

    def __str__(self) -> str:
        return f"({self.x},{self.y})"


@dataclass
class BaseEntity:
    team: Union[str, int]
    health: int
    status_queue: list[str] = field(default_factory=list)
    dead: bool = False

    def apply_damage(self, amount: int) -> None:
        self.health -= amount
        if self.health <= -1:
            self.dead = True
