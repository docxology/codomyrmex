"""
Tests for Security Audit Module
"""

import tempfile

import pytest

from codomyrmex.security.audit import (
    AuditEvent,
    AuditEventType,
    AuditLogger,
    AuditSeverity,
    FileAuditStore,
    InMemoryAuditStore,
)


class TestAuditEvent:
    """Tests for AuditEvent."""

    def test_create(self):
        """Should create audit event."""
        event = AuditEvent(
            id="e1",
            event_type=AuditEventType.AUTH_LOGIN,
            action="login",
            actor="user@example.com",
        )

        assert event.actor == "user@example.com"

    def test_signature(self):
        """Should generate signature."""
        event = AuditEvent(
            id="e1",
            event_type=AuditEventType.DATA_ACCESS,
            action="read",
        )

        assert len(event.signature) == 16

    def test_to_json(self):
        """Should convert to JSON."""
        event = AuditEvent(
            id="e1",
            event_type=AuditEventType.AUTH_LOGIN,
            action="login",
        )

        json_str = event.to_json()
        assert "auth.login" in json_str


class TestInMemoryAuditStore:
    """Tests for InMemoryAuditStore."""

    def test_store(self):
        """Should store events."""
        store = InMemoryAuditStore()
        event = AuditEvent(
            id="e1",
            event_type=AuditEventType.AUTH_LOGIN,
            action="login",
        )

        store.store(event)

        assert len(store.get_all()) == 1

    def test_max_events(self):
        """Should enforce max events."""
        store = InMemoryAuditStore(max_events=5)

        for i in range(10):
            store.store(AuditEvent(
                id=f"e{i}",
                event_type=AuditEventType.DATA_ACCESS,
                action="read",
            ))

        assert len(store.get_all()) == 5

    def test_query_by_type(self):
        """Should query by type."""
        store = InMemoryAuditStore()
        store.store(AuditEvent("e1", AuditEventType.AUTH_LOGIN, "login"))
        store.store(AuditEvent("e2", AuditEventType.DATA_ACCESS, "read"))

        results = store.query(event_type=AuditEventType.AUTH_LOGIN)

        assert len(results) == 1

    def test_query_by_actor(self):
        """Should query by actor."""
        store = InMemoryAuditStore()
        store.store(AuditEvent("e1", AuditEventType.AUTH_LOGIN, "login", actor="user1"))
        store.store(AuditEvent("e2", AuditEventType.AUTH_LOGIN, "login", actor="user2"))

        results = store.query(actor="user1")

        assert len(results) == 1


class TestFileAuditStore:
    """Tests for FileAuditStore."""

    def test_store_and_query(self):
        """Should store and query from file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            store = FileAuditStore(f.name)

            store.store(AuditEvent("e1", AuditEventType.AUTH_LOGIN, "login", actor="user"))

            results = store.query(actor="user")

        assert len(results) == 1


class TestAuditLogger:
    """Tests for AuditLogger."""

    def test_log(self):
        """Should log events."""
        logger = AuditLogger()

        event = logger.log(
            event_type=AuditEventType.AUTH_LOGIN,
            action="user_login",
            actor="admin",
        )

        assert event.id.startswith("audit_")

    def test_log_login(self):
        """Should log login."""
        logger = AuditLogger()

        event = logger.log_login("user@example.com", "192.168.1.1")

        assert event.event_type == AuditEventType.AUTH_LOGIN

    def test_log_failed_login(self):
        """Should log failed login."""
        logger = AuditLogger()

        event = logger.log_login("user", success=False)

        assert event.event_type == AuditEventType.AUTH_FAILED
        assert event.severity == AuditSeverity.WARNING

    def test_log_data_access(self):
        """Should log data access."""
        logger = AuditLogger()

        event = logger.log_data_access("user", "users", "123")

        assert event.event_type == AuditEventType.DATA_ACCESS
        assert event.resource == "users"

    def test_log_admin_action(self):
        """Should log admin action."""
        logger = AuditLogger()

        event = logger.log_admin_action("admin", "delete_user", {"user_id": "123"})

        assert event.event_type == AuditEventType.ADMIN_ACTION
        assert event.severity == AuditSeverity.WARNING

    def test_query(self):
        """Should query events."""
        logger = AuditLogger()
        logger.log_login("user1")
        logger.log_login("user2")

        events = logger.query(actor="user1")

        assert len(events) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
