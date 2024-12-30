from typing import Iterator


class FactorOracle:
    """
    This class will implement a Set Backwards Oracle Matching (SBOM) factor
    oracle; it's a datastructure constructed from a collection of text patterns
    used to match against text documents.

    Roughly speaking, the oracle is a directed graph of state transitions, with
    each transition corresponding to a single character read during document
    matching.  The maximum length of any path in the graph is no greater than
    the maximum length of the largest input pattern -- and each paths is
    created from a _reversed_ representation of the corresponding pattern.

    Conversely, we can read-ahead by at least the _minimum_-length pattern
    in the pattern collection from the start of the string and also any other
    time that we encounter a position from which no patterns could possibly
    match.

    So, if our patterns are "twelve", "notes", and "food", and we attempt a
    match of those patterns against a document "food products", we can begin by
    looking at character 4 (the min-length pattern, "food", has length 4) in
    the document, and our oracle would begin matching from the character "d",
    proceeding through two reverse steps of "o" and "o" before finding a
    terminal state (complete string match found) of "f".
    """
    @staticmethod
    def _build_trie(terms: list[str]) -> dict:
        root = {}
        for term in terms:
            node = root
            for char in term:
                if char not in node:
                    node[char] = {}
                node = node[char]
            node[None] = True
        return root

    @staticmethod
    def _traverse(trie: dict[str, str]) -> Iterator[tuple[str, str | None, int]]:
        nodes = [(trie, None, 0)]
        while nodes:
            node, parent, depth = nodes.pop(0)
            for subnode, subtrie in node.items():
                yield depth, subnode, parent
                if isinstance(subtrie, dict):
                    nodes.append((subtrie, subnode, depth + 1))

    def __init__(self, terms: list[str]):
        pass

    def search(self, document):
        for char in iter(document):
            pass
        return False


def search_naive(document: str, terms: list[str]) -> bool:
    return all(term in document for term in terms)


def search_sbom(document: str, terms: list[str]) -> bool:
    factor_oracle = FactorOracle(terms)
    return factor_oracle.search(document)
