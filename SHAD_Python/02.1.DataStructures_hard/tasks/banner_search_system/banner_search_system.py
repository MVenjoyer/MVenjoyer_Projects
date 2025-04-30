import re
from collections import defaultdict
import typing as tp
import heapq
from collections import Counter


def normalize(
        text: str
) -> str:
    """
    Removes punctuation and digits and convert to lower case
    :param text: text to normalize
    :return: normalized query
    """
    return re.sub(r'[^а-яa-z\s]', '', text.lower())


def get_words(
        query: str
) -> list[str]:
    """
    Split by words and leave only words with letters greater than 3
    :param query: query to split
    :return: filtered and split query by words
    """
    return [word for word in query.split() if len(word) > 3]


def build_index(
        banners: list[str]
) -> dict[str, list[int]]:
    """
    Create index from words to banners ids with preserving order and without repetitions
    :param banners: list of banners for indexation
    :return: mapping from word to banners ids
    """
    result: defaultdict[str, list[int]] = defaultdict(list)
    for i, s in enumerate(banners):
        for j in get_words(normalize(s)):
            if not result[j] or result[j][len(result[j]) - 1] < i:
                result[j].append(i)
    return dict(result)


def get_banner_indices_by_query(
        query: str,
        index: dict[str, list[int]]
) -> list[int]:
    """
    Extract banners indices from index, if all words from query contains in indexed banner
    :param query: query to find banners
    :param index: index to search banners
    :return: list of indices of suitable banners
    """
    lst: list[str] = get_words(normalize(query))
    seq: list[tp.Sequence[int]] = []
    for words in lst:
        if x := index.get(words):
            seq.append(x)
        else:
            return []
    heap: list[tp.Sequence[int]] = []
    result: list[int] = []
    idx: list[int] = [0 for _ in range(0, len(seq))]
    for i, value in enumerate(seq):
        if value:
            heapq.heappush(heap, (value[0], i))
    while heap:
        if idx[heap[0][1]] + 1 < len(seq[heap[0][1]]):
            value = heapq.heappushpop(heap, (seq[heap[0][1]][idx[heap[0][1]] + 1], heap[0][1]))
        else:
            value = heapq.heappop(heap)
        idx[value[1]] += 1
        result.append(value[0])
    counter = Counter(result)
    return [i for i, el in counter.items() if el >= len(lst)]


#########################
# Don't change this code
#########################

def get_banners(
        query: str,
        index: dict[str, list[int]],
        banners: list[str]
) -> list[str]:
    """
    Extract banners matched to queries
    :param query: query to match
    :param index: word-banner_ids index
    :param banners: list of banners
    :return: list of matched banners
    """
    indices = get_banner_indices_by_query(query, index)
    return [banners[i] for i in indices]

#########################
