"""Tests for Trust Calibration Study Harness (R4)."""

from __future__ import annotations

import pytest

from codomyrmex.colony_kernel.research.calibration_study import (
    CalibrationRecord,
    TrustCalibrationReport,
    TrustCalibrationStudy,
)


def test_trust_calibration_analysis_complete_case() -> None:
    study = TrustCalibrationStudy()
    # Add perfectly calibrated instances
    study.add_record("c1", 0.9, True)
    study.add_record("c2", 0.8, True)
    study.add_record("c3", 0.2, False)
    study.add_record("c4", 0.1, False)
    study.add_record("c5", 0.7, None)  # Censored / missing

    report = study.analyze_calibration(bins=2, missing_policy="complete_case")

    assert isinstance(report, TrustCalibrationReport)
    assert report.total_records == 5
    assert report.evaluated_records == 4
    assert report.missing_records == 1
    assert report.missingness_rate == 0.2
    assert report.brier_score < 0.1
    assert len(report.reliability_diagram_bins) > 0


def test_trust_calibration_analysis_conservative_missingness() -> None:
    study = TrustCalibrationStudy()
    study.add_record("c1", 0.9, True)
    study.add_record("c2", 0.8, None)  # Treated as False under conservative

    report = study.analyze_calibration(bins=2, missing_policy="conservative")
    assert report.evaluated_records == 2
    assert report.missing_records == 1


def test_trust_calibration_validation_and_errors() -> None:
    study = TrustCalibrationStudy()
    with pytest.raises(ValueError, match="empty"):
        study.analyze_calibration()

    with pytest.raises(ValueError, match="predicted_score"):
        study.add_record("bad", 1.5, True)

    for non_finite in (float("nan"), float("inf"), float("-inf")):
        with pytest.raises(ValueError, match="predicted_score"):
            study.add_record("non-finite", non_finite, True)
