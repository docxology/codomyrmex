from typing import Any, Dict, List
from .ledger import Ledger, AccountType
from codomyrmex.visualization import BarPlot, LinePlot

def plot_account_balances(ledger: Ledger) -> BarPlot:
    """
    Generates a bar chart of account balances.
    Returns: BarPlot object.
    """
    accounts = list(ledger._accounts.values())
    names = [acc.name for acc in accounts]
    balances = [acc.balance for acc in accounts]
    
    return BarPlot(
        title="Account Balances",
        x_label="Account",
        y_label="Balance",
        categories=names,
        values=balances
    )

def plot_transaction_volume(ledger: Ledger) -> LinePlot:
    """
    Generates a line chart of transaction volume over time.
    """
    # Group transactions by date (simplified)
    if not ledger._transactions:
        return LinePlot("Transaction Volume", [], [], "Date", "Count")

    dates = [t.timestamp.strftime("%Y-%m-%d") for t in ledger._transactions]
    # Simple count per day (stub)
    start_date = min(dates) if dates else "N/A"
    
    return LinePlot(
        title=f"Transaction Volume (Since {start_date})",
        x_label="Transaction Index",
        y_label="Amount",
        x_data=list(range(len(ledger._transactions))),
        y_data=[t.amount for t in ledger._transactions]
    )
