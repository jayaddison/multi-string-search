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
from collections import defaultdict
from typing import Iterator


class TrieNode:
    def __init__(self, parent_node=None, parent_char=None, children=None, terms=None):
        self.parent_node = parent_node
        self.parent_char = parent_char
        self.children = {}
        self.terms = frozenset(terms or [])

        if children:
            for char in children:
                self.children[char] = children[char]
                children[char].parent_node = self
                children[char].parent_char = char

    def __eq__(self, other):
        assert isinstance(other, TrieNode)
        if self.terms != other.terms:
            return False
        try:
            pairs = zip(self.children, other.children, strict=True)
            if not all(a == b for a, b in pairs):
                return False
        except ValueError:
            return False
        if self.parent_char != other.parent_char:
            return False
        return True

    def __contains__(self, child_char):
        return child_char in self.children

    def __getitem__(self, child_char):
        return self.children[child_char]

    def __iter__(self) -> Iterator[tuple[int, "TrieNode"]]:
        nodes = [(0, self)]
        while nodes:
            depth, node = nodes.pop(0)
            yield depth, node
            nodes.extend((depth + 1, child) for child in node.children.values())

    def add_child(self, child_node, child_char):
        assert child_char not in self.children
        self.children[child_char] = child_node

    def add_term(self, term):
        self.terms = frozenset(self.terms | {term})

    def set_id(self, value):
        self.id = value

    @staticmethod
    def from_terms(terms: list[str], prefix_length: int) -> "TrieNode":
        root = TrieNode()
        for term in terms:
            node, parent = root, None
            for char in term[:prefix_length][::-1]:  # reversed prefixes
                parent = node
                if char in node:
                    node = node[char]
                else:
                    node = TrieNode(parent_node=node, parent_char=char)
                    parent.add_child(node, char)
            node.add_term(term)
        return root


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
    terminal state (complete prefix match found) of "f".

       L -> E -> W -> T

       E -> T -> O -> N

       D -> O -> O -> F

    For these example patterns we don't have much overlap between the input
    patterns; when overlapping patterns do exist, the oracle factor's graph
    consolidates (de-duplicates) the overlapping parts.
    """
    @staticmethod
    def _build_graph(root: dict) -> tuple[dict]:
        edges = defaultdict(dict)
        inbound = defaultdict(set)

        for idx, (_, node) in enumerate(root):
            node.set_id(idx)

            parent = node.parent_node
            if parent is None:
                assert node is root
                continue

            to_char = node.parent_char
            edges[parent.id][to_char] = node

            transitions = []
            while parent is not root:
                parent, parent_char = parent.parent_node, parent.parent_char
                if parent.id:
                    transitions.append(parent_char)
                if len(inbound[parent.id]):
                    break

            if transitions:
                placement_idx = 0
                while transitions:
                    char = transitions.pop()
                    if char in edges[placement_idx]:
                        placement_idx = edges[placement_idx][char].id
                    else:
                        break
                else:
                    if to_char not in edges[placement_idx]:
                        edges[placement_idx][to_char] = node
                        inbound[placement_idx] |= {to_char}

            if to_char not in edges[root.id]:
                edges[root.id][to_char] = node
                inbound[node.id] |= {to_char}

        return edges

    def __init__(self, query_terms: set[str]):
        self._query_terms = query_terms
        self._prefix_length = min(map(len, query_terms))
        self._trie = TrieNode.from_terms(self._query_terms, self._prefix_length)
        self._graph = FactorOracle._build_graph(self._trie)
        self._export_graph()

    def _export_graph(self):
        import graphviz
        dot = graphviz.Digraph()
        for node_id, transitions in self._graph.items():
            dot.node(str(node_id))
            for char, to_node in transitions.items():
                dot.edge(str(node_id), str(to_node.id), label=char)
        dot.render(outfile="testing.png")

    def search(self, document):
        remaining = set(self._query_terms)
        while (window := document[:self._prefix_length]) and remaining:

            # Optimization: no results can be found in a window smaller than the prefix
            if len(window) < self._prefix_length:
                break

            # Read backwards through the window, and correspondingly down the trie
            state, advance = self._trie, self._prefix_length
            for char in reversed(window):
                state, advance = self._graph[state.id].get(char), advance - 1
                if state is None or state.terms:
                    break
            assert advance >= 0

            document = document[advance:]
            if not state:
                continue

            remaining -= {term for term in state.terms if document.startswith(term)}
            document = document[1:]
        return not bool(remaining)


def search_naive(document: str, terms: set[str]) -> bool:
    return all(term in document for term in terms)


def search_sbom(document: str, terms: set[str]) -> bool:
    factor_oracle = FactorOracle(terms)
    return factor_oracle.search(document)
