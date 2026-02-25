"""Comprehensive tests for the model_ops module.

Tests cover Dataset management, DatasetSanitizer, FineTuningJob,
Evaluator, metric functions, the evaluation submodule classes
(AccuracyMetric, PrecisionMetric, etc.), ModelEvaluator, ConfusionMatrix,
and factory functions.
"""

import json
import math

import pytest

from codomyrmex.model_ops import (
    AccuracyMetric,
    AUCROCMetric,
    ConfusionMatrix,
    Dataset,
    DatasetSanitizer,
    EvaluationResult,
    Evaluator,
    F1Metric,
    FineTuningJob,
    MAEMetric,
    ModelEvaluator,
    MSEMetric,
    PrecisionMetric,
    R2Metric,
    RecallMetric,
    RMSEMetric,
    TaskType,
    create_evaluator,
    exact_match_metric,
    length_ratio_metric,
)


# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_dataset_creation_empty():
    """Test empty dataset creation."""
    ds = Dataset()
    assert len(ds) == 0
    assert ds.data == []


@pytest.mark.unit
def test_dataset_creation_with_data():
    """Test dataset creation with provided data."""
    data = [{"prompt": "hello", "completion": "world"}]
    ds = Dataset(data)
    assert len(ds) == 1


@pytest.mark.unit
def test_dataset_validation_prompt_completion():
    """Test validation accepts prompt/completion format."""
    ds = Dataset([{"prompt": "a", "completion": "b"}])
    assert ds.validate() is True


@pytest.mark.unit
def test_dataset_validation_messages_format():
    """Test validation accepts messages format."""
    ds = Dataset([{"messages": [{"role": "user", "content": "hi"}]}])
    assert ds.validate() is True


@pytest.mark.unit
def test_dataset_validation_mixed_formats():
    """Test validation accepts mixed format datasets."""
    ds = Dataset([
        {"prompt": "a", "completion": "b"},
        {"messages": [{"role": "user", "content": "hi"}]},
    ])
    assert ds.validate() is True


@pytest.mark.unit
def test_dataset_validation_invalid():
    """Test validation rejects invalid format."""
    ds = Dataset([{"wrong": "format"}])
    assert ds.validate() is False


@pytest.mark.unit
def test_dataset_validation_empty_is_valid():
    """Test empty dataset is considered valid."""
    ds = Dataset([])
    assert ds.validate() is True


@pytest.mark.unit
def test_dataset_to_jsonl(tmp_path):
    """Test exporting dataset to JSONL file."""
    path = str(tmp_path / "data.jsonl")
    ds = Dataset([
        {"prompt": "a", "completion": "b"},
        {"prompt": "c", "completion": "d"},
    ])
    ds.to_jsonl(path)

    with open(path) as f:
        lines = f.readlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["prompt"] == "a"


@pytest.mark.unit
def test_dataset_from_file(tmp_path):
    """Test loading dataset from JSONL file."""
    path = str(tmp_path / "data.jsonl")
    with open(path, "w") as f:
        f.write(json.dumps({"prompt": "hello", "completion": "world"}) + "\n")
        f.write(json.dumps({"prompt": "foo", "completion": "bar"}) + "\n")

    ds = Dataset.from_file(path)
    assert len(ds) == 2
    assert ds.data[0]["prompt"] == "hello"


@pytest.mark.unit
def test_dataset_from_file_skips_blank_lines(tmp_path):
    """Test loading skips blank lines."""
    path = str(tmp_path / "data.jsonl")
    with open(path, "w") as f:
        f.write(json.dumps({"prompt": "a", "completion": "b"}) + "\n")
        f.write("\n")
        f.write(json.dumps({"prompt": "c", "completion": "d"}) + "\n")

    ds = Dataset.from_file(path)
    assert len(ds) == 2


# ---------------------------------------------------------------------------
# DatasetSanitizer
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_sanitizer_strip_keys():
    """Test stripping specified keys from dataset examples."""
    ds = Dataset([
        {"prompt": "hi", "pii": "secret", "extra": "data"},
        {"prompt": "hello"},
    ])
    sanitized = DatasetSanitizer.strip_keys(ds, ["pii", "extra"])
    assert "pii" not in sanitized.data[0]
    assert "extra" not in sanitized.data[0]
    assert sanitized.data[0]["prompt"] == "hi"
    assert len(sanitized.data) == 2


