"""Unit tests for case management."""

import pytest

from codomyrmex.cerebrum import (
    Case,
    CaseBase,
    CaseNotFoundError,
    CaseRetriever,
    InvalidCaseError,
)


@pytest.mark.unit
class TestCase:
    """Test Case class."""

    def test_create_case(self):
        """Test case creation."""
        case = Case(
            case_id="test_001",
            features={"x": 1, "y": 2},
            outcome="success"
        )
        assert case.case_id == "test_001"
        assert case.features == {"x": 1, "y": 2}
        assert case.outcome == "success"

    def test_case_validation(self):
        """Test case validation."""
        with pytest.raises(InvalidCaseError):
            Case(case_id="", features={"x": 1})

        with pytest.raises(InvalidCaseError):
            Case(case_id="test", features={})

    def test_case_to_dict(self):
        """Test case serialization."""
        case = Case(case_id="test", features={"x": 1}, outcome="success")
        data = case.to_dict()
        assert data["case_id"] == "test"
        assert data["features"] == {"x": 1}
        assert data["outcome"] == "success"

    def test_case_from_dict(self):
        """Test case deserialization."""
        data = {
            "case_id": "test",
            "features": {"x": 1},
            "outcome": "success"
        }
        case = Case.from_dict(data)
        assert case.case_id == "test"
        assert case.features == {"x": 1}
        assert case.outcome == "success"


@pytest.mark.unit
class TestCaseBase:
    """Test CaseBase class."""

    def test_add_case(self):
        """Test adding cases."""
        case_base = CaseBase()
        case = Case(case_id="test", features={"x": 1})
        case_base.add_case(case)
        assert case_base.size() == 1

    def test_get_case(self):
        """Test retrieving cases."""
        case_base = CaseBase()
        case = Case(case_id="test", features={"x": 1})
        case_base.add_case(case)
        retrieved = case_base.get_case("test")
        assert retrieved.case_id == "test"

    def test_get_case_not_found(self):
        """Test retrieving non-existent case."""
        case_base = CaseBase()
        with pytest.raises(CaseNotFoundError):
            case_base.get_case("nonexistent")

    def test_retrieve_similar(self):
        """Test retrieving similar cases."""
        case_base = CaseBase()

        # Add cases
        case1 = Case(case_id="case1", features={"x": 1, "y": 1})
        case2 = Case(case_id="case2", features={"x": 2, "y": 2})
        case3 = Case(case_id="case3", features={"x": 10, "y": 10})

        case_base.add_case(case1)
        case_base.add_case(case2)
        case_base.add_case(case3)

        # Query
        query = Case(case_id="query", features={"x": 1.5, "y": 1.5})
        similar = case_base.retrieve_similar(query, k=2)

        assert len(similar) == 2
        # case1 and case2 should be more similar than case3
        assert similar[0][0].case_id in ["case1", "case2"]

    def test_compute_similarity(self):
        """Test similarity computation."""
        case_base = CaseBase()
        case1 = Case(case_id="case1", features={"x": 1, "y": 1})
        case2 = Case(case_id="case2", features={"x": 1, "y": 1})
        case3 = Case(case_id="case3", features={"x": 10, "y": 10})

        similarity_same = case_base.compute_similarity(case1, case2)
        similarity_different = case_base.compute_similarity(case1, case3)

        assert similarity_same > similarity_different
        assert 0 <= similarity_same <= 1
        assert 0 <= similarity_different <= 1


@pytest.mark.unit
class TestCaseRetriever:
    """Test CaseRetriever class."""

    def test_retrieve(self):
        """Test case retrieval."""
        case_base = CaseBase()
        case1 = Case(case_id="case1", features={"x": 1}, metadata={"frequency": 2.0})
        case2 = Case(case_id="case2", features={"x": 2}, metadata={"frequency": 1.0})
        case_base.add_case(case1)
        case_base.add_case(case2)

        retriever = CaseRetriever(case_base, weighting_strategy="frequency")
        query = Case(case_id="query", features={"x": 1.5})
        results = retriever.retrieve(query, k=2)

        assert len(results) == 2


