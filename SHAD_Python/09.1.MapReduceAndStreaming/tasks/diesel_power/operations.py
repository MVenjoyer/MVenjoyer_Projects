import string
from abc import abstractmethod, ABC
import typing as tp
from itertools import groupby
from operator import itemgetter
import heapq
import re

TRow = dict[str, tp.Any]
TRowsIterable = tp.Iterable[TRow]
TRowsGenerator = tp.Generator[TRow, None, None]


class Operation(ABC):
    @abstractmethod
    def __call__(self, rows: TRowsIterable, *args: tp.Any, **kwargs: tp.Any) -> TRowsGenerator:
        pass


class Read(Operation):
    def __init__(self, filename: str, parser: tp.Callable[[str], TRow]) -> None:
        self.filename = filename
        self.parser = parser

    def __call__(self, *args: tp.Any, **kwargs: tp.Any) -> TRowsGenerator:
        with open(self.filename) as f:
            for line in f:
                yield self.parser(line)


class ReadIterFactory(Operation):
    def __init__(self, name: str) -> None:
        self.name = name

    def __call__(self, *args: tp.Any, **kwargs: tp.Any) -> TRowsGenerator:
        for row in kwargs[self.name]():
            yield row


# Operations


class Mapper(ABC):
    """Base class for mappers"""

    @abstractmethod
    def __call__(self, row: TRow) -> TRowsGenerator:
        """
        :param row: one table row
        """
        pass


class Map(Operation):
    def __init__(self, mapper: Mapper) -> None:
        self.mapper = mapper

    def __call__(self, rows: TRowsIterable, *args: tp.Any, **kwargs: tp.Any) -> TRowsGenerator:
        for row in rows:
            yield from self.mapper(row)


class Reducer(ABC):
    """Base class for reducers"""

    @abstractmethod
    def __call__(self, group_key: tuple[str, ...], rows: TRowsIterable) -> TRowsGenerator:
        """
        :param rows: table rows
        """
        pass


class Reduce(Operation):
    def __init__(self, reducer: Reducer, keys: tp.Sequence[str]) -> None:
        self.reducer = reducer
        self.keys = keys

    def __call__(self, rows: TRowsIterable, *args: tp.Any, **kwargs: tp.Any) -> TRowsGenerator:
        for group_key, group_rows in groupby(rows, key=itemgetter(*self.keys)):
            yield from self.reducer(tuple(self.keys), group_rows)


class Joiner(ABC):
    """Base class for joiners"""

    def __init__(self, suffix_a: str = '_1', suffix_b: str = '_2') -> None:
        self._a_suffix = suffix_a
        self._b_suffix = suffix_b

    @abstractmethod
    def __call__(self, keys: tp.Sequence[str], rows_a: TRowsIterable, rows_b: TRowsIterable) -> TRowsGenerator:
        """
        :param keys: join keys
        :param rows_a: left table rows
        :param rows_b: right table rows
        """
        pass


class Join(Operation):
    def __init__(self, joiner: Joiner, keys: tp.Sequence[str]):
        self.keys = keys
        self.joiner = joiner

    def __call__(self, rows: TRowsIterable, *args: tp.Any, **kwargs: tp.Any) -> TRowsGenerator:
        left = groupby(rows, key=itemgetter(*self.keys))
        right = groupby(args[0], key=itemgetter(*self.keys))
        kl, gl = next(left, (None, []))
        kr, gr = next(right, (None, []))
        while kl is not None or kr is not None:
            if kl is not None and kr is not None and kl == kr:
                yield from self.joiner(self.keys, gl, gr)
                kl, gl = next(left, (None, []))
                kr, gr = next(right, (None, []))
            elif kr is None or kl is not None and kr is not None and kl < kr:
                yield from self.joiner(self.keys, gl, [])
                kl, gl = next(left, (None, []))
            elif kl is None or kl is not None and kr is not None and kl > kr:
                yield from self.joiner(self.keys, [], gr)
                kr, gr = next(right, (None, []))


# Dummy operators


class DummyMapper(Mapper):
    """Yield exactly the row passed"""

    def __call__(self, row: TRow) -> TRowsGenerator:
        yield row


