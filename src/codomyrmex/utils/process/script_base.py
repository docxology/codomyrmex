#!/usr/bin/env python3
"""Unified Script Base Module.

Provides a standardized foundation for all codomyrmex scripts with:
- Configurable CLI argument parsing
- Unified logging with file and console output
- Configuration loading from files, environment, and CLI
- Output directory management with timestamped runs
- Result saving in JSON and structured formats
- Performance tracking and metrics

Usage:
    from codomyrmex.utils.process.script_base import ScriptBase, ScriptConfig

    class MyScript(ScriptBase):
        def __init__(self):
            super().__init__(
                name="my_script",
                description="Does something useful",
                version="1.0.0"
            )

        def add_arguments(self, parser):
            parser.add_argument("--custom-arg", help="Custom argument")

        def run(self, args, config):
            self.log_info("Running script...")
            result = {"status": "success", "data": {...}}
            return result

    if __name__ == "__main__":
        script = MyScript()
        sys.exit(script.execute())
"""

import argparse
import json
import logging
import os
import traceback
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

# Ensure codomyrmex is importable
try:
    from codomyrmex.logging_monitoring import get_logger, setup_logging
    from codomyrmex.logging_monitoring.core.logger_config import (
        LogContext,
        PerformanceLogger,
    )
except ImportError:
    # Fallback for standalone execution
    import logging as _logging
    def get_logger(name):
        return _logging.getLogger(name)
    def setup_logging():
        _logging.basicConfig(level=_logging.INFO)
    class LogContext:
        def __init__(self, **kwargs):
            _logging.warning("codomyrmex not installed: LogContext operating as no-op. Install codomyrmex for full functionality.")
        def __enter__(self): return self
        def __exit__(self, *args): return None  # No-op context manager exit
    class PerformanceLogger:
        def __init__(self, logger_name):
            _logging.warning("codomyrmex not installed: PerformanceLogger operating as no-op. Install codomyrmex for full functionality.")
        def time_operation(self, name, **kwargs):
            from contextlib import contextmanager
            @contextmanager
            def ctx():
                yield
            return ctx()

logger = logging.getLogger(__name__)


@dataclass
class ScriptConfig:
    """Configuration container for scripts."""
    # Execution settings
    dry_run: bool = False
    verbose: bool = False
    quiet: bool = False

    # Output settings
    output_dir: Path | None = None
    output_format: str = "json"  # json, yaml, text
    save_output: bool = True

    # Logging settings
    log_level: str = "INFO"
    log_file: Path | None = None
    log_format: str = "text"  # text, json

    # Runtime settings
    timeout: int = 300  # seconds
    max_retries: int = 3
    retry_delay: float = 1.0

    # Custom config from file/env
    custom: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ScriptConfig":
        """Create config from dictionary."""
        known_fields = {f.name for f in cls.__dataclass_fields__.values()}
        known_data = {k: v for k, v in data.items() if k in known_fields}
        custom_data = {k: v for k, v in data.items() if k not in known_fields}

        config = cls(**known_data)
        config.custom.update(custom_data)
        return config

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ScriptResult:
    """Standardized script execution result."""
    script_name: str
    status: str  # success, failed, timeout, error, skipped
    start_time: str
    end_time: str
    duration_seconds: float
    exit_code: int
    data: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    config_used: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, default=str)


