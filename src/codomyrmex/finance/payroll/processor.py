"""Payroll processing with tax withholding, deductions, and pay-stub generation.

Calculates net pay from gross salary by applying federal tax (via
:class:`TaxCalculator`), social-security and medicare withholdings, and any
employee-specific deductions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import ROUND_HALF_EVEN, Decimal

from codomyrmex.finance.taxes.calculator import TaxCalculator, TaxResult

# Standard FICA rates (2024)
SOCIAL_SECURITY_RATE = Decimal("0.062")
SOCIAL_SECURITY_WAGE_BASE = Decimal("168600.00")
MEDICARE_RATE = Decimal("0.0145")


class PayrollError(Exception):
    """Raised on invalid payroll inputs."""


@dataclass
class PayStub:
    """A single pay-period earnings and withholding statement.

    Attributes:
        employee_name: Name of the employee.
        employee_id: Employee identifier.
        pay_period: Description such as ``"2024-01 monthly"``.
        gross_pay: Total pay before any deductions.
        federal_tax: Federal income tax withheld.
        social_security: Social Security withholding.
        medicare: Medicare withholding.
        other_deductions: dict of additional deduction names to amounts.
        net_pay: Take-home pay after all deductions.
        generated_at: Timestamp of stub generation.
    """

    employee_name: str
    employee_id: str
    pay_period: str
    gross_pay: Decimal
    federal_tax: Decimal
    social_security: Decimal
    medicare: Decimal
    other_deductions: dict[str, Decimal] = field(default_factory=dict)
    net_pay: Decimal = field(default_factory=lambda: Decimal("0.00"))
    generated_at: datetime = field(default_factory=datetime.now)


class PayrollProcessor:
    """Process payroll for employees.

    Usage::

        processor = PayrollProcessor()
        pay = processor.calculate_pay(8500, pay_period="monthly")
        print(pay)  # dict with gross, net, withholdings

        stub = processor.generate_pay_stub(
            employee={"name": "Alice", "id": "E001"},
            period={"label": "Jan 2024", "gross_salary": 8500},
        )
    """

    # Number of pay periods per year for each cadence
    PERIODS_PER_YEAR = {
        "weekly": 52,
        "biweekly": 26,
        "semimonthly": 24,
        "monthly": 12,
        "annual": 1,
    }

    def __init__(self, tax_calculator: TaxCalculator | None = None) -> None:
        """Initialise with an optional tax calculator.

        Args:
            tax_calculator: A :class:`TaxCalculator` instance.  If ``None``,
                a default calculator with standard US brackets is used.
        """
        self.tax_calculator = tax_calculator or TaxCalculator()

    def calculate_pay(
        self,
        gross_salary: Decimal | float,
        pay_period: str = "monthly",
    ) -> dict:
        """Calculate net pay and withholdings for a single pay period.

        Args:
            gross_salary: Gross pay for the period.
            pay_period: One of ``"weekly"``, ``"biweekly"``, ``"semimonthly"``,
                ``"monthly"``, or ``"annual"``.

        Returns:
            A dict with ``gross``, ``annualized``, ``federal_tax``,
            ``social_security``, ``medicare``, ``total_deductions``, and
            ``net_pay``.

        Raises:
            PayrollError: On invalid inputs.
        """
        gross_salary = Decimal(str(gross_salary)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_EVEN
        )
        if gross_salary < Decimal(0):
            raise PayrollError("Gross salary must be non-negative.")
        if pay_period not in self.PERIODS_PER_YEAR:
            raise PayrollError(
                f"Unknown pay_period '{pay_period}'. "
                f"Choose from: {', '.join(self.PERIODS_PER_YEAR)}"
            )

        periods = self.PERIODS_PER_YEAR[pay_period]
        annualized = gross_salary * periods

        # Federal tax (annualised then pro-rated back to period)
        tax_result: TaxResult = self.tax_calculator.calculate_tax(annualized)
        federal_tax_period = (tax_result.total_tax / periods).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_EVEN
        )

        # Social Security (capped at wage base)
        ss_taxable = min(gross_salary, (SOCIAL_SECURITY_WAGE_BASE / periods))
        social_security = (ss_taxable * SOCIAL_SECURITY_RATE).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_EVEN
        )

        # Medicare (no cap)
        medicare = (gross_salary * MEDICARE_RATE).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_EVEN
        )

        total_deductions = federal_tax_period + social_security + medicare
        net_pay = gross_salary - total_deductions

        return {
            "gross": gross_salary,
            "annualized": annualized,
            "federal_tax": federal_tax_period,
            "social_security": social_security,
            "medicare": medicare,
            "total_deductions": total_deductions,
            "net_pay": net_pay,
        }

    def generate_pay_stub(
        self,
        employee: dict,
        period: dict,
    ) -> PayStub:
        """Generate a detailed pay stub for an employee.

        Args:
            employee: dict with at least ``"name"`` (str) and ``"id"`` (str).
                May also include ``"deductions"`` -- a dict mapping deduction
                names to per-period amounts (e.g. ``{"401k": 500}``).
            period: dict with ``"label"`` (str, e.g. ``"Jan 2024"``) and
                ``"gross_salary"`` (float).  Optional ``"pay_period"``
                defaults to ``"monthly"``.

        Returns:
            A populated :class:`PayStub`.

        Raises:
            PayrollError: On missing or invalid fields.
        """
        name = employee.get("name")
        emp_id = employee.get("id")
        if not name or not emp_id:
            raise PayrollError("Employee must have 'name' and 'id'.")

        gross = Decimal(str(period.get("gross_salary", 0))).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_EVEN
        )
        label = period.get("label", "Unknown Period")
        cadence = period.get("pay_period", "monthly")

        pay = self.calculate_pay(gross, cadence)

        # Additional employee deductions (retirement, insurance, etc.)
        extra_deductions: dict[str, Decimal] = {}
        for ded_name, ded_amount in employee.get("deductions", {}).items():
            ded_amount = Decimal(str(ded_amount)).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_EVEN
            )
            extra_deductions[ded_name] = ded_amount

        total_extra = sum(extra_deductions.values(), Decimal("0.00"))
        net_pay = (pay["net_pay"] - total_extra).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_EVEN
        )

        return PayStub(
            employee_name=name,
            employee_id=emp_id,
            pay_period=f"{label} ({cadence})",
            gross_pay=gross,
            federal_tax=pay["federal_tax"],
            social_security=pay["social_security"],
            medicare=pay["medicare"],
            other_deductions=extra_deductions,
            net_pay=net_pay,
        )
