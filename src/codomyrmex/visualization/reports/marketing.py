from typing import List, Any
from ..core.dashboard import Dashboard
from ..plots.funnel import FunnelChart
from ..plots.pie import PieChart
from ..plots.wordcloud import WordCloud
from ..components.badge import Badge
from ..components.timeline import Timeline, TimelineEvent
from .base import Report

class MarketingReport(Report):
    """
    Generates a marketing campaign analysis report.
    """
    def __init__(self):
        super().__init__("Marketing Analysis")

    def generate(self) -> None:
        # 1. Campaign Status
        self.dashboard.add_section(
            "Active Campaigns",
            [
                Badge("Brand Awareness Q1", "success"),
                Badge("Product Launch v2", "primary"),
                Badge("Retention Email", "warning")
            ]
        )
        
        # 2. Conversion Funnel
        stages = ["Impressions", "Clicks", "Signups", "Purchases"]
        values = [10000, 2500, 500, 150]
        self.dashboard.add_section(
            "Conversion Funnel",
            FunnelChart("User Acquisition", stages, values)
        )
        
        # 3. Demographics (Pie)
        segments = ["Gen Z", "Millennials", "Gen X", "Boomers"]
        counts = [30, 40, 20, 10]
        self.dashboard.add_section(
            "Audience Demographics",
            PieChart("Age Distribution", segments, counts)
        )
        
        # 4. Sentiment (WordCloud)
        terms = [("Love", 50), ("Fast", 40), ("Easy", 35), ("Expensive", 10), ("Support", 20)]
        self.dashboard.add_section(
            "Customer Sentiment",
            WordCloud("Feedback Topics", terms)
        )
        
        # 5. Campaign Timeline
        events = [
            TimelineEvent("2026-01-01", "Campaign Start", "Launched cross-channel"),
            TimelineEvent("2026-01-15", "Mid-point Review", "Optimized ad spend"),
            TimelineEvent("2026-02-01", "Campaign End", "Final reporting")
        ]
        self.dashboard.add_section(
            "Campaign History",
            Timeline(events)
        )
