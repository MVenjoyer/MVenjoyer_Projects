import typing as tp


def convert_to_common_type(data: list[tp.Any]) -> list[tp.Any]:
    """
    Takes list of multiple types' elements and convert each element to common type according to given rules
    :param data: list of multiple types' elements
    :return: list with elements converted to common type
    """
    new_list: list[tp.Any] = []
    # list
    # int
    # float
    # bool
    # str
    common_type: type = type(None)
    for item in data:
        match (type(item).__name__, common_type.__name__):
            case ("list", _) | ("tuple", _):
                common_type = list
            case ("str", "int") | ("str", "bool") | ("str", "float"):
                if item != "" and item != "None":
                    common_type = str
            case ("float", "int") | ("float", "bool"):
                common_type = float
            case ("int", "bool"):
                if item == 0 or item == 1:
                    common_type = bool
                else:
                    common_type = int
            case (_, "NoneType"):
                if item == 0 or item == 1:
                    common_type = bool
                elif item == 'None':
                    common_type = type(None)
                else:
                    common_type = type(item)
    for item in data:
        match common_type.__name__:
            case "list":
                if type(item) is tuple:
                    new_list.append(list(item))
                elif item is None or item == '':
                    new_list.append([])
                elif type(item) is list:
                    new_list.append(item)
                else:
                    new_list.append([item])
            case "str":
                if item is not None:
                    new_list.append(str(item))
                else:
                    new_list.append("")
            case "float":
                if item == '' or item is None:
                    new_list.append(0.0)
                else:
                    new_list.append(float(item))
            case "int":
                if item == '' or item is None:
                    new_list.append(0)
                else:
                    new_list.append(int(item))
            case "bool":
                if item == '' or item is None:
                    new_list.append(False)
                else:
                    new_list.append(bool(item))
            case _:
                new_list.append('')
    return new_list
