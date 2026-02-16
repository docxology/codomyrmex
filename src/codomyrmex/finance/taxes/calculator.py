"""Progressive tax calculation with bracket support and deductions.

Implements a standard progressive (marginal) tax system where different
portions of income are taxed at increasing rates.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# Default US-style federal brackets (simplified, 2024-era rates)
DEFAULT_BRACKETS: list[dict] = [
    {"min": 0, "max": 11_600, "rate": 0.10},
    {"min": 11_600, "max": 47_150, "rate": 0.12},
    {"min": 47_150, "max": 100_525, "rate": 0.22},
    {"min": 100_525, "max": 191_950, "rate": 0.24},
    {"min": 191_950, "max": 243_725, "rate": 0.32},
    {"min": 243_725, "max": 609_350, "rate": 0.35},
    {"min": 609_350, "max": float("inf"), "rate": 0.37},
]


class TaxError(Exception):
    """Raised on invalid tax calculation inputs."""


@dataclass
class TaxResult:
    """Result of a tax calculation.

    Attributes:
        gross_income: Income before deductions.
        taxable_income: Income after deductions.
        total_tax: Total tax owed.
        effective_rate: Overall effective tax rate (tax / gross_income).
        marginal_rate: The highest bracket rate applied.
        bracket_breakdown: Tax owed per bracket.
    """

    gross_income: float
    taxable_income: float
    total_tax: float
    effective_rate: float
    marginal_rate: float
    bracket_breakdown: list[dict] = field(default_factory=list)


class TaxCalculator:
    """Progressive tax calculator with bracket-based computation.

    Usage::

        calc = TaxCalculator()
        result = calc.calculate_tax(85_000)
        print(result.total_tax, result.effective_rate)
    """

    def __init__(self, brackets: Optional[list[dict]] = None) -> None:
        """Initialise with optional custom tax brackets.

        Each bracket dict must have ``min`` (float), ``max`` (float), and
        ``rate`` (float 0-1).  Brackets are sorted by ``min`` automatically.

        Args:
            brackets: Custom bracket definitions.  Defaults to simplified
                US federal brackets.
        """
        raw = brackets if brackets is not None else DEFAULT_BRACKETS
        # Validate and sort
        for b in raw:
            if not all(k in b for k in ("min", "max", "rate")):
                raise TaxError("Each bracket must have 'min', 'max', and 'rate' keys.")
            if b["rate"] < 0 or b["rate"] > 1:
                raise TaxError(f"Rate must be between 0 and 1, got {b['rate']}.")
        self.brackets: list[dict] = sorted(raw, key=lambda b: b["min"])

    def calculate_tax(self, income: float) -> TaxResult:
        """Calculate progressive tax on the given income.

        Args:
            income: Taxable income (must be >= 0).

        Returns:
            A :class:`TaxResult` with detailed breakdown.

        Raises:
            TaxError: If income is negative.
        """
        if income < 0:
            raise TaxError("Income must be non-negative.")

        total_tax = 0.0
        marginal_rate = 0.0
        breakdown: list[dict] = []

        remaining = income
        for bracket in self.brackets:
            if remaining <= 0:
                break
            bracket_min = bracket["min"]
            bracket_max = bracket["max"]
            rate = bracket["rate"]

            taxable_in_bracket = min(remaining, bracket_max - bracket_min)
            if taxable_in_bracket <= 0:
                continue

            tax_for_bracket = taxable_in_bracket * rate
            total_tax += tax_for_bracket
            marginal_rate = rate
            remaining -= taxable_in_bracket

            breakdown.append({
                "bracket_min": bracket_min,
                "bracket_max": bracket_max,
                "rate": rate,
                "taxable_amount": taxable_in_bracket,
                "tax": tax_for_bracket,
            })

        effective_rate = total_tax / income if income > 0 else 0.0

        return TaxResult(
            gross_income=income,
            taxable_income=income,
            total_tax=round(total_tax, 2),
            effective_rate=round(effective_rate, 6),
            marginal_rate=marginal_rate,
            bracket_breakdown=breakdown,
        )

    def apply_deductions(
        self,
        income: float,
        deductions: list[dict],
    ) -> float:
        """Apply deductions to gross income and return taxable income.

        Each deduction dict should have:
            - ``name`` (str): Label for the deduction.
            - ``amount`` (float): Dollar amount to deduct.
            - ``type`` (str, optional): ``"standard"`` or ``"itemized"``
              (default ``"itemized"``).

        The taxable income will never go below zero.

        Args:
            income: Gross income.
            deductions: List of deduction dicts.

        Returns:
            Adjusted taxable income.
        """
        if income < 0:
            raise TaxError("Income must be non-negative.")

        total_deduction = 0.0
        for ded in deductions:
            amount = float(ded.get("amount", 0))
            if amount < 0:
                raise TaxError(f"Deduction amount must be non-negative: {ded}")
            total_deduction += amount

        return max(0.0, income - total_deduction)
