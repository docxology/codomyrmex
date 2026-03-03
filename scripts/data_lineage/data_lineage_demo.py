#!/usr/bin/env python3
"""
Data Lineage Orchestrator Demo

Demonstrates the full lifecycle of tracking data lineage and performing
impact analysis using the improved codomyrmex.data_lineage module.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from codomyrmex.data_lineage import EdgeType, ImpactAnalyzer, LineageTracker, NodeType


def main() -> int:
    print("--- Starting Data Lineage Demo ---")

    # 1. Initialize the tracker
    tracker = LineageTracker()

    # 2. Register Source Datasets
    print("Registering source datasets...")
    tracker.register_dataset(
        id="raw_sales",
        name="Raw Sales Data",
        location="s3://datalake/raw/sales/2026/03/01/"
    )
    tracker.register_dataset(
        id="raw_products",
        name="Raw Product Catalog",
        location="s3://datalake/raw/products/latest"
    )

    # 3. Register Transformations
    print("Registering data transformations...")
    # This automatically registers output datasets if they don't exist
    tracker.register_transformation(
        id="clean_sales_job",
        name="Sales Data Cleaning",
        inputs=["raw_sales", "raw_products"],
        outputs=["clean_sales"]
    )

    tracker.register_transformation(
        id="sales_aggregation",
        name="Daily Sales Aggregator",
        inputs=["clean_sales"],
        outputs=["daily_sales_summary"]
    )

    # 4. Register Downstream Consumers (Models/Dashboards)
    print("Registering downstream consumers...")
    # Manual node creation for specific types
    from codomyrmex.data_lineage import LineageEdge, LineageNode

    # Model
    model_node = LineageNode(id="revenue_forecast", name="Revenue Forecast Model", node_type=NodeType.MODEL)
    tracker.graph.add_node(model_node)
    tracker.graph.add_edge(LineageEdge("daily_sales_summary", "revenue_forecast", EdgeType.INPUT_TO))

    # Dashboard
    dashboard_node = LineageNode(id="exec_dashboard", name="Executive KPI Dashboard", node_type=NodeType.DASHBOARD)
    tracker.graph.add_node(dashboard_node)
    tracker.graph.add_edge(LineageEdge("daily_sales_summary", "exec_dashboard", EdgeType.USED_BY))

    # 5. Perform Traceability Queries
    print("\n--- Lineage Traceability ---")
    node_id = "daily_sales_summary"
    origins = tracker.get_origin(node_id)
    print(f"Origins for '{node_id}':")
    for node in origins:
        print(f"  - {node.name} ({node.id})")

    # 6. Perform Impact Analysis
    print("\n--- Impact Analysis ---")
    source_to_change = "raw_sales"
    analyzer = ImpactAnalyzer(tracker.graph)
    impact = analyzer.analyze_change(source_to_change)

    print(f"Impact of changing '{source_to_change}':")
    print(f"  Total affected nodes: {impact['total_affected']}")
    print(f"  Affected Models: {', '.join(impact['affected_models'])}")
    print(f"  Affected Dashboards: {', '.join(impact['affected_dashboards'])}")
    print(f"  Risk Level: {impact['risk_level'].upper()}")

    # 7. Visualization Export (DOT)
    print("\n--- DOT Export (Sample) ---")
    dot_content = tracker.graph.export_to_dot()
    print(f"Graph DOT length: {len(dot_content)} characters")

    # 8. Cycle Validation
    print("\n--- Graph Validation ---")
    cycles = tracker.graph.validate_graph()
    if not cycles:
        print("Graph is a valid DAG (no cycles).")
    else:
        print(f"ALERT: Cycles detected involving nodes: {cycles}")

    print("\n--- Demo Completed Successfully ---")
    return 0


    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "data_lineage" / "config.yaml"
    config_data = {}
    if config_path.exists():
        with open(config_path) as f:
            config_data = yaml.safe_load(f) or {}
            print("Loaded config from config/data_lineage/config.yaml")

if __name__ == "__main__":
    sys.exit(main())
