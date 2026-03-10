"""Tests for model_ops.evaluation.metrics — pure math, zero external deps.

Zero-mock policy: real class instantiation and arithmetic assertions only.
All expected values computed by hand for verifiability.
"""
import math

import pytest

from codomyrmex.model_ops.evaluation.metrics import (
    AccuracyMetric,
    AUCROCMetric,
    ConfusionMatrix,
    EvaluationResult,
    F1Metric,
    MAEMetric,
    ModelEvaluator,
    MSEMetric,
    PrecisionMetric,
    R2Metric,
    RecallMetric,
    RMSEMetric,
    TaskType,
    create_evaluator,
)

# ──────────────────────────── TaskType ────────────────────────────────────


class TestTaskType:
    def test_binary_classification_value(self):
        assert TaskType.BINARY_CLASSIFICATION.value == "binary_classification"

    def test_multiclass_classification_value(self):
        assert TaskType.MULTICLASS_CLASSIFICATION.value == "multiclass_classification"

    def test_regression_value(self):
        assert TaskType.REGRESSION.value == "regression"

    def test_three_task_types(self):
        assert len(TaskType) == 3


# ──────────────────────────── EvaluationResult ────────────────────────────


class TestEvaluationResult:
    def test_basic_construction(self):
        er = EvaluationResult(
            metrics={"accuracy": 0.9},
            task_type=TaskType.BINARY_CLASSIFICATION,
            sample_count=100,
        )
        assert er.metrics["accuracy"] == 0.9
        assert er.sample_count == 100
        assert er.task_type == TaskType.BINARY_CLASSIFICATION

    def test_to_dict_contains_required_keys(self):
        er = EvaluationResult(
            metrics={"mse": 0.1},
            task_type=TaskType.REGRESSION,
            sample_count=50,
        )
        d = er.to_dict()
        assert "metrics" in d
        assert "task_type" in d
        assert "sample_count" in d
        assert "metadata" in d

    def test_to_dict_task_type_is_string(self):
        er = EvaluationResult(
            metrics={}, task_type=TaskType.REGRESSION, sample_count=0
        )
        assert isinstance(er.to_dict()["task_type"], str)

    def test_metadata_defaults_empty(self):
        er = EvaluationResult(metrics={}, task_type=TaskType.REGRESSION, sample_count=0)
        assert er.metadata == {}

    def test_metadata_can_be_set(self):
        er = EvaluationResult(
            metrics={}, task_type=TaskType.REGRESSION, sample_count=0,
            metadata={"dataset": "test_set"},
        )
        assert er.metadata["dataset"] == "test_set"


# ──────────────────────────── AccuracyMetric ──────────────────────────────


class TestAccuracyMetric:
    def test_name(self):
        assert AccuracyMetric().name == "accuracy"

    def test_perfect_accuracy(self):
        y_true = [0, 1, 1, 0]
        y_pred = [0, 1, 1, 0]
        assert AccuracyMetric().compute(y_true, y_pred) == 1.0

    def test_zero_accuracy(self):
        y_true = [0, 1, 0, 1]
        y_pred = [1, 0, 1, 0]
        assert AccuracyMetric().compute(y_true, y_pred) == 0.0

    def test_partial_accuracy(self):
        y_true = [0, 1, 1, 0]
        y_pred = [0, 1, 0, 0]  # 3 correct out of 4
        assert AccuracyMetric().compute(y_true, y_pred) == 0.75

    def test_empty_returns_zero(self):
        assert AccuracyMetric().compute([], []) == 0.0

    def test_single_correct(self):
        assert AccuracyMetric().compute([1], [1]) == 1.0

    def test_single_incorrect(self):
        assert AccuracyMetric().compute([0], [1]) == 0.0

    def test_multiclass_accuracy(self):
        y_true = [0, 1, 2, 0, 1, 2]
        y_pred = [0, 1, 2, 0, 2, 1]  # 4 correct out of 6
        assert abs(AccuracyMetric().compute(y_true, y_pred) - 4 / 6) < 1e-9


# ──────────────────────────── PrecisionMetric ─────────────────────────────


