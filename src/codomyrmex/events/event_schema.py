from typing import Dict, List, Any, Optional, Union, Tuple
import json
import logging

from dataclasses import dataclass, field
from enum import Enum
import jsonschema

from codomyrmex.logging_monitoring.logger_config import get_logger




























"""
Event Schema for Codomyrmex Event System

This module defines event types, schemas, and validation for the Codomyrmex
event-driven architecture.
"""


# Import logging
try:
    logger = get_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)


class EventPriority(Enum):
    """Event priority levels for logging and processing."""

    DEBUG = "debug"
    INFO = "info"
    NORMAL = "normal"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class EventType(Enum):
    """Standard event types in Codomyrmex."""

    # System events
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"
    SYSTEM_ERROR = "system.error"
    SYSTEM_CONFIG_CHANGE = "system.config_change"

    # Module events
    MODULE_LOAD = "module.load"
    MODULE_UNLOAD = "module.unload"
    MODULE_ERROR = "module.error"
    MODULE_CONFIG_UPDATE = "module.config_update"

    # Plugin events
    PLUGIN_LOAD = "plugin.load"
    PLUGIN_UNLOAD = "plugin.unload"
    PLUGIN_EXECUTE = "plugin.execute"
    PLUGIN_ERROR = "plugin.error"

    # Analysis events
    ANALYSIS_START = "analysis.start"
    ANALYSIS_PROGRESS = "analysis.progress"
    ANALYSIS_COMPLETE = "analysis.complete"
    ANALYSIS_ERROR = "analysis.error"

    # Build events
    BUILD_START = "build.start"
    BUILD_PROGRESS = "build.progress"
    BUILD_COMPLETE = "build.complete"
    BUILD_ERROR = "build.error"

    # Deployment events
    DEPLOY_START = "deploy.start"
    DEPLOY_PROGRESS = "deploy.progress"
    DEPLOY_COMPLETE = "deploy.complete"
    DEPLOY_ERROR = "deploy.error"
    DEPLOY_ROLLBACK = "deploy.rollback"

    # Monitoring events
    METRIC_UPDATE = "metric.update"
    ALERT_TRIGGERED = "alert.triggered"
    HEALTH_CHECK = "health.check"
    PERFORMANCE_DEGRADATION = "performance.degradation"

    # User interaction events
    USER_ACTION = "user.action"
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    USER_ERROR = "user.error"

    # Data events
    DATA_RECEIVED = "data.received"
    DATA_PROCESSED = "data.processed"
    DATA_STORED = "data.stored"
    DATA_ERROR = "data.error"

    # Security events
    SECURITY_VIOLATION = "security.violation"
    SECURITY_SCAN_COMPLETE = "security.scan_complete"
    SECURITY_ALERT = "security.alert"

    # Custom events (for extensions)
    CUSTOM = "custom"


@dataclass
class Event:
    """Represents an event in the system."""

    event_type: EventType
    source: str
    event_id: str = field(default_factory=lambda: str(__import__('uuid').uuid4()))
    timestamp: float = field(default_factory=lambda: __import__('time').time())
    correlation_id: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: Union[int, EventPriority] = 0  # 0=normal, 1=high, 2=critical or EventPriority

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_type": self.event_type.value,
            "source": self.source,
            "timestamp": self.timestamp,
            "correlation_id": self.correlation_id,
            "data": self.data,
            "metadata": self.metadata,
            "priority": self.priority
        }

    def to_json(self) -> str:
        """Convert event to JSON string."""
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create event from dictionary."""
        event_type = EventType(data["event_type"])
        return cls(
            event_type=event_type,
            source=data["source"],
            event_id=data.get("event_id", str(__import__('uuid').uuid4())),
            timestamp=data.get("timestamp", __import__('time').time()),
            correlation_id=data.get("correlation_id"),
            data=data.get("data", {}),
            metadata=data.get("metadata", {}),
            priority=data.get("priority", 0)
        )

    @classmethod
    def from_json(cls, json_str: str) -> 'Event':
        """Create event from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)


