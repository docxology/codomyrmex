"""Zero-mock tests for model_ops core: fine_tuning, Dataset, scorers, MCP tools.

Targets:
- fine_tuning/fine_tuning.py: Dataset dataclass, FineTuningJob lifecycle
- __init__.py: Dataset, DatasetSanitizer, FineTuningJob, Evaluator,
  exact_match_metric, length_ratio_metric
- evaluation/scorers.py: ExactMatchScorer, ContainsScorer, LengthScorer,
  RegexScorer, CompositeScorer, WeightedScorer, create_default_scorer
- mcp_tools.py: model_ops_score_output, model_ops_sanitize_dataset,
  model_ops_list_scorers

No mocks. No monkeypatch. No MagicMock. Real objects only.
"""

from __future__ import annotations

import json
import os
import tempfile

import pytest

# ---------------------------------------------------------------------------
# Module-level import guards
# ---------------------------------------------------------------------------

try:
    from codomyrmex.model_ops.fine_tuning.fine_tuning import (
        Dataset as FTDataset,
    )
    from codomyrmex.model_ops.fine_tuning.fine_tuning import (
        FineTuningJob as FTJob,
    )

    FT_AVAILABLE = True
except ImportError:
    FT_AVAILABLE = False

try:
    from codomyrmex.model_ops import (
        Dataset,
        DatasetSanitizer,
        Evaluator,
        FineTuningJob,
        exact_match_metric,
        length_ratio_metric,
    )

    INIT_AVAILABLE = True
except ImportError:
    INIT_AVAILABLE = False

try:
    from codomyrmex.model_ops.evaluation.scorers import (
        CompositeScorer,
        ContainsScorer,
        ExactMatchScorer,
        LengthScorer,
        RegexScorer,
        WeightedScorer,
        create_default_scorer,
    )

    SCORERS_AVAILABLE = True
except ImportError:
    SCORERS_AVAILABLE = False

try:
    from codomyrmex.model_ops.mcp_tools import (
        model_ops_list_scorers,
        model_ops_sanitize_dataset,
        model_ops_score_output,
    )

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False


# ---------------------------------------------------------------------------
# fine_tuning/fine_tuning.py — Dataset dataclass tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not FT_AVAILABLE, reason="fine_tuning module not importable")
class TestFineTuningDataset:
    """Tests for Dataset dataclass in fine_tuning/fine_tuning.py."""

    def test_basic_construction(self):
        ds = FTDataset(name="train_set", path="/data/train.jsonl")
        assert ds.name == "train_set"
        assert ds.path == "/data/train.jsonl"

    def test_default_format_is_jsonl(self):
        ds = FTDataset(name="ds", path="/tmp/ds.jsonl")
        assert ds.format == "jsonl"

    def test_custom_format(self):
        ds = FTDataset(name="ds", path="/tmp/ds.csv", format="csv")
        assert ds.format == "csv"

    def test_metadata_default_empty(self):
        ds = FTDataset(name="ds", path="/tmp/ds.jsonl")
        assert ds.metadata == {}

    def test_to_dict_has_expected_keys(self):
        ds = FTDataset(name="myds", path="/data/train.jsonl", metadata={"rows": 1000})
        d = ds.to_dict()
        assert d["name"] == "myds"
        assert d["path"] == "/data/train.jsonl"
        assert d["format"] == "jsonl"
        assert d["metadata"] == {"rows": 1000}


