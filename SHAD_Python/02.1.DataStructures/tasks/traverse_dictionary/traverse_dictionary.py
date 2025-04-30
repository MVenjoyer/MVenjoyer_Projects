import typing as tp
from collections import deque


def traverse_dictionary_immutable(
        dct: tp.Mapping[str, tp.Any],
        prefix: str = "") -> list[tuple[str, int]]:
    """
    :param dct: dictionary of undefined depth with integers or other dicts as leaves with same properties
    :param prefix: prefix for key used for passing total path through recursion
    :return: list with pairs: (full key from root to leaf joined by ".", value)
    """
    result: list[tuple[str, int]] = []
    for key, value in dct.items():
        if type(value) is int:
            result.append((prefix + key, value))
        else:
            result += traverse_dictionary_immutable(value, prefix + key + ".")
    return result


def traverse_dictionary_mutable(
        dct: tp.Mapping[str, tp.Any],
        result: list[tuple[str, int]],
        prefix: str = "") -> None:
    """
    :param dct: dictionary of undefined depth with integers or other dicts as leaves with same properties
    :param result: list with pairs: (full key from root to leaf joined by ".", value)
    :param prefix: prefix for key used for passing total path through recursion
    :return: None
    """
    for key, value in dct.items():
        if type(value) is int:
            result.append((prefix + key, value))
        else:
            traverse_dictionary_mutable(value, result, prefix + key + ".")


def traverse_dictionary_iterative(
        dct: tp.Mapping[str, tp.Any]
) -> list[tuple[str, int]]:
    """
    :param dct: dictionary of undefined depth with integers or other dicts as leaves with same properties
    :return: list with pairs: (full key from root to leaf joined by ".", value)
    """
    result: list[tuple[str, int]] = []
    need_to_visit = deque([(key, value) for key, value in dct.items()])
    while need_to_visit:
        if type(need_to_visit[0][1]) is int:
            result.append(need_to_visit.popleft())
        else:
            x = need_to_visit.popleft()
            need_to_visit.extendleft([(x[0] + "." + key, value) for key, value in x[1].items()])
    return result
