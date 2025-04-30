import typing
from typing import Tuple, TypeVar, Protocol


class NoDict(Protocol):
    def __len__(self) -> int:
        ...


T = TypeVar('T', bound=NoDict, covariant=True)
B = TypeVar('B', bound=NoDict, covariant=True)
C = TypeVar('C', str, typing.List[str], covariant=True)


def f(a: Tuple[T, B, C]) -> B:
    return a[1]


TEST_SAMPLES = """
# SUCCESS
f(("a", "b", "c"))

# SUCCESS
f(("a", "b", ["c", "d", "e"]))

# ERROR
f(("a", "b", "c", "d"))

# SUCCESS
class A(str):
    pass

a: A
a = f(("a", A(), A()))

# SUCCESS
f((["a", "b"], "c", "d"))

# SUCCESS
class A:
    def __len__(self) -> int:
        return 1

f((A(), "c", "d"))

# ERROR
class A:
    def __len__(self) -> int:
        return 1

f((A(), "c", {"d", "e"}))
"""
