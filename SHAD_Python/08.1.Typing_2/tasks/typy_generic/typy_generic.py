from typing import TypeVar, Generic

T = TypeVar('T', float, int)


class Pair(Generic[T]):
    def __init__(self, a: T, b: T) -> None:
        self.__first: T = a
        self.__second: T = b

    def sum(self) -> T:
        return self.__first + self.__second

    def first(self) -> T:
        return self.__first

    def second(self) -> T:
        return self.__second

    def __iadd__(self, pair: "Pair[T]") -> "Pair[T]":
        self.__first += pair.__first
        self.__second += pair.__second
        return self
