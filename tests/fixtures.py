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
