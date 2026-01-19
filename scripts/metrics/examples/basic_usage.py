#!/usr/bin/env python3
"""
Metrics Collection - Real Usage Examples

Demonstrates actual metrics capabilities:
- Counter, Gauge, Histogram, Summary
- Metrics aggregation
- Backend selection
"""

import sys
import os
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_error
from codomyrmex.metrics import get_metrics, Counter, Gauge

def main():
    setup_logging()
    print_info("Running Metrics Collection Examples...")

    # 1. Get Metrics Instance
    print_info("Initializing metrics (in_memory)...")
    m = get_metrics(backend="in_memory")
    
    # 2. Counter
    print_info("Testing Counter...")
    c = m.counter("requests_total")
    c.inc()
    c.inc(5)
    if c.get() == 6:
        print_success("  Counter functional.")
    
    # 3. Gauge
    print_info("Testing Gauge...")
    g = m.gauge("memory_usage")
    g.set(1024)
    g.inc(256)
    if g.get() == 1280:
        print_success("  Gauge functional.")

    # 4. Histogram & Summary
    print_info("Testing Histogram and Summary...")
    h = m.histogram("latency")
    h.observe(0.5)
    s = m.summary("payload_size")
    s.observe(512)
    print_success("  Histogram and Summary initialized and observed.")

    print_success("Metrics collection examples completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
