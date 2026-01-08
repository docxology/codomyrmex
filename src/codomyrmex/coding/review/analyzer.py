"""
Code Analysis

Provides analysis capabilities including pyscn integration and traditional tools.
"""

import glob
import json
import os
import re
import subprocess
import tempfile
from typing import Any

from codomyrmex.logging_monitoring.logger_config import get_logger

from .models import (
    AnalysisResult,
    Language,
    SeverityLevel,
    ToolNotFoundError,
)

logger = get_logger(__name__)

# Try to import performance monitoring
try:
    from codomyrmex.performance import monitor_performance
    PERFORMANCE_MONITORING_AVAILABLE = True
except ImportError:
    PERFORMANCE_MONITORING_AVAILABLE = False

    def monitor_performance(*args, **kwargs):
        """Decorator for performance monitoring (fallback)."""
        def decorator(func):
    """Brief description of decorator.

Args:
    func : Description of func

    Returns: Description of return value
"""
            return func
        return decorator


class PyscnAnalyzer:
    """Specialized analyzer using pyscn for advanced static analysis."""

    def __init__(self, config: dict[str, Any] = None):
        """
        Initialize pyscn analyzer with configuration.

        Args:
            config: Pyscn configuration options
        """
        self.config = config or {}
        self._check_pyscn_availability()

    def _check_pyscn_availability(self):
        """Check if pyscn is available and working."""
        try:
            # Try to run pyscn --version
            result = subprocess.run(
                ["pyscn", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                raise ToolNotFoundError("pyscn not available or not working")
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            raise ToolNotFoundError(
                "pyscn not found. Install with: pipx install pyscn"
            )

    @monitor_performance("pyscn_analyze_complexity")
    def analyze_complexity(self, file_path: str) -> list[dict[str, Any]]:
        """Analyze cyclomatic complexity using pyscn."""
        try:
            # Pyscn writes JSON to a file, we need to read it from there
            # Get the most recent .pyscn/reports file
            reports_dir = ".pyscn/reports"
            if os.path.exists(reports_dir):
                json_files = glob.glob(os.path.join(reports_dir, "*.json"))
                if json_files:
                    # Get the most recent file
                    latest_file = max(json_files, key=os.path.getmtime)

                    with open(latest_file) as f:
                        data = json.load(f)

                    # Pyscn returns data under "complexity" key in the main object
                    complexity_data = data.get("complexity", {})
                    if "Functions" in complexity_data:
                        # Extract functions from the Functions array
                        functions = []
                        for func_data in complexity_data["Functions"]:
                            # Extract complexity from Metrics
                            complexity = func_data.get("Metrics", {}).get("Complexity", 0)
                            functions.append({
                                "name": func_data.get("Name", ""),
                                "complexity": complexity,
                                "line_number": func_data.get("StartLine", 0),
                                "file_path": func_data.get("FilePath", ""),
                                "risk_level": func_data.get("RiskLevel", "")
                            })
                        return functions
            return []

        except (json.JSONDecodeError, FileNotFoundError, Exception) as e:
            logger.error(f"Error running pyscn complexity analysis on {file_path}: {e}")
            return []

    @monitor_performance("pyscn_detect_dead_code")
    def detect_dead_code(self, file_path: str) -> list[dict[str, Any]]:
        """Detect dead code using CFG analysis."""
        try:
            # Pyscn writes JSON to a file, we need to read it from there
            # Get the most recent .pyscn/reports file
            reports_dir = ".pyscn/reports"
            if os.path.exists(reports_dir):
                json_files = glob.glob(os.path.join(reports_dir, "*.json"))
                if json_files:
                    # Get the most recent file
                    latest_file = max(json_files, key=os.path.getmtime)

                    with open(latest_file) as f:
                        data = json.load(f)

                    # Pyscn returns data under "dead_code" key
                    dead_code_data = data.get("dead_code", {})
                    if "files" in dead_code_data:
                        # Extract findings from all files
                        findings = []
                        for file_data in dead_code_data["files"]:
                            for function_data in file_data.get("functions", []):
                                findings.extend(function_data.get("findings", []))
                        return findings
            return []

        except (json.JSONDecodeError, FileNotFoundError, Exception) as e:
            logger.error(f"Error running pyscn dead code analysis on {file_path}: {e}")
            return []

    @monitor_performance("pyscn_find_clones")
    def find_clones(self, files: list[str], threshold: float = 0.8) -> list[dict[str, Any]]:
        """Find code clones using APTED with LSH acceleration."""
        try:
            # For single file analysis, pyscn doesn't need a file list
            if len(files) == 1:
                cmd = [
                    "pyscn", "analyze", "--select", "clones",
                    "--json", f"--clone-threshold={threshold}",
                    files[0]
                ]
            else:
                # For multiple files, create temporary file list
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                    for file_path in files:
                        f.write(file_path + '\n')
                    file_list_path = f.name

                cmd = [
                    "pyscn", "analyze", "--select", "clones",
                    "--json", f"--clone-threshold={threshold}",
                    f"@{file_list_path}"
                ]

                subprocess.run(cmd, capture_output=True, text=True, timeout=120)

                # Clean up temporary file
                os.unlink(file_list_path)

            # Read from the generated JSON file
            reports_dir = ".pyscn/reports"
            if os.path.exists(reports_dir):
                json_files = glob.glob(os.path.join(reports_dir, "*.json"))
                if json_files:
                    # Get the most recent file
                    latest_file = max(json_files, key=os.path.getmtime)

                    with open(latest_file) as f:
                        data = json.load(f)

                    # Pyscn returns clone data under "clones" key
                    clones_data = data.get("clones", {})
                    if "groups" in clones_data:
                        return clones_data["groups"]
            return []

        except (json.JSONDecodeError, FileNotFoundError, Exception) as e:
            logger.error(f"Error running pyscn clone detection: {e}")
            return []

    @monitor_performance("pyscn_analyze_coupling")
    def analyze_coupling(self, file_path: str) -> list[dict[str, Any]]:
        """Analyze Coupling Between Objects (CBO) metrics."""
        try:
            cmd = ["pyscn", "analyze", "--select", "cbo", "--json", file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.stdout:
                data = json.loads(result.stdout)
                # Pyscn returns CBO data under "cbo" key
                cbo_data = data.get("cbo", {})
                if "files" in cbo_data:
                    # Extract coupling data from all files
                    coupling_data = []
                    for file_data in cbo_data["files"]:
                        coupling_data.extend(file_data.get("classes", []))
                    return coupling_data
                return []
            return []

        except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
            logger.error(f"Error running pyscn coupling analysis on {file_path}: {e}")
            return []

    @monitor_performance("pyscn_generate_report")
    def generate_report(self, output_dir: str = "reports") -> str:
        """Generate comprehensive pyscn HTML report."""
        try:
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)

            # Change to the directory we want to analyze
            old_cwd = os.getcwd()
            os.chdir(output_dir)

            try:
                # Generate comprehensive report
                cmd = ["pyscn", "analyze", "--format", "html", ".."]
                subprocess.run(cmd, capture_output=True, text=True, timeout=300)

                report_path = "index.html"
                if os.path.exists(report_path):
                    return os.path.abspath(report_path)
                else:
                    logger.warning("Pyscn report generation completed but no HTML file found")
                    return ""
            finally:
                os.chdir(old_cwd)

        except (subprocess.TimeoutExpired, Exception) as e:
            logger.error(f"Error generating pyscn report: {e}")
            return ""

