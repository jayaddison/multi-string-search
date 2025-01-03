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
        trie = TrieNode.from_terms(terms)

        expected_trie = TrieNode(
            children={
                "a": TrieNode(children={
                    "b": TrieNode(children={"c": TrieNode(terms={"abc"})}),
                    "a": TrieNode(children={
                        "b": TrieNode(
                            children={"c": TrieNode(terms={"aabc"})},
                            terms={"aab"}
                        )
                    })
                }),
                "b": TrieNode(children={
                    "a": TrieNode(children={"c": TrieNode(terms={"bac"})}),
                }),
            }
        )

        self.assertEqual(expected_trie, trie)

    def test_trie_traversal(self):
        terms = ("abc", "aab", "aabc", "bac")
        trie = TrieNode.from_terms(terms)
        traversal = [(depth, node.parent_char) for (depth, _, node) in trie]
        self.assertEqual([
            (0, None),
            (1, 'a'),
            (1, 'b'),
            (2, 'b'),
            (2, 'a'),
            (2, 'a'),
            (3, 'c'),  # abc
            (3, 'b'),  # aab
            (3, 'c'),  # bac
            (4, 'c'),  # aabc
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