class EventSchema:
    """
    Schema validation for events.

    Provides JSON Schema validation for different event types to ensure
    data consistency and type safety.
    """

    def __init__(self):
        """Initialize the event schema validator."""
        self.schemas: Dict[str, Dict[str, Any]] = {}
        self._load_standard_schemas()

    def validate_event(self, event: Event) -> Tuple[bool, List[str]]:
        """
        Validate an event against its schema.

        Args:
            event: Event to validate

        Returns:
            Tuple of (is_valid, list_of_validation_errors)
        """
        schema = self.schemas.get(event.event_type.value)
        if not schema:
            # No schema defined for this event type - allow it
            return True, []

        try:
            # Validate the event data against the schema
            jsonschema.validate(event.data, schema)
            return True, []
        except jsonschema.ValidationError as e:
            return False, [f"Schema validation failed: {e.message}"]
        except Exception as e:
            return False, [f"Validation error: {str(e)}"]

    def register_event_schema(self, event_type: EventType, schema: Dict[str, Any]) -> None:
        """
        Register a schema for an event type.

        Args:
            event_type: Event type to register schema for
            schema: JSON Schema definition
        """
        self.schemas[event_type.value] = schema
        logger.info(f"Registered schema for event type: {event_type.value}")

    def get_event_schema(self, event_type: EventType) -> Optional[Dict[str, Any]]:
        """
        Get the schema for an event type.

        Args:
            event_type: Event type

        Returns:
            Schema definition or None if not registered
        """
        return self.schemas.get(event_type.value)

    def list_registered_schemas(self) -> List[str]:
        """
        List all registered event type schemas.

        Returns:
            List of registered event type names
        """
        return list(self.schemas.keys())

    def _load_standard_schemas(self) -> None:
        """Load standard schemas for common event types."""

        # System startup event
        self.schemas[EventType.SYSTEM_STARTUP.value] = {
            "type": "object",
            "properties": {
                "version": {"type": "string"},
                "startup_time": {"type": "number"},
                "components_loaded": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["version"]
        }

        # Module load event
        self.schemas[EventType.MODULE_LOAD.value] = {
            "type": "object",
            "properties": {
                "module_name": {"type": "string"},
                "module_version": {"type": "string"},
                "load_time": {"type": "number"},
                "dependencies": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["module_name"]
        }

        # Analysis start event
        self.schemas[EventType.ANALYSIS_START.value] = {
            "type": "object",
            "properties": {
                "analysis_type": {"type": "string"},
                "target": {"type": "string"},
                "parameters": {"type": "object"},
                "estimated_duration": {"type": "number"}
            },
            "required": ["analysis_type", "target"]
        }

        # Analysis complete event
        self.schemas[EventType.ANALYSIS_COMPLETE.value] = {
            "type": "object",
            "properties": {
                "analysis_type": {"type": "string"},
                "target": {"type": "string"},
                "results": {"type": "object"},
                "duration": {"type": "number"},
                "success": {"type": "boolean"}
            },
            "required": ["analysis_type", "target", "success"]
        }

        # Build start event
        self.schemas[EventType.BUILD_START.value] = {
            "type": "object",
            "properties": {
                "build_type": {"type": "string"},
                "target": {"type": "string"},
                "parameters": {"type": "object"},
                "build_id": {"type": "string"}
            },
            "required": ["build_type", "target"]
        }

        # Build complete event
        self.schemas[EventType.BUILD_COMPLETE.value] = {
            "type": "object",
            "properties": {
                "build_type": {"type": "string"},
                "target": {"type": "string"},
                "build_id": {"type": "string"},
                "success": {"type": "boolean"},
                "artifacts": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "duration": {"type": "number"}
            },
            "required": ["build_type", "target", "build_id", "success"]
        }

        # Error events
        error_schema = {
            "type": "object",
            "properties": {
                "error_type": {"type": "string"},
                "error_message": {"type": "string"},
                "stack_trace": {"type": "string"},
                "context": {"type": "object"},
                "severity": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "critical"]
                }
            },
            "required": ["error_message"]
        }

        self.schemas[EventType.SYSTEM_ERROR.value] = error_schema
        self.schemas[EventType.MODULE_ERROR.value] = error_schema
        self.schemas[EventType.PLUGIN_ERROR.value] = error_schema
        self.schemas[EventType.ANALYSIS_ERROR.value] = error_schema
        self.schemas[EventType.BUILD_ERROR.value] = error_schema

        # Metric update event
        self.schemas[EventType.METRIC_UPDATE.value] = {
            "type": "object",
            "properties": {
                "metric_name": {"type": "string"},
                "metric_value": {"type": ["number", "string", "boolean"]},
                "metric_type": {
                    "type": "string",
                    "enum": ["counter", "gauge", "histogram", "summary"]
                },
                "labels": {"type": "object"},
                "timestamp": {"type": "number"}
            },
            "required": ["metric_name", "metric_value"]
        }

        # Alert triggered event
        self.schemas[EventType.ALERT_TRIGGERED.value] = {
            "type": "object",
            "properties": {
                "alert_name": {"type": "string"},
                "alert_level": {
                    "type": "string",
                    "enum": ["info", "warning", "error", "critical"]
                },
                "message": {"type": "string"},
                "threshold": {"type": ["number", "string"]},
                "current_value": {"type": ["number", "string"]},
                "context": {"type": "object"}
            },
            "required": ["alert_name", "alert_level", "message"]
        }

        logger.info(f"Loaded {len(self.schemas)} standard event schemas")


