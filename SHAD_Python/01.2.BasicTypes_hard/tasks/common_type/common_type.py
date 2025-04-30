def get_common_type(type1: type, type2: type) -> type:
    """
    Calculate common type according to rule, that it must have the most adequate interpretation after conversion.
    Look in tests for adequacy calibration.
    :param type1: one of [bool, int, float, complex, list, range, tuple, str] types
    :param type2: one of [bool, int, float, complex, list, range, tuple, str] types
    :return: the most concrete common type, which can be used to convert both input values
    """
    match (type1.__name__, type2.__name__):
        case ("list", "list") | ("tuple", "tuple"):
            return type1
        case ("list", "tuple") | ("tuple", "list") | ("list", "range") | ("range", "list"):
            return list
        case ("tuple", "range") | ("range", "tuple") | ("range", "range"):
            return tuple
        case ("str", _) | (_, "str") | ("list", _) | (_, "list") | ("tuple", _) | (_, "tuple") | ("range", _) | \
             (_, "range"):
            return str
        case ("bool", _):
            return type2
        case (_, "bool"):
            return type1
        case ("complex", _) | (_, "complex"):
            return complex
        case (_, "float") | ("float", _):
            return float
    return int
