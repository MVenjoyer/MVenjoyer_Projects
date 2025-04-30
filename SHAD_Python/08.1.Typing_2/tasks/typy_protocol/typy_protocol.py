from typing import TypeVar, Protocol, Optional

T = TypeVar('T', covariant=True)


class Gettable(Protocol[T]):
    def __getitem__(self, item: int) -> T:
        ...

    def __len__(self) -> int:
        ...


def get(container: Gettable[T], index: int) -> Optional[T]:
    if container:
        return container[index]
    return None
