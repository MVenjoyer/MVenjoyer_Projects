import sys
from contextlib import contextmanager
from typing import Iterator, TextIO, Type


@contextmanager
def supresser(*types_: Type[BaseException]) -> Iterator[None]:
    try:
        yield
    except types_:
        pass
    else:
        raise


@contextmanager
def retyper(type_from: Type[BaseException], type_to: Type[BaseException]) -> Iterator[None]:
    try:
        yield
    except type_from as e:
        raise type_to(*e.args) from None


@contextmanager
def dumper(stream: TextIO | None = None) -> Iterator[None]:
    try:
        yield
    except Exception as e:
        stream = stream if stream else sys.stderr
        stream.write(str(e))
        stream.write('\n')
        raise e
