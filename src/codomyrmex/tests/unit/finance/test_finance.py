"""Tests for the finance module.

Tests cover:
- Module import
- AccountType enum values
- Account creation and repr
- Ledger account creation and duplicate detection
- Transaction posting and balance validation
- Balance enforcement (debits must equal credits)
- Trial balance verification
- Balance sheet generation
- Income statement generation
- Transaction is_balanced property
- Forecaster: moving average, exponential smoothing, linear trend
- Forecaster: forecast method dispatch
- TaxCalculator: progressive bracket calculation
- TaxCalculator: deductions
- TaxCalculator: edge cases
"""

import pytest

from codomyrmex.finance.ledger import (
    Account,
    AccountType,
    Ledger,
    LedgerError,
    Transaction,
    TransactionEntry,
)
from codomyrmex.finance.forecasting.forecast import Forecaster, ForecastError
from codomyrmex.finance.taxes.calculator import TaxCalculator, TaxError, TaxResult


# ======================================================================
# Module & AccountType tests
# ======================================================================

@pytest.mark.unit
def test_module_import():
    """finance module is importable."""
    from codomyrmex import finance
    assert finance is not None


@pytest.mark.unit
def test_account_type_enum_values():
    """AccountType enum has five standard types with string values."""
    assert AccountType.ASSET.value == "asset"
    assert AccountType.LIABILITY.value == "liability"
    assert AccountType.EQUITY.value == "equity"
    assert AccountType.REVENUE.value == "revenue"
    assert AccountType.EXPENSE.value == "expense"


@pytest.mark.unit
def test_account_type_enum_count():
    """AccountType has exactly five members."""
    assert len(list(AccountType)) == 5


# ======================================================================
# Ledger account management tests
# ======================================================================

@pytest.mark.unit
def test_ledger_create_account():
    """Ledger.create_account registers a new account."""
    ledger = Ledger()
    acct = ledger.create_account("Cash", AccountType.ASSET)
    assert acct.name == "Cash"
    assert acct.account_type == AccountType.ASSET
    assert acct.balance == 0.0
    assert acct.id in ledger.accounts


@pytest.mark.unit
def test_ledger_duplicate_account_raises():
    """Ledger raises LedgerError on duplicate account name."""
    ledger = Ledger()
    ledger.create_account("Cash", AccountType.ASSET)
    with pytest.raises(LedgerError, match="already exists"):
        ledger.create_account("Cash", AccountType.ASSET)


@pytest.mark.unit
def test_ledger_create_multiple_accounts():
    """Ledger can hold multiple accounts of different types."""
    ledger = Ledger()
    cash = ledger.create_account("Cash", AccountType.ASSET)
    rev = ledger.create_account("Revenue", AccountType.REVENUE)
    exp = ledger.create_account("Expenses", AccountType.EXPENSE)
    assert len(ledger.accounts) == 3
    assert cash.account_type == AccountType.ASSET
    assert rev.account_type == AccountType.REVENUE
    assert exp.account_type == AccountType.EXPENSE


@pytest.mark.unit
def test_account_repr():
    """Account repr includes name, type, and balance."""
    acct = Account(id="x", name="Revenue", account_type=AccountType.REVENUE, balance=500.0)
    r = repr(acct)
    assert "Revenue" in r
    assert "revenue" in r
    assert "500.00" in r


# ======================================================================
# Transaction posting tests
# ======================================================================

@pytest.mark.unit
def test_ledger_post_transaction():
    """Ledger posts a balanced transaction and updates balances."""
    ledger = Ledger()
    cash = ledger.create_account("Cash", AccountType.ASSET)
    rev = ledger.create_account("Revenue", AccountType.REVENUE)

    txn = ledger.post_transaction(
        [
            {"account_id": cash.id, "amount": 1000.0},
            {"account_id": rev.id, "amount": -1000.0},
        ],
        description="Sale proceeds",
    )

    assert isinstance(txn, Transaction)
    assert ledger.get_balance(cash.id) == pytest.approx(1000.0)
    assert ledger.get_balance(rev.id) == pytest.approx(1000.0)


@pytest.mark.unit
def test_ledger_post_unbalanced_transaction_raises():
    """Ledger raises LedgerError when entries do not balance."""
    ledger = Ledger()
    cash = ledger.create_account("Cash", AccountType.ASSET)
    rev = ledger.create_account("Revenue", AccountType.REVENUE)

    with pytest.raises(LedgerError, match="does not balance"):
        ledger.post_transaction(
            [
                {"account_id": cash.id, "amount": 1000.0},
                {"account_id": rev.id, "amount": -500.0},
            ],
            description="Unbalanced",
        )


