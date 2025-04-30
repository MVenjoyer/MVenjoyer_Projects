import sys
import math
import re
from typing import Any

PROMPT = '>>> '


def run_calc(context: dict[str, Any] | None = None) -> None:
    """Run interactive calculator session in specified namespace"""
    context = context or {}
    while True:
        sys.stdout.write(PROMPT)
        if "" != (line := sys.stdin.readline()) != "^D":
            if "(" in line and ")" in line:
                func_name = re.split(r'[.)(]', line)[0].strip()
                if func_name not in context:
                    raise NameError(f"name '{func_name}' is not defined")
            sys.stdout.write(str(eval(line, {"__builtins__": None}, context)) + '\n')
            sys.stdout.flush()
        else:
            sys.stdout.write('\n')
            sys.stdout.flush()
            break


if __name__ == '__main__':
    context = {'math': math}
    run_calc(context)
