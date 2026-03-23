import os
import subprocess
import tempfile
from datetime import datetime
from typing import Any

from codomyrmex.logging_monitoring import get_logger

# Fabric Manager - Main integration class for Codomyrmex

"""
Provides comprehensive Fabric pattern management, execution, and integration
with the Codomyrmex ecosystem.
"""


class FabricManager:
    """
    Main Fabric integration manager for Codomyrmex.

    Provides comprehensive pattern management, execution, and output handling
    with seamless integration into the Codomyrmex ecosystem.
    """

    def __init__(self, fabric_binary: str = "fabric"):
        """
        Initialize the Fabric manager.

        Args:
            fabric_binary: Path to fabric binary (default: "fabric")
        """
        self.fabric_binary = fabric_binary
        self.logger = get_logger(__name__)
        self.fabric_available = self._check_fabric_availability()
        self.results_history: list[dict[str, Any]] = []

    def _check_fabric_availability(self) -> bool:
        """Check if Fabric binary is available."""
        try:
            result = subprocess.run(
                [self.fabric_binary, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            self.logger.warning("Fabric availability check failed: %s", e)
            return False

    def list_patterns(self) -> list[str]:  # type: ignore
        """
        Get list of available Fabric patterns.

        Returns:
            list of pattern names
        """
        if not self.fabric_available:
            return []

        try:
            result = subprocess.run(
                [self.fabric_binary, "--listpatterns"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                patterns = [
                    line.strip()
                    for line in result.stdout.split("\n")
                    if line.strip() and not line.startswith("Available patterns:")
                ]
                return patterns
        except subprocess.TimeoutExpired as e:
            self.logger.warning("Fabric command timed out: %s", str(e))
            raise

    def _make_error_result(self, pattern: str, error: str) -> dict[str, Any]:
        """Build and record an error result dict."""
        result = {
            "success": False,
            "error": error,
            "output": "",
            "pattern": pattern,
            "timestamp": datetime.now().isoformat(),
        }
        self.results_history.append(result)
        return result

    def _run_subprocess(
        self, cmd: list[str], input_text: str, pattern: str
    ) -> dict[str, Any]:
        """Write input to temp file, run cmd, return result dict."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp:
            tmp.write(input_text)
            tmp.flush()
            with open(tmp.name) as input_file:
                start_time = datetime.now()
                proc = subprocess.run(
                    cmd, stdin=input_file, capture_output=True, text=True, timeout=120
                )
                end_time = datetime.now()
            os.unlink(tmp.name)

        result_data = {
            "success": proc.returncode == 0,
            "output": proc.stdout,
            "error": proc.stderr if proc.returncode != 0 else "",
            "pattern": pattern,
            "duration": (end_time - start_time).total_seconds(),
            "timestamp": start_time.isoformat(),
        }
        self.results_history.append(result_data)
        if result_data["success"]:
            self.logger.info(
                "Fabric pattern '%s' executed successfully in %.2fs",
                pattern,
                result_data["duration"],
            )
        else:
            self.logger.error(
                "Fabric pattern '%s' failed: %s", pattern, result_data["error"]
            )
        return result_data

    def run_pattern(
        self, pattern: str, input_text: str, additional_args: list[str] | None = None
    ) -> dict[str, Any]:
        """Run a Fabric pattern with given input."""
        if not self.fabric_available:
            return {
                "success": False,
                "error": "Fabric not available",
                "output": "",
                "pattern": pattern,
            }

        cmd = [self.fabric_binary, "--pattern", pattern, *(additional_args or [])]
        try:
            return self._run_subprocess(cmd, input_text, pattern)
        except subprocess.TimeoutExpired:
            return self._make_error_result(pattern, "Pattern execution timeout")
        except Exception as e:
            return self._make_error_result(pattern, f"Execution error: {e!s}")

    def is_available(self) -> bool:
        """Check if Fabric is available."""
        return self.fabric_available

    def get_results_history(self) -> list[dict[str, Any]]:
        """Get history of pattern execution results."""
        return self.results_history.copy()