@pytest.mark.unit
def test_ledger_post_transaction_nonexistent_account_raises():
    """Posting to a nonexistent account raises LedgerError."""
    ledger = Ledger()
    cash = ledger.create_account("Cash", AccountType.ASSET)

    with pytest.raises(LedgerError, match="not found"):
        ledger.post_transaction(
            [
                {"account_id": cash.id, "amount": 100.0},
                {"account_id": "nonexistent", "amount": -100.0},
            ],
            description="Bad transaction",
        )


@pytest.mark.unit
def test_ledger_post_empty_entries_raises():
    """Posting a transaction with no entries raises LedgerError."""
    ledger = Ledger()
    with pytest.raises(LedgerError, match="at least one entry"):
        ledger.post_transaction([], description="Empty")


@pytest.mark.unit
def test_ledger_multiple_transactions_accumulate():
    """Multiple transactions accumulate balances."""
    ledger = Ledger()
    cash = ledger.create_account("Cash", AccountType.ASSET)
    rev = ledger.create_account("Revenue", AccountType.REVENUE)
    for i in range(5):
        ledger.post_transaction(
            [
                {"account_id": cash.id, "amount": 100.0},
                {"account_id": rev.id, "amount": -100.0},
            ],
            description=f"Sale {i}",
        )
    assert ledger.get_balance(cash.id) == pytest.approx(500.0)
    assert ledger.get_balance(rev.id) == pytest.approx(500.0)


@pytest.mark.unit
def test_ledger_expense_transaction():
    """Recording an expense: debit expense, credit cash."""
    ledger = Ledger()
    cash = ledger.create_account("Cash", AccountType.ASSET)
    equity = ledger.create_account("Capital", AccountType.EQUITY)
    expense = ledger.create_account("Office Supplies", AccountType.EXPENSE)

    # Fund cash
    ledger.post_transaction(
        [
            {"account_id": cash.id, "amount": 5000.0},
            {"account_id": equity.id, "amount": -5000.0},
        ],
        description="Initial funding",
    )

    # Record expense
    ledger.post_transaction(
        [
            {"account_id": expense.id, "amount": 200.0},
            {"account_id": cash.id, "amount": -200.0},
        ],
        description="Bought supplies",
    )

    assert ledger.get_balance(expense.id) == pytest.approx(200.0)
    assert ledger.get_balance(cash.id) == pytest.approx(4800.0)


@pytest.mark.unit
def test_ledger_get_balance_nonexistent_raises():
    """get_balance for unknown account raises LedgerError."""
    ledger = Ledger()
    with pytest.raises(LedgerError, match="not found"):
        ledger.get_balance("no-such-id")


# ======================================================================
# Transaction dataclass tests
# ======================================================================

@pytest.mark.unit
def test_transaction_is_balanced():
    """Transaction.is_balanced returns True when entries sum to zero."""
    txn = Transaction(
        id="tx1",
        entries=[
            TransactionEntry(account_id="a", amount=100.0),
            TransactionEntry(account_id="b", amount=-100.0),
        ],
        description="Balanced",
    )
    assert txn.is_balanced is True


@pytest.mark.unit
def test_transaction_is_not_balanced():
    """Transaction.is_balanced returns False when entries do not sum to zero."""
    txn = Transaction(
        id="tx2",
        entries=[
            TransactionEntry(account_id="a", amount=100.0),
            TransactionEntry(account_id="b", amount=-50.0),
        ],
        description="Unbalanced",
    )
    assert txn.is_balanced is False


# ======================================================================
# Trial balance and financial statements
# ======================================================================

@pytest.mark.unit
def test_ledger_trial_balance_empty():
    """Trial balance on empty ledger is balanced."""
    ledger = Ledger()
    tb = ledger.trial_balance()
    assert tb["balanced"] is True
    assert tb["total_debits"] == 0.0
    assert tb["total_credits"] == 0.0


@pytest.mark.unit
def test_ledger_trial_balance_after_transactions():
    """Trial balance is balanced after posting balanced transactions."""
    ledger = Ledger()
    cash = ledger.create_account("Cash", AccountType.ASSET)
    rev = ledger.create_account("Revenue", AccountType.REVENUE)
    ledger.post_transaction(
        [
            {"account_id": cash.id, "amount": 500.0},
            {"account_id": rev.id, "amount": -500.0},
        ],
        description="Sale",
    )
    tb = ledger.trial_balance()
    assert tb["balanced"] is True
    assert tb["total_debits"] == pytest.approx(500.0)
    assert tb["total_credits"] == pytest.approx(500.0)


