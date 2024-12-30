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
        traversal = list((depth, from_char, to_char) for (depth, from_char, to_char, _) in FactorOracle._traverse(trie))
        self.assertEqual([
            (0, None, 'a'),
            (0, None, 'b'),
            (1, 'a', 'b'),
            (1, 'a', 'a'),
            (1, 'b', 'a'),
            (2, 'b', 'c'),
            (2, 'a', 'b'),
            (2, 'a', 'c'),
            (3, 'c', None),  # abc
            (3, 'b', None),  # aab
            (3, 'b', 'c'),
            (3, 'c', None),  # bac
            (4, 'c', None),  # aabc
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
