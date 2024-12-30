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
        traversal = list(FactorOracle._traverse(trie))
        self.assertEqual([
            (0, 'a', None),
            (0, 'b', None),
            (1, 'b', 'a'),
            (1, 'a', 'a'),
            (1, 'a', 'b'),
            (2, 'c', 'b'),
            (2, 'b', 'a'),
            (2, 'c', 'a'),
            (3, None, 'c'),  # abc
            (3, None, 'b'),  # aab
            (3, 'c', 'b'),
            (3, None, 'c'),  # bac
            (4, None, 'c'),  # aabc
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