@pytest.mark.unit
def test_ledger_balance_sheet():
    """Balance sheet categorizes accounts and computes totals."""
    ledger = Ledger()
    cash = ledger.create_account("Cash", AccountType.ASSET)
    equity = ledger.create_account("Capital", AccountType.EQUITY)
    ledger.post_transaction(
        [
            {"account_id": cash.id, "amount": 10000.0},
            {"account_id": equity.id, "amount": -10000.0},
        ],
        description="Investment",
    )
    bs = ledger.get_balance_sheet()
    assert "Cash" in bs["assets"]
    assert "Capital" in bs["equity"]
    assert bs["total_assets"] == pytest.approx(10000.0)
    assert bs["total_equity"] == pytest.approx(10000.0)
    assert bs["balanced"] is True


@pytest.mark.unit
def test_ledger_income_statement():
    """Income statement computes revenue, expenses, and net income."""
    ledger = Ledger()
    cash = ledger.create_account("Cash", AccountType.ASSET)
    rev = ledger.create_account("Sales", AccountType.REVENUE)
    exp = ledger.create_account("Rent", AccountType.EXPENSE)

    ledger.post_transaction(
        [{"account_id": cash.id, "amount": 5000.0}, {"account_id": rev.id, "amount": -5000.0}],
        description="Revenue",
    )
    ledger.post_transaction(
        [{"account_id": exp.id, "amount": 1000.0}, {"account_id": cash.id, "amount": -1000.0}],
        description="Rent payment",
    )

    stmt = ledger.get_income_statement()
    assert stmt["total_revenue"] == pytest.approx(5000.0)
    assert stmt["total_expenses"] == pytest.approx(1000.0)
    assert stmt["net_income"] == pytest.approx(4000.0)


@pytest.mark.unit
def test_ledger_repr():
    """Ledger repr includes name, account count, and transaction count."""
    ledger = Ledger("Test Ledger")
    r = repr(ledger)
    assert "Test Ledger" in r
    assert "accounts=0" in r
    assert "transactions=0" in r


# ======================================================================
# Forecaster tests
# ======================================================================

@pytest.mark.unit
def test_forecaster_moving_average_basic():
    """Moving average with window=3 on simple data."""
    fc = Forecaster([10, 20, 30, 40, 50])
    ma = fc.moving_average(window=3)
    assert len(ma) == 3
    assert ma[0] == pytest.approx(20.0)
    assert ma[1] == pytest.approx(30.0)
    assert ma[2] == pytest.approx(40.0)


@pytest.mark.unit
def test_forecaster_moving_average_window_1():
    """Moving average with window=1 returns the data itself."""
    data = [5.0, 10.0, 15.0]
    fc = Forecaster(data)
    ma = fc.moving_average(window=1)
    assert ma == data


@pytest.mark.unit
def test_forecaster_moving_average_insufficient_data_raises():
    """Moving average raises ForecastError when data < window."""
    fc = Forecaster([1.0, 2.0])
    with pytest.raises(ForecastError, match="at least"):
        fc.moving_average(window=5)


@pytest.mark.unit
def test_forecaster_moving_average_invalid_window_raises():
    """Moving average raises ForecastError for window < 1."""
    fc = Forecaster([1.0, 2.0, 3.0])
    with pytest.raises(ForecastError, match="Window"):
        fc.moving_average(window=0)


@pytest.mark.unit
def test_forecaster_exponential_smoothing_basic():
    """Exponential smoothing produces list of same length as input."""
    fc = Forecaster([100, 110, 105, 120, 130])
    smoothed = fc.exponential_smoothing(alpha=0.3)
    assert len(smoothed) == 5
    assert smoothed[0] == pytest.approx(100.0)


@pytest.mark.unit
def test_forecaster_exponential_smoothing_invalid_alpha_raises():
    """Exponential smoothing raises ForecastError for alpha out of (0,1)."""
    fc = Forecaster([1.0, 2.0, 3.0])
    with pytest.raises(ForecastError, match="Alpha"):
        fc.exponential_smoothing(alpha=0.0)
    with pytest.raises(ForecastError, match="Alpha"):
        fc.exponential_smoothing(alpha=1.0)


@pytest.mark.unit
def test_forecaster_exponential_smoothing_empty_data_raises():
    """Exponential smoothing raises ForecastError on empty data."""
    fc = Forecaster([])
    with pytest.raises(ForecastError, match="No data"):
        fc.exponential_smoothing()


@pytest.mark.unit
def test_forecaster_linear_trend_basic():
    """Linear trend returns slope, intercept, r_squared."""
    fc = Forecaster([10, 20, 30, 40, 50])
    trend = fc.linear_trend()
    assert trend["slope"] == pytest.approx(10.0)
    assert trend["intercept"] == pytest.approx(10.0)
    assert trend["r_squared"] == pytest.approx(1.0)


