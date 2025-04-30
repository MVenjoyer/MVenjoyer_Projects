def find_value(nums: list[int] | range, value: int) -> bool:
    """
    Find value in sorted sequence
    :param nums: sequence of integers. Could be empty
    :param value: integer to find
    :return: True if value exists, False otherwise
    """
    left = -1
    right = len(nums)
    while right - left > 1:
        m = (left + right) // 2
        if nums[m] < value:
            left = m
        else:
            right = m
    return right < len(nums) and nums[right] == value