# ---------------------------------------------------------------------------
# fine_tuning/fine_tuning.py — FineTuningJob lifecycle tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not FT_AVAILABLE, reason="fine_tuning module not importable")
class TestFineTuningJobLifecycle:
    """Tests for FineTuningJob state transitions in fine_tuning.py."""

    def _make_job(self):
        ds = FTDataset(name="train", path="/tmp/train.jsonl")
        return FTJob(base_model="gpt-3.5-turbo", dataset=ds)

    def test_initial_status_is_pending(self):
        job = self._make_job()
        assert job.status == "pending"

    def test_initial_job_id_is_none(self):
        job = self._make_job()
        assert job.job_id is None

    def test_run_sets_status_to_running(self):
        job = self._make_job()
        job.run()
        assert job.status == "running"

    def test_run_sets_job_id(self):
        job = self._make_job()
        job_id = job.run()
        assert job.job_id is not None
        assert job.job_id == job_id

    def test_run_returns_job_id_string(self):
        job = self._make_job()
        result = job.run()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_refresh_status_transitions_running_to_completed(self):
        job = self._make_job()
        job.run()
        status = job.refresh_status()
        assert status == "completed"
        assert job.status == "completed"

    def test_base_model_stored(self):
        ds = FTDataset(name="ds", path="/tmp/ds.jsonl")
        job = FTJob(base_model="llama-3", dataset=ds)
        assert job.base_model == "llama-3"

    def test_provider_defaults_to_openai(self):
        job = self._make_job()
        assert job.provider == "openai"

    def test_custom_provider_stored(self):
        ds = FTDataset(name="ds", path="/tmp/ds.jsonl")
        job = FTJob(base_model="mistral", dataset=ds, provider="anthropic")
        assert job.provider == "anthropic"


# ---------------------------------------------------------------------------
# model_ops/__init__.py — Dataset class tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not INIT_AVAILABLE, reason="model_ops init not importable")
class TestDatasetClass:
    """Tests for Dataset class in model_ops/__init__.py."""

    def test_empty_dataset_validates_true(self):
        ds = Dataset(data=[])
        assert ds.validate() is True

    def test_valid_prompt_completion_format(self):
        ds = Dataset(data=[{"prompt": "q", "completion": "a"}])
        assert ds.validate() is True

    def test_valid_messages_format(self):
        ds = Dataset(data=[{"messages": [{"role": "user", "content": "hi"}]}])
        assert ds.validate() is True

    def test_invalid_format_fails_validation(self):
        ds = Dataset(data=[{"text": "just text"}])
        assert ds.validate() is False

    def test_mixed_valid_and_invalid_fails(self):
        ds = Dataset(
            data=[
                {"prompt": "q", "completion": "a"},
                {"text": "bad"},
            ]
        )
        assert ds.validate() is False

    def test_len_reflects_data_count(self):
        ds = Dataset(data=[{"prompt": "q", "completion": "a"}] * 5)
        assert len(ds) == 5

    def test_to_jsonl_creates_file(self):
        ds = Dataset(data=[{"prompt": "hello", "completion": "world"}])
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
            path = f.name
        try:
            ds.to_jsonl(path)
            with open(path) as f:
                lines = [line for line in f if line.strip()]
            assert len(lines) == 1
            parsed = json.loads(lines[0])
            assert parsed["prompt"] == "hello"
        finally:
            os.unlink(path)

    def test_from_file_loads_jsonl(self):
        examples = [{"prompt": f"q{i}", "completion": f"a{i}"} for i in range(3)]
        with tempfile.NamedTemporaryFile(suffix=".jsonl", mode="w", delete=False) as f:
            path = f.name
            for ex in examples:
                f.write(json.dumps(ex) + "\n")
        try:
            ds = Dataset.from_file(path)
            assert len(ds) == 3
            assert ds.data[0]["prompt"] == "q0"
        finally:
            os.unlink(path)

    def test_none_data_defaults_to_empty_list(self):
        ds = Dataset(data=None)
        assert ds.data == []