class FirstReducer(Reducer):
    """Yield only first row from passed ones"""

    def __call__(self, group_key: tuple[str, ...], rows: TRowsIterable) -> TRowsGenerator:
        for row in rows:
            yield row
            break


# Mappers


class FilterPunctuation(Mapper):
    """Left only non-punctuation symbols"""

    def __init__(self, column: str):
        """
        :param column: name of column to process
        """
        self.column = column

    def __call__(self, row: TRow) -> TRowsGenerator:
        translator = str.maketrans('', '', string.punctuation)
        new_row = row.copy()
        new_row[self.column] = new_row[self.column].translate(translator)
        yield new_row


class LowerCase(Mapper):
    """Replace column value with value in lower case"""

    def __init__(self, column: str):
        """
        :param column: name of column to process
        """
        self.column = column

    @staticmethod
    def _lower_case(txt: str) -> str:
        return txt.lower()

    def __call__(self, row: TRow) -> TRowsGenerator:
        new_row = row.copy()
        new_row[self.column] = self._lower_case(new_row[self.column])
        yield new_row


class Split(Mapper):
    """Split row on multiple rows by separator"""

    def __init__(self, column: str, separator: str | None = None) -> None:
        """
        :param column: name of column to split
        :param separator: string to separate by
        """
        self.column = column
        self.separator = separator if separator else r'\s+'

    def __call__(self, row: TRow) -> TRowsGenerator:
        begin: int = 0
        for match in re.finditer(self.separator, row[self.column]):
            end, new_b = match.span()
            new_row = row.copy()
            new_row[self.column] = row[self.column][begin:end]
            begin = new_b
            yield new_row
        new_row = row.copy()
        new_row[self.column] = row[self.column][begin:]
        yield new_row


class Product(Mapper):
    """Calculates product of multiple columns"""

    def __init__(self, columns: tp.Sequence[str], result_column: str = 'product') -> None:
        """
        :param columns: column names to product
        :param result_column: column name to save product in
        """
        self.columns = columns
        self.result_column = result_column

    def __call__(self, row: TRow) -> TRowsGenerator:
        res = 1
        for col in self.columns:
            res *= row[col]
        new_row = row.copy()
        new_row[self.result_column] = res
        yield new_row


class Filter(Mapper):
    """Remove records that don't satisfy some condition"""

    def __init__(self, condition: tp.Callable[[TRow], bool]) -> None:
        """
        :param condition: if condition is not true - remove record
        """
        self.condition = condition

    def __call__(self, row: TRow) -> TRowsGenerator:
        if self.condition(row):
            yield row


class Project(Mapper):
    """Leave only mentioned columns"""

    def __init__(self, columns: tp.Sequence[str]) -> None:
        """
        :param columns: names of columns
        """
        self.columns = columns

    def __call__(self, row: TRow) -> TRowsGenerator:
        yield {k: v for k, v in row.items() if k in self.columns}


# Reducers


class TopN(Reducer):
    """Calculate top N by value"""

    def __init__(self, column: str, n: int) -> None:
        """
        :param column: column name to get top by
        :param n: number of top values to extract
        """
        self.column_max = column
        self.n = n

    def __call__(self, group_key: tuple[str, ...], rows: TRowsIterable) -> TRowsGenerator:
        heap: list[tuple[tp.Any, int | tp.Any, dict[str, tp.Any]]] = []
        counter = 0
        for row in rows:
            if len(heap) < self.n:
                heapq.heappush(heap, (row[self.column_max], counter, row))
            else:
                heapq.heappushpop(heap, (row[self.column_max], counter, row))
            counter += 1
        for r in heap:
            yield r[2]


class TermFrequency(Reducer):
    """Calculate frequency of values in column"""

    def __init__(self, words_column: str, result_column: str = 'tf') -> None:
        """
        :param words_column: name for column with words
        :param result_column: name for result column
        """
        self.words_column = words_column
        self.result_column = result_column

    def __call__(self, group_key: tuple[str, ...], rows: TRowsIterable) -> TRowsGenerator:
        seen_words: dict[tp.Any, int] = {}
        group_value: list[tp.Any] = []
        counter = 0
        for row in rows:
            if not group_value:
                group_value = [row[k] for k in group_key]
            word = row[self.words_column]
            if word not in seen_words:
                seen_words[word] = 1
            else:
                seen_words[word] += 1
            counter += 1
        for word, count in seen_words.items():
            new_row = {k: v for k, v in zip(group_key, group_value)}
            new_row[self.words_column] = word
            new_row[self.result_column] = count / counter
            yield new_row


