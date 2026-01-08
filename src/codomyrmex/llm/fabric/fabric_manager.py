from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import os
import subprocess
import tempfile

from codomyrmex.logging_monitoring import get_logger














"""
Fabric Manager - Main integration class for Codomyrmex

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
        self.results_history: List[Dict[str, Any]] = []

    def _check_fabric_availability(self) -> bool:
        """Check if Fabric binary is available."""
        try:
            result = subprocess.run(
                [self.fabric_binary, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def list_patterns(self) -> List[str]:
        """
        Get list of available Fabric patterns.

        Returns:
            List of pattern names
        """
        if not self.fabric_available:
            return []

        try:
            result = subprocess.run(
                [self.fabric_binary, "--listpatterns"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                patterns = [
                    line.strip()
                    for line in result.stdout.split('\n')
                    if line.strip() and not line.startswith('Available patterns:')
                ]
                return patterns
        except subprocess.TimeoutExpired:
            pass

        return []

    def run_pattern(
        self,
        pattern: str,
        input_text: str,
        additional_args: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Run a Fabric pattern with given input.

        Args:
            pattern: Name of the Fabric pattern to run
            input_text: Input text to process
            additional_args: Additional command-line arguments

        Returns:
            Dictionary with execution results
        """
        if not self.fabric_available:
            return {
                "success": False,
                "error": "Fabric not available",
                "output": "",
                "pattern": pattern
            }

        cmd = [self.fabric_binary, "--pattern", pattern]
        if additional_args:
            cmd.extend(additional_args)

        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
                tmp.write(input_text)
                tmp.flush()

                with open(tmp.name, 'r') as input_file:
                    start_time = datetime.now()
                    result = subprocess.run(
                        cmd,
                        stdin=input_file,
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    end_time = datetime.now()

                os.unlink(tmp.name)

                result_data = {
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr if result.returncode != 0 else "",
                    "pattern": pattern,
                    "duration": (end_time - start_time).total_seconds(),
                    "timestamp": start_time.isoformat()
                }

                self.results_history.append(result_data)

                if result_data["success"]:
                    self.logger.info(
                        f"Fabric pattern '{pattern}' executed successfully in {result_data['duration']:.2f}s"
                    )
                else:
                    self.logger.error(f"Fabric pattern '{pattern}' failed: {result_data['error']}")

                return result_data

        except subprocess.TimeoutExpired:
            error_result = {
                "success": False,
                "error": "Pattern execution timeout",
                "output": "",
                "pattern": pattern,
                "timestamp": datetime.now().isoformat()
            }
            self.results_history.append(error_result)
            return error_result
        except Exception as e:
            error_result = {
                "success": False,
                "error": f"Execution error: {str(e)}",
                "output": "",
                "pattern": pattern,
                "timestamp": datetime.now().isoformat()
            }
            self.results_history.append(error_result)
            return error_result

    def is_available(self) -> bool:
        """Check if Fabric is available."""
        return self.fabric_available

    def get_results_history(self) -> List[Dict[str, Any]]:
        """Get history of pattern execution results."""
        return self.results_history.copy()