class TestPrecisionMetric:
    def test_name(self):
        assert PrecisionMetric().name == "precision"

    def test_perfect_precision(self):
        y_true = [1, 1, 0]
        y_pred = [1, 1, 0]
        assert PrecisionMetric().compute(y_true, y_pred) == 1.0

    def test_zero_precision_no_positive_predictions(self):
        y_true = [1, 1]
        y_pred = [0, 0]
        assert PrecisionMetric().compute(y_true, y_pred) == 0.0

    def test_precision_with_false_positives(self):
        # tp=2, fp=1 → precision = 2/3
        y_true = [1, 1, 0]
        y_pred = [1, 1, 1]
        assert abs(PrecisionMetric().compute(y_true, y_pred) - 2 / 3) < 1e-9

    def test_custom_positive_class(self):
        y_true = ["cat", "cat", "dog"]
        y_pred = ["cat", "dog", "cat"]
        p = PrecisionMetric(positive_class="cat")
        # tp=1, fp=1 → precision = 0.5
        assert abs(p.compute(y_true, y_pred) - 0.5) < 1e-9

    def test_empty_returns_zero(self):
        assert PrecisionMetric().compute([], []) == 0.0


# ──────────────────────────── RecallMetric ────────────────────────────────


class TestRecallMetric:
    def test_name(self):
        assert RecallMetric().name == "recall"

    def test_perfect_recall(self):
        y_true = [1, 1, 0]
        y_pred = [1, 1, 0]
        assert RecallMetric().compute(y_true, y_pred) == 1.0

    def test_zero_recall_no_true_positives(self):
        y_true = [1, 1]
        y_pred = [0, 0]
        assert RecallMetric().compute(y_true, y_pred) == 0.0

    def test_recall_with_false_negatives(self):
        # tp=1, fn=1 → recall = 0.5
        y_true = [1, 1, 0]
        y_pred = [1, 0, 0]
        assert RecallMetric().compute(y_true, y_pred) == 0.5

    def test_no_positive_class_returns_zero(self):
        y_true = [0, 0, 0]
        y_pred = [0, 0, 0]
        assert RecallMetric().compute(y_true, y_pred) == 0.0

    def test_empty_returns_zero(self):
        assert RecallMetric().compute([], []) == 0.0


# ──────────────────────────── F1Metric ────────────────────────────────────


class TestF1Metric:
    def test_name(self):
        assert F1Metric().name == "f1"

    def test_perfect_f1(self):
        y_true = [1, 1, 0]
        y_pred = [1, 1, 0]
        assert F1Metric().compute(y_true, y_pred) == 1.0

    def test_zero_f1_no_predictions(self):
        y_true = [1, 1]
        y_pred = [0, 0]
        assert F1Metric().compute(y_true, y_pred) == 0.0

    def test_f1_harmonic_mean(self):
        # tp=2, fp=0, fn=1 → p=1.0, r=2/3 → f1 = 2*(1*2/3)/(1+2/3) = 4/5 = 0.8
        y_true = [1, 1, 1]
        y_pred = [1, 1, 0]
        expected = 2 * (1.0 * (2 / 3)) / (1.0 + 2 / 3)
        assert abs(F1Metric().compute(y_true, y_pred) - expected) < 1e-9

    def test_f1_balanced(self):
        # p=0.5, r=0.5 → f1=0.5
        y_true = [1, 1, 0, 0]
        y_pred = [1, 0, 1, 0]
        assert abs(F1Metric().compute(y_true, y_pred) - 0.5) < 1e-9


# ──────────────────────────── MSEMetric ───────────────────────────────────


class TestMSEMetric:
    def test_name(self):
        assert MSEMetric().name == "mse"

    def test_perfect_mse(self):
        y_true = [1.0, 2.0, 3.0]
        y_pred = [1.0, 2.0, 3.0]
        assert MSEMetric().compute(y_true, y_pred) == 0.0

    def test_mse_known_value(self):
        # errors = [1, 1, 1] → MSE = 1.0
        y_true = [0.0, 0.0, 0.0]
        y_pred = [1.0, 1.0, 1.0]
        assert MSEMetric().compute(y_true, y_pred) == 1.0

    def test_mse_mixed_errors(self):
        # errors^2 = [4, 1] → MSE = 2.5
        y_true = [0.0, 0.0]
        y_pred = [2.0, 1.0]
        assert abs(MSEMetric().compute(y_true, y_pred) - 2.5) < 1e-9

    def test_empty_returns_zero(self):
        assert MSEMetric().compute([], []) == 0.0


# ──────────────────────────── MAEMetric ───────────────────────────────────