@pytest.mark.unit
def test_sanitizer_filter_by_length():
    """Test filtering examples by content length."""
    ds = Dataset([
        {"prompt": "a", "completion": "b"},        # length = 2
        {"prompt": "hello world", "completion": "foo bar baz"},  # length = 22
    ])
    filtered = DatasetSanitizer.filter_by_length(ds, min_length=5, max_length=100)
    assert len(filtered.data) == 1
    assert filtered.data[0]["prompt"] == "hello world"


@pytest.mark.unit
def test_sanitizer_filter_by_length_keeps_all():
    """Test filter keeps all when bounds are wide."""
    ds = Dataset([
        {"prompt": "a", "completion": "b"},
        {"prompt": "hello", "completion": "world"},
    ])
    filtered = DatasetSanitizer.filter_by_length(ds, min_length=0, max_length=10000)
    assert len(filtered.data) == 2


# ---------------------------------------------------------------------------
# FineTuningJob
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_fine_tuning_job_initial_state():
    """Test FineTuningJob starts in pending state."""
    ds = Dataset([{"prompt": "A", "completion": "B"}])
    job = FineTuningJob(base_model="gpt-4o", dataset=ds)
    assert job.status == "pending"
    assert job.job_id is None


@pytest.mark.unit
def test_fine_tuning_job_run():
    """Test running a fine-tuning job transitions to running."""
    ds = Dataset([{"prompt": "A", "completion": "B"}])
    job = FineTuningJob(base_model="gpt-4o", dataset=ds)
    job_id = job.run()
    assert job_id is not None
    assert job_id.startswith("ft-")
    assert job.status == "running"


@pytest.mark.unit
def test_fine_tuning_job_refresh_completes():
    """Test refresh_status transitions running to completed."""
    job = FineTuningJob()
    job.run()
    status = job.refresh_status()
    assert status == "completed"
    assert job.status == "completed"


@pytest.mark.unit
def test_fine_tuning_job_refresh_pending_stays_pending():
    """Test refresh_status on pending job stays pending."""
    job = FineTuningJob()
    status = job.refresh_status()
    assert status == "pending"


# ---------------------------------------------------------------------------
# Evaluator (simple metric-function based)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_evaluator_exact_match():
    """Test Evaluator with exact_match_metric."""
    evaluator = Evaluator(metrics={"EM": exact_match_metric})
    results = evaluator.evaluate(["hello ", "world"], ["hello", "world"])
    assert results["EM"] == 1.0


@pytest.mark.unit
def test_evaluator_exact_match_mismatch():
    """Test Evaluator with mismatched predictions."""
    evaluator = Evaluator(metrics={"EM": exact_match_metric})
    results = evaluator.evaluate(["a"], ["b"])
    assert results["EM"] == 0.0


@pytest.mark.unit
def test_evaluator_length_ratio():
    """Test Evaluator with length_ratio_metric."""
    evaluator = Evaluator(metrics={"LR": length_ratio_metric})
    results = evaluator.evaluate(["hello"], ["hello"])
    assert results["LR"] == 1.0


@pytest.mark.unit
def test_evaluator_handles_metric_errors():
    """Test Evaluator handles metric functions that raise."""
    def bad_metric(preds, refs):
        raise RuntimeError("boom")

    evaluator = Evaluator(metrics={"bad": bad_metric})
    results = evaluator.evaluate(["a"], ["b"])
    assert results["bad"] == 0.0


# ---------------------------------------------------------------------------
# Metric classes (evaluation submodule)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_accuracy_metric():
    """Test AccuracyMetric computation."""
    metric = AccuracyMetric()
    assert metric.name == "accuracy"
    score = metric.compute([1, 0, 1, 0], [1, 0, 0, 0])
    assert score == 0.75


@pytest.mark.unit
def test_accuracy_metric_empty():
    """Test AccuracyMetric with empty lists."""
    metric = AccuracyMetric()
    assert metric.compute([], []) == 0.0


@pytest.mark.unit
def test_precision_metric():
    """Test PrecisionMetric computation."""
    metric = PrecisionMetric(positive_class=1)
    # y_true=[1,0,1,0], y_pred=[1,1,0,0] -> TP=1, FP=1 -> precision=0.5
    score = metric.compute([1, 0, 1, 0], [1, 1, 0, 0])
    assert score == 0.5


