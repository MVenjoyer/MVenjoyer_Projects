from types import FunctionType
from typing import Any

CO_VARARGS = 4
CO_VARKEYWORDS = 8

ERR_TOO_MANY_POS_ARGS = 'Too many positional arguments'
ERR_TOO_MANY_KW_ARGS = 'Too many keyword arguments'
ERR_MULT_VALUES_FOR_ARG = 'Multiple values for arguments'
ERR_MISSING_POS_ARGS = 'Missing positional arguments'
ERR_MISSING_KWONLY_ARGS = 'Missing keyword-only arguments'
ERR_POSONLY_PASSED_AS_KW = 'Positional-only argument passed as keyword argument'


def bind_args(func: FunctionType, *args: Any, **kwargs: Any) -> dict[str, Any]:
    """Bind values from `args` and `kwargs` to corresponding arguments of `func`

    :param func: function to be inspected
    :param args: positional arguments to be bound
    :param kwargs: keyword arguments to be bound
    :return: `dict[argument_name] = argument_value` if binding was successful,
             raise TypeError with one of `ERR_*` error descriptions otherwise
    """
    code = func.__code__
    flags = code.co_flags
    varargs = flags & CO_VARARGS == CO_VARARGS
    varkeywords = flags & CO_VARKEYWORDS == CO_VARKEYWORDS
    variables = code.co_varnames
    args_amount = code.co_argcount
    pos_only_amount = code.co_posonlyargcount
    name_only_amount = code.co_kwonlyargcount
    default = func.__defaults__ or ()
    default_len = len(default)
    kw_default = func.__kwdefaults__ or ()
    answer: dict[str, Any] = {}
    pos = 0
    name = 0
    used_kwargs = set()
    used_pos_args = set()
    for i in range(pos_only_amount):
        if i < len(args):
            used_pos_args.add(variables[i])
            answer[variables[i]] = args[i]
            pos += 1
        elif variables[i] in kwargs:
            if pos_only_amount > len(args) and varkeywords:
                raise TypeError(ERR_MISSING_POS_ARGS)
            raise TypeError(ERR_POSONLY_PASSED_AS_KW)
        elif (x := i - (args_amount - default_len)) < 0:
            raise TypeError(ERR_MISSING_POS_ARGS)
        else:
            used_pos_args.add(variables[i])
            answer[variables[i]] = default[x]
            pos += 1
    for i in range(pos_only_amount, args_amount):
        if pos < len(args):
            answer[variables[i]] = args[i]
            pos += 1
        elif name < len(args) + len(kwargs) and variables[i] in kwargs:
            answer[variables[i]] = kwargs[variables[i]]
            used_kwargs.add(variables[i])
            name += 1
        elif (x := i - (args_amount - default_len)) < 0:
            for el in kwargs.keys():
                if el in answer and el not in used_kwargs:
                    raise TypeError(ERR_POSONLY_PASSED_AS_KW)
            raise TypeError(ERR_MISSING_POS_ARGS)
        elif default:
            for el in kwargs.keys():
                if el in answer and el not in used_kwargs:
                    raise TypeError(ERR_POSONLY_PASSED_AS_KW)
            answer[variables[i]] = default[x]
            pos += 1
    if pos < len(args) and not varargs:
        raise TypeError(ERR_TOO_MANY_POS_ARGS)
    for i in range(args_amount, args_amount + name_only_amount):
        if variables[i] in kwargs:
            answer[variables[i]] = kwargs[variables[i]]
            used_kwargs.add(variables[i])
            name += 1
        elif kw_default and variables[i] in kw_default:
            answer[variables[i]] = kw_default[variables[i]]
            used_kwargs.add(variables[i])
            name += 1
        else:
            raise TypeError(ERR_MISSING_KWONLY_ARGS)
    if name < len(kwargs):
        for key in answer:
            if key not in used_pos_args:
                if key in kwargs and key not in used_kwargs and key in answer:
                    raise TypeError(ERR_MULT_VALUES_FOR_ARG)
                elif not varkeywords:
                    raise TypeError(ERR_MISSING_POS_ARGS)
        if not varkeywords:
            raise TypeError(ERR_TOO_MANY_KW_ARGS)
    if varargs:
        answer[variables[args_amount + name_only_amount]] = args[pos:]
    if varkeywords:
        answer[variables[args_amount + name_only_amount + (1 if varargs else 0)]] = {k: v for k, v in kwargs.items() if
                                                                                     k not in used_kwargs}
    return answer