class TestMAEMetric:
    def test_name(self):
        assert MAEMetric().name == "mae"

    def test_perfect_mae(self):
        assert MAEMetric().compute([1.0, 2.0], [1.0, 2.0]) == 0.0

    def test_mae_known_value(self):
        # |errors| = [2, 1] → MAE = 1.5
        y_true = [0.0, 0.0]
        y_pred = [2.0, 1.0]
        assert abs(MAEMetric().compute(y_true, y_pred) - 1.5) < 1e-9

    def test_mae_symmetry(self):
        # positive and negative errors should cancel in MAE (absolute values)
        y_true = [0.0, 0.0]
        y_pred = [1.0, -1.0]
        assert MAEMetric().compute(y_true, y_pred) == 1.0

    def test_empty_returns_zero(self):
        assert MAEMetric().compute([], []) == 0.0


# ──────────────────────────── RMSEMetric ──────────────────────────────────


class TestRMSEMetric:
    def test_name(self):
        assert RMSEMetric().name == "rmse"

    def test_perfect_rmse(self):
        assert RMSEMetric().compute([1.0, 2.0], [1.0, 2.0]) == 0.0

    def test_rmse_is_sqrt_of_mse(self):
        y_true = [0.0, 0.0, 0.0]
        y_pred = [1.0, 2.0, 3.0]
        mse = MSEMetric().compute(y_true, y_pred)
        rmse = RMSEMetric().compute(y_true, y_pred)
        assert abs(rmse - math.sqrt(mse)) < 1e-9

    def test_rmse_known_value(self):
        # errors^2 = [1, 1, 1, 1] → MSE=1, RMSE=1
        y_true = [0.0, 0.0, 0.0, 0.0]
        y_pred = [1.0, 1.0, 1.0, 1.0]
        assert abs(RMSEMetric().compute(y_true, y_pred) - 1.0) < 1e-9


# ──────────────────────────── R2Metric ────────────────────────────────────


class TestR2Metric:
    def test_name(self):
        assert R2Metric().name == "r2"

    def test_perfect_r2(self):
        y_true = [1.0, 2.0, 3.0]
        y_pred = [1.0, 2.0, 3.0]
        assert R2Metric().compute(y_true, y_pred) == 1.0

    def test_r2_zero_when_predicting_mean(self):
        y_true = [1.0, 2.0, 3.0]
        y_pred = [2.0, 2.0, 2.0]  # mean prediction
        assert abs(R2Metric().compute(y_true, y_pred) - 0.0) < 1e-9

    def test_r2_negative_for_worse_than_mean(self):
        y_true = [1.0, 2.0, 3.0]
        y_pred = [3.0, 2.0, 1.0]  # reversed
        assert R2Metric().compute(y_true, y_pred) < 0.0

    def test_r2_empty_returns_zero(self):
        assert R2Metric().compute([], []) == 0.0

    def test_r2_constant_true_returns_one(self):
        # ss_tot=0, ss_res=0 → 1.0
        y_true = [2.0, 2.0, 2.0]
        y_pred = [2.0, 2.0, 2.0]
        assert R2Metric().compute(y_true, y_pred) == 1.0

    def test_r2_constant_true_bad_pred_returns_zero(self):
        # ss_tot=0, ss_res!=0 → 0.0
        y_true = [2.0, 2.0, 2.0]
        y_pred = [3.0, 3.0, 3.0]
        assert R2Metric().compute(y_true, y_pred) == 0.0


# ──────────────────────────── AUCROCMetric ────────────────────────────────


class TestAUCROCMetric:
    def test_name(self):
        assert AUCROCMetric().name == "auc_roc"

    def test_perfect_auc(self):
        y_true = [0, 0, 1, 1]
        y_scores = [0.1, 0.2, 0.8, 0.9]  # perfect separation
        assert AUCROCMetric().compute(y_true, y_scores) == 1.0

    def test_random_auc_is_around_half(self):
        y_true = [0, 1, 0, 1]
        y_scores = [0.5, 0.5, 0.5, 0.5]  # all same → 0.5
        assert abs(AUCROCMetric().compute(y_true, y_scores) - 0.5) < 1e-9

    def test_no_positives_returns_zero(self):
        y_true = [0, 0, 0]
        y_scores = [0.1, 0.2, 0.3]
        assert AUCROCMetric().compute(y_true, y_scores) == 0.0

    def test_no_negatives_returns_zero(self):
        y_true = [1, 1, 1]
        y_scores = [0.7, 0.8, 0.9]
        assert AUCROCMetric().compute(y_true, y_scores) == 0.0


# ──────────────────────────── ConfusionMatrix ─────────────────────────────