@pytest.mark.unit
def test_precision_metric_no_positives():
    """Test PrecisionMetric when no positive predictions."""
    metric = PrecisionMetric(positive_class=1)
    score = metric.compute([1, 1], [0, 0])
    assert score == 0.0


@pytest.mark.unit
def test_recall_metric():
    """Test RecallMetric computation."""
    metric = RecallMetric(positive_class=1)
    # y_true=[1,0,1,0], y_pred=[1,1,0,0] -> TP=1, FN=1 -> recall=0.5
    score = metric.compute([1, 0, 1, 0], [1, 1, 0, 0])
    assert score == 0.5


@pytest.mark.unit
def test_f1_metric():
    """Test F1Metric computation."""
    metric = F1Metric(positive_class=1)
    # precision=0.5, recall=0.5 -> F1=0.5
    score = metric.compute([1, 0, 1, 0], [1, 1, 0, 0])
    assert score == 0.5


@pytest.mark.unit
def test_f1_metric_perfect():
    """Test F1Metric with perfect predictions."""
    metric = F1Metric(positive_class=1)
    score = metric.compute([1, 0, 1, 0], [1, 0, 1, 0])
    assert score == 1.0


@pytest.mark.unit
def test_mse_metric():
    """Test MSEMetric computation."""
    metric = MSEMetric()
    # (1-2)^2 + (3-3)^2 = 1, MSE = 0.5
    score = metric.compute([1.0, 3.0], [2.0, 3.0])
    assert abs(score - 0.5) < 1e-9


@pytest.mark.unit
def test_mae_metric():
    """Test MAEMetric computation."""
    metric = MAEMetric()
    score = metric.compute([1.0, 3.0], [2.0, 5.0])
    assert abs(score - 1.5) < 1e-9


@pytest.mark.unit
def test_rmse_metric():
    """Test RMSEMetric computation."""
    metric = RMSEMetric()
    score = metric.compute([1.0, 3.0], [2.0, 3.0])
    expected = math.sqrt(0.5)
    assert abs(score - expected) < 1e-9


@pytest.mark.unit
def test_r2_metric_perfect():
    """Test R2Metric with perfect predictions."""
    metric = R2Metric()
    score = metric.compute([1.0, 2.0, 3.0], [1.0, 2.0, 3.0])
    assert abs(score - 1.0) < 1e-9


@pytest.mark.unit
def test_r2_metric_poor():
    """Test R2Metric with constant predictions."""
    metric = R2Metric()
    score = metric.compute([1.0, 2.0, 3.0], [2.0, 2.0, 2.0])
    assert score == 0.0


@pytest.mark.unit
def test_auc_roc_metric():
    """Test AUCROCMetric with separated scores."""
    metric = AUCROCMetric()
    # Perfect separation: all positives scored higher
    y_true = [1, 1, 0, 0]
    y_scores = [0.9, 0.8, 0.3, 0.1]
    score = metric.compute(y_true, y_scores)
    assert score == 1.0


@pytest.mark.unit
def test_auc_roc_metric_mixed():
    """Test AUCROCMetric with mixed ordering gives score between 0 and 1."""
    metric = AUCROCMetric()
    # Scores that don't perfectly separate classes
    y_true = [1, 0, 1, 0]
    y_scores = [0.6, 0.7, 0.4, 0.3]
    score = metric.compute(y_true, y_scores)
    assert 0.0 <= score <= 1.0


# ---------------------------------------------------------------------------
# ConfusionMatrix
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_confusion_matrix_binary():
    """Test ConfusionMatrix for binary classification."""
    y_true = [1, 1, 0, 0]
    y_pred = [1, 0, 0, 1]
    cm = ConfusionMatrix(y_true, y_pred)
    assert cm.get_cell(1, 1) == 1  # TP
    assert cm.get_cell(1, 0) == 1  # FN
    assert cm.get_cell(0, 0) == 1  # TN
    assert cm.get_cell(0, 1) == 1  # FP


@pytest.mark.unit
def test_confusion_matrix_to_dict():
    """Test ConfusionMatrix serialization."""
    cm = ConfusionMatrix([0, 1], [0, 1])
    d = cm.to_dict()
    assert "classes" in d
    assert "matrix" in d


