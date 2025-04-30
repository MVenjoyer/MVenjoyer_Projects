import time
import types
import typing


class TimeoutException(BaseException):
    def __init__(self) -> None:
        pass


class SoftTimeoutException(TimeoutException):
    def __init__(self) -> None:
        pass


class HardTimeoutException(TimeoutException):
    def __init__(self) -> None:
        pass


class TimeCatcher:
    def __init__(self, soft_timeout: float | None = None, hard_timeout: float | None = None) -> None:
        self._start_time: float = 0.0
        assert soft_timeout is None or soft_timeout > 0
        assert hard_timeout is None or hard_timeout > 0
        assert soft_timeout is None or hard_timeout is None or soft_timeout <= hard_timeout
        self._soft_timeout = soft_timeout
        self._hard_timeout = hard_timeout

    def __enter__(self) -> typing.Self:
        self._start_time = time.time()
        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None,
                 exc_tb: types.TracebackType | None) -> None:
        self._answer = time.time() - self._start_time
        if exc_type is not None and isinstance(exc_val, BaseException):
            raise exc_val
        if self._soft_timeout is not None and self._answer > self._soft_timeout:
            raise SoftTimeoutException
        if self._hard_timeout is not None and self._answer > self._hard_timeout:
            raise HardTimeoutException

    def __float__(self) -> float:
        return float(time.time() - self._start_time)

    def __str__(self) -> str:
        return "Time consumed: " + str(self._answer)
