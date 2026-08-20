"""Trust Calibration and Outcome Evaluation Harness (R4).

Evaluates gate score and trust metric calibration against true observed outcomes,
computing Brier scores, Expected Calibration Error (ECE), reliability diagrams,
and Platt-style logistic probability mappings with formal missingness handling.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from codomyrmex.colony_kernel.research.metrics import (
    brier_score,
    confidence_interval,
    expected_calibration_error,
    log_loss,
    reliability_bins,
    selective_risk,
)


@dataclass(frozen=True)
class CalibrationRecord:
    """Single paired score-outcome observation with optional missingness indicator."""

    case_id: str
    predicted_score: float
    true_outcome: bool | None  # None indicates censored / missing outcome
    metadata: dict[str, Any]


@dataclass(frozen=True)
class TrustCalibrationReport:
    """Comprehensive trust calibration and uncertainty diagnostic report."""

    total_records: int
    evaluated_records: int
    missing_records: int
    missingness_rate: float
    brier_score: float
    expected_calibration_error: float
    log_loss_value: float
    reliability_diagram_bins: list[dict[str, Any]]
    selective_risk_coverage_50: float
    brier_ci_95: tuple[float, float]


class TrustCalibrationStudy:
    """Computes calibration diagnostics on attested outcome histories."""

    def __init__(self, records: Sequence[CalibrationRecord] | None = None) -> None:
        self.records: list[CalibrationRecord] = list(records) if records else []

    def add_record(
        self,
        case_id: str,
        predicted_score: float,
        true_outcome: bool | None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Add a score-outcome pair."""
        if not (0.0 <= predicted_score <= 1.0):
            raise ValueError(
                f"predicted_score must be in [0.0, 1.0], got {predicted_score}"
            )
        self.records.append(
            CalibrationRecord(
                case_id=case_id,
                predicted_score=predicted_score,
                true_outcome=true_outcome,
                metadata=metadata or {},
            )
        )

    def analyze_calibration(
        self,
        *,
        bins: int = 5,
        missing_policy: str = "complete_case",
    ) -> TrustCalibrationReport:
        """Run full calibration audit.

        Args:
            bins: Number of bins for reliability diagram / ECE.
            missing_policy: 'complete_case' drops missing, 'conservative' treats missing as failure (False).

        Returns:
            TrustCalibrationReport with all diagnostic metrics.
        """
        if not self.records:
            raise ValueError("Cannot analyze calibration on an empty record set")

        total = len(self.records)
        missing_cnt = sum(1 for r in self.records if r.true_outcome is None)
        missing_rate = missing_cnt / total

        valid_records: list[tuple[float, bool]] = []
        for r in self.records:
            if r.true_outcome is None:
                if missing_policy == "conservative":
                    valid_records.append((r.predicted_score, False))
                elif missing_policy == "complete_case":
                    continue
                else:
                    raise ValueError(f"Unknown missing_policy: {missing_policy}")
            else:
                valid_records.append((r.predicted_score, r.true_outcome))

        if not valid_records:
            raise ValueError(
                "No evaluable records remaining after missingness filtering"
            )

        scores = [s for s, _ in valid_records]
        outcomes = [o for _, o in valid_records]

        bs = brier_score(outcomes, scores)
        ece = expected_calibration_error(outcomes, scores, bins=bins)
        ll = log_loss(outcomes, scores)
        rel_bins = reliability_bins(outcomes, scores, bins=bins)
        sel_risk = selective_risk(outcomes, scores, coverage=0.5)

        # Compute descriptive bootstrap CI for Brier score
        brier_ci = confidence_interval(
            [float((s - float(o)) ** 2) for s, o in valid_records],
            confidence=0.95,
        )

        return TrustCalibrationReport(
            total_records=total,
            evaluated_records=len(valid_records),
            missing_records=missing_cnt,
            missingness_rate=missing_rate,
            brier_score=bs,
            expected_calibration_error=ece,
            log_loss_value=ll,
            reliability_diagram_bins=rel_bins,
            selective_risk_coverage_50=sel_risk.get("coverage", 0.0),
            brier_ci_95=brier_ci,
        )
