import pytest

from codomyrmex.search.mcp_tools import (
    search_documents,
    search_fuzzy,
    search_index_query,
)


@pytest.mark.unit
class TestSearchMcpTools:
    def test_search_documents_success(self):
        docs = ["apple pie", "orange juice", "apple cider"]
        res = search_documents("apple", docs, top_k=2)
        assert res["status"] == "ok"
        assert res["query"] == "apple"
        assert len(res["results"]) <= 2

    def test_search_documents_error(self):
        res = search_documents("apple", None)
        assert res["status"] == "error"

    def test_search_index_query_success(self):
        docs = ["python programming", "java programming"]
        res = search_index_query("python", docs)
        assert res["status"] == "ok"
        assert res["query"] == "python"
        assert res["index_size"] == 2
        assert len(res["results"]) > 0

    def test_search_index_query_error(self):
        res = search_index_query("python", None)
        assert res["status"] == "error"

    def test_search_fuzzy_success(self):
        candidates = ["python", "java", "javascript"]
        res = search_fuzzy("pythn", candidates)
        assert res["status"] == "ok"
        assert res["query"] == "pythn"
        assert res["best_match"] == "python"
        assert len(res["matches"]) > 0

    def test_search_fuzzy_error(self):
        res = search_fuzzy("pythn", None)
        assert res["status"] == "error"
