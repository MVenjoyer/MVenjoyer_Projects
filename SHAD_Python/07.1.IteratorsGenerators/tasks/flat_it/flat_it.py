from collections.abc import Iterable, Iterator
from typing import Any


def flat_it(sequence: Iterable[Any]) -> Iterator[Any]:
    """
    :param sequence: iterable with arbitrary level of nested iterables
    :return: generator producing flatten sequence
    """
    for el in sequence:
        if isinstance(el, str):
            for char in el:
                yield char
        else:
            try:
                iter(el)
                yield from flat_it(el)
            except TypeError:
                yield el