class ScriptBase(ABC):
    """Base class for all codomyrmex scripts.

    Provides unified infrastructure for:
    - CLI argument parsing with standard + custom args
    - Configuration loading from multiple sources
    - Structured logging to console and file
    - Output directory and file management
    - Result collection and saving
    - Performance tracking
    """

    def __init__(
        self,
        name: str,
        description: str,
        version: str = "1.0.0",
        default_output_dir: Path | None = None,
    ):
        """Initialize script base.

        Args:
            name: Script identifier (used for logging, config, output)
            description: Human-readable description
            version: Script version string
            default_output_dir: Default output directory (optional)
        """
        self.name = name
        self.description = description
        self.version = version
        self.default_output_dir = default_output_dir

        # Will be set during execution
        self.logger = None
        self.perf_logger = None
        self.config: ScriptConfig | None = None
        self.run_id: str | None = None
        self.output_path: Path | None = None
        self._warnings: list[str] = []
        self._errors: list[str] = []
        self._metrics: dict[str, Any] = {}

    def create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser with standard arguments."""
        parser = argparse.ArgumentParser(
            prog=self.name,
            description=self.description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=self._get_epilog(),
        )

        # Version
        parser.add_argument(
            "--version", action="version",
            version=f"%(prog)s {self.version}"
        )

        # Execution mode
        exec_group = parser.add_argument_group("Execution Options")
        exec_group.add_argument(
            "--dry-run", "-n", action="store_true",
            help="Show what would be done without executing"
        )
        exec_group.add_argument(
            "--timeout", "-t", type=int, default=300,
            help="Execution timeout in seconds (default: 300)"
        )
        exec_group.add_argument(
            "--max-retries", type=int, default=3,
            help="Maximum retry attempts on failure (default: 3)"
        )

        # Output settings
        output_group = parser.add_argument_group("Output Options")
        output_group.add_argument(
            "--output-dir", "-o", type=Path,
            help="Output directory for results and logs"
        )
        output_group.add_argument(
            "--output-format", choices=["json", "yaml", "text"],
            default="json", help="Output format (default: json)"
        )
        output_group.add_argument(
            "--no-save", action="store_true",
            help="Don't save output files"
        )

        # Logging settings
        log_group = parser.add_argument_group("Logging Options")
        log_group.add_argument(
            "--log-level", "-l",
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            default="INFO", help="Logging level (default: INFO)"
        )
        log_group.add_argument(
            "--log-file", type=Path,
            help="Log file path (default: auto-generated in output dir)"
        )
        log_group.add_argument(
            "--log-format", choices=["text", "json"],
            default="text", help="Log format (default: text)"
        )
        log_group.add_argument(
            "--verbose", "-v", action="store_true",
            help="Enable verbose output (sets log level to DEBUG)"
        )
        log_group.add_argument(
            "--quiet", "-q", action="store_true",
            help="Suppress non-error output"
        )

        # Configuration
        config_group = parser.add_argument_group("Configuration Options")
        config_group.add_argument(
            "--config", "-c", type=Path,
            help="Configuration file path (YAML or JSON)"
        )
        config_group.add_argument(
            "--env-prefix", default=self.name.upper().replace("-", "_"),
            help=f"Environment variable prefix (default: {self.name.upper().replace('-', '_')})"
        )

        # Add custom arguments
        self.add_arguments(parser)

        return parser

    def _get_epilog(self) -> str:
        """Generate parser epilog with examples."""
        return f"""
Examples:
  {self.name}                          # Run with defaults
  {self.name} --dry-run                # Preview without executing
  {self.name} --verbose                # Verbose output
  {self.name} --config config.yaml     # Use config file
  {self.name} --output-dir ./results   # Custom output directory
  {self.name} --output-format yaml     # Output in YAML format

Environment Variables:
  {self.name.upper().replace('-', '_')}_*  # Script-specific settings
  CODOMYRMEX_LOG_LEVEL                     # Global log level
  CODOMYRMEX_LOG_FILE                      # Global log file
