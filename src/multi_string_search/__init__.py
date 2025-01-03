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
        if self.is_terminal != other.is_terminal:
            return False
        try:
            if not all(
                self_child == other_child
                for (self_child, other_child)
                in zip(self.children, other.children, strict=True)
            ):
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
        nodes, idx = [(0, self)], 0
        while nodes:
            (depth, node), idx = nodes.pop(0), idx + 1
            yield depth, idx, node
            nodes.extend((depth + 1, child) for child in node.children.values())

    def add_child(self, child_node, child_char):
        assert child_char not in self.children
        self.children[child_char] = child_node

    def add_term(self, term):
        self.terms = frozenset(self.terms | {term})

    @property
    def is_terminal(self):
        return bool(self.terms)

    @staticmethod
    def from_terms(terms: list[str]) -> "TrieNode":
        root = TrieNode()
        for term in terms:
            node, parent = root, None
            for char in term:
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
    def _build_graph(root: dict) -> tuple[dict, set[str]]:
        import graphviz
        dot = graphviz.Digraph()

        nodes = {}
        edges = defaultdict(dict)
        inbound = defaultdict(set)
        terminals = set()

        nodes[id(root)] = root_idx = 0
        for _, idx, node in root:
            nodes[id(node)] = idx
            if node.is_terminal:
                terminals.add(idx)

            dot.node(str(idx))

            parent = node.parent_node
            if parent is None:
                assert node is root
                continue

            to_char = node.parent_char
            parent_idx = nodes[id(parent)]
            edges[parent_idx][to_char] = idx
            dot.edge(str(parent_idx), str(idx), label=to_char)

            transitions = []
            while parent is not root:
                parent, parent_char = parent.parent_node, parent.parent_char
                parent_idx = nodes[id(parent)]
                if parent_idx:
                    transitions.append(parent_char)
                if len(inbound[parent_idx]):
                    break

            if transitions:
                placement_idx = 0
                while transitions:
                    char = transitions.pop()
                    if char in edges[placement_idx]:
                        placement_idx = edges[placement_idx][char]
                    else:
                        break
                else:
                    if to_char not in edges[placement_idx]:
                        edges[placement_idx][to_char] = idx
                        inbound[placement_idx] |= {to_char}
                        dot.edge(str(placement_idx), str(idx), label=to_char)

            if to_char not in edges[root_idx]:
                edges[root_idx][to_char] = idx
                inbound[idx] |= {to_char}
                dot.edge(str(root_idx), str(idx), label=to_char)

        dot.render(outfile="testing.png")
        return edges, terminals

    def __init__(self, query_terms: set[str]):
        self._query_terms, self._prefix_length = (
            query_terms,
            min(len(term) for term in query_terms),
        )
        trie = TrieNode.from_terms(terms=[
            reversed(term[:self._prefix_length])
            for term in self._query_terms
        ])
        self._graph = FactorOracle._build_graph(trie)

    def search(self, document):
        edges, terminals = self._graph
        remaining = set(self._query_terms)
        while window := document[:self._prefix_length]:
            state, advance = 0, len(window) - 1
            try:
                for char in reversed(window):
                    state = edges[state][char]
                    if state in terminals:
                        # TODO: yield further matching candidates?
                        break
                    advance -= 1
            except KeyError:
                pass

            assert advance >= 0
            document = document[advance:]  # advance past failed char
            if state in terminals:
                # TODO: only compare terms associated with the relevant terminal
                remaining -= {term for term in remaining if document.startswith(term)}
                if not remaining:
                    return True
            if advance == 0:
                document = document[1:]
        return False


def search_naive(document: str, terms: set[str]) -> bool:
    return all(term in document for term in terms)


def search_sbom(document: str, terms: set[str]) -> bool:
    factor_oracle = FactorOracle(terms)
    return factor_oracle.search(document)
