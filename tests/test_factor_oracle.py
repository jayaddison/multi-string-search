from unittest import TestCase

from multi_string_search import search_sbom

from tests.fixtures import (
    DOCUMENT,
    complete_subset_queries,
    overlapping_set_queries,
    disjoint_set_queries,
)


class TestFactorOracleSearch(TestCase):

    def test_complete_queries(self):
        for terms in complete_subset_queries:
            assert search_sbom(DOCUMENT, terms) is True

    def test_overlapping_queries(self):
        for terms in overlapping_set_queries:
            assert search_sbom(DOCUMENT, terms) is False

    def test_disjoint_queries(self):
        for terms in disjoint_set_queries:
            assert search_sbom(DOCUMENT, terms) is False