"""

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Override to add custom arguments.

        Args:
            parser: Argument parser to extend
        """
        return None  # Override in subclass to add CLI arguments

    def load_config(self, args: argparse.Namespace) -> ScriptConfig:
        """Load configuration from multiple sources.

        Priority (highest to lowest):
        1. Command line arguments
        2. Environment variables
        3. Config file
        4. Defaults

        Args:
            args: Parsed command line arguments

        Returns:
            Merged configuration
        """
        config_data = {}

        # Load from config file
        if args.config and args.config.exists():
            config_data.update(self._load_config_file(args.config))

        # Load from environment
        env_prefix = getattr(args, 'env_prefix', self.name.upper().replace("-", "_"))
        config_data.update(self._load_env_config(env_prefix))

        # Apply CLI arguments (highest priority)
        cli_config = {
            "dry_run": args.dry_run,
            "verbose": args.verbose,
            "quiet": args.quiet,
            "output_dir": args.output_dir,
            "output_format": args.output_format,
            "save_output": not args.no_save,
            "log_level": "DEBUG" if args.verbose else args.log_level,
            "log_file": args.log_file,
            "log_format": args.log_format,
            "timeout": args.timeout,
            "max_retries": args.max_retries,
        }

        # Only override if explicitly set
        for key, value in cli_config.items():
            if value is not None:
                config_data[key] = value

        return ScriptConfig.from_dict(config_data)

    def _load_config_file(self, path: Path) -> dict[str, Any]:
        """Load configuration from file."""
        try:
            with open(path) as f:
                if path.suffix in (".yaml", ".yml"):
                    return yaml.safe_load(f) or {}
                elif path.suffix == ".json":
                    return json.load(f)
                else:
                    self.log_warning(f"Unknown config format: {path.suffix}")
                    return {}
        except Exception as e:
            logger.warning("Failed to load config file %s: %s", path, e)
            self.log_warning(f"Failed to load config file: {e}")
            return {}

    def _load_env_config(self, prefix: str) -> dict[str, Any]:
        """Load configuration from environment variables."""
        config = {}
        prefix = prefix.upper() + "_"

        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower()
                # Parse boolean values
                if value.lower() in ("true", "1", "yes"):
                    config[config_key] = True
                elif value.lower() in ("false", "0", "no"):
                    config[config_key] = False
                # Parse numeric values
                elif value.isdigit():
                    config[config_key] = int(value)
                else:
                    try:
                        config[config_key] = float(value)
                    except ValueError:
                        config[config_key] = value

        return config

    def setup_output_directory(self) -> Path:
        """Set up output directory for this run."""
        self.run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        if self.config.output_dir:
            base_dir = Path(self.config.output_dir)
        elif self.default_output_dir:
            base_dir = self.default_output_dir
        else:
            # Default to scripts/output/{script_name}
            base_dir = Path(__file__).parent.parent.parent.parent.parent / "scripts" / "output" / self.name

        self.output_path = base_dir / self.run_id
        self.output_path.mkdir(parents=True, exist_ok=True)

        return self.output_path

    def setup_logging(self) -> None:
        """Set up logging for this script."""
        # Set log level via environment for global setup
        os.environ["CODOMYRMEX_LOG_LEVEL"] = self.config.log_level

        if self.config.log_format == "json":
            os.environ["CODOMYRMEX_LOG_FORMAT"] = "JSON"

        # Set up file logging if output is enabled
        if self.config.save_output and self.output_path:
            log_file = self.config.log_file or (self.output_path / f"{self.name}.log")
            os.environ["CODOMYRMEX_LOG_FILE"] = str(log_file)

        setup_logging()
        self.logger = get_logger(self.name)
        self.perf_logger = PerformanceLogger(f"{self.name}.performance")

    def log_info(self, message: str) -> None:
        """Log info message."""
        if self.logger and not self.config.quiet:
            self.logger.info(message)
        if not self.config.quiet:
            print(f"ℹ️  {message}")

    def log_success(self, message: str) -> None:
        """Log success message."""
        if self.logger:
            self.logger.info(f"SUCCESS: {message}")
        print(f"✅ {message}")

    def log_warning(self, message: str) -> None:
        """Log warning message."""
        self._warnings.append(message)
        if self.logger:
            self.logger.warning(message)
        if not self.config.quiet:
            print(f"⚠️  {message}")

    def log_error(self, message: str) -> None:
        """Log error message."""
        self._errors.append(message)
        if self.logger:
            self.logger.error(message)
        print(f"❌ {message}")

    def log_debug(self, message: str) -> None:
        """Log debug message."""
        if self.logger:
            self.logger.debug(message)
        if self.config.verbose:
            print(f"🔍 {message}")

    def add_metric(self, name: str, value: Any) -> None:
        """Add a metric to the result."""
        self._metrics[name] = value

    def save_result(self, result: ScriptResult) -> Path | None:
        """Save execution result to file."""
        if not self.config.save_output or not self.output_path:
            return None

        # Determine output file path
        ext = {"json": ".json", "yaml": ".yaml", "text": ".txt"}[self.config.output_format]
        result_file = self.output_path / f"result{ext}"

        try:
            with open(result_file, "w") as f:
                if self.config.output_format == "json":
                    json.dump(result.to_dict(), f, indent=2, default=str)
                elif self.config.output_format == "yaml":
                    yaml.dump(result.to_dict(), f, default_flow_style=False)
                else:
                    f.write(self._format_text_result(result))

            self.log_debug(f"Result saved to: {result_file}")
            return result_file
        except Exception as e:
            logger.warning("Failed to save result to %s: %s", result_file, e)
            self.log_warning(f"Failed to save result: {e}")
            return None

    def _format_text_result(self, result: ScriptResult) -> str:
        """Format result as human-readable text."""
        lines = [
            f"Script: {result.script_name}",
            f"Status: {result.status}",
            f"Duration: {result.duration_seconds:.2f}s",
            f"Exit Code: {result.exit_code}",
            "",
            "Data:",
            json.dumps(result.data, indent=2, default=str),
        ]

        if result.errors:
            lines.extend(["", "Errors:", *[f"  - {e}" for e in result.errors]])

        if result.warnings:
            lines.extend(["", "Warnings:", *[f"  - {w}" for w in result.warnings]])

        if result.metrics:
            lines.extend(["", "Metrics:", json.dumps(result.metrics, indent=2)])

        return "\n".join(lines)

    @abstractmethod
    def run(self, args: argparse.Namespace, config: ScriptConfig) -> dict[str, Any]:
        """Execute the script logic.

        Override this method to implement script functionality.

        Args:
            args: Parsed command line arguments
            config: Loaded configuration

        Returns:
            Dictionary with execution results/data
        """
        pass

    def execute(self, argv: list[str] | None = None) -> int:
        """Execute the script with full lifecycle management.

        Args:
            argv: Command line arguments (defaults to sys.argv[1:])

        Returns:
            Exit code (0 for success, non-zero for failure)
        """
        start_time = datetime.now()
        exit_code = 0
        result_data = {}
        status = "success"

        try:
            # Parse arguments
            parser = self.create_parser()
            args = parser.parse_args(argv)

            # Load configuration
            self.config = self.load_config(args)

            # Set up output directory
            if self.config.save_output:
                self.setup_output_directory()

            # Set up logging
            self.setup_logging()

            self.log_info(f"{self.name} v{self.version}")
            self.log_info("=" * 50)

            if self.config.dry_run:
                self.log_info("DRY RUN MODE - No changes will be made")

            if self.config.verbose:
                self.log_debug(f"Configuration: {self.config.to_dict()}")

            # Execute with performance tracking
            with self.perf_logger.time_operation(f"{self.name}_execution"):
                result_data = self.run(args, self.config)

            self.log_success(f"{self.name} completed successfully")

        except KeyboardInterrupt:
            status = "interrupted"
            exit_code = 130
            self.log_warning("Execution interrupted by user")

        except TimeoutError as e:
            status = "timeout"
            exit_code = 124
            self.log_error(f"Execution timed out: {e}")

        except Exception as e:
            status = "error"
            exit_code = 1
            self.log_error(f"Execution failed: {e}")
            if self.config and self.config.verbose:
                traceback.print_exc()

        finally:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # Build result
            result = ScriptResult(
                script_name=self.name,
                status=status,
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                duration_seconds=duration,
                exit_code=exit_code,
                data=result_data or {},
                errors=self._errors,
                warnings=self._warnings,
                metrics=self._metrics,
                config_used=self.config.to_dict() if self.config else {},
            )

            # Save result
            if self.config and self.config.save_output:
                result_path = self.save_result(result)
                if result_path:
                    self.log_info(f"Results saved to: {result_path}")

            # Print summary
            if not (self.config and self.config.quiet):
                print()
                print(f"Duration: {duration:.2f}s")
                if self.output_path:
                    print(f"Output: {self.output_path}")

        return exit_code


