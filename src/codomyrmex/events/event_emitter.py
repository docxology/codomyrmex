"""
Event Emitter for Codomyrmex Event System

This module provides components with the ability to emit events to the event bus
in a convenient and standardized way.
"""

import uuid
from typing import Dict, List, Any, Optional, Union

# Import logging
try:
    from codomyrmex.logging_monitoring.logger_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from .event_bus import get_event_bus, EventBus
from .event_schema import Event, EventType


class EventEmitter:
    """
    Event emitter for components that want to publish events.

    Provides a convenient interface for emitting events with automatic
    correlation ID generation, metadata handling, and batch operations.
    """

    def __init__(self, source: str, event_bus: Optional[EventBus] = None):
        """
        Initialize the event emitter.

        Args:
            source: Source identifier for emitted events
            event_bus: Event bus to publish to (uses global if None)
        """
        self.source = source
        self.event_bus = event_bus or get_event_bus()
        self.default_correlation_id: Optional[str] = None
        self.default_metadata: Dict[str, Any] = {}
        self.enabled = True

        logger.debug(f"EventEmitter initialized for source: {source}")

    def emit(self, event_type: EventType, data: Optional[Dict[str, Any]] = None,
             correlation_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None,
             priority: int = 0) -> None:
        """
        Emit a single event.

        Args:
            event_type: Type of event to emit
            data: Event data payload
            correlation_id: Correlation ID for event tracing
            metadata: Additional metadata
            priority: Event priority (0=normal, 1=high, 2=critical)
        """
        if not self.enabled:
            return

        event = self._create_event(
            event_type=event_type,
            data=data or {},
            correlation_id=correlation_id,
            metadata=metadata,
            priority=priority
        )

        try:
            self.event_bus.publish(event)
            logger.debug(f"Emitted event: {event_type.value} from {self.source}")
        except Exception as e:
            logger.error(f"Failed to emit event {event_type.value}: {e}")

    def emit_sync(self, event_type: EventType, data: Optional[Dict[str, Any]] = None,
                 correlation_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None,
                 priority: int = 0) -> None:
        """
        Emit a single event synchronously.

        Args:
            event_type: Type of event to emit
            data: Event data payload
            correlation_id: Correlation ID for event tracing
            metadata: Additional metadata
            priority: Event priority (0=normal, 1=high, 2=critical)
        """
        self.emit(event_type, data, correlation_id, metadata, priority)

    async def emit_async(self, event_type: EventType, data: Optional[Dict[str, Any]] = None,
                        correlation_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None,
                        priority: int = 0) -> None:
        """
        Emit a single event asynchronously.

        Args:
            event_type: Type of event to emit
            data: Event data payload
            correlation_id: Correlation ID for event tracing
            metadata: Additional metadata
            priority: Event priority (0=normal, 1=high, 2=critical)
        """
        if not self.enabled:
            return

        event = self._create_event(
            event_type=event_type,
            data=data or {},
            correlation_id=correlation_id,
            metadata=metadata,
            priority=priority
        )

        try:
            await self.event_bus.publish_async(event)
            logger.debug(f"Emitted async event: {event_type.value} from {self.source}")
        except Exception as e:
            logger.error(f"Failed to emit async event {event_type.value}: {e}")

    def emit_batch(self, events: List[Dict[str, Any]]) -> None:
        """
        Emit multiple events in batch.

        Args:
            events: List of event dictionaries with keys: event_type, data, correlation_id, metadata, priority
        """
        if not self.enabled:
            return

        for event_data in events:
            self.emit(
                event_type=event_data["event_type"],
                data=event_data.get("data"),
                correlation_id=event_data.get("correlation_id"),
                metadata=event_data.get("metadata"),
                priority=event_data.get("priority", 0)
            )

    async def emit_batch_async(self, events: List[Dict[str, Any]]) -> None:
        """
        Emit multiple events in batch asynchronously.

        Args:
            events: List of event dictionaries with keys: event_type, data, correlation_id, metadata, priority
        """
        if not self.enabled:
            return

        tasks = []
        for event_data in events:
            event = self._create_event(
                event_type=event_data["event_type"],
                data=event_data.get("data", {}),
                correlation_id=event_data.get("correlation_id"),
                metadata=event_data.get("metadata"),
                priority=event_data.get("priority", 0)
            )

            tasks.append(self.event_bus.publish_async(event))

        if tasks:
            try:
                await asyncio.gather(*tasks, return_exceptions=True)
                logger.debug(f"Emitted {len(tasks)} events in batch from {self.source}")
            except Exception as e:
                logger.error(f"Failed to emit batch events: {e}")

    def start_operation(self, operation_name: str, operation_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Start an operation and emit a start event.

        Args:
            operation_name: Name of the operation
            operation_data: Additional operation data

        Returns:
            Correlation ID for the operation
        """
        correlation_id = self._generate_correlation_id()
        self.set_correlation_context(correlation_id)

        self.emit(
            EventType.CUSTOM,
            data={
                "operation": operation_name,
                "phase": "start",
                "operation_data": operation_data or {}
            },
            correlation_id=correlation_id,
            metadata={"operation_type": "start"}
        )

        return correlation_id

    def update_operation(self, correlation_id: str, operation_name: str,
                        progress: Optional[float] = None, status: Optional[str] = None,
                        data: Optional[Dict[str, Any]] = None) -> None:
        """
        Update operation progress.

        Args:
            correlation_id: Operation correlation ID
            operation_name: Name of the operation
            progress: Progress percentage (0-100)
            status: Status message
            data: Additional data
        """
        event_data = {
            "operation": operation_name,
            "phase": "progress",
            "correlation_id": correlation_id
        }

        if progress is not None:
            event_data["progress"] = progress
        if status is not None:
            event_data["status"] = status
        if data:
            event_data.update(data)

        self.emit(
            EventType.CUSTOM,
            data=event_data,
            correlation_id=correlation_id,
            metadata={"operation_type": "progress"}
        )

    def end_operation(self, correlation_id: str, operation_name: str,
                     success: bool = True, result: Optional[Any] = None,
                     error: Optional[str] = None) -> None:
        """
        End an operation and emit a completion event.

        Args:
            correlation_id: Operation correlation ID
            operation_name: Name of the operation
            success: Whether the operation succeeded
            result: Operation result
            error: Error message if failed
        """
        event_data = {
            "operation": operation_name,
            "phase": "end",
            "success": success
        }

        if result is not None:
            event_data["result"] = result
        if error is not None:
            event_data["error"] = error

        self.emit(
            EventType.CUSTOM,
            data=event_data,
            correlation_id=correlation_id,
            metadata={"operation_type": "end", "success": success},
            priority=2 if not success else 0  # High priority for failures
        )

        self.clear_correlation_context()

    def emit_error(self, error_type: str, error_message: str,
                  context: Optional[Dict[str, Any]] = None,
                  correlation_id: Optional[str] = None) -> None:
        """
        Emit an error event.

        Args:
            error_type: Type of error
            error_message: Error message
            context: Additional error context
            correlation_id: Correlation ID
        """
        self.emit(
            EventType.SYSTEM_ERROR,
            data={
                "error_type": error_type,
                "error_message": error_message,
                "context": context or {}
            },
            correlation_id=correlation_id,
            priority=2  # High priority for errors
        )

    def emit_metric(self, metric_name: str, value: Union[int, float, str, bool],
                   metric_type: str = "gauge", labels: Optional[Dict[str, str]] = None) -> None:
        """
        Emit a metric event.

        Args:
            metric_name: Name of the metric
            value: Metric value
            metric_type: Type of metric (gauge, counter, histogram, summary)
            labels: Metric labels for categorization
        """
        self.emit(
            EventType.METRIC_UPDATE,
            data={
                "metric_name": metric_name,
                "metric_value": value,
                "metric_type": metric_type,
                "labels": labels or {}
            }
        )

    def emit_alert(self, alert_name: str, level: str, message: str,
                  threshold: Optional[Any] = None, current_value: Optional[Any] = None) -> None:
        """
        Emit an alert event.

        Args:
            alert_name: Name of the alert
            level: Alert level (info, warning, error, critical)
            message: Alert message
            threshold: Threshold value that triggered the alert
            current_value: Current value that exceeded threshold
        """
        priority_map = {"info": 0, "warning": 1, "error": 2, "critical": 2}

        self.emit(
            EventType.ALERT_TRIGGERED,
            data={
                "alert_name": alert_name,
                "alert_level": level,
                "message": message,
                "threshold": threshold,
                "current_value": current_value
            },
            priority=priority_map.get(level, 0)
        )

    def set_correlation_context(self, correlation_id: str) -> None:
        """
        Set the default correlation ID for subsequent events.

        Args:
            correlation_id: Correlation ID to use
        """
        self.default_correlation_id = correlation_id

    def clear_correlation_context(self) -> None:
        """Clear the default correlation context."""
        self.default_correlation_id = None

    def set_default_metadata(self, metadata: Dict[str, Any]) -> None:
        """
        Set default metadata for all emitted events.

        Args:
            metadata: Default metadata dictionary
        """
        self.default_metadata = metadata.copy()

    def enable(self) -> None:
        """Enable event emission."""
        self.enabled = True

    def disable(self) -> None:
        """Disable event emission."""
        self.enabled = False

    def _create_event(self, event_type: EventType, data: Dict[str, Any],
                     correlation_id: Optional[str], metadata: Optional[Dict[str, Any]],
                     priority: int) -> Event:
        """Create an event with default values."""
        # Merge default metadata
        final_metadata = self.default_metadata.copy()
        if metadata:
            final_metadata.update(metadata)

        return Event(
            event_type=event_type,
            source=self.source,
            correlation_id=correlation_id or self.default_correlation_id,
            data=data,
            metadata=final_metadata,
            priority=priority
        )

    def _generate_correlation_id(self) -> str:
        """Generate a unique correlation ID."""
        return str(uuid.uuid4())


# Context manager for operation tracking
class EventOperationContext:
    """
    Context manager for tracking operations with automatic event emission.
    """

    def __init__(self, emitter: EventEmitter, operation_name: str,
                 operation_data: Optional[Dict[str, Any]] = None):
        """
        Initialize the operation context.

        Args:
            emitter: EventEmitter to use
            operation_name: Name of the operation
            operation_data: Additional operation data
        """
        self.emitter = emitter
        self.operation_name = operation_name
        self.operation_data = operation_data or {}
        self.correlation_id: Optional[str] = None
        self.start_time: Optional[float] = None

    def __enter__(self):
        """Brief description of __enter__.
        
        Args:
            self : Description of self
        
            Returns: Description of return value
        """
"""
        import time
        self.start_time = time.time()
        self.correlation_id = self.emitter.start_operation(self.operation_name, self.operation_data)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Brief description of __exit__.
        
        Args:
            self : Description of self
            exc_type : Description of exc_type
            exc_val : Description of exc_val
            exc_tb : Description of exc_tb
        
            Returns: Description of return value
        """
"""
        import time
        end_time = time.time()
        duration = end_time - (self.start_time or end_time)

        if exc_type is None:
            # Success
            self.emitter.end_operation(
                self.correlation_id,
                self.operation_name,
                success=True,
                result={"duration": duration}
            )
        else:
            # Failure
            error_msg = str(exc_val) if exc_val else "Unknown error"
            self.emitter.end_operation(
                self.correlation_id,
                self.operation_name,
                success=False,
                error=error_msg,
                result={"duration": duration}
            )


# Convenience functions
def create_emitter(source: str) -> EventEmitter:
    """
    Create an event emitter for a source.

    Args:
        source: Source identifier

    Returns:
        EventEmitter instance
    """
    return EventEmitter(source)


def emit_event(event_type: EventType, source: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> None:
    """
    Convenience function to emit a single event.

    Args:
        event_type: Type of event
        source: Event source
        data: Event data
        **kwargs: Additional event parameters
    """
    emitter = EventEmitter(source)
    emitter.emit(event_type, data, **kwargs)
