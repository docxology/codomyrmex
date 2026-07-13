"""System Resource Monitoring for Hermes.

Provides hardware-aware execution checks by surfacing RAM, CPU, and Swap
metrics natively via psutil, allowing Hermes to proactively abort actions
that could cause Out-Of-Memory cascades.
"""

import logging

import psutil

logger = logging.getLogger(__name__)


def _get_system_metrics() -> dict[str, float]:
    """Gather live hardware usage metrics.

    Returns:
        dict with CPU, RAM, and swap usage metrics.
    """
    memory = psutil.virtual_memory()
    try:
        swap_percent = float(psutil.swap_memory().percent)
    except (OSError, psutil.Error) as exc:
        logger.debug("Swap metrics unavailable: %s", exc)
        swap_percent = 0.0
    bytes_per_mb = 1024 * 1024

    return {
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "ram_usage_percent": memory.percent,
        "ram_available_mb": memory.available / bytes_per_mb,
        "ram_total_mb": memory.total / bytes_per_mb,
        "swap_usage_percent": swap_percent,
    }
