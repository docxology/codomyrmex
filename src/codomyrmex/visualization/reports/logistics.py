from typing import List, Any
from ..core.dashboard import Dashboard
from ..plots.sankey import SankeyDiagram
from ..plots.gantt import GanttChart
from ..plots.network import NetworkGraph
from ..components.alert import Alert
from ..components.progress import ProgressBar
from .base import Report

class LogisticsReport(Report):
    """
    Generates a supply chain and logistics report.
    """
    def __init__(self):
        super().__init__("Logistics & Operations")

    def generate(self) -> None:
        # 1. Alerts
        self.dashboard.add_section(
            "System Alerts",
            [
                Alert("Shipment #1234 delayed due to weather.", "warning"),
                Alert("Warehouse B capacity at 95%.", "danger"),
                Alert("Route optimization completed successfully.", "success")
            ]
        )
        
        # 2. Fleet Status
        self.dashboard.add_section(
            "Fleet Utilization",
            ProgressBar(78.0, 100.0, label="78% of Fleet Active", color="#17a2b8")
        )
        
        # 3. Supply Chain Flow (Sankey)
        links = [
            ("Supplier A", "Warehouse 1", 500),
            ("Supplier B", "Warehouse 1", 300),
            ("Supplier B", "Warehouse 2", 200),
            ("Warehouse 1", "Distribution Center", 600),
            ("Warehouse 2", "Distribution Center", 150),
            ("Distribution Center", "Retail", 700),
            ("Distribution Center", "Direct", 50)
        ]
        self.dashboard.add_section(
            "Goods Flow",
            SankeyDiagram("Supply Chain Volume", links)
        )
        
        # 4. Delivery Schedule (Gantt)
        tasks = ["Route A Planning", "Loading", "Transit", "Unloading"]
        starts = [8, 9, 10, 14] # Hours
        durations = [1, 1, 4, 1]
        self.dashboard.add_section(
            "Delivery Schedule (Truck 5)",
            GanttChart("Daily Operations", tasks, starts, durations)
        )
        
        # 5. Route Topology (Network)
        nodes = ["Hub", "Depot 1", "Depot 2", "Store A", "Store B"]
        edges = [
            ("Hub", "Depot 1"), ("Hub", "Depot 2"),
            ("Depot 1", "Store A"), ("Depot 2", "Store B")
        ]
        self.dashboard.add_section(
            "Network Topology",
            NetworkGraph("Distribution Network", nodes, edges)
        )
