from collections.abc import Sequence


def find_median(nums1: Sequence[int], nums2: Sequence[int]) -> float:
    """
    Find median of two sorted sequences. At least one of sequences should be not empty.
    :param nums1: sorted sequence of integers
    :param nums2: sorted sequence of integers
    :return: middle value if sum of sequences' lengths is odd
             average of two middle values if sum of sequences' lengths is even
    """
    if (n := len(nums1)) > len(nums2):
        return find_median(nums2, nums1)
    lft, right = -1, n
    while True:
        m = (lft + right) // 2
        k = (n + len(nums2)) // 2 - m - 1
        m0 = nums1[m - 1] if 0 <= m - 1 < n else float('-inf')
        m1 = nums1[m] if 0 <= m < n else float('-inf')
        m2 = nums1[m + 1] if m + 1 < n else float('inf')
        k0 = nums2[k - 1] if 0 <= k - 1 < len(nums2) else float('-inf')
        k1 = nums2[k] if 0 <= k < len(nums2) else float('-inf')
        k2 = nums2[k + 1] if k + 1 < len(nums2) else float('inf')
        if k1 <= m1 <= k2 or m1 <= k1 <= m2:
            if (n + len(nums2)) % 2 == 1:
                return float(max(m1, k1))
            elif m1 > k1:
                return (m1 + max(k1, m0)) / 2
            else:
                return (k1 + max(m1, k0)) / 2
        elif m1 > k2:
            right = m - 1
        else:
            lft = m + 1
