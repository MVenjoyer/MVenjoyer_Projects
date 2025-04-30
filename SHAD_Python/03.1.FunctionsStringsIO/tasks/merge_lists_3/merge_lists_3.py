import typing as tp
import heapq


def merge(input_streams: tp.Sequence[tp.IO[bytes]], output_stream: tp.IO[bytes]) -> None:
    """
    Merge input_streams in output_stream
    :param input_streams: list of input streams. Contains byte-strings separated by "\n". Nonempty stream ends with "\n"
    :param output_stream: output stream. Contains byte-strings separated by "\n". Nonempty stream ends with "\n"
    :return: None
    """
    heap: list[tp.Sequence[int]] = []
    for i, value in enumerate(input_streams):
        if line := value.readline():
            heapq.heappush(heap, (int(line.decode().strip()), i))
    while heap:
        if line1 := input_streams[heap[0][1]].readline():
            value1 = heapq.heappushpop(heap, (int(line1.decode().strip()), heap[0][1]))
        else:
            value1 = heapq.heappop(heap)
        output_stream.write((str(value1[0])).encode() + b'\n')
