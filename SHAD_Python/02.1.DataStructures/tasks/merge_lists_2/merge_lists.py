import typing as tp
import heapq


def merge(seq: tp.Sequence[tp.Sequence[int]]) -> list[int]:
    """
    :param seq: sequence of sorted sequences
    :return: merged sorted list
    """
    heap: list[tp.Sequence[int]] = []
    result: list[int] = []
    index: list[int] = [0 for _ in range(0, len(seq))]
    for i, value in enumerate(seq):
        if value:
            heapq.heappush(heap, (value[0], i))
    while heap:
        if index[heap[0][1]] + 1 < len(seq[heap[0][1]]):
            value = heapq.heappushpop(heap, (seq[heap[0][1]][index[heap[0][1]] + 1], heap[0][1]))
        else:
            value = heapq.heappop(heap)
        index[value[1]] += 1
        result.append(value[0])
    return result
