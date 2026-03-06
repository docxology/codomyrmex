"""Hardware and environment profilers."""

import multiprocessing
import os
import platform
import shutil
import subprocess
import sys
from typing import Any

try:
    import psutil
except ImportError:
    pass

try:
    from codomyrmex.logging_monitoring import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class HardwareProfiler:
    """Detects and profiles system hardware capabilities."""

    @staticmethod
    def get_hardware_info() -> dict[str, Any]:
        """Get CPU, RAM, OS, and GPU information."""
        info = {
            "cpu_count": multiprocessing.cpu_count(),
            "cpu_threads": os.cpu_count(),
            "os": platform.system(),
            "os_release": platform.release(),
            "os_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "gpu": HardwareProfiler.get_gpu_info(),
        }

        if psutil:
            try:
                info["cpu_freq"] = psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
                info["total_ram_gb"] = round(psutil.virtual_memory().total / (1024**3), 2)
                info["available_ram_gb"] = round(psutil.virtual_memory().available / (1024**3), 2)
            except Exception as e:
                logger.debug(f"Failed to get psutil info: {e}")
        else:
            info["cpu_freq"] = None
            info["total_ram_gb"] = None
            info["available_ram_gb"] = None
            logger.debug("psutil not available, RAM info will be missing")

        return info

    @staticmethod
    def get_gpu_info() -> dict[str, Any]:
        """Attempt to detect GPU information without specialized libraries."""
        gpu_info = {"available": False, "details": []}

        # Check for nvidia-smi (NVIDIA)
        nvidia_smi = shutil.which("nvidia-smi")
        if nvidia_smi:
            try:
                result = subprocess.run(
                    [nvidia_smi, "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader,nounits"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    gpu_info["available"] = True
                    for line in result.stdout.strip().split("\n"):
                        if line:
                            parts = line.split(", ")
                            if len(parts) >= 3:
                                gpu_info["details"].append({
                                    "vendor": "NVIDIA",
                                    "model": parts[0],
                                    "memory_mb": float(parts[1]),
                                    "driver_version": parts[2]
                                })
            except Exception as e:
                logger.debug(f"Failed to run nvidia-smi: {e}")

        # Check for rocm-smi (AMD)
        rocm_smi = shutil.which("rocm-smi")
        if rocm_smi:
            gpu_info["available"] = True
            gpu_info["details"].append({"vendor": "AMD", "tool": "rocm-smi detected"})

        # Check for system_profiler (macOS)
        if platform.system() == "Darwin":
            try:
                # Use a more targeted command to improve performance
                result = subprocess.run(
                    ["system_profiler", "SPDisplaysDataType", "-detailLevel", "mini"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    if "Chipset Model" in result.stdout:
                        gpu_info["available"] = True
                        for line in result.stdout.split("\n"):
                            if "Chipset Model" in line:
                                gpu_info["details"].append({
                                    "vendor": "Apple/Other",
                                    "model": line.split(":")[1].strip()
                                })
            except Exception as e:
                logger.debug(f"Failed to run system_profiler: {e}")

        return gpu_info


class EnvironmentProfiler:
    """Detects the current execution environment (CI, Docker, etc.)."""

    @staticmethod
    def get_environment_info() -> dict[str, Any]:
        """Get comprehensive environment information."""
        return {
            "type": EnvironmentProfiler.get_environment_type(),
            "python": EnvironmentProfiler.get_python_info(),
            "cwd": os.getcwd(),
            "env_vars_count": len(os.environ),
            "is_venv": EnvironmentProfiler.is_virtual_env(),
        }

    @staticmethod
    def get_environment_type() -> str:
        """Detect environment type."""
        if os.environ.get("GITHUB_ACTIONS"):
            return "ci_github"
        if os.environ.get("TRAVIS"):
            return "ci_travis"
        if os.environ.get("CIRCLECI"):
            return "ci_circleci"
        if os.path.exists("/.dockerenv"):
            return "docker"
        if os.environ.get("KUBERNETES_SERVICE_HOST"):
            return "kubernetes"
        if os.environ.get("WSL_DISTRO_NAME") or "microsoft-standard" in platform.release().lower():
            return "wsl"
        return "local"

    @staticmethod
    def is_virtual_env() -> bool:
        """Check if running in a virtual environment."""
        return (
            hasattr(sys, "real_prefix") or
            (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix) or
            os.environ.get("VIRTUAL_ENV") is not None
        )

    @staticmethod
    def get_python_info() -> dict[str, Any]:
        """Get Python runtime information."""
        return {
            "version": sys.version,
            "version_info": list(sys.version_info),
            "executable": sys.executable,
            "prefix": sys.prefix,
            "base_prefix": getattr(sys, "base_prefix", sys.prefix),
            "path": sys.path[:5],  # Top 5 for brevity
        }
