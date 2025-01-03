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
    def _build_trie(terms: list[str]) -> dict:
        root = {"..": (None, None)}
        for term in terms:
            node, parent = root, None
            for char in term:
                if char not in node:
                    node[char] = {}
                node, parent = node[char], node
                node[".."] = parent, char
            node[None] = True
        return root

    @staticmethod
    def _traverse(trie: dict) -> Iterator[tuple[int, str | None, dict, dict | None, bool]]:
        nodes = [(0, trie)]
        yield 0, None, trie, None, False
        while nodes:
            depth, node = nodes.pop(0)
            for to_char, subnode in node.items():
                if to_char == "..":
                    continue
                if isinstance(subnode, dict):
                    yield depth, to_char, subnode, node, None in subnode
                    nodes.append((depth + 1, subnode))

    def _build_graph(root: dict, prefixes: list[str]) -> tuple[dict, set[str]]:
        import graphviz
        dot = graphviz.Digraph(comment=f"{{{','.join(prefixes)}}}")

        nodes = {}
        edges = defaultdict(dict)
        inbound = defaultdict(set)
        terminals = set()

        nodes[id(root)] = root_idx = 0
        for idx, (_, to_char, node, parent, node_is_terminal) in enumerate(FactorOracle._traverse(root)):
            nodes[id(node)] = idx
            if node_is_terminal:
                terminals.add(idx)

            dot.node(str(idx))
            if parent is None:
                assert node is root
                continue

            parent_idx = nodes[id(parent)]
            edges[parent_idx][to_char] = idx
            dot.edge(str(parent_idx), str(idx), label=to_char)

            transitions = []
            while parent_idx != root_idx:
                parent, parent_char = parent[".."]
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

    def __init__(self, terms: set[str]):
        self.terms = terms
        self.prefix_length = min(len(term) for term in terms)
        prefixes = [term[:self.prefix_length] for term in terms]
        reversed_prefixes = [reversed(prefix) for prefix in prefixes]
        trie = FactorOracle._build_trie(reversed_prefixes)
        edges, terminals = FactorOracle._build_graph(trie, prefixes)
        self._graph = {"edges": edges, "terminals": terminals}

    def search(self, document):
        edges, terminals = self._graph.values()
        found = set()
        while window := document[:self.prefix_length]:
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
                found |= {term for term in self.terms if document.startswith(term)}
                if len(found) == len(self.terms):
                    return True
            if advance == 0:
                document = document[1:]
        return False


def search_naive(document: str, terms: set[str]) -> bool:
    return all(term in document for term in terms)


def search_sbom(document: str, terms: set[str]) -> bool:
    factor_oracle = FactorOracle(terms)
    return factor_oracle.search(document)
