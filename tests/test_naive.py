from unittest import TestCase

from multi_string_search import search_naive


complete_subset_queries = (
  ["sample paragraph", "confirm the behaviour", "text search"],
  ["paragraph of text", "Set-Backwards-Oracle-Matching", "multi-pattern"],
  ["text"],
)

overlapping_set_queries = (
  ["sample paragraph", "unrelated paragraph"],
  ["paragraph of text", "diagram of results"],
  ["factor oracle construction", "online text search"],
)

disjoint_set_queries = (
  ["factor oracle"],
  ["textual", "unrelated paragraph"],
  ["disjoint", "queries"],
)


DOCUMENT = None
with open("tests/dataset.txt") as f:
    DOCUMENT = f.read()


class TestNaiveSearch(TestCase):

    def test_complete_queries(self):
        for terms in complete_subset_queries:
            assert search_naive(DOCUMENT, terms) is True

    def test_overlapping_queries(self):
        for terms in overlapping_set_queries:
            assert search_naive(DOCUMENT, terms) is False

    def test_disjoint_queries(self):
        for terms in disjoint_set_queries:
            assert search_naive(DOCUMENT, terms) is False
