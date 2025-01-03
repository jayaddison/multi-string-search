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
    counter = 0

    def __init__(self, parent=None, char=None, children=None, terms=None):
        self.parent = parent
        self.char = char
        self.children = children or {}
        self.terms = frozenset(terms or [])
        self.allocate_id()

        for char in self.children:
            children[char].parent = self
            children[char].char = char

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
        if self.char != other.char:
            return False
        return True

    def __contains__(self, child_char):
        return child_char in self.children

    def __getitem__(self, child_char):
        return self.children[child_char]

    def __iter__(self) -> Iterator[tuple[int, "TrieNode"]]:
        nodes = [self]
        while nodes:
            node = nodes.pop(0)
            yield node
            nodes.extend(node.children.values())

    def add_child(self, child_node, child_char):
        assert child_char not in self.children
        self.children[child_char] = child_node

    def add_term(self, term):
        self.terms = frozenset(self.terms | {term})

    def allocate_id(self):
        self.id, TrieNode.counter = TrieNode.counter, TrieNode.counter + 1

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
                    node = TrieNode(parent=node, char=char)
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
        edges, destination_nodes = defaultdict(dict), set()
        for node in root:
            if node is root:
                continue

            # Always create a transition from the parent node to this one
            parent = node.parent
            edges[parent.id][node.char] = node

            # Collect the path from the nearest node with inbound transitions to here
            transitions = []
            while parent is not root:
                parent, char = parent.parent, parent.char
                if parent.id:
                    transitions.append(char)
                if parent.id in destination_nodes:
                    break

            # Navigate from the root of the trie based on the collected path (if any)
            placement = root
            for char in transitions:
                placement = edges[placement.id].get(char) or root
                if placement is root:
                    break

            # If we navigated to an available non-root node, add a transition from there
            if placement is not root and node.char not in edges[placement.id]:
                edges[placement.id][node.char] = node
                destination_nodes.add(placement.id)

            # If the root node is unaware of the current symbol, add a direct transition
            if node.char not in edges[root.id]:
                edges[root.id][node.char] = node
                destination_nodes.add(node.id)

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

            # Advance to the next successfully-matched character in the document
            document = document[advance:]
            if not state:
                continue

            # Remove any terms associated with the matched state node
            remaining -= {term for term in state.terms if document.startswith(term)}
            document = document[1:]

        # Return success if all query terms have been found
        return len(remaining) == 0


def search_naive(document: str, terms: set[str]) -> bool:
    return all(term in document for term in terms)


def search_sbom(document: str, terms: set[str]) -> bool:
    factor_oracle = FactorOracle(terms)
    return factor_oracle.search(document)
