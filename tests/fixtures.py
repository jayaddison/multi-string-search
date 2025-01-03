complete_subset_queries = (
  ["sample paragraph", "confirm the behaviour", "text search"],
  ["paragraph of text", "Set-Backwards-Oracle-Matching", "multi-pattern"],
  ["text"],
  ["This is", "Thi", "his", "is"],
  ["ab", "bc", "def", "ghi", "hij", "yz"],
)

overlapping_set_queries = (
  ["sample paragraph", "unrelated paragraph"],
  ["paragraph of text", "diagram of results"],
  ["factor oracle construction", "online text search"],
  ["abc", "bcd", "nml", "xyz"],
)

disjoint_set_queries = (
  ["factor oracle"],
  ["textual", "unrelated paragraph"],
  ["disjoint", "queries"],
  ["acegi", "zxvtr"],
)

DOCUMENT = None
with open("tests/dataset.txt") as f:
    DOCUMENT = f.read()
