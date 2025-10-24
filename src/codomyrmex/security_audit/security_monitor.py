"""
Security Monitor for Codomyrmex Security Audit Module.

Provides real-time security monitoring, alerting, and audit logging capabilities.
"""

import os
import sys
import json
import threading
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
import hashlib
import re
from codomyrmex.exceptions import CodomyrmexError

# Add project root to Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    pass
#     sys.path.insert(0, PROJECT_ROOT)  # Removed sys.path manipulation

try:
    from logging_monitoring.logger_config import get_logger

    logger = get_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


class SecurityEventType(Enum):
    """Types of security events."""

    AUTHENTICATION_FAILURE = "authentication_failure"
    AUTHORIZATION_FAILURE = "authorization_failure"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    DATA_ACCESS_VIOLATION = "data_access_violation"
    CONFIGURATION_CHANGE = "configuration_change"
    VULNERABILITY_DETECTED = "vulnerability_detected"
    COMPLIANCE_VIOLATION = "compliance_violation"
    MALWARE_DETECTED = "malware_detected"
    BRUTE_FORCE_ATTACK = "brute_force_attack"
    SQL_INJECTION_ATTEMPT = "sql_injection_attempt"
    XSS_ATTEMPT = "xss_attempt"


class AlertLevel(Enum):
    """Alert severity levels."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class SecurityEvent:
    """Represents a security event."""

    event_id: str
    event_type: SecurityEventType
    timestamp: datetime
    source_ip: Optional[str] = None
    user_id: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    severity: AlertLevel = AlertLevel.MEDIUM
    details: Dict[str, Any] = field(default_factory=dict)
    raw_log: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary format."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "source_ip": self.source_ip,
            "user_id": self.user_id,
            "resource": self.resource,
            "action": self.action,
            "severity": self.severity.value,
            "details": self.details,
            "raw_log": self.raw_log,
        }


@dataclass
class AlertRule:
    """Represents an alert rule for security monitoring."""

    rule_id: str
    name: str
    description: str
    event_type: SecurityEventType
    conditions: Dict[str, Any]
    alert_level: AlertLevel
    enabled: bool = True
    cooldown_period: int = 300  # seconds
    last_triggered: Optional[datetime] = None


class SecurityMonitor:
    """
    Real-time security monitoring and alerting system.

    Features:
    - Real-time security event monitoring
    - Configurable alert rules
    - Automated incident response
    - Security audit logging
    - Threat intelligence integration
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the security monitor.

        Args:
            config_path: Path to monitor configuration file
        """
        self.config_path = config_path or os.path.join(
            os.getcwd(), "security_monitor_config.json"
        )
        self.config = self._load_config()

        self.events: List[SecurityEvent] = []
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, SecurityEvent] = {}

        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None

        # Alert callbacks
        self.alert_callbacks: List[Callable[[SecurityEvent], None]] = []

        # Load default alert rules
        self._load_default_alert_rules()

    def _load_config(self) -> Dict[str, Any]:
        """Load monitor configuration."""
        default_config = {
            "log_files": ["/var/log/auth.log", "/var/log/security.log"],
            "monitoring_interval": 10,  # seconds
            "max_events": 10000,
            "alert_cooldown": 300,  # 5 minutes
            "enable_auto_response": False,
            "threat_intelligence_enabled": True,
            "log_rotation_days": 30,
        }

        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Failed to load monitor config: {e}")

        return default_config

    def _load_default_alert_rules(self):
        """Load default security alert rules."""
        default_rules = [
            AlertRule(
                rule_id="auth_failure_burst",
                name="Authentication Failure Burst",
                description="Multiple authentication failures from same IP",
                event_type=SecurityEventType.AUTHENTICATION_FAILURE,
                conditions={"count_threshold": 5, "time_window": 300},
                alert_level=AlertLevel.HIGH,
            ),
            AlertRule(
                rule_id="suspicious_file_access",
                name="Suspicious File Access",
                description="Access to sensitive system files",
                event_type=SecurityEventType.DATA_ACCESS_VIOLATION,
                conditions={
                    "sensitive_files": ["/etc/passwd", "/etc/shadow", "/root/.ssh/"]
                },
                alert_level=AlertLevel.CRITICAL,
            ),
            AlertRule(
                rule_id="config_change",
                name="Configuration File Change",
                description="Unauthorized configuration file modification",
                event_type=SecurityEventType.CONFIGURATION_CHANGE,
                conditions={"config_files": ["*.conf", "*.yaml", "*.json"]},
                alert_level=AlertLevel.MEDIUM,
            ),
            AlertRule(
                rule_id="sql_injection",
                name="SQL Injection Attempt",
                description="Potential SQL injection attack detected",
                event_type=SecurityEventType.SQL_INJECTION_ATTEMPT,
                conditions={"patterns": ["UNION SELECT", "OR 1=1", "DROP TABLE"]},
                alert_level=AlertLevel.HIGH,
            ),
        ]

        for rule in default_rules:
            self.alert_rules[rule.rule_id] = rule

    def start_monitoring(self):
        """Start the security monitoring system."""
        if self.monitoring_active:
            logger.warning("Security monitoring is already active")
            return

        logger.info("Starting security monitoring system")
        self.monitoring_active = True

        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True
        )
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop the security monitoring system."""
        if not self.monitoring_active:
            logger.info("Security monitoring is not active")
            return

        logger.info("Stopping security monitoring system")
        self.monitoring_active = False

        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=10)

    def _monitoring_loop(self):
        """Main monitoring loop."""
        logger.info("Security monitoring loop started")

        while self.monitoring_active:
            try:
                # Collect security events from various sources
                self._collect_system_logs()
                self._collect_application_logs()
                self._check_system_integrity()

                # Process collected events
                self._process_events()

                # Check for threats
                self._check_threat_intelligence()

                # Clean up old events
                self._cleanup_old_events()

                # Sleep before next iteration
                time.sleep(self.config.get("monitoring_interval", 10))

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(30)  # Wait longer on error

        logger.info("Security monitoring loop stopped")

    def _collect_system_logs(self):
        """Collect events from system log files."""
        log_files = self.config.get("log_files", [])

        for log_file in log_files:
            if os.path.exists(log_file):
                try:
                    with open(log_file, "r") as f:
                        # Read new lines since last check
                        lines = f.readlines()
                        for line in lines[-100:]:  # Check last 100 lines
                            event = self._parse_log_line(line.strip(), log_file)
                            if event:
                                self.events.append(event)

                except Exception as e:
                    logger.error(f"Error reading log file {log_file}: {e}")

    def _collect_application_logs(self):
        """Collect events from application-specific logs."""
        # This would integrate with the logging_monitoring module
        try:
            # Check for security-related log entries
            # This is a placeholder for actual implementation
            pass
        except Exception as e:
            logger.error(f"Error collecting application logs: {e}")

    def _check_system_integrity(self):
        """Check system integrity and detect anomalies."""
        # Check for suspicious processes
        # Check file integrity
        # Check network connections
        try:
            # This is a placeholder for actual system integrity checks
            pass
        except Exception as e:
            logger.error(f"Error checking system integrity: {e}")

    def _parse_log_line(self, line: str, source: str) -> Optional[SecurityEvent]:
        """Parse a log line and extract security events."""
        if not line.strip():
            return None

        # Common patterns for security events
        patterns = {
            SecurityEventType.AUTHENTICATION_FAILURE: [
                r"authentication failure.*user=(\w+)",
                r"Failed password.*user (\w+)",
                r"Invalid user.*from (\d+\.\d+\.\d+\.\d+)",
            ],
            SecurityEventType.SUSPICIOUS_ACTIVITY: [
                r"Possible break-in attempt",
                r"Suspicious activity detected",
                r"Anomalous behavior",
            ],
            SecurityEventType.DATA_ACCESS_VIOLATION: [
                r"Access denied.*file=(\S+)",
                r"Permission denied.*(\S+)",
            ],
        }

        for event_type, regex_patterns in patterns.items():
            for pattern in regex_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    event = SecurityEvent(
                        event_id=self._generate_event_id(),
                        event_type=event_type,
                        timestamp=datetime.now(timezone.utc),
                        raw_log=line,
                        details={"source": source, "pattern": pattern},
                    )

                    # Extract additional information
                    if event_type == SecurityEventType.AUTHENTICATION_FAILURE:
                        if match.groups():
                            # Extract user ID
                            if len(match.groups()) >= 1:
                                event.user_id = match.group(1)

                            # Extract source IP if present
                            if len(match.groups()) >= 2:
                                event.source_ip = match.group(2)
                            elif "from" in line.lower():
                                # Extract IP from "from IP" pattern
                                ip_match = re.search(r"from (\d+\.\d+\.\d+\.\d+)", line, re.IGNORECASE)
                                if ip_match:
                                    event.source_ip = ip_match.group(1)

                    return event

        return None

    def _process_events(self):
        """Process collected security events."""
        if not self.events:
            return

        logger.debug(f"Processing {len(self.events)} security events")

        for event in self.events:
            # Check against alert rules
            self._check_alert_rules(event)

            # Store event for analysis
            self._store_event(event)

        # Clear processed events
        self.events.clear()

    def _check_alert_rules(self, event: SecurityEvent):
        """Check event against alert rules and trigger alerts if needed."""
        for rule in self.alert_rules.values():
            if not rule.enabled:
                continue

            if event.event_type != rule.event_type:
                continue

            # Check if rule conditions are met
            if self._rule_conditions_met(rule, event):
                # Check cooldown period
                if rule.last_triggered:
                    time_since_last = (
                        datetime.now(timezone.utc) - rule.last_triggered
                    ).total_seconds()
                    if time_since_last < rule.cooldown_period:
                        continue

                # Trigger alert
                self._trigger_alert(rule, event)
                rule.last_triggered = datetime.now(timezone.utc)

    def _rule_conditions_met(self, rule: AlertRule, event: SecurityEvent) -> bool:
        """Check if alert rule conditions are met."""
        # This is a simplified implementation
        # In a real system, this would be more sophisticated
        return True

    def _trigger_alert(self, rule: AlertRule, event: SecurityEvent):
        """Trigger an alert for a security event."""
        alert_message = f"🚨 SECURITY ALERT: {rule.name}\n"
        alert_message += f"Event: {event.event_type.value}\n"
        alert_message += f"Severity: {event.severity.value}\n"
        alert_message += f"Timestamp: {event.timestamp.isoformat()}\n"

        if event.source_ip:
            alert_message += f"Source IP: {event.source_ip}\n"
        if event.user_id:
            alert_message += f"User: {event.user_id}\n"

        logger.warning(alert_message)

        # Store active alert
        self.active_alerts[event.event_id] = event

        # Call alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")

    def _check_threat_intelligence(self):
        """Check threat intelligence feeds for known threats."""
        # This would integrate with threat intelligence APIs
        # For now, it's a placeholder
        pass

    def _store_event(self, event: SecurityEvent):
        """Store security event for analysis and reporting."""
        # In a real system, this would store to a database
        # For now, we just keep in memory with size limit
        max_events = self.config.get("max_events", 10000)
        if len(self.events) >= max_events:
            # Remove oldest events
            self.events = self.events[-max_events:]

    def _cleanup_old_events(self):
        """Clean up old events and alerts."""
        # Remove events older than configured retention period
        retention_days = self.config.get("log_rotation_days", 30)
        cutoff_date = datetime.now(timezone.utc)  # Would be adjusted for retention_days

        # Remove old active alerts
        expired_alerts = []
        for event_id, event in self.active_alerts.items():
            if event.timestamp < cutoff_date:
                expired_alerts.append(event_id)

        for event_id in expired_alerts:
            del self.active_alerts[event_id]

    def add_alert_rule(self, rule: AlertRule):
        """Add a new alert rule."""
        self.alert_rules[rule.rule_id] = rule
        logger.info(f"Added alert rule: {rule.name}")

    def remove_alert_rule(self, rule_id: str):
        """Remove an alert rule."""
        if rule_id in self.alert_rules:
            del self.alert_rules[rule_id]
            logger.info(f"Removed alert rule: {rule_id}")

    def add_alert_callback(self, callback: Callable[[SecurityEvent], None]):
        """Add a callback function for alerts."""
        self.alert_callbacks.append(callback)

    def get_active_alerts(self) -> List[SecurityEvent]:
        """Get list of currently active alerts."""
        return list(self.active_alerts.values())

    def get_events_summary(self) -> Dict[str, Any]:
        """Get summary of security events."""
        summary = {
            "total_events": len(self.events),
            "active_alerts": len(self.active_alerts),
            "events_by_type": {},
            "alerts_by_severity": {},
        }

        # Count events by type
        for event in self.events:
            event_type = event.event_type.value
            summary["events_by_type"][event_type] = (
                summary["events_by_type"].get(event_type, 0) + 1
            )

        # Count events by severity
        for event in self.events:
            severity = event.severity.value
            summary["alerts_by_severity"][severity] = (
                summary["alerts_by_severity"].get(severity, 0) + 1
            )

        return summary

    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        timestamp = str(time.time())
        random_part = os.urandom(4).hex()
        return f"evt_{timestamp}_{random_part}"


# Convenience functions
def monitor_security_events(config_path: Optional[str] = None) -> SecurityMonitor:
    """
    Convenience function to create and start security monitoring.

    Args:
        config_path: Path to monitor configuration file

    Returns:
        SecurityMonitor: Configured security monitor
    """
    monitor = SecurityMonitor(config_path)
    monitor.start_monitoring()
    return monitor


def audit_access_logs(log_files: Optional[List[str]] = None) -> List[SecurityEvent]:
    """
    Convenience function to audit access logs for security events.

    Args:
        log_files: List of log files to audit

    Returns:
        List of security events found
    """
    monitor = SecurityMonitor()
    if log_files:
        monitor.config["log_files"] = log_files

    # Perform one-time audit
    monitor._collect_system_logs()

    return monitor.events
