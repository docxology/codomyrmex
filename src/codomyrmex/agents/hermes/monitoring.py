"""System Resource Monitoring for Hermes.

Provides hardware-aware execution checks by surfacing RAM, CPU, and Swap
metrics natively via psutil, allowing Hermes to proactively abort actions
that could cause Out-Of-Memory cascades.
"""

from typing import Any

import psutil


def _get_system_metrics() -> dict[str, float]:
    """Gather live hardware usage metrics.

    Returns:
        dict with keys: cpu_percent, ram_usage_percent, swap_usage_percent
    """
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()

    return {
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "ram_usage_percent": memory.percent,
        "swap_usage_percent": swap.percent,
    }
