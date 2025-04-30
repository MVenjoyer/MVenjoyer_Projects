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


class GroupProcessor:
    def __init__(self, keys):
        self.keys = keys

    def process(self, rows):
        if not self.keys:
            return iter(((0, rows),))
        else:
            return iter((key, group) for key, group in groupby(rows, key=itemgetter(*self.keys)))


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
        for group_key, group_rows in GroupProcessor(self.keys).process(rows):
            yield from self.reducer(tuple(self.keys), group_rows)


class Joiner(ABC):
    """Base class for joiners"""

    def __init__(self, suffix_a: str = "_1", suffix_b: str = "_2") -> None:
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
        left = GroupProcessor(self.keys).process(rows)
        right = GroupProcessor(self.keys).process(args[0])
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
        yield {**row,
               self.column: re.sub(fr"[\\{string.punctuation}]", "", row[self.column])}


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
        self.separator = separator if separator else r"\s+"

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

    def __init__(self, columns: tp.Sequence[str], result_column: str = "product") -> None:
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
    """Remove records that don"t satisfy some condition"""

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


class Divide(Mapper):
    """
    Divides two columns and adds the result to a new column.
    """

    def __init__(self, first_col: str = "doc_count",
                 second_col: str = "docw_count", answer_col: str = "IDF") -> None:
        """
        param: [answer_col] = first_col/second_col
        """
        self.answer_col = answer_col
        self.first_col = first_col
        self.second_col = second_col

    def __call__(self, row: TRow) -> TRowsGenerator:
        answer = row[self.first_col] / row[self.second_col]
        new_row = row.copy()
        new_row.pop(self.first_col)
        new_row.pop(self.second_col)
        new_row[self.answer_col] = answer
        yield new_row


class Del(Mapper):
    """
    Removes specified columns from each row.
    """

    def __init__(self, dest: tp.Sequence[str]) -> None:
        """
        param: dest - seq of els, that have to be removed
        """
        self.dest = dest

    def __call__(self, row: TRow) -> TRowsGenerator:
        new_row = row.copy()
        for d in self.dest:
            new_row.pop(d)
        yield new_row


class Evaluate(Mapper):
    """
    Applies a given function to transform each row.
    """

    def __init__(self, func: tp.Callable[[TRow], TRow]) -> None:
        """
        param: func - func that has to be applied on row
        """
        self.func = func

    def __call__(self, row: TRow) -> TRowsGenerator:
        new_row = row.copy()
        yield self.func(new_row)


# Reducers


class TopN(Reducer):
    """Calculate top N by value"""

    def __init__(self, column: str, n: int, rever: bool = False) -> None:
        """
        :param column: column name to get top by
        :param n: number of top values to extract
        """
        self.column_max = column
        self.n = n
        self.rever = rever

    def __call__(self, group_key: tuple[str, ...], rows: TRowsIterable) -> TRowsGenerator:
        heap: list[tuple[tp.Any, int | tp.Any, dict[str, tp.Any]]] = []
        counter = 0
        for row in rows:
            if len(heap) < self.n:
                heapq.heappush(heap, (row[self.column_max], counter, row))
            else:
                heapq.heappushpop(heap, (row[self.column_max], counter, row))
            counter += 1
        if reversed:
            for _, _, r in heapq.nlargest(self.n, heap):
                yield r
        else:
            for _, _, r in heapq.nsmallest(self.n, heap):
                yield r


class TermFrequency(Reducer):
    """Calculate frequency of values in column"""

    def __init__(self, words_column: str, result_column: str = "tf") -> None:
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
    Example for group_key=("a",) and column="d"
        {"a": 1, "b": 5, "c": 2}
        {"a": 1, "b": 6, "c": 1}
        =>
        {"a": 1, "d": 2}
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
    Example for key=("a",) and column="b"
        {"a": 1, "b": 2, "c": 4}
        {"a": 1, "b": 3, "c": 5}
        =>
        {"a": 1, "b": 5}
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


class First(Reducer):
    """
    Outputs the first unique row for each group based on a specified column.
    """

    def __init__(self, column: str) -> None:
        """
        param: column - The column used to identify unique rows.
        """
        self.dest_col = column

    def __call__(self, group_key: tuple[str, ...], rows: TRowsIterable) -> TRowsGenerator:
        seen: dict[str, bool] = {}
        for row in rows:
            if row[self.dest_col] not in seen:
                seen[row[self.dest_col]] = True
                yield row


class CountRows(Reducer):
    """
    Counts the number of rows in each group and adds the result as a new column.
    """

    def __init__(self, column: str, answer_column: str = "doc_count") -> None:
        """
        param:
            - column: The column used for grouping.
            - answer_column: The column name to store the count.
        """
        self.dest_col = column
        self.answer_col = answer_column

    def __call__(self, group_key: tuple[str, ...], rows: TRowsIterable) -> TRowsGenerator:
        counter = 0
        group_row: dict[str, tp.Any] = {}
        for row in rows:
            if counter == 0:
                for k, v in row.items():
                    if k in group_key:
                        group_row[k] = v
            counter += 1
        group_row[self.answer_col] = counter
        yield group_row


class UniversalReducer(Reducer):
    """
    Applies a custom function to process rows in a group.
    """

    def __init__(self, func: tp.Callable[[tp.Any], tp.Any]) -> None:
        """
        param: func - A callable that takes a list of rows and returns processed rows.
        """
        self.func = func

    def __call__(self, group_key: tuple[str, ...], rows: TRowsIterable) -> TRowsGenerator:
        processed = self.func(list(rows))
        for row in processed:
            yield row


class Mean(Reducer):
    """
    Computes the mean of a specified column for each group and adds the result as a new column.
    """

    def __init__(self, sum_col: str) -> None:
        """
        param: sum_col - The column name for which the mean is computed.
        """
        self.sum_col = sum_col

    def __call__(self, group_key: tuple[str, ...], rows: TRowsIterable) -> TRowsGenerator:
        lst: dict[tp.Any, tp.Any] = {}
        counter = 0
        for row in rows:
            counter += 1
            if len(lst) == 0:
                for k, v in row.items():
                    if k in group_key or k == self.sum_col:
                        lst[k] = v
            else:
                lst[self.sum_col] += row[self.sum_col]
        if counter != 0:
            lst[self.sum_col] /= counter
        yield lst


# Joiners


class InnerJoiner(Joiner):
    """Join with inner strategy"""

    def __init__(self, suffix_a: str = "", suffix_b: str = "") -> None:
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
