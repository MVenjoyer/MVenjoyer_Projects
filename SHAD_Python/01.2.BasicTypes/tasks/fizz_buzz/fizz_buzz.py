def get_fizz_buzz(n: int) -> list[int | str]:
    """
    If value divided by 3 - "Fizz",
       value divided by 5 - "Buzz",
       value divided by 15 - "FizzBuzz",
    else - value.
    :param n: size of sequence
    :return: list of values.
    """
    fizz_buzz_list: list[int | str] = []
    for i in range(n):
        if (i + 1) % 15 == 0:
            fizz_buzz_list.append("FizzBuzz")
        elif (i + 1) % 3 == 0:
            fizz_buzz_list.append("Fizz")
        elif (i + 1) % 5 == 0:
            fizz_buzz_list.append("Buzz")
        else:
            fizz_buzz_list.append(i + 1)
    return fizz_buzz_list
