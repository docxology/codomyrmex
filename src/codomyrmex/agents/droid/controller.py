"""Droid controller and configuration utilities.

This module provides thread-safe droid controller with configuration management,
metrics tracking, and task execution capabilities.
"""
from __future__ import annotations

import json
import os
import time
from collections.abc import Iterable
from dataclasses import asdict, dataclass, replace
from enum import Enum
from pathlib import Path
from threading import RLock
from typing import Any
from collections.abc import Callable

from codomyrmex.logging_monitoring.logger_config import get_logger
from codomyrmex.performance import monitor_performance, performance_context

"""Droid controller and configuration utilities."""

"""Droid controller and configuration utilities."""


logger = get_logger(__name__)


class DroidMode(Enum):
    """Operating modes for the droid controller."""

    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TEST = "test"
    MAINTENANCE = "maintenance"


class DroidStatus(Enum):
    """Lifecycle status values for the droid controller."""

    STOPPED = "stopped"
    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"


def _to_bool(value: str) -> bool:
    """Convert string to boolean."""
    return value.lower() in ("1", "true", "yes", "on")


@dataclass(frozen=True)
class DroidConfig:
    """Immutable configuration for the droid controller."""

    identifier: str = "droid"
    mode: DroidMode = DroidMode.DEVELOPMENT
    llm_provider: str = "openai"
    llm_model: str = "gpt-3.5-turbo"
    safe_mode: bool = True
    telemetry_opt_in: bool = False
    max_parallel_tasks: int = 1
    max_retry_attempts: int = 3
    retry_backoff_seconds: float = 1.0
    heartbeat_interval_seconds: float = 30.0
    log_level: str = "INFO"
    allowed_operations: Iterable[str] | None = None
    blocked_operations: Iterable[str] | None = None

    def validate(self) -> None:
        """Validate.
        """
        if self.max_parallel_tasks < 1:
            raise ValueError("max_parallel_tasks must be at least 1")
        if self.max_retry_attempts < 0:
            raise ValueError("max_retry_attempts cannot be negative")
        if self.retry_backoff_seconds < 0:
            raise ValueError("retry_backoff_seconds cannot be negative")
        if self.heartbeat_interval_seconds <= 0:
            raise ValueError("heartbeat_interval_seconds must be greater than 0")

    @property
    def allowed(self) -> frozenset[str] | None:
        """Get allowed operations as a frozen set."""
        return (
            frozenset(self.allowed_operations)
            if self.allowed_operations is not None
            else None
        )

    @property
    def blocked(self) -> frozenset[str] | None:
        """Get blocked operations as a frozen set."""
        return (
            frozenset(self.blocked_operations)
            if self.blocked_operations is not None
            else None
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DroidConfig:
        """From Dict.

            Args:        cls: Parameter for the operation.        data: Data to process.

            Returns:        The result of the operation.
            """
        payload = dict(data)
        mode = payload.get("mode")
        if isinstance(mode, str):
            payload["mode"] = DroidMode(mode.lower())
        config = cls(**payload)
        config.validate()
        return config

    @classmethod
    def from_json(cls, raw: str) -> DroidConfig:
        """Create config from JSON string."""
        return cls.from_dict(json.loads(raw))

    @classmethod
    def from_file(cls, path: str | os.PathLike[str]) -> DroidConfig:
        """Create config from JSON file."""
        with open(path, encoding="utf-8") as handle:
            return cls.from_json(handle.read())

    @classmethod
    def from_env(cls, prefix: str = "DROID_") -> DroidConfig:
        """From Env.

            Args:        cls: Parameter for the operation.        prefix: Parameter for the operation.

            Returns:        The result of the operation.
            """
        mapping: dict[str, Any] = {}

        def set_if_present(name: str, transform: Callable[[str], Any]) -> None:
            """Set mapping value if environment variable is present."""
            env_val = os.environ.get(f"{prefix}{name.upper()}")
            if env_val is not None:
                mapping[name] = transform(env_val)

        set_if_present("identifier", str)
        set_if_present("mode", lambda v: DroidMode(v.lower()))
        set_if_present("llm_provider", str)
        set_if_present("llm_model", str)
        set_if_present("safe_mode", _to_bool)
        set_if_present("telemetry_opt_in", _to_bool)
        set_if_present("max_parallel_tasks", int)
        set_if_present("max_retry_attempts", int)
        set_if_present("retry_backoff_seconds", float)
        set_if_present("heartbeat_interval_seconds", float)
        set_if_present("log_level", str)

        return cls.from_dict(mapping) if mapping else cls()

    def with_overrides(self, **kwargs: Any) -> DroidConfig:
        """Return new config with overrides applied."""
        new_config = replace(self, **kwargs)
        new_config.validate()
        return new_config

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary."""
        data = asdict(self)
        data["mode"] = self.mode.value
        return data


@dataclass
class DroidMetrics:
    """Runtime metrics tracked for droid sessions."""

    sessions_started: int = 0
    sessions_completed: int = 0
    tasks_executed: int = 0
    tasks_failed: int = 0
    last_error: str | None = None
    last_task: str | None = None
    last_heartbeat_epoch: float | None = None

    def snapshot(self) -> dict[str, Any]:
        """Return snapshot of current metrics."""
        return asdict(self)

    def reset(self) -> None:
        """Reset.
            """
        self.sessions_started = 0
        self.sessions_completed = 0
        self.tasks_executed = 0
        self.tasks_failed = 0
        self.last_error = None
        self.last_task = None
        self.last_heartbeat_epoch = None


class DroidController:
    """Thread-safe controller coordinating droid operations."""

    def __init__(self, config: DroidConfig):
        """  Init  .

            Args:        config: Configuration settings.
            """
        config.validate()
        self._config = config
        self._status = DroidStatus.STOPPED
        self._metrics = DroidMetrics()
        self._lock = RLock()
        self._active_tasks = 0
        self._last_status_change = time.time()

    @property
    def config(self) -> DroidConfig:
        """Get current configuration."""
        return self._config

    @property
    def status(self) -> DroidStatus:
        """Get current status."""
        return self._status

    @property
    def metrics(self) -> dict[str, Any]:
        """Get current metrics snapshot."""
        return self._metrics.snapshot()

    @property
    def last_status_change(self) -> float:
        """Get timestamp of last status change."""
        return self._last_status_change

    def update_config(self, **overrides: Any) -> DroidConfig:
        """Update configuration with overrides."""
        with self._lock:
            new_config = self._config.with_overrides(**overrides)
            self._config = new_config
            logger.info("droid config updated", extra={"config": new_config.to_dict()})
            return new_config

    def reset_metrics(self) -> None:
        """Reset all metrics to zero."""
        with self._lock:
            self._metrics.reset()
            logger.info("droid metrics reset")

    @monitor_performance("droid_start")
    def start(self) -> None:
        """Start the droid controller."""
        with self._lock:
            if self._status == DroidStatus.RUNNING:
                logger.debug("droid already running")
                return
            self._metrics.sessions_started += 1
            self._status = DroidStatus.IDLE
            self._last_status_change = time.time()
            logger.info("droid started", extra={"config": self._config.to_dict()})

    @monitor_performance("droid_stop")
    def stop(self) -> None:
        """Stop the droid controller."""
        with self._lock:
            if self._status == DroidStatus.STOPPED:
                logger.debug("droid already stopped")
                return
            self._status = DroidStatus.STOPPED
            self._active_tasks = 0
            self._metrics.sessions_completed += 1
            self._last_status_change = time.time()
            logger.info("droid stopped")

    def record_heartbeat(self) -> None:
        """Record a heartbeat timestamp."""
        with self._lock:
            self._metrics.last_heartbeat_epoch = time.time()
            logger.debug(
                "droid heartbeat",
                extra={"timestamp": self._metrics.last_heartbeat_epoch},
            )

    def _check_operation_permissions(self, operation_id: str) -> None:
        """Check if operation is permitted."""
        if (
            self._config.allowed is not None
            and operation_id not in self._config.allowed
        ):
            raise PermissionError(f"operation '{operation_id}' is not allowed")
        if self._config.blocked is not None and operation_id in self._config.blocked:
            raise PermissionError(f"operation '{operation_id}' is blocked")

    def _enter_execution(self) -> None:
        """Enter task execution state."""
        if self._active_tasks >= self._config.max_parallel_tasks:
            raise RuntimeError("maximum number of parallel tasks reached")
        self._active_tasks += 1
        self._status = DroidStatus.RUNNING
        self._last_status_change = time.time()

    def _exit_execution(self) -> None:
        """Exit task execution state."""
        self._active_tasks = max(0, self._active_tasks - 1)
        if self._status == DroidStatus.ERROR:
            return
        self._status = (
            DroidStatus.IDLE if self._active_tasks == 0 else DroidStatus.RUNNING
        )
        self._last_status_change = time.time()

    def _transition_to_error(self) -> None:
        """Transition to error state."""
        self._status = DroidStatus.ERROR
        self._last_status_change = time.time()

    @monitor_performance("droid_execute_task")
    def execute_task(
        self, operation_id: str, handler: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> Any:
        """Execute a task through the droid controller."""
        with self._lock:
            if self._status == DroidStatus.STOPPED:
                raise RuntimeError("droid is stopped")
            if self._config.safe_mode and handler.__name__.startswith("unsafe_"):
                raise PermissionError("unsafe handler rejected in safe mode")
            self._check_operation_permissions(operation_id)
            self._enter_execution()

        try:
            with performance_context("droid_task", operation_id=operation_id):
                result = handler(*args, **kwargs)
        except Exception as exc:  # pragma: no cover - handled in tests
            with self._lock:
                self._metrics.tasks_failed += 1
                self._metrics.last_error = str(exc)
                self._metrics.last_task = operation_id
                self._transition_to_error()
            logger.exception("droid task failed", extra={"operation_id": operation_id})
            raise
        else:
            with self._lock:
                self._metrics.tasks_executed += 1
                self._metrics.last_task = operation_id
                self._metrics.last_error = None
            logger.debug("droid task completed", extra={"operation_id": operation_id})
            return result
        finally:
            with self._lock:
                self._exit_execution()


def create_default_controller(**overrides: Any) -> DroidController:
    """Create Default Controller.

        Returns:        The result of the operation.
        """
    config = DroidConfig().with_overrides(**overrides) if overrides else DroidConfig()
    controller = DroidController(config)
    controller.start()
    return controller


def save_config_to_file(config: DroidConfig, path: str | os.PathLike[str]) -> None:
    """Save Config To File.

        Args:        config: Configuration settings.        path: Path to the file or directory.
        """
    data = json.dumps(config.to_dict(), indent=2)
    Path(path).write_text(data, encoding="utf-8")
    logger.info("droid config saved", extra={"path": str(path)})


def load_config_from_file(path: str | os.PathLike[str]) -> DroidConfig:

    return DroidConfig.from_file(path)


__all__ = [
    "DroidMode",
    "DroidStatus",
    "DroidConfig",
    "DroidMetrics",
    "DroidController",
    "create_default_controller",
    "save_config_to_file",
    "load_config_from_file",
]
