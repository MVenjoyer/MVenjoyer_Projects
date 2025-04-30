def merge_iterative(lst_a: list[int], lst_b: list[int]) -> list[int]:
    """
    Merge two sorted lists in one sorted list
    :param lst_a: first sorted list
    :param lst_b: second sorted list
    :return: merged sorted list
    """
    new_list: list[int] = []
    lst_a_i: int = 0
    lst_b_i: int = 0
    while lst_a_i < len(lst_a) or lst_b_i < len(lst_b):
        if lst_b_i >= len(lst_b) or (lst_a_i < len(lst_a) and lst_a[lst_a_i] <= lst_b[lst_b_i]):
            new_list.append(lst_a[lst_a_i])
            lst_a_i += 1
        else:
            new_list.append(lst_b[lst_b_i])
            lst_b_i += 1
    return new_list


def merge_sorted(lst_a: list[int], lst_b: list[int]) -> list[int]:
    """
    Merge two sorted lists in one sorted list using `sorted`
    :param lst_a: first sorted list
    :param lst_b: second sorted list
    :return: merged sorted list
    """
    return sorted(lst_a + lst_b)
