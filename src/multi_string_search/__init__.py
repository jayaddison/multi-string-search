from typing import Iterator


class FactorOracle:
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
    def _traverse(trie: dict[str, str]) -> Iterator[tuple[str, str | None]]:
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
