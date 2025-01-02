"""
    multi-string-search: prototyped multi-pattern text search implementations
    Copyright (C) 2024 James Addison <jay@jp-hosting.net>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from typing import Iterator


class FactorOracle:
    """
    This class will implement a Set Backwards Oracle Matching (SBOM) factor
    oracle; it's a datastructure constructed from a collection of text patterns
    used to match against text documents.

    Roughly speaking, the oracle is a directed graph of state transitions, with
    each transition corresponding to a single character read during document
    matching.  It is used to match against a sliding range (window) of
    characters in a document -- we choose the largest window size we can, to
    reduce the number of comparison steps -- but the window can be no larger
    than the shortest of the search patterns.

    At the start of the document, and in cases where we know that no pattern
    can possibly match the latest-read character, we can advance the window
    by its complete length.  In other cases we proceed one character at a
    time.

    So, if our patterns are "twelve", "notes", and "food", and we attempt a
    match of those patterns against a document "food products", we can begin by
    looking at character 4 (the min-length pattern, "food", has length 4) in
    the document, and our oracle would begin matching from the character "d",
    proceeding through two reverse steps of "o" and "o" before finding a
    terminal state (complete string match found) of "f".

       L -> E -> W -> T

       E -> T -> O -> N

       D -> O -> O -> F

    For these example patterns we don't have much overlap between the input
    patterns; when overlapping patterns do exist, the oracle factor's graph
    consolidates (de-duplicates) the overlapping parts.
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
    def _traverse(trie: dict[str, str]) -> Iterator[tuple[str, dict[str, str], str | None, int]]:
        nodes = [(0, None, trie)]
        while nodes:
            depth, from_char, node = nodes.pop(0)
            for to_char, subnode in node.items():
                yield depth, from_char, to_char, subnode, node, subnode is True
                if isinstance(subnode, dict):
                    nodes.append((depth + 1, to_char, subnode))

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
