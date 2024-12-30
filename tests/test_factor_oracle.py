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
        assert trie == {
            'a': {
                'b': {'c': {None: True}},
                'a': {'b': {None: True, "c": {None: True}}},
            },
            'b': {
                'a': {'c': {None: True}},
            },
        }

    def test_trie_traversal(self):
        terms = ("abc", "aab", "aabc", "bac")
        trie = FactorOracle._build_trie(terms)
        traversal = list(FactorOracle._traverse(trie))
        assert traversal == [
            (0, 'a', None),
            (1, 'b', 'a'),
            (2, 'c', 'b'),
            (3, None, 'c'),  # abc
            (1, 'a', 'a'),
            (2, 'b', 'a'),
            (3, None, 'b'),  # aab
            (3, 'c', 'b'),
            (4, None, 'c'),  # aabc
            (0, 'b', None),
            (1, 'a', 'b'),
            (2, 'c', 'a'),
            (3, None, 'c'),  # bac
        ]

    def test_complete_queries(self):
        for terms in complete_subset_queries:
            assert search_sbom(DOCUMENT, terms) is True

    def test_overlapping_queries(self):
        for terms in overlapping_set_queries:
            assert search_sbom(DOCUMENT, terms) is False

    def test_disjoint_queries(self):
        for terms in disjoint_set_queries:
            assert search_sbom(DOCUMENT, terms) is False