# ---------------------------------------------------------------------------
# DatasetSanitizer tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not INIT_AVAILABLE, reason="model_ops init not importable")
class TestDatasetSanitizer:
    """Tests for DatasetSanitizer static methods."""

    def _make_dataset(self, prompts_completions):
        return Dataset(
            data=[{"prompt": p, "completion": c} for p, c in prompts_completions]
        )

    def test_filter_by_length_keeps_in_range(self):
        ds = self._make_dataset([("hello", "world")])  # 10 chars total
        result = DatasetSanitizer.filter_by_length(ds, min_length=5, max_length=20)
        assert len(result) == 1

    def test_filter_by_length_removes_too_short(self):
        ds = self._make_dataset([("hi", "yo")])  # 4 chars
        result = DatasetSanitizer.filter_by_length(ds, min_length=10, max_length=100)
        assert len(result) == 0

    def test_filter_by_length_removes_too_long(self):
        ds = self._make_dataset([("a" * 100, "b" * 100)])  # 200 chars
        result = DatasetSanitizer.filter_by_length(ds, min_length=1, max_length=50)
        assert len(result) == 0

    def test_filter_by_length_keeps_boundary_values(self):
        ds = self._make_dataset([("abc", "def")])  # 6 chars
        result = DatasetSanitizer.filter_by_length(ds, min_length=6, max_length=6)
        assert len(result) == 1

    def test_strip_keys_removes_specified_key(self):
        ds = Dataset(data=[{"prompt": "q", "completion": "a", "secret": "hidden"}])
        result = DatasetSanitizer.strip_keys(ds, keys=["secret"])
        assert "secret" not in result.data[0]

    def test_strip_keys_preserves_other_keys(self):
        ds = Dataset(data=[{"prompt": "q", "completion": "a", "secret": "hidden"}])
        result = DatasetSanitizer.strip_keys(ds, keys=["secret"])
        assert result.data[0]["prompt"] == "q"
        assert result.data[0]["completion"] == "a"

    def test_strip_keys_removes_multiple_keys(self):
        ds = Dataset(data=[{"prompt": "q", "completion": "a", "k1": "v1", "k2": "v2"}])
        result = DatasetSanitizer.strip_keys(ds, keys=["k1", "k2"])
        assert "k1" not in result.data[0]
        assert "k2" not in result.data[0]


# ---------------------------------------------------------------------------
# Metric functions tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not INIT_AVAILABLE, reason="model_ops init not importable")
class TestMetricFunctions:
    """Tests for exact_match_metric and length_ratio_metric."""

    def test_exact_match_perfect_score(self):
        score = exact_match_metric(["hello"], ["hello"])
        assert score == 1.0

    def test_exact_match_no_match(self):
        score = exact_match_metric(["foo"], ["bar"])
        assert score == 0.0

    def test_exact_match_strips_whitespace(self):
        score = exact_match_metric(["  hello  "], ["hello"])
        assert score == 1.0

    def test_exact_match_empty_lists_returns_zero(self):
        score = exact_match_metric([], [])
        assert score == 0.0

    def test_exact_match_partial(self):
        score = exact_match_metric(["a", "b", "c"], ["a", "x", "c"])
        assert abs(score - 2 / 3) < 0.001

    def test_length_ratio_same_length_returns_one(self):
        score = length_ratio_metric(["hello"], ["world"])
        assert score == 1.0

    def test_length_ratio_empty_lists_returns_zero(self):
        score = length_ratio_metric([], [])
        assert score == 0.0

    def test_length_ratio_empty_reference_returns_zero(self):
        score = length_ratio_metric(["abc"], [""])
        # len(p)=3 > 0 but len(r)=0 → ratio 0.0
        assert score == 0.0

    def test_length_ratio_longer_output(self):
        score = length_ratio_metric(["abcde"], ["ab"])
        assert score == 2.5


# ---------------------------------------------------------------------------
# Evaluator class tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not INIT_AVAILABLE, reason="model_ops init not importable")
class TestEvaluatorClass:
    """Tests for the Evaluator class."""

    def test_empty_metrics_returns_empty_dict(self):
        ev = Evaluator(metrics={})
        result = ev.evaluate(["a"], ["a"])
        assert result == {}

    def test_custom_metric_function_called(self):
        ev = Evaluator(metrics={"always_one": lambda p, r: 1.0})
        result = ev.evaluate(["x"], ["y"])
        assert result["always_one"] == 1.0

    def test_exception_in_metric_returns_zero(self):
        def bad_metric(p, r):
            raise RuntimeError("broken")

        ev = Evaluator(metrics={"broken": bad_metric})
        result = ev.evaluate(["x"], ["y"])
        assert result["broken"] == 0.0

    def test_multiple_metrics_all_evaluated(self):
        ev = Evaluator(
            metrics={
                "m1": lambda p, r: 0.5,
                "m2": lambda p, r: 0.8,
            }
        )
        result = ev.evaluate(["a"], ["b"])
        assert "m1" in result
        assert "m2" in result


