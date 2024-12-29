def search_naive(document: str, terms: list[str]) -> bool:
    return all(term in document for term in terms)
