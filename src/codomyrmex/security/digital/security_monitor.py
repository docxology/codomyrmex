"""Security Monitor for Codomyrmex Security Audit Module.

Provides real-time security monitoring, alerting, and audit logging capabilities.
"""

import json
import os
import re
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from collections.abc import Callable

from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)


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
    source_ip: str | None = None
    user_id: str | None = None
    resource: str | None = None
    action: str | None = None
    severity: AlertLevel = AlertLevel.MEDIUM
    details: dict[str, Any] = field(default_factory=dict)
    raw_log: str | None = None

    def to_dict(self) -> dict[str, Any]:
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
    conditions: dict[str, Any]
    alert_level: AlertLevel
    enabled: bool = True
    cooldown_period: int = 300  # seconds
    last_triggered: datetime | None = None


class SecurityMonitor:
    """Real-time security monitoring and alerting system."""

    def __init__(self, config_path: str | None = None):
        """Initialize the security monitor."""
        self.config_path = config_path
        self.config = self._load_config()

        self.events: list[SecurityEvent] = []
        self.alert_rules: dict[str, AlertRule] = {}
        self.active_alerts: dict[str, SecurityEvent] = {}

        self.monitoring_active = False
        self.monitor_thread: threading.Thread | None = None
        self.alert_callbacks: list[Callable[[SecurityEvent], None]] = []

        # Load default alert rules
        self._load_default_alert_rules()

    def _load_config(self) -> dict[str, Any]:
        """Load monitor configuration."""
        default_config = {
            "log_files": ["/var/log/auth.log", "/var/log/security.log"],
            "monitoring_interval": 10,
            "max_events": 10000,
            "alert_cooldown": 300,
            "enable_auto_response": False,
            "threat_intelligence_enabled": True,
            "log_rotation_days": 30,
        }

        if self.config_path and os.path.exists(self.config_path):
            try:
                with open(self.config_path) as f:
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
                self._collect_system_logs()
                self._process_events()
                self._cleanup_old_events()
                time.sleep(self.config.get("monitoring_interval", 10))

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(30)

        logger.info("Security monitoring loop stopped")

    def _collect_system_logs(self):
        """Collect events from system log files."""
        log_files = self.config.get("log_files", [])
        for log_file in log_files:
            if os.path.exists(log_file):
                try:
                    with open(log_file, errors='ignore') as f:
                        lines = f.readlines()
                        for line in lines[-100:]:
                            event = self._parse_log_line(line.strip(), log_file)
                            if event:
                                self.events.append(event)
                except Exception as e:
                    logger.error(f"Error reading log file {log_file}: {e}")

    def _parse_log_line(self, line: str, source: str) -> SecurityEvent | None:
        """Parse a log line and extract security events."""
        if not line.strip():
            return None

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

                    if event_type == SecurityEventType.AUTHENTICATION_FAILURE:
                         if match.groups():
                            if len(match.groups()) >= 1:
                                event.user_id = match.group(1)
                            if len(match.groups()) >= 2:
                                event.source_ip = match.group(2)
                            else:
                                ip_match = re.search(r"from (\d+\.\d+\.\d+\.\d+)", line, re.IGNORECASE)
                                if ip_match:
                                    event.source_ip = ip_match.group(1)
                    return event
        return None

    def _process_events(self):
        """Process collected security events."""
        if not self.events:
            return

        for event in self.events:
            self._check_alert_rules(event)

        self.events.clear()

    def _check_alert_rules(self, event: SecurityEvent):
        """Check event against alert rules."""
        for rule in self.alert_rules.values():
            if not rule.enabled:
                continue
            if event.event_type != rule.event_type:
                continue

            # Simplified trigger (always triggers if type matches for now)
            self._trigger_alert(rule, event)
            rule.last_triggered = datetime.now(timezone.utc)

    def _trigger_alert(self, rule: AlertRule, event: SecurityEvent):
        """Trigger an alert for a security event."""
        logger.warning(f"🚨 SECURITY ALERT: {rule.name} - {event.event_type.value}")
        self.active_alerts[event.event_id] = event
        for callback in self.alert_callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")

    def _cleanup_old_events(self):
        """Clean up old events and alerts."""
        max_events = self.config.get("max_events", 10000)
        if len(self.active_alerts) > max_events:
            # Simple cleanup - clear if too many
            self.active_alerts.clear()

    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        return f"evt_{time.time()}_{os.urandom(4).hex()}"

    def get_events_summary(self) -> dict[str, Any]:
        """Get summary of security events."""
        return {
            "total_events": len(self.events),
            "active_alerts": len(self.active_alerts)
        }


# Convenience functions
def monitor_security_events(config_path: str | None = None) -> SecurityMonitor:
    """Convenience function to create and start security monitoring."""
    monitor = SecurityMonitor(config_path)
    monitor.start_monitoring()
    return monitor

def audit_access_logs(log_files: list[str] | None = None) -> list[SecurityEvent]:
    """Convenience function to audit access logs for security events."""
    monitor = SecurityMonitor()
    if log_files:
        monitor.config["log_files"] = log_files
    monitor._collect_system_logs()
    return monitor.events
