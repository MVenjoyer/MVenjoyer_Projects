def filter_list_by_list(lst_a: list[int] | range, lst_b: list[int] | range) -> list[int]:
    """
    Filter first sorted list by other sorted list
    :param lst_a: first sorted list
    :param lst_b: second sorted list
    :return: filtered sorted list
    """
    new_list: list[int] = []
    lst_a_i: int = 0
    lst_b_i: int = 0
    while lst_a_i < len(lst_a) or lst_b_i < len(lst_b):
        if lst_b_i >= len(lst_b) or (lst_a_i < len(lst_a) and lst_a[lst_a_i] < lst_b[lst_b_i]):
            new_list.append(lst_a[lst_a_i])
            lst_a_i += 1
        elif lst_a_i < len(lst_a) and lst_b_i < len(lst_b) and lst_a[lst_a_i] == lst_b[lst_b_i]:
            lst_a_i += 1
        else:
            lst_b_i += 1
    return new_list
