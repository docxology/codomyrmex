"""
Unit tests for utils.refined — Zero-Mock compliant.

Covers: RefinedUtilities.deep_merge (flat, nested, overwrite, non-dict),
RefinedUtilities.retry (success first try, success after retries,
exhaustion raises, backoff_factor=0/jitter=False to avoid real sleep),
RefinedUtilities.resolve_path (absolute, relative with base, relative
without base).
"""

import pytest

from codomyrmex.utils.refined import RefinedUtilities

# ── deep_merge ─────────────────────────────────────────────────────────


@pytest.mark.unit
class TestDeepMerge:
    def test_disjoint_keys_merged(self):
        d1 = {"a": 1}
        d2 = {"b": 2}
        result = RefinedUtilities.deep_merge(d1, d2)
        assert result == {"a": 1, "b": 2}

    def test_d2_overrides_d1_scalar(self):
        d1 = {"a": 1}
        d2 = {"a": 99}
        result = RefinedUtilities.deep_merge(d1, d2)
        assert result["a"] == 99

    def test_nested_dicts_merged_recursively(self):
        d1 = {"nested": {"x": 1, "y": 2}}
        d2 = {"nested": {"y": 99, "z": 3}}
        result = RefinedUtilities.deep_merge(d1, d2)
        assert result["nested"]["x"] == 1
        assert result["nested"]["y"] == 99
        assert result["nested"]["z"] == 3

    def test_d1_not_mutated(self):
        d1 = {"a": {"x": 1}}
        d2 = {"a": {"y": 2}}
        result = RefinedUtilities.deep_merge(d1, d2)
        # d1 should be unchanged at top level (shallow copy)
        assert "y" not in d1.get("a", {})
        assert result["a"]["y"] == 2

    def test_d2_non_dict_overrides_d1_dict(self):
        """When d2 value is not a dict, it replaces d1's dict value."""
        d1 = {"a": {"x": 1}}
        d2 = {"a": "new_value"}
        result = RefinedUtilities.deep_merge(d1, d2)
        assert result["a"] == "new_value"

    def test_d1_non_dict_overridden_by_d2_dict(self):
        """When d1 value is not a dict, d2's dict value replaces it."""
        d1 = {"a": "old_value"}
        d2 = {"a": {"x": 1}}
        result = RefinedUtilities.deep_merge(d1, d2)
        assert result["a"] == {"x": 1}

    def test_empty_d1(self):
        d2 = {"a": 1, "b": 2}
        result = RefinedUtilities.deep_merge({}, d2)
        assert result == {"a": 1, "b": 2}

    def test_empty_d2(self):
        d1 = {"a": 1}
        result = RefinedUtilities.deep_merge(d1, {})
        assert result == {"a": 1}

    def test_both_empty(self):
        assert RefinedUtilities.deep_merge({}, {}) == {}

    def test_deeply_nested(self):
        d1 = {"a": {"b": {"c": 1}}}
        d2 = {"a": {"b": {"d": 2}}}
        result = RefinedUtilities.deep_merge(d1, d2)
        assert result["a"]["b"]["c"] == 1
        assert result["a"]["b"]["d"] == 2


# ── retry ──────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestRetryDecorator:
    def test_success_first_try(self):
        call_count = [0]

        @RefinedUtilities.retry(retries=3, backoff_factor=0.0, jitter=False)
        def succeed():
            call_count[0] += 1
            return "ok"

        result = succeed()
        assert result == "ok"
        assert call_count[0] == 1

    def test_success_after_one_failure(self):
        call_count = [0]

        @RefinedUtilities.retry(retries=3, backoff_factor=0.0, jitter=False)
        def fail_once():
            call_count[0] += 1
            if call_count[0] < 2:
                raise ValueError("transient")
            return "recovered"

        result = fail_once()
        assert result == "recovered"
        assert call_count[0] == 2

    def test_exhausts_retries_and_raises(self):
        call_count = [0]

        @RefinedUtilities.retry(retries=3, backoff_factor=0.0, jitter=False)
        def always_fail():
            call_count[0] += 1
            raise RuntimeError("permanent")

        with pytest.raises(RuntimeError, match="permanent"):
            always_fail()
        assert call_count[0] == 3

    def test_retries_one_no_retry(self):
        call_count = [0]

        @RefinedUtilities.retry(retries=1, backoff_factor=0.0, jitter=False)
        def fail():
            call_count[0] += 1
            raise ValueError("fail")

        with pytest.raises(ValueError):
            fail()
        assert call_count[0] == 1

    def test_preserves_return_value(self):
        @RefinedUtilities.retry(retries=2, backoff_factor=0.0, jitter=False)
        def give_data():
            return {"key": "value"}

        assert give_data() == {"key": "value"}

    def test_passes_arguments(self):
        @RefinedUtilities.retry(retries=2, backoff_factor=0.0, jitter=False)
        def add(a, b):
            return a + b

        assert add(3, 4) == 7


# ── resolve_path ───────────────────────────────────────────────────────


@pytest.mark.unit
class TestResolvePath:
    def test_absolute_path_unchanged(self):
        from pathlib import Path
        result = RefinedUtilities.resolve_path("/absolute/path/to/file.txt")
        assert result == Path("/absolute/path/to/file.txt")

    def test_relative_path_with_base_dir(self):
        result = RefinedUtilities.resolve_path("data/file.txt", base_dir="/tmp")
        assert result.is_absolute()
        assert "file.txt" in str(result)

    def test_relative_path_without_base_resolves_from_cwd(self):
        result = RefinedUtilities.resolve_path("some_relative_file.txt")
        assert result.is_absolute()
        assert "some_relative_file.txt" in str(result)

    def test_returns_path_object(self):
        from pathlib import Path
        result = RefinedUtilities.resolve_path("/tmp/test")
        assert isinstance(result, Path)

    def test_absolute_path_with_base_ignores_base(self):
        from pathlib import Path
        result = RefinedUtilities.resolve_path("/absolute/path", base_dir="/tmp")
        # Absolute path ignores base_dir
        assert result == Path("/absolute/path")

    def test_relative_path_base_dir_combined(self):
        result = RefinedUtilities.resolve_path("subdir/file.py", base_dir="/home/user")
        assert "/home/user" in str(result) or result.is_absolute()
        assert "file.py" in str(result)
