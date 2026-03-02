"""
Comprehensive unit tests for the Finance module — Zero-Mock compliant.
"""

from decimal import Decimal

import pytest

from codomyrmex.finance import (
    AccountType,
    Forecaster,
    Ledger,
    LedgerError,
    PayrollProcessor,
    TaxCalculator,
    TaxError,
)

# --- Ledger Tests ---

@pytest.mark.unit
class TestLedger:
    def test_ledger_initialization(self):
        ledger = Ledger("Test Ledger")
        assert ledger.name == "Test Ledger"
        assert len(ledger.accounts) == 0
        assert len(ledger.transactions) == 0

    def test_create_account_valid(self):
        ledger = Ledger()
        acc = ledger.create_account("Assets:Cash", AccountType.ASSET)
        assert acc.name == "Assets:Cash"
        assert acc.account_type == AccountType.ASSET
        assert acc.balance == Decimal("0.00")

    def test_create_account_invalid_name(self):
        ledger = Ledger()
        with pytest.raises(LedgerError, match="must follow 'Category:Subcategory'"):
            ledger.create_account("Cash", AccountType.ASSET)

    def test_create_account_duplicate(self):
        ledger = Ledger()
        ledger.create_account("Assets:Cash", AccountType.ASSET)
        with pytest.raises(LedgerError, match="already exists"):
            ledger.create_account("Assets:Cash", AccountType.ASSET)

    def test_post_transaction_balanced(self):
        ledger = Ledger()
        cash = ledger.create_account("Assets:Cash", AccountType.ASSET)
        revenue = ledger.create_account("Revenue:Sales", AccountType.REVENUE)

        ledger.post_transaction([
            {"account_id": cash.id, "amount": Decimal("100.00")},
            {"account_id": revenue.id, "amount": Decimal("-100.00")}
        ], description="Sale")

        assert ledger.get_balance(cash.id) == Decimal("100.00")
        assert ledger.get_balance(revenue.id) == Decimal("100.00")
        assert len(ledger.transactions) == 1

    def test_post_transaction_unbalanced(self):
        ledger = Ledger()
        cash = ledger.create_account("Assets:Cash", AccountType.ASSET)
        with pytest.raises(LedgerError, match="does not balance"):
            ledger.post_transaction([
                {"account_id": cash.id, "amount": Decimal("100.00")}
            ], description="Unbalanced")

    def test_account_frozen(self):
        ledger = Ledger()
        cash = ledger.create_account("Assets:Cash", AccountType.ASSET)
        revenue = ledger.create_account("Revenue:Sales", AccountType.REVENUE)
        cash.frozen = True

        with pytest.raises(LedgerError, match="is frozen"):
            ledger.post_transaction([
                {"account_id": cash.id, "amount": Decimal("100.00")},
                {"account_id": revenue.id, "amount": Decimal("-100.00")}
            ], description="Sale")

    def test_trial_balance(self):
        ledger = Ledger()
        bank = ledger.create_account("Assets:Bank", AccountType.ASSET)
        equity = ledger.create_account("Equity:Capital", AccountType.EQUITY)

        ledger.post_transaction([
            {"account_id": bank.id, "amount": Decimal("1000.00")},
            {"account_id": equity.id, "amount": Decimal("-1000.00")}
        ], description="Investment")

        tb = ledger.trial_balance()
        assert tb["balanced"] is True
        assert tb["total_debits"] == Decimal("1000.00")
        assert tb["total_credits"] == Decimal("1000.00")

# --- Tax Tests ---

@pytest.mark.unit
class TestTaxes:
    def test_calculate_tax_us(self):
        calc = TaxCalculator(jurisdiction="US")
        # 50,000 income
        # Bracket 1: 11600 * 0.10 = 1160
        # Bracket 2: (47150 - 11600) * 0.12 = 35550 * 0.12 = 4266
        # Bracket 3: (50000 - 47150) * 0.22 = 2850 * 0.22 = 627
        # Total = 1160 + 4266 + 627 = 6053
        result = calc.calculate_tax(50000)
        assert result.total_tax == Decimal("6053.00")
        assert result.effective_rate == Decimal("0.121060")

    def test_calculate_tax_uk(self):
        calc = TaxCalculator(jurisdiction="UK")
        # 20,000 income
        # Bracket 1: 12570 * 0 = 0
        # Bracket 2: (20000 - 12570) * 0.20 = 7430 * 0.20 = 1486
        result = calc.calculate_tax(20000)
        assert result.total_tax == Decimal("1486.00")

    def test_unsupported_jurisdiction(self):
        with pytest.raises(TaxError, match="Unsupported jurisdiction"):
            TaxCalculator(jurisdiction="FR")

# --- Payroll Tests ---

@pytest.mark.unit
class TestPayroll:
    def test_calculate_pay_monthly(self):
        processor = PayrollProcessor()
        # Gross 5000 monthly
        pay = processor.calculate_pay(5000, pay_period="monthly")
        assert pay["gross"] == Decimal("5000.00")
        assert pay["social_security"] == Decimal("310.00") # 5000 * 0.062
        assert pay["medicare"] == Decimal("72.50") # 5000 * 0.0145
        assert pay["net_pay"] < Decimal("5000.00")

    def test_generate_pay_stub(self):
        processor = PayrollProcessor()
        employee = {"name": "Alice", "id": "E001", "deductions": {"Health": 100}}
        period = {"label": "Jan 2024", "gross_salary": 5000}
        stub = processor.generate_pay_stub(employee, period)
        assert stub.employee_name == "Alice"
        assert stub.other_deductions["Health"] == Decimal("100.00")
        # Net pay should be reduced by Health deduction
        pay = processor.calculate_pay(5000)
        assert stub.net_pay == pay["net_pay"] - Decimal("100.00")

# --- Forecasting Tests ---

@pytest.mark.unit
class TestForecasting:
    def test_linear_trend(self):
        # Perfectly linear: y = 10x + 100
        data = [100, 110, 120, 130, 140]
        fc = Forecaster(data)
        trend = fc.linear_trend()
        assert trend["slope"] == Decimal("10")
        assert trend["intercept"] == Decimal("100")
        assert trend["r_squared"] == Decimal("1.0")

    def test_monte_carlo_projection(self):
        data = [100, 110, 105, 120, 130]
        fc = Forecaster(data)
        proj = fc.project(periods=3)
        assert len(proj["projections"]) == 3
        # Should roughly follow the trend
        assert proj["projections"][0] > 100

    def test_risk_metrics(self):
        fc = Forecaster()
        portfolio = {
            "positions": [{"quantity": 10, "cost_basis": 100, "current_price": 150}]
        }
        risk = fc.risk_metrics(portfolio)
        assert risk["total_value"] == Decimal("1500.00")
        assert risk["total_pnl"] == Decimal("500.00")
        assert risk["var_95"] > 0

    def test_moving_average(self):
        fc = Forecaster([100, 110, 120])
        ma = fc.moving_average(window=2)
        assert ma == [Decimal("105"), Decimal("115")]

    def test_exponential_smoothing(self):
        fc = Forecaster([100, 110])
        # s0 = 100
        # s1 = 0.3 * 110 + 0.7 * 100 = 33 + 70 = 103
        smoothed = fc.exponential_smoothing(alpha=0.3)
        assert smoothed == [Decimal("100"), Decimal("103")]
