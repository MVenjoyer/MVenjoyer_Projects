import dis
import types


def count_operations(source_code: types.CodeType) -> dict[str, int]:
    """Count byte code operations in given source code.

    :param source_code: the bytecode operation names to be extracted from
    :return: operation counts
    """
    op_count: dict[str, int] = {}

    def deep_count_operations(code: types.CodeType) -> None:
        for instr in dis.get_instructions(code):
            op_count[instr.opname] = op_count.get(instr.opname, 0) + 1
            if isinstance(instr.argval, types.CodeType):
                deep_count_operations(instr.argval)

    deep_count_operations(source_code)
    return op_count
