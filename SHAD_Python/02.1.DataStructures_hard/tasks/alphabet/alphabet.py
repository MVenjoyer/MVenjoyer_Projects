import enum


class Status(enum.Enum):
    NEW = 0
    EXTRACTED = 1
    FINISHED = 2


def dfs(
        v: str,
        graph: dict[str, set[str]],
        visited: dict[str, bool],
        stack: list[str]
) -> list[str]:
    for u in graph[v]:
        if not visited[u]:
            dfs(u, graph, visited, stack)
    if not visited[v]:
        stack.append(v)
    visited[v] = True
    return stack


def extract_alphabet(
        graph: dict[str, set[str]]
) -> list[str]:
    """
    Extract alphabet from graph
    :param graph: graph with partial order
    :return: alphabet
    """
    visited: dict[str, bool] = {key: False for key in graph.keys()}
    stack: list[str] = []
    for key in graph.keys():
        dfs(key, graph, visited, stack)
    return stack[::-1]


def build_graph(
        words: list[str]
) -> dict[str, set[str]]:
    """
    Build graph from ordered words. Graph should contain all letters from words
    :param words: ordered words
    :return: graph
    """
    dct: dict[str, set[str]] = {}
    for word1, word2 in zip(words, words[1:]):
        was_break = False
        for i in range(max(len(word1), len(word2))):
            if i >= len(word1):
                if word2[i] not in dct:
                    dct[word2[i]] = set()
            elif i >= len(word2):
                if word1[i] not in dct:
                    dct[word1[i]] = set()
            elif not was_break and word1[i] != word2[i]:
                if word1[i] not in dct:
                    dct[word1[i]] = set()
                if word2[i] not in dct:
                    dct[word2[i]] = set()
                dct[word1[i]].add(word2[i])
                was_break = True
            elif word1[i] not in dct:
                dct[word1[i]] = set()
    return dct if len(words) != 1 else {c: set() for c in words[0]}


#########################
# Don't change this code
#########################

def get_alphabet(
        words: list[str]
) -> list[str]:
    """
    Extract alphabet from sorted words
    :param words: sorted words
    :return: alphabet
    """
    graph = build_graph(words)
    return extract_alphabet(graph)

#########################
