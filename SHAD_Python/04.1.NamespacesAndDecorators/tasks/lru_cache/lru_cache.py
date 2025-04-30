from collections.abc import Callable
from collections import OrderedDict
from typing import Any, TypeVar, ParamSpec
import functools

Function = TypeVar('Function', bound=Callable[..., Any])
R = TypeVar("R")
P = ParamSpec("P")


def cache(max_size: int) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Returns decorator, which stores result of function
    for `max_size` most recent function arguments.
    :param max_size: max amount of unique arguments to store values for
    :return: decorator, which wraps any function passed
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        dct_cache: OrderedDict[Any, Any] = OrderedDict()

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            key = tuple(args) + tuple(kwargs.items())
            if dct_cache.get(key):
                dct_cache.move_to_end(key)
                return dct_cache[key]
            result = func(*args, **kwargs)
            dct_cache[key] = result
            if dct_cache.__len__() > max_size:
                dct_cache.popitem(last=False)
            return result

        return wrapper

    return decorator
