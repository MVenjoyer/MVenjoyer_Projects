from dataclasses import dataclass, field, InitVar
from abc import ABC, abstractmethod

DISCOUNT_PERCENTS = 15


@dataclass(frozen=True, order=True)
class Item:
    item_id: int = field(compare=False)
    title: str = field(compare=True)
    cost: int = field(compare=True)

    def __post_init__(self) -> None:
        assert self.cost > 0
        assert self.title


@dataclass
class Position(ABC):
    item: Item

    @property
    @abstractmethod
    def cost(self) -> float:
        pass


@dataclass
class CountedPosition(Position):
    count: int = 1

    @property
    def cost(self) -> float:
        return self.item.cost * self.count


@dataclass
class WeightedPosition(Position):
    weight: float = 1.0

    @property
    def cost(self) -> float:
        return self.item.cost * self.weight


@dataclass
class Order:
    order_id: int
    positions: list[Position] = field(default_factory=list)
    cost: int = 0
    have_promo: InitVar[bool] = field(default=False)

    def __post_init__(self, have_promo: bool) -> None:
        setattr(self, 'have_promo', have_promo)
        self.cost = int(
            sum(position.cost if not have_promo else position.cost * (1 - DISCOUNT_PERCENTS / 100) for position in
                self.positions))
