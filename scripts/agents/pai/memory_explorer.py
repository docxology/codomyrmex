#!/usr/bin/env python3
"""
PAI Memory System Explorer

Explore the PAI three-tier memory system: enumerate stores, count items,
analyze directory structure, and correlate memory stores with Algorithm phases.

Usage:
    python scripts/agents/pai/memory_explorer.py                  # Full report
    python scripts/agents/pai/memory_explorer.py --store LEARNING  # Single store
    python scripts/agents/pai/memory_explorer.py --json            # JSON output

Upstream: https://github.com/danielmiessler/Personal_AI_Infrastructure
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.agents.pai import PAIBridge, PAIConfig, ALGORITHM_PHASES
from codomyrmex.utils.cli_helpers import (
    setup_logging, print_info, print_success, print_warning,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="PAI Memory System Explorer — enumerate and analyze memory stores",
    )
    parser.add_argument("--store", "-s", help="Inspect a specific memory store by name")
    parser.add_argument("--json", "-j", action="store_true", dest="json_output", help="JSON output")
    return parser.parse_args()


def _header(title: str) -> None:
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}")


def overview(bridge: PAIBridge) -> dict:
    """Overview of all memory stores."""
    stores = bridge.list_memory_stores()
    _header(f"Memory Stores ({len(stores)} total)")

    if not stores:
        print_warning("  No memory stores found.")
        return {"stores": [], "total_items": 0}

    total_items = sum(s.item_count for s in stores)
    for s in sorted(stores, key=lambda x: x.item_count, reverse=True):
        bar = "█" * min(s.item_count, 40)
        print(f"  {s.name:25s}  {s.item_count:>5} items  {bar}")

    print(f"\n  Total: {total_items} items across {len(stores)} stores")
    return {"stores": [s.__dict__ for s in stores], "total_items": total_items}


def inspect_store(bridge: PAIBridge, store_name: str) -> dict:
    """Inspect a single memory store."""
    info = bridge.get_memory_info(store_name)
    _header(f"Store Detail: {store_name}")

    if info is None:
        print_warning(f"  Store '{store_name}' not found.")
        available = [s.name for s in bridge.list_memory_stores()]
        if available:
            print_info(f"  Available stores: {', '.join(available)}")
        return {"found": False, "name": store_name}

    print(f"  Name       : {info.name}")
    print(f"  Path       : {info.path}")
    print(f"  Item count : {info.item_count}")

    # List files in store
    store_path = Path(info.path)
    if store_path.exists() and store_path.is_dir():
        files = sorted(store_path.iterdir())[:20]
        print(f"\n  Contents (first {len(files)}):")
        for f in files:
            kind = "📁" if f.is_dir() else "📄"
            size = f.stat().st_size if f.is_file() else 0
            print(f"    {kind} {f.name:35s}  {size:>8,} bytes")
        if len(list(store_path.iterdir())) > 20:
            print(f"    ... and {len(list(store_path.iterdir())) - 20} more")

    return {"found": True, **info.__dict__}


def phase_mapping(bridge: PAIBridge) -> dict:
    """Map memory stores to Algorithm phases."""
    _header("Memory → Algorithm Phase Mapping")

    stores = bridge.list_memory_stores()
    store_names = {s.name.upper() for s in stores}

    # Heuristic mapping of store names to phases
    mapping = {
        "LEARNING": "LEARN (7/7)",
        "REFLECTIONS": "LEARN (7/7)",
        "AGENTS": "THINK (2/7)",
        "RESEARCH": "OBSERVE (1/7)",
        "STATE": "EXECUTE (5/7)",
        "WORK": "BUILD (4/7)",
        "HISTORY": "OBSERVE (1/7)",
    }

    mapped = 0
    for store in stores:
        phase = mapping.get(store.name.upper(), "—")
        icon = "✅" if phase != "—" else "  "
        print(f"  {icon} {store.name:25s} → {phase}")
        if phase != "—":
            mapped += 1

    covered_phases = set()
    for name in store_names:
        if name in mapping:
            covered_phases.add(mapping[name])

    print(f"\n  Phase coverage: {len(covered_phases)}/{len(ALGORITHM_PHASES)} phases")
    print(f"  Mapped stores : {mapped}/{len(stores)}")

    return {
        "mapped": mapped,
        "total_stores": len(stores),
        "covered_phases": len(covered_phases),
        "total_phases": len(ALGORITHM_PHASES),
    }


def main() -> int:
    args = parse_args()
    setup_logging()

    bridge = PAIBridge()
    if not bridge.is_installed():
        print_warning("PAI is not installed. Showing empty results.")

    results: dict = {}

    if args.store:
        results["detail"] = inspect_store(bridge, args.store)
    else:
        results["overview"] = overview(bridge)
        results["phase_mapping"] = phase_mapping(bridge)

    if args.json_output:
        print("\n" + json.dumps(results, indent=2, default=str))

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
