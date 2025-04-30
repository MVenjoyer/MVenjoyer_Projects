import typing as tp


def revert(dct: tp.Mapping[str, str]) -> dict[str, list[str]]:
    """
    :param dct: dictionary to revert in format {key: value}
    :return: reverted dictionary {value: [key1, key2, key3]}
    """
    new_dct: dict[str, list[str]] = {}
    for key, value in dct.items():
        if not new_dct.get(value, []):
            new_dct[value] = [key]
        else:
            new_dct[value].append(key)
    return new_dct