class TestConfusionMatrix:
    def test_classes_sorted(self):
        cm = ConfusionMatrix([0, 1, 2], [0, 1, 2])
        assert cm.classes == [0, 1, 2]

    def test_perfect_prediction_diagonal(self):
        cm = ConfusionMatrix([0, 1], [0, 1])
        assert cm.get_cell(0, 0) == 1
        assert cm.get_cell(1, 1) == 1
        assert cm.get_cell(0, 1) == 0
        assert cm.get_cell(1, 0) == 0

    def test_all_wrong_fills_off_diagonal(self):
        cm = ConfusionMatrix([0, 0], [1, 1])
        assert cm.get_cell(0, 1) == 2
        assert cm.get_cell(0, 0) == 0

    def test_to_dict_has_classes_and_matrix(self):
        cm = ConfusionMatrix([0, 1], [0, 1])
        d = cm.to_dict()
        assert "classes" in d
        assert "matrix" in d

    def test_to_dict_matrix_shape(self):
        cm = ConfusionMatrix([0, 1, 2], [0, 1, 2])
        d = cm.to_dict()
        assert len(d["matrix"]) == 3
        assert all(len(row) == 3 for row in d["matrix"])

    def test_str_contains_confusion_matrix_header(self):
        cm = ConfusionMatrix([0, 1], [0, 1])
        s = str(cm)
        assert "Confusion Matrix" in s

    def test_missing_cell_returns_zero(self):
        cm = ConfusionMatrix([0], [0])
        assert cm.get_cell(1, 1) == 0  # class never seen


# ──────────────────────────── ModelEvaluator ──────────────────────────────


class TestModelEvaluator:
    def test_binary_classification_has_four_metrics(self):
        ev = ModelEvaluator(TaskType.BINARY_CLASSIFICATION)
        assert len(ev.metrics) == 4

    def test_regression_has_four_metrics(self):
        ev = ModelEvaluator(TaskType.REGRESSION)
        assert len(ev.metrics) == 4

    def test_binary_metrics_names(self):
        ev = ModelEvaluator(TaskType.BINARY_CLASSIFICATION)
        names = {m.name for m in ev.metrics}
        assert "accuracy" in names
        assert "precision" in names
        assert "recall" in names
        assert "f1" in names

    def test_regression_metrics_names(self):
        ev = ModelEvaluator(TaskType.REGRESSION)
        names = {m.name for m in ev.metrics}
        assert "mse" in names
        assert "mae" in names
        assert "rmse" in names
        assert "r2" in names

    def test_evaluate_returns_evaluation_result(self):
        ev = ModelEvaluator(TaskType.BINARY_CLASSIFICATION)
        result = ev.evaluate([0, 1, 1, 0], [0, 1, 1, 0])
        assert isinstance(result, EvaluationResult)

    def test_evaluate_sample_count(self):
        ev = ModelEvaluator(TaskType.BINARY_CLASSIFICATION)
        result = ev.evaluate([0, 1, 1, 0], [0, 1, 0, 0])
        assert result.sample_count == 4

    def test_evaluate_perfect_classification(self):
        ev = ModelEvaluator(TaskType.BINARY_CLASSIFICATION)
        result = ev.evaluate([0, 1, 0, 1], [0, 1, 0, 1])
        assert result.metrics["accuracy"] == 1.0

    def test_evaluate_regression(self):
        ev = ModelEvaluator(TaskType.REGRESSION)
        result = ev.evaluate([1.0, 2.0, 3.0], [1.0, 2.0, 3.0])
        assert result.metrics["mse"] == 0.0
        assert result.metrics["r2"] == 1.0

    def test_add_metric_increases_count(self):
        ev = ModelEvaluator(TaskType.BINARY_CLASSIFICATION)
        initial = len(ev.metrics)
        ev.add_metric(AUCROCMetric())
        assert len(ev.metrics) == initial + 1

    def test_evaluate_task_type_in_result(self):
        ev = ModelEvaluator(TaskType.REGRESSION)
        result = ev.evaluate([1.0], [1.0])
        assert result.task_type == TaskType.REGRESSION


# ──────────────────────────── create_evaluator ────────────────────────────


class TestCreateEvaluator:
    def test_binary_string(self):
        ev = create_evaluator("binary")
        assert ev.task_type == TaskType.BINARY_CLASSIFICATION

    def test_multiclass_string(self):
        ev = create_evaluator("multiclass")
        assert ev.task_type == TaskType.MULTICLASS_CLASSIFICATION

    def test_regression_string(self):
        ev = create_evaluator("regression")
        assert ev.task_type == TaskType.REGRESSION

    def test_invalid_raises_value_error(self):
        with pytest.raises(ValueError):
            create_evaluator("unknown_task")

    def test_returns_model_evaluator_instance(self):
        ev = create_evaluator("binary")
        assert isinstance(ev, ModelEvaluator)
