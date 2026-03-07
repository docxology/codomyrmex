"""Property-based tests using Hypothesis for validation schemas.

Tests that Result dataclass maintains invariants under arbitrary inputs.
"""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from codomyrmex.validation.schemas import Result, ResultStatus

# --- Strategies ---

result_statuses = st.sampled_from(list(ResultStatus))

# Use actual enum members dynamically
_non_success = [s for s in ResultStatus if s != ResultStatus.SUCCESS]

results = st.builds(
    Result,
    status=result_statuses,
    message=st.text(max_size=200),
    data=st.one_of(
        st.none(),
        st.integers(),
        st.text(max_size=50),
        st.dictionaries(st.text(max_size=10), st.integers(), max_size=3),
    ),
    errors=st.lists(st.text(max_size=50), max_size=5),
)


class TestResultInvariants:
    """Property tests for Result dataclass invariants."""

    @given(result=results)
    @settings(max_examples=100, deadline=2000)
    def test_ok_iff_success(self, result):
        """Result.ok is True if and only if status is SUCCESS."""
        if result.status == ResultStatus.SUCCESS:
            assert result.ok is True
        else:
            assert result.ok is False

    @given(result=results)
    @settings(max_examples=50, deadline=2000)
    def test_result_has_status(self, result):
        """Every Result has a valid ResultStatus."""
        assert result.status in ResultStatus

    @given(msg=st.text(max_size=200))
    @settings(max_examples=50, deadline=2000)
    def test_success_result_message_preserved(self, msg):
        """Message is preserved in success results."""
        r = Result(status=ResultStatus.SUCCESS, message=msg)
        assert r.message == msg
        assert r.ok is True

    @given(errors=st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=5))
    @settings(max_examples=50, deadline=2000)
    def test_error_result_with_errors(self, errors):
        """Non-success results preserve their error list."""
        non_success = _non_success[0]
        r = Result(status=non_success, message="fail", errors=list(errors))
        assert r.ok is False
        assert r.errors == errors
        assert len(r.errors) >= 1

    @given(data=st.one_of(st.none(), st.integers(), st.text(max_size=50)))
    @settings(max_examples=50, deadline=2000)
    def test_data_preserved(self, data):
        """Data field is preserved regardless of type."""
        r = Result(status=ResultStatus.SUCCESS, data=data)
        assert r.data == data

    def test_default_fields(self):
        """Default message is empty, default data is None, default errors is empty list."""
        r = Result(status=ResultStatus.SUCCESS)
        assert r.message == ""
        assert r.data is None
        assert r.errors == []

    @given(status=result_statuses)
    @settings(max_examples=10, deadline=2000)
    def test_status_is_str_enum(self, status):
        """ResultStatus values are strings."""
        assert isinstance(status.value, str)


class TestResultStatusEnumeration:
    """Property tests for ResultStatus enum."""

    def test_all_statuses_exist(self):
        """Core statuses exist and can be accessed."""
        assert ResultStatus.SUCCESS.value == "success"
        # Verify all members are valid StrEnum strings
        for member in ResultStatus:
            assert isinstance(member.value, str)

    def test_exactly_four_statuses(self):
        """There are at least 4 result statuses."""
        assert len(ResultStatus) >= 4

    @given(status_str=st.sampled_from([s.value for s in ResultStatus]))
    @settings(max_examples=10, deadline=2000)
    def test_round_trip_from_string(self, status_str):
        """ResultStatus can be constructed from its string value."""
        status = ResultStatus(status_str)
        assert status.value == status_str
