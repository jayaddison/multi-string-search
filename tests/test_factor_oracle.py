from unittest import TestCase

from multi_string_search import FactorOracle, search_sbom

from tests.fixtures import (
    DOCUMENT,
    complete_subset_queries,
    overlapping_set_queries,
    disjoint_set_queries,
)


class TestFactorOracleSearch(TestCase):

    def test_trie_build(self):
        terms = ("abc", "aab", "aabc", "bac")
        trie = FactorOracle._build_trie(terms)

        def del_parent_node_references(node):
            del node[".."]
            for _, subnode in node.items():
                if isinstance(subnode, dict):
                    del_parent_node_references(subnode)
        del_parent_node_references(trie)

        self.assertEqual({
            'a': {
                'b': {'c': {None: True}},
                'a': {'b': {None: True, "c": {None: True}}},
            },
            'b': {
                'a': {'c': {None: True}},
            },
        }, trie)

    def test_trie_traversal(self):
        terms = ("abc", "aab", "aabc", "bac")
        trie = FactorOracle._build_trie(terms)
        traversal = list((depth, transition) for (depth, transition, _, _, _) in FactorOracle._traverse(trie))
        self.assertEqual([
            (0, None),
            (0, 'a'),
            (0, 'b'),
            (1, 'b'),
            (1, 'a'),
            (1, 'a'),
            (2, 'c'),  # abc
            (2, 'b'),  # aab
            (2, 'c'),  # bac
            (3, 'c'),  # aabc
        ], traversal)

    def test_complete_queries(self):
        for terms in complete_subset_queries:
            self.assertTrue(search_sbom(DOCUMENT, terms))

    def test_overlapping_queries(self):
        for terms in overlapping_set_queries:
            self.assertFalse(search_sbom(DOCUMENT, terms))

    def test_disjoint_queries(self):
        for terms in disjoint_set_queries:
            self.assertFalse(search_sbom(DOCUMENT, terms))
