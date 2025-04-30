import functools
import time
import typing


def profiler(func):  # type: ignore
    """
    Returns profiling decorator, which counts calls of function
    and measure last function execution time.
    Results are stored as function attributes: `calls`, `last_time_taken`
    :param func: function to decorate
    :return: decorator, which wraps any function passed
    """

    @functools.wraps(func)
    def wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        if wrapper.depth == 0:
            wrapper.calls = 0
        wrapper.depth += 1
        wrapper.calls += 1
        start = time.time()
        result = func(*args, **kwargs)
        wrapper.last_time_taken = time.time() - start
        wrapper.depth -= 1
        return result

    wrapper.depth = 0
    wrapper.calls = 0
    wrapper.last_time_taken = 0.0
    return wrapper