class ConfigurableScript(ScriptBase):
    """Extended script base with additional configuration helpers."""

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get a configuration value with fallback to default.

        Args:
            key: Configuration key (supports dot notation for nested)
            default: Default value if not found

        Returns:
            Configuration value
        """
        if not self.config:
            return default

        # Check custom config first
        if key in self.config.custom:
            return self.config.custom[key]

        # Check standard config
        if hasattr(self.config, key):
            return getattr(self.config, key)

        # Handle dot notation
        parts = key.split(".")
        value = self.config.custom
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
        return value

    def require_config(self, key: str, message: str | None = None) -> Any:
        """Get a required configuration value.

        Args:
            key: Configuration key
            message: Custom error message

        Returns:
            Configuration value

        Raises:
            ValueError: If configuration is missing
        """
        value = self.get_config_value(key)
        if value is None:
            raise ValueError(message or f"Required configuration missing: {key}")
        return value


# Convenience function for simple scripts
def run_script(
    name: str,
    description: str,
    run_func: Callable[[argparse.Namespace, ScriptConfig], dict[str, Any]],
    add_args_func: Callable[[argparse.ArgumentParser], None] | None = None,
    version: str = "1.0.0",
) -> int:
    """Convenience function to run a simple script.

    Args:
        name: Script name
        description: Script description
        run_func: Main execution function
        add_args_func: Optional function to add custom arguments
        version: Script version

    Returns:
        Exit code
    """
    class SimpleScript(ScriptBase):
        """Functional component: SimpleScript."""
        def add_arguments(self, parser):
            if add_args_func:
                add_args_func(parser)

        def run(self, args, config):
            return run_func(args, config)

    script = SimpleScript(name=name, description=description, version=version)
    return script.execute()
