#!/usr/bin/env python3
"""
Orchestrator script for the Finance module.
Demonstrates Ledger, Taxes, Payroll, and Forecasting.
"""

from codomyrmex.finance import (
    AccountType,
    Forecaster,
    Ledger,
    PayrollProcessor,
    TaxCalculator,
)
from codomyrmex.finance.visualization import balance_sheet_text, income_statement_text


def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "finance" / "config.yaml"
    config_data = {}
    if config_path.exists():
        with open(config_path) as f:
            config_data = yaml.safe_load(f) or {}
            print("Loaded config from config/finance/config.yaml")

    print("--- Codomyrmex Finance Orchestrator ---")

    # 1. Initialize Ledger
    ledger = Ledger("Autonomous Corp")

    # 2. Setup Chart of Accounts
    bank = ledger.create_account("Assets:Bank", AccountType.ASSET)
    equity = ledger.create_account("Equity:InitialCapital", AccountType.EQUITY)
    revenue = ledger.create_account("Revenue:Sales", AccountType.REVENUE)
    payroll_exp = ledger.create_account("Expenses:Payroll", AccountType.EXPENSE)
    tax_exp = ledger.create_account("Expenses:Taxes", AccountType.EXPENSE)

    print(f"Initialized ledger: {ledger}")

    # 3. Record Initial Investment
    ledger.post_transaction(
        entries=[
            {"account_id": bank.id, "amount": 100000.0},
            {"account_id": equity.id, "amount": -100000.0},
        ],
        description="Initial investment",
    )

    # 4. Record Sales
    ledger.post_transaction(
        entries=[
            {"account_id": bank.id, "amount": 50000.0},
            {"account_id": revenue.id, "amount": -50000.0},
        ],
        description="Software licenses sold",
    )

    # 5. Process Payroll
    payroll = PayrollProcessor()
    # Monthly salary of $8000
    pay_data = payroll.calculate_pay(8000.0, pay_period="monthly")
    print(f"\nProcessed monthly payroll: Net Pay = ${pay_data['net_pay']:.2f}")

    ledger.post_transaction(
        entries=[
            {"account_id": payroll_exp.id, "amount": 8000.0},
            {"account_id": bank.id, "amount": -8000.0},
        ],
        description="Monthly payroll - January",
    )

    # 6. Estimate Taxes
    tax_calc = TaxCalculator()
    # Net income so far: 50000 - 8000 = 42000
    # Annualize it roughly: 42000 * 12 = 504000
    tax_result = tax_calc.calculate_tax(42000.0 * 12)
    print(f"Annual tax estimate on $504k: ${tax_result.total_tax:,.2f} (Effective: {tax_result.effective_rate*100:.1f}%)")

    # Record estimated tax for the month
    tax_due = float(tax_result.total_tax / 12)
    ledger.post_transaction(
        entries=[
            {"account_id": tax_exp.id, "amount": tax_due},
            {"account_id": bank.id, "amount": -tax_due},
        ],
        description="Estimated tax provision - January",
    )

    # 7. Forecasting
    # Historical monthly revenue:
    history = [45000.0, 48000.0, 52000.0, 50000.0, 55000.0]
    forecaster = Forecaster(history)
    future = forecaster.forecast(periods=3, method="monte_carlo")
    print("\nRevenue Forecast (Monte Carlo):")
    for i, val in enumerate(future, 1):
        print(f"  Month {i}: ${val:,.2f}")

    # Risk Metrics
    portfolio = {
        "name": "Retirement fund",
        "base_currency": "USD",
        "positions": [
            {"symbol": "VOO", "quantity": 100, "cost_basis": 400, "current_price": 500},
            {"symbol": "MSFT", "quantity": 50, "cost_basis": 300, "current_price": 420},
        ]
    }
    risk = forecaster.risk_metrics(portfolio)
    print(f"\nPortfolio Value: ${risk['total_value']:,.2f}")
    print(f"Value at Risk (95%): ${risk['var_95']:,.2f}")

    # 8. Reports
    print("\n--- Financial Statements ---")
    all_accounts = list(ledger.accounts.values())
    print(balance_sheet_text(all_accounts))
    print("\n")
    print(income_statement_text(all_accounts))

    sheet = ledger.get_balance_sheet()
    print(f"Balance Sheet Balanced: {sheet['balanced']}")
    print(f"Total Assets: ${sheet['total_assets']:,.2f}")

    income = ledger.get_income_statement()
    print(f"Net Income: ${income['net_income']:,.2f}")

if __name__ == "__main__":
    main()
