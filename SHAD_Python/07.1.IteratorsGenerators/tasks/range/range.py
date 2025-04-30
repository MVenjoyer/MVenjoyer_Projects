from collections.abc import Iterable, Iterator, Sized


class RangeIterator(Iterator[int]):
    """The iterator class for Range"""

    def __init__(self, range_: 'Range') -> None:
        self.current = range_.start
        self.end = range_.end
        self.step = range_.step

    def __iter__(self) -> 'RangeIterator':
        return self

    def __next__(self) -> int:
        if (self.current >= self.end and self.step > 0) or (self.current <= self.end and self.step < 0):
            raise StopIteration
        result = self.current
        self.current += self.step
        return result


class Range(Sized, Iterable[int]):
    """The range-like type, which represents an immutable sequence of numbers"""

    def __init__(self, *args: int) -> None:
        """
        :param args: either it's a single `stop` argument
            or sequence of `start, stop[, step]` arguments.
        If the `step` argument is omitted, it defaults to 1.
        If the `start` argument is omitted, it defaults to 0.
        If `step` is zero, ValueError is raised.
        """
        match len(args):
            case 1:
                self.start = 0
                self.end = args[0]
                self.step = 1
            case 2:
                self.start = args[0]
                self.end = args[1]
                self.step = 1
                if self.start > self.end:
                    self.start = 0
                    self.end = 0
            case 3:
                self.start = args[0]
                self.end = args[1]
                self.step = args[-1]
                if (self.end - self.start) * self.step <= 0:
                    self.start = 0
                    self.end = 0

    def __iter__(self) -> 'RangeIterator':
        return RangeIterator(self)

    def __repr__(self) -> str:
        if self.step == 1:
            return f"range({self.start}, {self.end})"
        return f"range({self.start}, {self.end}, {self.step})"

    def __str__(self) -> str:
        return self.__repr__()

    def __contains__(self, key: int) -> bool:
        return ((self.start <= key < self.end and self.step > 0) or (
                self.start >= key > self.end and self.step < 0)) and (key - self.start) % self.step == 0

    def __getitem__(self, key: int) -> int:
        if self.__len__() > key >= 0:
            return self.start + key * self.step
        else:
            raise IndexError

    def __len__(self) -> int:
        return (abs(self.end - self.start) - 1) // abs(self.step) + 1