class Count(Reducer):
    """
    Count records by key
    Example for group_key=('a',) and column='d'
        {'a': 1, 'b': 5, 'c': 2}
        {'a': 1, 'b': 6, 'c': 1}
        =>
        {'a': 1, 'd': 2}
    """

    def __init__(self, column: str) -> None:
        """
        :param column: name for result column
        """
        self.column = column

    def __call__(self, group_key: tuple[str, ...], rows: TRowsIterable) -> TRowsGenerator:
        counter = 0
        new_row: dict[tp.Any, int] = {}
        for row in rows:
            if not new_row:
                new_row = row
            counter += 1
        new_row[self.column] = counter
        yield {k: v for k, v in new_row.items() if k in group_key or k == self.column}


class Sum(Reducer):
    """
    Sum values aggregated by key
    Example for key=('a',) and column='b'
        {'a': 1, 'b': 2, 'c': 4}
        {'a': 1, 'b': 3, 'c': 5}
        =>
        {'a': 1, 'b': 5}
    """

    def __init__(self, column: str) -> None:
        """
        :param column: name for sum column
        """
        self.column = column

    def __call__(self, group_key: tuple[str, ...], rows: TRowsIterable) -> TRowsGenerator:
        lst: dict[tp.Any, tp.Any] = {}
        for row in rows:
            if len(lst) == 0:
                for k, v in row.items():
                    if k in group_key or k == self.column:
                        lst[k] = v
            else:
                lst[self.column] += row[self.column]
        yield lst


# Joiners


class InnerJoiner(Joiner):
    """Join with inner strategy"""

    def __init__(self, suffix_a: str = '', suffix_b: str = '') -> None:
        super().__init__(suffix_a, suffix_b)

    def __call__(self, keys: tp.Sequence[str], rows_a: TRowsIterable, rows_b: TRowsIterable) -> TRowsGenerator:
        if rows_a and rows_b:
            rows_b_c = list(rows_b)
            for row_a in rows_a:
                for row_b in rows_b_c:
                    new_row = row_a.copy()
                    for key in row_b:
                        if key not in new_row:
                            new_row[key] = row_b[key]
                        elif key not in keys:
                            new_row[key + self._b_suffix] = row_b[key]
                            new_row[key + self._a_suffix] = new_row.pop(key)
                    yield new_row


class OuterJoiner(Joiner):
    """Join with outer strategy"""

    def __call__(self, keys: tp.Sequence[str], rows_a: TRowsIterable, rows_b: TRowsIterable) -> TRowsGenerator:
        rows_b_c = list(rows_b)
        counter = 0
        for row_a in rows_a:
            for row_b in rows_b_c:
                new_row = row_a.copy()
                new_row.update(row_b)
                counter += 1
                yield new_row
            if counter == 0:
                yield row_a
        if counter == 0:
            for row_b in rows_b_c:
                yield row_b


class LeftJoiner(Joiner):
    """Join with left strategy"""

    def __call__(self, keys: tp.Sequence[str], rows_a: TRowsIterable, rows_b: TRowsIterable) -> TRowsGenerator:
        rows_b_c = list(rows_b)
        counter = 0
        for row_a in rows_a:
            for row_b in rows_b_c:
                new_row = row_a.copy()
                new_row.update(row_b)
                counter += 1
                yield new_row
            if counter == 0:
                yield row_a


class RightJoiner(Joiner):
    """Join with right strategy"""

    def __call__(self, keys: tp.Sequence[str], rows_a: TRowsIterable, rows_b: TRowsIterable) -> TRowsGenerator:
        rows_a_c = list(rows_a)
        counter = 0
        for row_b in rows_b:
            for row_a in rows_a_c:
                new_row = row_a.copy()
                new_row.update(row_b)
                counter += 1
                yield new_row
            if counter == 0:
                yield row_b
