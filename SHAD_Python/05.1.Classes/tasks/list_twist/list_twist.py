from collections import UserList
import typing as tp


class ListTwist(UserList[tp.Any]):
    """
    List-like class with additional attributes:
        * reversed, R - return reversed list
        * first, F - insert or retrieve first element;
                     Undefined for empty list
        * last, L -  insert or retrieve last element;
                     Undefined for empty list
        * size, S -  set or retrieve size of list;
                     If size less than list length - truncate to size;
                     If size greater than list length - pad with Nones
    """

    def __init__(self, initial: tp.Any = []):
        super().__init__(initial)

    def __getattr__(self, item: str) -> tp.Any:
        if item in ('reversed', 'R'):
            return self[::-1]
        if item in ('first', 'F'):
            return self[0]
        if item in ('last', 'L'):
            return self[-1]
        if item in ('size', 'S'):
            return len(self)
        raise AttributeError()

    def __setattr__(self, key: str, value: tp.Any) -> None:
        if key in ('reversed', 'R'):
            self.data = value[::-1]
        elif key in ('first', 'F'):
            self.data[0] = value
        elif key in ('last', 'L'):
            self.data[-1] = value
        elif key in ('size', 'S'):
            if value < len(self):
                self.data = self.data[:value]
            else:
                self.data += [None] * (value - len(self))
        else:
            return super().__setattr__(key, value)
