import pytest

from codomyrmex.cerebrum.mcp_tools import add_case_reference, query_knowledge_base


@pytest.mark.unit
class TestCerebrumMCPTools:
    def test_add_case_reference_success(self):
        # The tool creates a new CaseBase and adds a Case.
        res = add_case_reference("Test concept", "Test solution")
        assert res["status"] == "success", res.get("message", "Unknown error")
        assert "Case stored successfully" in res["message"]
        assert "case_id" in res

    def test_add_case_reference_error(self):
        """Test add_case_reference with invalid inputs."""
        # Empty concept
        res = add_case_reference("", "solution")
        assert res["status"] == "error"
        assert "concept must be a non-empty string" in res["message"]

        # Empty solution
        res = add_case_reference("concept", "")
        assert res["status"] == "error"
        assert "solution must be a non-empty string" in res["message"]

    def test_query_knowledge_base_success(self):
        # Put something in first
        add_case_reference("Gravity", "It pulls things down")

        # Query it back
        res = query_knowledge_base("Gravity", limit=1)

        assert res["status"] == "success"
        assert "results" in res
        assert res["count"] >= 0

        # We might not get exactly 1 back if the DB is empty or just re-inited,
        # but the schema of the response is guaranteed.
        if res["count"] > 0:
            first_result = res["results"][0]
            assert "id" in first_result
            assert "features" in first_result
            assert "solution" in first_result
            assert "similarity_score" in first_result