# Convenience functions for creating common events

def create_system_startup_event(version: str, components: List[str]) -> Event:
    """Create a system startup event."""
    return Event(
        event_type=EventType.SYSTEM_STARTUP,
        source="system",
        data={
            "version": version,
            "components_loaded": components,
            "startup_time": __import__('time').time()
        }
    )


def create_module_load_event(module_name: str, version: str, load_time: float) -> Event:
    """Create a module load event."""
    return Event(
        event_type=EventType.MODULE_LOAD,
        source="module_loader",
        data={
            "module_name": module_name,
            "module_version": version,
            "load_time": load_time
        }
    )


def create_analysis_start_event(analysis_type: str, target: str, parameters: Optional[Dict[str, Any]] = None) -> Event:
    """Create an analysis start event."""
    return Event(
        event_type=EventType.ANALYSIS_START,
        source="analysis_engine",
        data={
            "analysis_type": analysis_type,
            "target": target,
            "parameters": parameters or {}
        }
    )


def create_analysis_complete_event(analysis_type: str, target: str, results: Dict[str, Any], duration: float, success: bool) -> Event:
    """Create an analysis complete event."""
    return Event(
        event_type=EventType.ANALYSIS_COMPLETE,
        source="analysis_engine",
        data={
            "analysis_type": analysis_type,
            "target": target,
            "results": results,
            "duration": duration,
            "success": success
        }
    )


def create_error_event(event_type: EventType, source: str, error_message: str, error_type: str = "unknown", context: Optional[Dict[str, Any]] = None) -> Event:
    """Create an error event."""
    return Event(
        event_type=event_type,
        source=source,
        data={
            "error_type": error_type,
            "error_message": error_message,
            "context": context or {}
        },
        priority=2  # High priority for errors
    )


def create_metric_event(metric_name: str, value: Union[int, float, str, bool], metric_type: str = "gauge", labels: Optional[Dict[str, str]] = None) -> Event:
    """Create a metric update event."""
    return Event(
        event_type=EventType.METRIC_UPDATE,
        source="metrics_collector",
        data={
            "metric_name": metric_name,
            "metric_value": value,
            "metric_type": metric_type,
            "labels": labels or {},
            "timestamp": __import__('time').time()
        }
    )


def create_alert_event(alert_name: str, level: str, message: str, threshold: Any = None, current_value: Any = None) -> Event:
    """Create an alert event."""
    priority_map = {"info": 0, "warning": 1, "error": 2, "critical": 2}

    return Event(
        event_type=EventType.ALERT_TRIGGERED,
        source="alert_manager",
        data={
            "alert_name": alert_name,
            "alert_level": level,
            "message": message,
            "threshold": threshold,
            "current_value": current_value
        },
        priority=priority_map.get(level, 0)
    )
