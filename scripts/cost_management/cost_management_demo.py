#!/usr/bin/env python3
"""
Cost Management Demo Script

Demonstrates functionality of the cost_management module.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from codomyrmex.cost_management import (
    BudgetManager,
    BudgetPeriod,
    CostCategory,
    CostTracker,
    JSONCostStore,
)


def run_demo():
    print("--- Codomyrmex Cost Management Demo ---")

    # 1. Initialize Tracker and Store
    # Use JSONCostStore for simple persistence demonstration
    store_file = PROJECT_ROOT / "@output" / "demo_costs.json"
    if store_file.exists():
        store_file.unlink()

    store = JSONCostStore(store_file)
    tracker = CostTracker(store=store)
    budgets = BudgetManager(tracker)

    print(f"Tracking costs in: {store_file}")

    # 2. Setup Budgets
    print("\nSetting up budgets...")
    llm_budget = budgets.create(
        name="Daily LLM",
        amount=1.00,  # $1.00 budget
        period=BudgetPeriod.DAILY,
        category=CostCategory.LLM_INFERENCE,
    )

    compute_budget = budgets.create(
        name="Weekly Compute",
        amount=10.00,
        period=BudgetPeriod.WEEKLY,
        category=CostCategory.COMPUTE,
    )

    # 3. Record Costs
    print("\nRecording sample costs...")

    # Simulated LLM Inference calls
    tracker.record(
        amount=0.02,
        category=CostCategory.LLM_INFERENCE,
        description="GPT-4o completion (small)",
        tags={"model": "gpt-4o", "project": "demo"},
    )

    tracker.record(
        amount=0.45,
        category=CostCategory.LLM_INFERENCE,
        description="Claude 3.5 Sonnet completion (large)",
        tags={"model": "claude-3-5-sonnet", "project": "demo"},
    )

    # Simulated Compute cost
    tracker.record(
        amount=2.50,
        category=CostCategory.COMPUTE,
        description="GPU VM instance hourly",
        resource_id="vm-gpu-01",
        tags={"provider": "aws"},
    )

    # 4. Check Utilization and Alerts
    print("\nChecking budget utilization:")
    for b in budgets.list_budgets():
        util = budgets.get_utilization(b)
        print(
            f"  {b.name}: ${util * b.amount:.2f} / ${b.amount:.2f} ({util * 100:.1f}%)"
        )

    print("\nChecking for alerts...")
    alerts = budgets.check_budgets()
    for alert in alerts:
        print(f"  [ALERT] {alert.message}")

    # 5. Spend Gating
    print("\nTesting spend gating:")
    large_llm_cost = 0.60
    can_spend = budgets.can_spend(large_llm_cost, category=CostCategory.LLM_INFERENCE)
    print(
        f"  Can spend ${large_llm_cost} on LLM? {'YES' if can_spend else 'NO (Budget limit reached)'}"
    )

    # Record another cost to trigger higher alert
    tracker.record(
        amount=0.40, category=CostCategory.LLM_INFERENCE, description="Batch processing"
    )

    print("\nChecking for new alerts after additional spend...")
    new_alerts = budgets.check_budgets()
    for alert in new_alerts:
        print(f"  [ALERT] {alert.message}")

    # 6. Generate Summary
    print("\nFinal Cost Summary:")
    summary = tracker.get_summary(period=BudgetPeriod.DAILY)
    print(f"  Total Spend: ${summary.total:.4f}")
    print("  Spend by Category:")
    for cat, amount in summary.by_category.items():
        print(f"    - {cat}: ${amount:.4f}")

    print("\nDemo completed successfully.")


def main() -> int:
    try:
        run_demo()
        return 0
    except Exception as e:
        print(f"Error running demo: {e}")
        import traceback

        traceback.print_exc()
        return 1

    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml

    config_path = (
        Path(__file__).resolve().parent.parent.parent
        / "config"
        / "cost_management"
        / "config.yaml"
    )
    config_data = {}
    if config_path.exists():
        with open(config_path) as f:
            config_data = yaml.safe_load(f) or {}
            print("Loaded config from config/cost_management/config.yaml")


if __name__ == "__main__":
    sys.exit(main())
