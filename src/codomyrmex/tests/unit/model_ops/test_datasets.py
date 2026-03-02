"""
Unit tests for model_ops.datasets.datasets — Zero-Mock compliant.

Covers: Dataset (construction, validate, to_jsonl/from_file roundtrip),
DatasetSanitizer (strip_keys, filter_by_length).
"""

import json
import tempfile

import pytest

from codomyrmex.model_ops.datasets.datasets import Dataset, DatasetSanitizer

# ── Dataset ────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestDataset:
    def test_empty_dataset(self):
        ds = Dataset([])
        assert ds.data == []

    def test_dataset_stores_data(self):
        items = [{"messages": [{"role": "user", "content": "hi"}]}]
        ds = Dataset(items)
        assert ds.data == items

    def test_validate_valid_messages(self):
        ds = Dataset([
            {"messages": [{"role": "user", "content": "hi"}]},
            {"messages": [{"role": "user", "content": "hello"}]},
        ])
        assert ds.validate() is True

    def test_validate_valid_prompt(self):
        ds = Dataset([{"prompt": "tell me a story"}])
        assert ds.validate() is True

    def test_validate_mixed_formats(self):
        ds = Dataset([
            {"messages": "some"},
            {"prompt": "some"},
        ])
        assert ds.validate() is True

    def test_validate_invalid_item(self):
        ds = Dataset([{"other_key": "value"}])
        assert ds.validate() is False

    def test_validate_empty_dataset(self):
        # Empty dataset has no invalid items → True
        ds = Dataset([])
        assert ds.validate() is True

    def test_validate_stops_at_first_invalid(self):
        ds = Dataset([
            {"messages": "ok"},
            {"bad_key": "value"},
            {"messages": "also ok"},
        ])
        # Second item is invalid — returns False
        assert ds.validate() is False

    def test_to_jsonl_and_from_file_roundtrip(self):
        original = [
            {"messages": [{"role": "user", "content": "hello"}]},
            {"prompt": "world", "label": "test"},
        ]
        ds = Dataset(original)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            path = f.name

        ds.to_jsonl(path)
        loaded = Dataset.from_file(path)
        assert loaded.data == original

    def test_from_file_each_line_parsed(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False
        ) as f:
            for i in range(5):
                f.write(json.dumps({"id": i, "messages": f"msg{i}"}) + "\n")
            path = f.name

        ds = Dataset.from_file(path)
        assert len(ds.data) == 5
        assert ds.data[0]["id"] == 0
        assert ds.data[4]["id"] == 4


# ── DatasetSanitizer ───────────────────────────────────────────────────────


@pytest.mark.unit
class TestDatasetSanitizer:
    def test_strip_keys_removes_specified(self):
        ds = Dataset([
            {"name": "Alice", "ssn": "123-45-6789", "age": 30},
            {"name": "Bob", "ssn": "987-65-4321", "age": 25},
        ])
        cleaned = DatasetSanitizer.strip_keys(ds, ["ssn"])
        for item in cleaned.data:
            assert "ssn" not in item
            assert "name" in item

    def test_strip_keys_preserves_others(self):
        ds = Dataset([{"a": 1, "b": 2, "c": 3}])
        cleaned = DatasetSanitizer.strip_keys(ds, ["b"])
        assert cleaned.data[0] == {"a": 1, "c": 3}

    def test_strip_keys_missing_key_ok(self):
        ds = Dataset([{"a": 1}])
        cleaned = DatasetSanitizer.strip_keys(ds, ["nonexistent"])
        assert cleaned.data[0] == {"a": 1}

    def test_strip_keys_returns_new_dataset(self):
        ds = Dataset([{"x": 1}])
        cleaned = DatasetSanitizer.strip_keys(ds, [])
        assert cleaned is not ds

    def test_filter_by_length_within_range(self):
        ds = Dataset([
            {"prompt": "short"},
            {"prompt": "a" * 100},
            {"prompt": "a" * 200},
        ])
        filtered = DatasetSanitizer.filter_by_length(ds, min_len=5, max_len=150)
        assert len(filtered.data) == 2

    def test_filter_by_length_default_range(self):
        ds = Dataset([{"prompt": "hello"}])
        filtered = DatasetSanitizer.filter_by_length(ds)
        assert len(filtered.data) == 1

    def test_filter_by_length_excludes_too_short(self):
        ds = Dataset([{"prompt": "hi"}, {"prompt": "hello world"}])
        filtered = DatasetSanitizer.filter_by_length(ds, min_len=5)
        assert len(filtered.data) == 1
        assert filtered.data[0]["prompt"] == "hello world"

    def test_filter_by_length_uses_messages_fallback(self):
        ds = Dataset([{"messages": "hello there"}])
        filtered = DatasetSanitizer.filter_by_length(ds, min_len=5, max_len=100)
        assert len(filtered.data) == 1

    def test_filter_by_length_empty_result(self):
        ds = Dataset([{"prompt": "x"}])
        filtered = DatasetSanitizer.filter_by_length(ds, min_len=1000)
        assert len(filtered.data) == 0