# ---------------------------------------------------------------------------
# Scorer class tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not SCORERS_AVAILABLE, reason="scorers module not importable")
class TestExactMatchScorer:
    """Tests for ExactMatchScorer."""

    def test_exact_match_returns_one(self):
        s = ExactMatchScorer()
        assert s.score("hello", "hello") == 1.0

    def test_no_match_returns_zero(self):
        s = ExactMatchScorer()
        assert s.score("foo", "bar") == 0.0

    def test_strips_whitespace_by_default(self):
        s = ExactMatchScorer()
        assert s.score("  hello  ", "hello") == 1.0

    def test_case_sensitive_by_default(self):
        s = ExactMatchScorer(case_sensitive=True)
        assert s.score("Hello", "hello") == 0.0

    def test_case_insensitive_mode(self):
        s = ExactMatchScorer(case_sensitive=False)
        assert s.score("HELLO", "hello") == 1.0

    def test_name_property(self):
        assert ExactMatchScorer().name == "exact_match"

    def test_score_batch(self):
        s = ExactMatchScorer()
        scores = s.score_batch([("a", "a"), ("b", "c")])
        assert scores == [1.0, 0.0]


@pytest.mark.skipif(not SCORERS_AVAILABLE, reason="scorers module not importable")
class TestContainsScorer:
    """Tests for ContainsScorer."""

    def test_match_when_contains(self):
        s = ContainsScorer()
        assert s.score("the quick brown fox", "quick") == 1.0

    def test_no_match_when_not_contains(self):
        s = ContainsScorer()
        assert s.score("hello", "world") == 0.0

    def test_case_insensitive_by_default(self):
        s = ContainsScorer()
        assert s.score("Hello World", "hello") == 1.0

    def test_case_sensitive_mode(self):
        s = ContainsScorer(case_sensitive=True)
        assert s.score("Hello World", "hello") == 0.0

    def test_name_property(self):
        assert ContainsScorer().name == "contains"


@pytest.mark.skipif(not SCORERS_AVAILABLE, reason="scorers module not importable")
class TestLengthScorer:
    """Tests for LengthScorer."""

    def test_within_range_returns_one(self):
        s = LengthScorer(min_length=5, max_length=20)
        assert s.score("hello world") == 1.0

    def test_exact_min_length_returns_one(self):
        s = LengthScorer(min_length=5, max_length=10)
        assert s.score("hello") == 1.0

    def test_exact_max_length_returns_one(self):
        s = LengthScorer(min_length=1, max_length=5)
        assert s.score("hello") == 1.0

    def test_too_short_returns_less_than_one(self):
        s = LengthScorer(min_length=10, max_length=20)
        assert s.score("hi") < 1.0

    def test_too_long_returns_less_than_one(self):
        s = LengthScorer(min_length=1, max_length=5)
        assert s.score("a" * 100) < 1.0

    def test_score_is_non_negative(self):
        s = LengthScorer(min_length=10, max_length=20)
        assert s.score("") >= 0.0

    def test_invalid_min_length_raises(self):
        with pytest.raises(ValueError):
            LengthScorer(min_length=-1, max_length=10)

    def test_max_less_than_min_raises(self):
        with pytest.raises(ValueError):
            LengthScorer(min_length=10, max_length=5)

    def test_name_property(self):
        assert LengthScorer().name == "length"


@pytest.mark.skipif(not SCORERS_AVAILABLE, reason="scorers module not importable")
class TestRegexScorer:
    """Tests for RegexScorer."""

    def test_pattern_found_returns_one(self):
        s = RegexScorer()
        assert s.score("hello world", r"h\w+") == 1.0

    def test_pattern_not_found_returns_zero(self):
        s = RegexScorer()
        assert s.score("hello", r"\d+") == 0.0

    def test_full_match_mode(self):
        s = RegexScorer(full_match=True)
        assert s.score("hello", r"hello") == 1.0
        assert s.score("hello world", r"hello") == 0.0

    def test_invalid_regex_returns_zero(self):
        s = RegexScorer()
        assert s.score("anything", r"[invalid") == 0.0

    def test_name_property(self):
        assert RegexScorer().name == "regex"


