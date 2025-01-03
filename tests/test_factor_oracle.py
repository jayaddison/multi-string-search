from unittest import TestCase

from multi_string_search import FactorOracle, TrieNode, search_sbom

from tests.fixtures import (
    DOCUMENT,
    complete_subset_queries,
    overlapping_set_queries,
    disjoint_set_queries,
)


class TestFactorOracleSearch(TestCase):

    def test_trie_build(self):
        terms = ("abc", "aab", "aabc", "bac")
        trie = TrieNode.from_terms(terms, 3)

        expected_trie = TrieNode(
            children={
                "c": TrieNode(children={
                    "b": TrieNode(children={"a": TrieNode(terms={"abc", "aabc"})}),
                    "a": TrieNode(children={"b": TrieNode(terms={"bac"})}),
                }),
                "b": TrieNode(children={
                    "a": TrieNode(children={"a": TrieNode(terms={"aab"})}),
                }),
            }
        )

        self.assertEqual(expected_trie, trie)

    def test_trie_traversal(self):
        terms = ("cba", "baa", "cbaa", "cab")
        trie = TrieNode.from_terms(terms, 4)
        traversal = [node.char for node in trie]

        expected_traversal = [
            None,
            "a",
            "b",
            "b",
            "a",
            "a",
            "c",  # abc
            "b",  # aab
            "c",  # bac
            "c",  # aabc
        ]

        self.assertEqual(expected_traversal, traversal)

    def test_complete_queries(self):
        for terms in complete_subset_queries:
            self.assertTrue(search_sbom(DOCUMENT, terms))

    def test_overlapping_queries(self):
        for terms in overlapping_set_queries:
            self.assertFalse(search_sbom(DOCUMENT, terms))

    def test_disjoint_queries(self):
        for terms in disjoint_set_queries:
            self.assertFalse(search_sbom(DOCUMENT, terms))