@pytest.mark.unit
def test_forecaster_linear_trend_insufficient_data_raises():
    """Linear trend raises ForecastError with fewer than 2 points."""
    fc = Forecaster([42.0])
    with pytest.raises(ForecastError, match="at least 2"):
        fc.linear_trend()


@pytest.mark.unit
def test_forecaster_forecast_moving_average():
    """Forecast with moving_average projects last MA value."""
    fc = Forecaster([10, 20, 30, 40, 50])
    forecast = fc.forecast(periods=3, method="moving_average", window=3)
    assert len(forecast) == 3
    assert all(v == pytest.approx(40.0) for v in forecast)


@pytest.mark.unit
def test_forecaster_forecast_linear_trend():
    """Forecast with linear_trend extrapolates the fitted line."""
    fc = Forecaster([10, 20, 30, 40, 50])
    forecast = fc.forecast(periods=2, method="linear_trend")
    assert forecast[0] == pytest.approx(60.0)
    assert forecast[1] == pytest.approx(70.0)


@pytest.mark.unit
def test_forecaster_forecast_unknown_method_raises():
    """Forecast with unknown method raises ForecastError."""
    fc = Forecaster([1, 2, 3])
    with pytest.raises(ForecastError, match="Unknown method"):
        fc.forecast(periods=1, method="magic")


@pytest.mark.unit
def test_forecaster_forecast_zero_periods_raises():
    """Forecast with periods < 1 raises ForecastError."""
    fc = Forecaster([1, 2, 3])
    with pytest.raises(ForecastError, match="periods"):
        fc.forecast(periods=0)


# ======================================================================
# TaxCalculator tests
# ======================================================================

@pytest.mark.unit
def test_tax_calculator_zero_income():
    """Zero income yields zero tax."""
    calc = TaxCalculator()
    result = calc.calculate_tax(0.0)
    assert result.total_tax == 0.0
    assert result.effective_rate == 0.0


@pytest.mark.unit
def test_tax_calculator_first_bracket_only():
    """Income within first bracket uses only the lowest rate."""
    calc = TaxCalculator()
    result = calc.calculate_tax(5000.0)
    assert result.total_tax == pytest.approx(500.0)
    assert result.marginal_rate == pytest.approx(0.10)


@pytest.mark.unit
def test_tax_calculator_negative_income_raises():
    """Negative income raises TaxError."""
    calc = TaxCalculator()
    with pytest.raises(TaxError, match="non-negative"):
        calc.calculate_tax(-1000.0)


@pytest.mark.unit
def test_tax_calculator_custom_brackets():
    """Custom brackets are used instead of defaults."""
    brackets = [
        {"min": 0, "max": 10000, "rate": 0.10},
        {"min": 10000, "max": float("inf"), "rate": 0.20},
    ]
    calc = TaxCalculator(brackets=brackets)
    result = calc.calculate_tax(20000.0)
    assert result.total_tax == pytest.approx(3000.0)


@pytest.mark.unit
def test_tax_calculator_invalid_rate_raises():
    """Rate outside [0,1] raises TaxError."""
    brackets = [{"min": 0, "max": 100, "rate": 1.5}]
    with pytest.raises(TaxError, match="between 0 and 1"):
        TaxCalculator(brackets=brackets)


@pytest.mark.unit
def test_tax_calculator_result_is_tax_result():
    """calculate_tax returns a TaxResult dataclass."""
    calc = TaxCalculator()
    result = calc.calculate_tax(50000.0)
    assert isinstance(result, TaxResult)
    assert result.gross_income == 50000.0


@pytest.mark.unit
def test_tax_calculator_apply_deductions_reduces_income():
    """apply_deductions reduces gross income by deduction amounts."""
    calc = TaxCalculator()
    taxable = calc.apply_deductions(
        100000.0,
        [
            {"name": "Standard", "amount": 14600, "type": "standard"},
            {"name": "Charity", "amount": 5000, "type": "itemized"},
        ],
    )
    assert taxable == pytest.approx(80400.0)


@pytest.mark.unit
def test_tax_calculator_apply_deductions_floor_at_zero():
    """Deductions cannot reduce taxable income below zero."""
    calc = TaxCalculator()
    taxable = calc.apply_deductions(1000.0, [{"name": "Big", "amount": 50000}])
    assert taxable == 0.0


@pytest.mark.unit
def test_tax_calculator_bracket_breakdown_amounts_sum_to_total():
    """The sum of per-bracket taxes equals total_tax."""
    calc = TaxCalculator()
    result = calc.calculate_tax(75000.0)
    bracket_sum = sum(b["tax"] for b in result.bracket_breakdown)
    assert bracket_sum == pytest.approx(result.total_tax, abs=0.01)
