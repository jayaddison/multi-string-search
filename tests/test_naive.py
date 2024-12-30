from unittest import TestCase

from multi_string_search import search_naive

from tests.fixtures import (
    DOCUMENT,
    complete_subset_queries,
    overlapping_set_queries,
    disjoint_set_queries,
)


class TestNaiveSearch(TestCase):

    def test_complete_queries(self):
        for terms in complete_subset_queries:
            self.assertTrue(search_naive(DOCUMENT, terms))

    def test_overlapping_queries(self):
        for terms in overlapping_set_queries:
            self.assertFalse(search_naive(DOCUMENT, terms))

    def test_disjoint_queries(self):
        for terms in disjoint_set_queries:
            self.assertFalse(search_naive(DOCUMENT, terms))
