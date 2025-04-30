import typing as tp
from pathlib import Path
import sys


def tail(filename: Path, lines_amount: int = 10, output: tp.IO[bytes] | None = None) -> None:
    """
    :param filename: file to read lines from (the file can be very large)
    :param lines_amount: number of lines to read
    :param output: stream to write requested amount of last lines from file
                   (if nothing specified stdout will be used)
    """
    splitting = b'\r\n'
    if output is None:
        output = sys.stdout.buffer
        splitting = b'\n'
    chunk_size = 256
    buffer = bytearray()
    counter = 0
    with open(filename, 'rb') as file:
        file.seek(0, 2)
        file_size = file.tell()
        chunk_size = min(file_size, chunk_size)
        chunk = bytearray(chunk_size)
        mv = memoryview(chunk)
        while counter + (x := mv.tobytes().count(b'\n')) <= lines_amount + 1 and len(buffer) < file_size:
            if chunk_size > file_size - len(buffer):
                last = bytearray(file_size - len(buffer))
                file.seek(0, 0)
                file.readinto(last)
                buffer += last + buffer
                break
            file.seek(-min(chunk_size, file_size - len(buffer)), 1)
            file.readinto(chunk)
            buffer = chunk + buffer
            file.seek(-min(chunk_size, file_size - len(buffer)), 1)
            counter += x
        lines = buffer.splitlines()
        last_lines = lines[-lines_amount:] if lines_amount > 0 else []
        if splitting != b'\n':
            result = splitting.join(last_lines)
        else:
            result = splitting.join(last_lines) + splitting
        output.write(result)