@pytest.mark.unit
def test_confusion_matrix_str():
    """Test ConfusionMatrix string representation."""
    cm = ConfusionMatrix([0, 1], [0, 1])
    s = str(cm)
    assert "Confusion Matrix" in s


# ---------------------------------------------------------------------------
# ModelEvaluator
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_model_evaluator_classification():
    """Test ModelEvaluator for binary classification."""
    evaluator = ModelEvaluator(TaskType.BINARY_CLASSIFICATION)
    result = evaluator.evaluate([1, 0, 1, 0], [1, 0, 0, 0])
    assert isinstance(result, EvaluationResult)
    assert "accuracy" in result.metrics
    assert result.metrics["accuracy"] == 0.75
    assert result.sample_count == 4


@pytest.mark.unit
def test_model_evaluator_regression():
    """Test ModelEvaluator for regression."""
    evaluator = ModelEvaluator(TaskType.REGRESSION)
    result = evaluator.evaluate([1.0, 2.0, 3.0], [1.0, 2.0, 3.0])
    assert "mse" in result.metrics
    assert result.metrics["mse"] == 0.0


@pytest.mark.unit
def test_model_evaluator_add_metric():
    """Test adding a custom metric to ModelEvaluator."""
    evaluator = ModelEvaluator(TaskType.REGRESSION)
    evaluator.add_metric(AccuracyMetric())
    result = evaluator.evaluate([1, 2, 3], [1, 2, 3])
    assert "accuracy" in result.metrics


@pytest.mark.unit
def test_evaluation_result_to_dict():
    """Test EvaluationResult serialization."""
    result = EvaluationResult(
        metrics={"accuracy": 0.95},
        task_type=TaskType.BINARY_CLASSIFICATION,
        sample_count=100,
    )
    d = result.to_dict()
    assert d["task_type"] == "binary_classification"
    assert d["sample_count"] == 100


# ---------------------------------------------------------------------------
# create_evaluator factory
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_create_evaluator_binary():
    """Test create_evaluator for binary classification."""
    evaluator = create_evaluator("binary")
    assert isinstance(evaluator, ModelEvaluator)
    assert evaluator.task_type == TaskType.BINARY_CLASSIFICATION


@pytest.mark.unit
def test_create_evaluator_regression():
    """Test create_evaluator for regression."""
    evaluator = create_evaluator("regression")
    assert evaluator.task_type == TaskType.REGRESSION


@pytest.mark.unit
def test_create_evaluator_unknown_raises():
    """Test create_evaluator raises on unknown task type."""
    with pytest.raises(ValueError, match="Unknown task type"):
        create_evaluator("unknown_task")


# ---------------------------------------------------------------------------
# Metric functions
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_exact_match_metric_empty():
    """Test exact_match_metric with empty lists."""
    assert exact_match_metric([], []) == 0.0


@pytest.mark.unit
def test_length_ratio_metric_equal():
    """Test length_ratio_metric with equal length strings."""
    ratio = length_ratio_metric(["abc", "de"], ["xyz", "fg"])
    assert ratio == 1.0


@pytest.mark.unit
def test_length_ratio_metric_empty_reference():
    """Test length_ratio_metric with empty reference strings."""
    ratio = length_ratio_metric(["", "abc"], ["", "abc"])
    # First pair: both empty -> 1.0; second pair: equal -> 1.0
    assert ratio == 1.0


# From test_coverage_boost_r6.py
class TestQualityEvaluation:
    def test_quality_dimension(self):
        from codomyrmex.model_ops.evaluation.quality import QualityDimension
        assert len(list(QualityDimension)) > 0

    def test_dimension_score(self):
        from codomyrmex.model_ops.evaluation.quality import DimensionScore, QualityDimension
        dim = list(QualityDimension)[0]
        s = DimensionScore(dimension=dim, score=0.95)
        assert s.score == 0.95

    def test_quality_analyzer(self):
        from codomyrmex.model_ops.evaluation.quality import QualityAnalyzer
        qa = QualityAnalyzer()
        assert qa is not None

    def test_quality_report(self):
        from codomyrmex.model_ops.evaluation.quality import QualityReport
        r = QualityReport(overall_score=0.9)
        assert r.overall_score == 0.9
