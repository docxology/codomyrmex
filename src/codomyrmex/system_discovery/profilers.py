"""Hardware and environment profilers."""

import sys
import os
import platform
import multiprocessing
import psutil
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)

class HardwareProfiler:
    """Detects and profiles system hardware capabilities."""
    
    @staticmethod
    def get_hardware_info() -> Dict[str, Any]:
        """Get CPU, RAM, and OS information."""
        return {
            "cpu_count": multiprocessing.cpu_count(),
            "cpu_freq": psutil.cpu_freq()._asdict() if hasattr(psutil, "cpu_freq") and psutil.cpu_freq() else None,
            "total_ram_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "os": platform.system(),
            "os_release": platform.release(),
            "architecture": platform.machine()
        }

class EnvironmentProfiler:
    """Detects the current execution environment (CI, Docker, etc.)."""
    
    @staticmethod
    def get_environment_type() -> str:
        """Detect environment type."""
        if os.environ.get("GITHUB_ACTIONS"):
            return "ci_github"
        if os.environ.get("TRAVIS"):
            return "ci_travis"
        if os.path.exists("/.dockerenv"):
            return "docker"
        if os.environ.get("KUBERNETES_SERVICE_HOST"):
            return "kubernetes"
        return "local"

    @staticmethod
    def get_python_info() -> Dict[str, Any]:
        """Get Python runtime information."""
        return {
            "python_version": sys.version,
            "executable": sys.executable,
            "path": sys.path
        }
