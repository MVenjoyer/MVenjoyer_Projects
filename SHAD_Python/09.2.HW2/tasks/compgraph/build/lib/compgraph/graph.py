import typing as tp

from . import operations as ops
from . import external_sort as es


class Graph:
    """Computational graph implementation"""

    def __init__(self):
        self.operations = []

    def __iter__(self):
        return iter(self.operations)

    @staticmethod
    def graph_from_iter(name: str) -> 'Graph':
        """Construct new graph which reads data from row iterator (in form of sequence of Rows
        from 'kwargs' passed to 'run' method) into graph data-flow
        Use ops.ReadIterFactory
        :param name: name of kwarg to use as data source
        """
        graph = Graph()
        graph.operations.append(('read', ops.ReadIterFactory(name)))
        return graph

    @staticmethod
    def graph_from_file(filename: str, parser: tp.Callable[[str], ops.TRow]) -> 'Graph':
        """Construct new graph extended with operation for reading rows from file
        Use ops.Read
        :param filename: filename to read from
        :param parser: parser from string to Row
        """
        graph = Graph()
        graph.operations.append(('read', ops.Read(filename, parser)))
        return graph

    def map(self, mapper: ops.Mapper) -> 'Graph':
        """Construct new graph extended with map operation with particular mapper
        :param mapper: mapper to use
        """
        self.operations.append(('map', mapper))
        return self

    def reduce(self, reducer: ops.Reducer, keys: tp.Sequence[str]) -> 'Graph':
        """Construct new graph extended with reduce operation with particular reducer
        :param reducer: reducer to use
        :param keys: keys for grouping
        """
        self.operations.append(('reduce', (reducer, keys)))
        return self

    def sort(self, keys: tp.Sequence[str]) -> 'Graph':
        """Construct new graph extended with sort operation
        :param keys: sorting keys (typical is tuple of strings)
        """
        self.operations.append(('sort', keys))
        return self

    def join(self, joiner: ops.Joiner, join_graph: 'Graph', keys: tp.Sequence[str]) -> 'Graph':
        """Construct new graph extended with join operation with another graph
        :param joiner: join strategy to use
        :param join_graph: other graph to join with
        :param keys: keys for grouping
        """
        self.operations.append(('join', (joiner, join_graph, keys)))
        return self

    def run(self, **kwargs: tp.Any) -> ops.TRowsIterable:
        """Single method to start execution; data sources passed as kwargs"""
        data_source = None
        for op_type, op_data in self.operations:
            if op_type == 'read':
                data_source = op_data(**kwargs)
            elif op_type == 'map':
                data_source = ops.Map(op_data)(data_source)
            elif op_type == 'reduce':
                reducer, keys = op_data
                data_source = ops.Reduce(reducer, keys)(data_source)
            elif op_type == 'sort':
                data_source = es.ExternalSort(op_data)(data_source)
            elif op_type == 'join':
                joiner, join_graph, keys = op_data
                data_source = ops.Join(joiner, keys)(data_source, join_graph.run(**kwargs))

        return data_source

    def copy(self):
        """Return copy of the graph"""
        new_graph = Graph()
        new_graph.operations = self.operations.copy()
        return new_graph
