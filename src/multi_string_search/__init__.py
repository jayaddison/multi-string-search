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
    def _traverse(trie: dict[str, str]) -> Iterator[tuple[str, dict[str, str], str | None, int]]:
        nodes = [(0, None, trie)]
        yield 0, None, None, trie, None, False
        while nodes:
            depth, from_char, node = nodes.pop(0)
            for to_char, subnode in node.items():
                if to_char == "..":
                    continue
                yield depth, from_char, to_char, subnode, node, subnode is True
                if isinstance(subnode, dict):
                    nodes.append((depth + 1, to_char, subnode))

    def _build_graph(root: dict[str, str], prefixes: list[str]) -> dict[str, str]:
        import graphviz
        dot = graphviz.Digraph(comment=f"{{{','.join(prefixes)}}}")

        nodes = {id(None): 0}
        edges = defaultdict(dict)
        inbound = defaultdict(set)
        nodes[id(root)] = root_idx = 0

        for idx, (_, from_char, to_char, node, parent, node_is_terminal) in enumerate(FactorOracle._traverse(root)):
            nodes[id(node)] = idx
            if node_is_terminal:
                continue

            dot.node(str(idx))

            parent_idx = nodes[id(parent)]
            edges[parent_idx][from_char] = idx
            dot.edge(str(parent_idx), str(idx), label=to_char)

            transitions = []
            while parent_idx != root_idx:
                parent, parent_char = parent[".."]
                parent_idx = nodes[id(parent)]
                transitions.append(parent_char)
                if len(inbound[parent_idx]):
                    break

            if len(inbound[parent_idx]):
                placement = root
                for char in transitions:
                    if char in placement:
                        placement = placement[char]
                    else:
                        break
                else:
                    placement_idx = nodes[id(placement)]
                    inbound[placement_idx] |= {from_char}
                    dot.edge(str(placement_idx), str(idx), label=to_char)
                    continue

            if from_char not in edges[root_idx]:
                edges[root_idx][from_char] = idx
                inbound[idx] |= {from_char}
                dot.edge(str(root_idx), str(idx), label=from_char)

        dot.render(outfile="testing.png")

    def __init__(self, terms: set[str]):
        prefix_length = min(len(term) for term in terms)
        prefixes = [term[:prefix_length] for term in terms]
        reversed_prefixes = [reversed(prefix) for prefix in prefixes]
        trie = FactorOracle._build_trie(reversed_prefixes)
        self._graph = FactorOracle._build_graph(trie, prefixes)

    def search(self, document):
        for char in iter(document):
            pass
        return False


def search_naive(document: str, terms: set[str]) -> bool:
    return all(term in document for term in terms)


def search_sbom(document: str, terms: set[str]) -> bool:
    factor_oracle = FactorOracle(terms)
    return factor_oracle.search(document)
