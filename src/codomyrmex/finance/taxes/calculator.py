"""Progressive tax calculation with bracket support and deductions.

Implements a standard progressive (marginal) tax system where different
portions of income are taxed at increasing rates.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import ROUND_HALF_EVEN, Decimal

# Default US-style federal brackets (simplified, 2024-era rates)
US_FEDERAL_2024: list[dict] = [
    {"min": Decimal("0"), "max": Decimal("11600"), "rate": Decimal("0.10")},
    {"min": Decimal("11600"), "max": Decimal("47150"), "rate": Decimal("0.12")},
    {"min": Decimal("47150"), "max": Decimal("100525"), "rate": Decimal("0.22")},
    {"min": Decimal("100525"), "max": Decimal("191950"), "rate": Decimal("0.24")},
    {"min": Decimal("191950"), "max": Decimal("243725"), "rate": Decimal("0.32")},
    {"min": Decimal("243725"), "max": Decimal("609350"), "rate": Decimal("0.35")},
    {"min": Decimal("609350"), "max": Decimal("Infinity"), "rate": Decimal("0.37")},
]

JURISDICTIONS: dict[str, list[dict]] = {
    "US": US_FEDERAL_2024,
    "UK": [  # Simplified UK 2024/25
        {"min": Decimal("0"), "max": Decimal("12570"), "rate": Decimal("0.00")},
        {"min": Decimal("12570"), "max": Decimal("50270"), "rate": Decimal("0.20")},
        {"min": Decimal("50270"), "max": Decimal("125140"), "rate": Decimal("0.40")},
        {"min": Decimal("125140"), "max": Decimal("Infinity"), "rate": Decimal("0.45")},
    ],
}


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

    gross_income: Decimal
    taxable_income: Decimal
    total_tax: Decimal
    effective_rate: Decimal
    marginal_rate: Decimal
    bracket_breakdown: list[dict] = field(default_factory=list)


class TaxCalculator:
    """Progressive tax calculator with bracket-based computation.

    Usage::

        calc = TaxCalculator(jurisdiction="US")
        result = calc.calculate_tax(85_000)
        print(result.total_tax, result.effective_rate)
    """

    def __init__(
        self,
        jurisdiction: str = "US",
        brackets: list[dict] | None = None,
    ) -> None:
        """Initialise with optional custom tax brackets or jurisdiction.

        Each bracket dict must have ``min``, ``max``, and ``rate``.
        Brackets are sorted by ``min`` automatically.

        Args:
            jurisdiction: Jurisdiction code (e.g., "US", "UK").
            brackets: Custom bracket definitions. If provided, overrides jurisdiction.
        """
        if brackets is not None:
            raw = brackets
        elif jurisdiction in JURISDICTIONS:
            raw = JURISDICTIONS[jurisdiction]
        else:
            raise TaxError(f"Unsupported jurisdiction: {jurisdiction}")

        # Validate and sort
        for b in raw:
            if not all(k in b for k in ("min", "max", "rate")):
                raise TaxError("Each bracket must have 'min', 'max', and 'rate' keys.")
            if b["rate"] < 0 or b["rate"] > 1:
                raise TaxError(f"Rate must be between 0 and 1, got {b['rate']}.")
        self.brackets: list[dict] = sorted(raw, key=lambda b: b["min"])

    @staticmethod
    def supported_jurisdictions() -> list[str]:
        """Return list of supported jurisdiction codes."""
        return list(JURISDICTIONS.keys())

    def calculate_tax(self, income: Decimal | float) -> TaxResult:
        """Calculate progressive tax on the given income.

        Args:
            income: Taxable income (must be >= 0).

        Returns:
            A :class:`TaxResult` with detailed breakdown.

        Raises:
            TaxError: If income is negative.
        """
        income = Decimal(str(income)).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
        if income < Decimal("0"):
            raise TaxError("Income must be non-negative.")

        total_tax = Decimal("0.00")
        marginal_rate = Decimal("0.00")
        breakdown: list[dict] = []

        remaining = income
        for bracket in self.brackets:
            if remaining <= Decimal("0"):
                break
            bracket_min = bracket["min"]
            bracket_max = bracket["max"]
            rate = bracket["rate"]

            taxable_in_bracket = min(remaining, bracket_max - bracket_min)
            if taxable_in_bracket <= Decimal("0"):
                continue

            tax_for_bracket = (taxable_in_bracket * rate).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_EVEN
            )
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

        effective_rate = (
            (total_tax / income).quantize(Decimal("0.000001"), rounding=ROUND_HALF_EVEN)
            if income > 0
            else Decimal("0.000000")
        )

        return TaxResult(
            gross_income=income,
            taxable_income=income,
            total_tax=total_tax,
            effective_rate=effective_rate,
            marginal_rate=marginal_rate,
            bracket_breakdown=breakdown,
        )

    def apply_deductions(
        self,
        income: Decimal | float,
        deductions: list[dict],
    ) -> Decimal:
        """Apply deductions to gross income and return taxable income.

        Each deduction dict should have:
            - ``name`` (str): Label for the deduction.
            - ``amount`` (float | Decimal): Dollar amount to deduct.
            - ``type`` (str, optional): ``"standard"`` or ``"itemized"``
              (default ``"itemized"``).

        The taxable income will never go below zero.

        Args:
            income: Gross income.
            deductions: List of deduction dicts.

        Returns:
            Adjusted taxable income.
        """
        income = Decimal(str(income)).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
        if income < Decimal("0"):
            raise TaxError("Income must be non-negative.")

        total_deduction = Decimal("0.00")
        for ded in deductions:
            amount = Decimal(str(ded.get("amount", 0))).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_EVEN
            )
            if amount < Decimal("0"):
                raise TaxError(f"Deduction amount must be non-negative: {ded}")
            total_deduction += amount

        return max(Decimal("0.00"), income - total_deduction)
