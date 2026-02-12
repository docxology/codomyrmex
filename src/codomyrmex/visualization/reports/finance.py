from typing import List, Any
from ..core.dashboard import Dashboard
from ..plots.candlestick import CandlestickChart
from ..plots.line import LinePlot
from ..plots.bar import BarPlot
from ..components.basic import Card, Table
from ..components.statbox import StatBox
from .base import Report

class FinanceReport(Report):
    """
    Generates a financial overview report.
    """
    def __init__(self):
        super().__init__("Financial Overview")

    def generate(self) -> None:
        # 1. KPI Cards
        self.dashboard.add_section(
            "Key Performance Indicators",
            [
                StatBox("Total Revenue", "$1,250,000", "+12.5%", "up"),
                StatBox("Net Profit", "$320,000", "+8.2%", "up"),
                StatBox("Op. Expenses", "$850,000", "-2.1%", "down"), # Down is good for expenses
                Card("Cash on Hand", "$145,000")
            ]
        )
        
        # 2. Stock Performance (Candlestick)
        # Mock data
        dates = ["Mon", "Tue", "Wed", "Thu", "Fri"]
        opens = [100, 102, 101, 103, 105]
        highs = [103, 104, 102, 106, 108]
        lows = [99, 101, 100, 102, 104]
        closes = [102, 101, 103, 105, 107]
        
        self.dashboard.add_section(
            "Stock Performance",
            CandlestickChart("CDMX Stock", dates, opens, highs, lows, closes)
        )
        
        # 3. Revenue Trend (Line)
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
        revenue = [100, 120, 115, 130, 145, 160]
        self.dashboard.add_section(
            "Revenue Trend",
            LinePlot("Monthly Revenue ($k)", months, [revenue], ["Revenue"])
        )
        
        # 4. Expense Breakdown (Bar)
        categories = ["R&D", "Marketing", "G&A", "COGS"]
        expenses = [40, 25, 15, 20]
        self.dashboard.add_section(
            "Expense Breakdown",
            BarPlot("Q1 Expenses (%)", categories, expenses)
        )