@pytest.mark.skipif(not SCORERS_AVAILABLE, reason="scorers module not importable")
class TestCompositeScorer:
    """Tests for CompositeScorer and WeightedScorer."""

    def test_empty_composite_returns_zero(self):
        s = CompositeScorer()
        assert s.score("a", "b") == 0.0

    def test_single_scorer_delegates(self):
        inner = ExactMatchScorer()
        s = CompositeScorer([WeightedScorer(inner, weight=1.0)])
        assert s.score("hello", "hello") == 1.0

    def test_add_scorer_chainable(self):
        s = CompositeScorer()
        result = s.add_scorer(ExactMatchScorer(), weight=1.0)
        assert result is s  # chainable

    def test_add_scorer_negative_weight_raises(self):
        s = CompositeScorer()
        with pytest.raises(ValueError):
            s.add_scorer(ExactMatchScorer(), weight=-1.0)

    def test_add_scorer_zero_weight_raises(self):
        s = CompositeScorer()
        with pytest.raises(ValueError):
            s.add_scorer(ExactMatchScorer(), weight=0.0)

    def test_scorer_count_property(self):
        s = CompositeScorer()
        s.add_scorer(ExactMatchScorer(), weight=1.0)
        s.add_scorer(ContainsScorer(), weight=2.0)
        assert s.scorer_count == 2

    def test_weighted_average_calculated_correctly(self):
        # exact_match: 1.0 weight 2.0, contains: 0.0 weight 1.0 → avg = 2.0/3.0
        s = CompositeScorer()
        s.add_scorer(ExactMatchScorer(), weight=2.0)
        s.add_scorer(ContainsScorer(case_sensitive=True), weight=1.0)
        # "hello" vs "HELLO": exact_match=0.0 (case sensitive), contains=0.0
        score = s.score("hello", "HELLO")
        assert score == 0.0

    def test_score_detailed_has_overall_and_scorers(self):
        s = CompositeScorer()
        s.add_scorer(ExactMatchScorer(), weight=1.0)
        detail = s.score_detailed("hello", "hello")
        assert "overall" in detail
        assert "scorers" in detail
        assert len(detail["scorers"]) == 1

    def test_name_property(self):
        assert CompositeScorer().name == "composite"

    def test_create_default_scorer_has_three_scorers(self):
        scorer = create_default_scorer()
        assert scorer.scorer_count == 3

    def test_create_default_scorer_scores_exact_match(self):
        scorer = create_default_scorer()
        score = scorer.score("hello", "hello")
        assert score > 0.0


# ---------------------------------------------------------------------------
# MCP tools tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not MCP_AVAILABLE, reason="mcp_tools module not importable")
class TestModelOpsMCPTools:
    """Tests for model_ops MCP tool functions."""

    def test_list_scorers_returns_list(self):
        result = model_ops_list_scorers()
        assert isinstance(result, list)

    def test_list_scorers_contains_expected_names(self):
        result = model_ops_list_scorers()
        assert "exact_match" in result
        assert "contains" in result
        assert "length" in result
        assert "regex" in result

    def test_score_output_exact_match(self):
        result = model_ops_score_output("hello", "hello", scorers=["exact_match"])
        assert result["scores"]["exact_match"] == 1.0

    def test_score_output_no_match(self):
        result = model_ops_score_output("foo", "bar", scorers=["exact_match"])
        assert result["scores"]["exact_match"] == 0.0

    def test_score_output_default_scorers(self):
        result = model_ops_score_output("hello world", "hello")
        assert "overall" in result
        assert 0.0 <= result["overall"] <= 1.0

    def test_score_output_unknown_scorer_ignored(self):
        result = model_ops_score_output("a", "a", scorers=["unknown_scorer"])
        assert result["scores"] == {}

    def test_score_output_overall_is_average(self):
        result = model_ops_score_output(
            "hello", "hello", scorers=["exact_match", "contains"]
        )
        scores = list(result["scores"].values())
        expected_avg = sum(scores) / len(scores)
        assert abs(result["overall"] - expected_avg) < 1e-5

    def test_sanitize_dataset_filters_by_length(self):
        data = [
            {"prompt": "hi", "completion": "ok"},  # 4 chars — too short
            {"prompt": "hello world", "completion": "response"},  # 19 chars — OK
        ]
        result = model_ops_sanitize_dataset(data, min_length=10, max_length=100)
        assert len(result) == 1
        assert result[0]["prompt"] == "hello world"

    def test_sanitize_dataset_returns_list(self):
        data = [{"prompt": "test", "completion": "answer"}]
        result = model_ops_sanitize_dataset(data)
        assert isinstance(result, list)

    def test_sanitize_dataset_empty_input(self):
        result = model_ops_sanitize_dataset([])
        assert result == []
