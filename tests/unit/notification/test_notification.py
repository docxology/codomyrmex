"""Unit tests for notification module."""

import os
import tempfile

import pytest


@pytest.mark.unit
class TestNotificationImports:
    """Test suite for notification module imports."""

    def test_module_imports(self):
        """Verify module can be imported without errors."""
        from codomyrmex.events import notification

        assert notification is not None

    def test_public_api_exists(self):
        """Verify expected public API is available."""
        from codomyrmex.events.notification import __all__

        expected_exports = [
            "NotificationChannel",
            "NotificationPriority",
            "NotificationStatus",
            "Notification",
            "NotificationResult",
            "NotificationProvider",
            "ConsoleProvider",
            "FileProvider",
            "WebhookProvider",
            "NotificationTemplate",
            "NotificationRouter",
            "NotificationService",
            "ALERT_TEMPLATE",
            "INFO_TEMPLATE",
            "ERROR_TEMPLATE",
        ]
        for export in expected_exports:
            assert export in __all__, f"Missing export: {export}"


@pytest.mark.unit
class TestNotificationChannel:
    """Test suite for NotificationChannel enum."""

    def test_channel_values(self):
        """Verify all notification channels are available."""
        from codomyrmex.events.notification import NotificationChannel

        assert NotificationChannel.EMAIL.value == "email"
        assert NotificationChannel.SLACK.value == "slack"
        assert NotificationChannel.WEBHOOK.value == "webhook"
        assert NotificationChannel.SMS.value == "sms"
        assert NotificationChannel.CONSOLE.value == "console"
        assert NotificationChannel.FILE.value == "file"


@pytest.mark.unit
class TestNotificationPriority:
    """Test suite for NotificationPriority enum."""

    def test_priority_values(self):
        """Verify all priorities are available."""
        from codomyrmex.events.notification import NotificationPriority

        assert NotificationPriority.LOW.value == "low"
        assert NotificationPriority.MEDIUM.value == "medium"
        assert NotificationPriority.HIGH.value == "high"
        assert NotificationPriority.CRITICAL.value == "critical"


@pytest.mark.unit
class TestNotificationStatus:
    """Test suite for NotificationStatus enum."""

    def test_status_values(self):
        """Verify all statuses are available."""
        from codomyrmex.events.notification import NotificationStatus

        assert NotificationStatus.PENDING.value == "pending"
        assert NotificationStatus.SENT.value == "sent"
        assert NotificationStatus.FAILED.value == "failed"
        assert NotificationStatus.DELIVERED.value == "delivered"


@pytest.mark.unit
class TestNotification:
    """Test suite for Notification dataclass."""

    def test_notification_creation(self):
        """Verify Notification can be created."""
        from codomyrmex.events.notification import (
            Notification,
            NotificationChannel,
            NotificationPriority,
        )

        notif = Notification(
            id="notif_1",
            subject="Test Alert",
            body="This is a test notification.",
            channel=NotificationChannel.EMAIL,
            priority=NotificationPriority.HIGH,
            recipient="user@example.com",
        )

        assert notif.id == "notif_1"
        assert notif.subject == "Test Alert"
        assert notif.channel == NotificationChannel.EMAIL

    def test_notification_to_dict(self):
        """Verify notification serialization."""
        from codomyrmex.events.notification import Notification, NotificationChannel

        notif = Notification(
            id="test",
            subject="Subject",
            body="Body",
            channel=NotificationChannel.CONSOLE,
        )

        result = notif.to_dict()
        assert result["id"] == "test"
        assert result["channel"] == "console"


@pytest.mark.unit
class TestNotificationResult:
    """Test suite for NotificationResult dataclass."""

    def test_result_creation(self):
        """Verify NotificationResult can be created."""
        from codomyrmex.events.notification import (
            NotificationChannel,
            NotificationResult,
            NotificationStatus,
        )

        result = NotificationResult(
            notification_id="notif_1",
            status=NotificationStatus.SENT,
            channel=NotificationChannel.EMAIL,
        )

        assert result.notification_id == "notif_1"
        assert result.status == NotificationStatus.SENT

    def test_result_is_success(self):
        """Verify is_success property."""
        from codomyrmex.events.notification import (
            NotificationChannel,
            NotificationResult,
            NotificationStatus,
        )

        sent = NotificationResult(
            notification_id="1",
            status=NotificationStatus.SENT,
            channel=NotificationChannel.CONSOLE,
        )
        assert sent.is_success is True

        failed = NotificationResult(
            notification_id="2",
            status=NotificationStatus.FAILED,
            channel=NotificationChannel.CONSOLE,
        )
        assert failed.is_success is False


@pytest.mark.unit
class TestConsoleProvider:
    """Test suite for ConsoleProvider."""

    def test_provider_channel(self):
        """Verify provider channel."""
        from codomyrmex.events.notification import ConsoleProvider, NotificationChannel

        provider = ConsoleProvider()
        assert provider.channel == NotificationChannel.CONSOLE

    def test_provider_send(self, capsys):
        """Verify console output."""
        from codomyrmex.events.notification import (
            ConsoleProvider,
            Notification,
            NotificationStatus,
        )

        provider = ConsoleProvider()
        notif = Notification(
            id="test",
            subject="Test Subject",
            body="Test body message",
        )

        result = provider.send(notif)

        assert result.status == NotificationStatus.SENT
        captured = capsys.readouterr()
        assert "Test Subject" in captured.out


@pytest.mark.unit
class TestFileProvider:
    """Test suite for FileProvider."""

    def test_provider_channel(self):
        """Verify provider channel."""
        from codomyrmex.events.notification import FileProvider, NotificationChannel

        provider = FileProvider()
        assert provider.channel == NotificationChannel.FILE

    def test_provider_send(self):
        """Verify file writing."""
        from codomyrmex.events.notification import (
            FileProvider,
            Notification,
            NotificationStatus,
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
            temp_path = f.name

        try:
            provider = FileProvider(file_path=temp_path)
            notif = Notification(
                id="test",
                subject="Test",
                body="File notification",
            )

            result = provider.send(notif)

            assert result.status == NotificationStatus.SENT

            with open(temp_path) as f:
                content = f.read()
                assert "test" in content
                assert "File notification" in content
        finally:
            os.unlink(temp_path)


@pytest.fixture
def webhook_server(monkeypatch):
    """Start local HTTP servers that record POSTs and answer with a status code."""
    import http.server
    import json
    import threading

    # Keep local test traffic off any configured HTTP proxy.
    monkeypatch.setenv("NO_PROXY", "127.0.0.1,localhost")
    monkeypatch.setenv("no_proxy", "127.0.0.1,localhost")
    servers = []

    def start(status_code):
        received = []

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_POST(self):
                length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(length)
                received.append(
                    {"headers": dict(self.headers), "json": json.loads(body)}
                )
                self.send_response(status_code)
                self.end_headers()
                self.wfile.write(b"ok")

            def log_message(self, format: str, *args: object) -> None:
                pass

        server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        servers.append(server)
        return f"http://127.0.0.1:{server.server_address[1]}/hook", received

    yield start
    for server in servers:
        server.shutdown()
        server.server_close()


@pytest.mark.unit
class TestWebhookProvider:
    """Test suite for WebhookProvider."""

    def test_provider_channel(self):
        """Verify provider channel."""
        from codomyrmex.events.notification import NotificationChannel, WebhookProvider

        provider = WebhookProvider(url="https://example.com/webhook")
        assert provider.channel == NotificationChannel.WEBHOOK

    def test_send_posts_json_to_the_url(self, webhook_server):
        """send() POSTs the notification as JSON and reports SENT on 2xx."""
        from codomyrmex.events.notification import (
            Notification,
            NotificationStatus,
            WebhookProvider,
        )

        url, received = webhook_server(200)
        provider = WebhookProvider(url=url, headers={"X-Token": "t"})
        notif = Notification(id="n1", subject="Test", body="Webhook test")

        result = provider.send(notif)

        assert result.status == NotificationStatus.SENT
        assert result.response["status_code"] == 200
        assert len(received) == 1
        assert received[0]["headers"]["Content-Type"] == "application/json"
        assert received[0]["headers"]["X-Token"] == "t"
        assert received[0]["json"]["id"] == "n1"
        assert received[0]["json"]["subject"] == "Test"

    def test_http_error_is_reported_as_failed(self, webhook_server):
        """A non-2xx response is FAILED with the status code recorded."""
        from codomyrmex.events.notification import (
            Notification,
            NotificationStatus,
            WebhookProvider,
        )

        url, _ = webhook_server(503)
        result = WebhookProvider(url=url).send(
            Notification(id="n2", subject="S", body="B")
        )

        assert result.status == NotificationStatus.FAILED
        assert result.response["status_code"] == 503
        assert result.error is not None
        assert "503" in result.error

    def test_unreachable_url_is_reported_as_failed(self):
        """Connection errors are FAILED, not SENT."""
        import socket

        from codomyrmex.events.notification import (
            Notification,
            NotificationStatus,
            WebhookProvider,
        )

        with socket.socket() as s:  # find a free port, then close it
            s.bind(("127.0.0.1", 0))
            port = s.getsockname()[1]
        result = WebhookProvider(url=f"http://127.0.0.1:{port}/hook", timeout=2).send(
            Notification(id="n3", subject="S", body="B")
        )

        assert result.status == NotificationStatus.FAILED
        assert result.error

    def test_rejects_non_http_urls(self):
        from codomyrmex.events.notification import WebhookProvider

        with pytest.raises(ValueError, match="http or https"):
            WebhookProvider(url="file:///etc/passwd")


@pytest.mark.unit
class TestNotificationTemplate:
    """Test suite for NotificationTemplate."""

    def test_template_creation(self):
        """Verify template creation."""
        from codomyrmex.events.notification import (
            NotificationPriority,
            NotificationTemplate,
        )

        template = NotificationTemplate(
            name="test_template",
            subject_template="Alert: {type}",
            body_template="Details: {message}",
            default_priority=NotificationPriority.HIGH,
        )

        assert template.name == "test_template"

    def test_template_render(self):
        """Verify template rendering."""
        from codomyrmex.events.notification import NotificationTemplate

        template = NotificationTemplate(
            name="alert",
            subject_template="{severity}: {title}",
            body_template="Alert: {message}\nSource: {source}",
        )

        notif = template.render(
            id="notif_1",
            severity="HIGH",
            title="CPU Alert",
            message="CPU at 95%",
            source="monitoring",
        )

        assert notif.subject == "HIGH: CPU Alert"
        assert "CPU at 95%" in notif.body
        assert "monitoring" in notif.body


@pytest.mark.unit
class TestNotificationRouter:
    """Test suite for NotificationRouter."""

    def test_router_default(self):
        """Verify default routing."""
        from codomyrmex.events.notification import (
            Notification,
            NotificationChannel,
            NotificationRouter,
        )

        router = NotificationRouter()
        router.add_default(NotificationChannel.EMAIL)

        notif = Notification(id="test", subject="Test", body="Test")
        channel = router.route(notif)

        assert channel == NotificationChannel.EMAIL

    def test_router_rule_matching(self):
        """Verify rule-based routing."""
        from codomyrmex.events.notification import (
            Notification,
            NotificationChannel,
            NotificationPriority,
            NotificationRouter,
        )

        router = NotificationRouter()
        router.add_rule(
            lambda n: n.priority == NotificationPriority.CRITICAL,
            NotificationChannel.SLACK,
        )
        router.add_default(NotificationChannel.CONSOLE)

        critical = Notification(
            id="1",
            subject="Critical",
            body="Test",
            priority=NotificationPriority.CRITICAL,
        )
        low = Notification(
            id="2",
            subject="Low",
            body="Test",
            priority=NotificationPriority.LOW,
        )

        assert router.route(critical) == NotificationChannel.SLACK
        assert router.route(low) == NotificationChannel.CONSOLE


@pytest.mark.unit
class TestNotificationService:
    """Test suite for NotificationService."""

    def test_service_creation(self):
        """Verify service creation."""
        from codomyrmex.events.notification import NotificationService

        service = NotificationService()
        assert service is not None

    def test_service_register_provider(self):
        """Verify provider registration."""
        from codomyrmex.events.notification import ConsoleProvider, NotificationService

        service = NotificationService()
        service.register_provider(ConsoleProvider())

        # Should not raise when sending to console
        from codomyrmex.events.notification import Notification

        notif = Notification(id="test", subject="Test", body="Test")
        result = service.send(notif)
        assert result.is_success is True

    def test_service_send_without_provider(self):
        """Verify failure when no provider registered."""
        from codomyrmex.events.notification import (
            Notification,
            NotificationChannel,
            NotificationService,
            NotificationStatus,
        )

        service = NotificationService()
        notif = Notification(
            id="test",
            subject="Test",
            body="Test",
            channel=NotificationChannel.EMAIL,  # No provider registered
        )

        result = service.send(notif)
        assert result.status == NotificationStatus.FAILED

    def test_service_register_template(self):
        """Verify template registration."""
        from codomyrmex.events.notification import (
            ConsoleProvider,
            NotificationService,
            NotificationTemplate,
        )

        service = NotificationService()
        service.register_provider(ConsoleProvider())

        template = NotificationTemplate(
            name="custom",
            subject_template="[{level}] {title}",
            body_template="{message}",
        )
        service.register_template(template)

        result = service.send_from_template(
            "custom",
            id="test",
            level="INFO",
            title="Test Title",
            message="Test message",
        )

        assert result.is_success is True

    def test_service_send_from_missing_template(self):
        """Verify failure when template not found."""
        from codomyrmex.events.notification import (
            NotificationService,
            NotificationStatus,
        )

        service = NotificationService()
        result = service.send_from_template("nonexistent", id="test")

        assert result.status == NotificationStatus.FAILED
        assert "not found" in (result.error or "")

    def test_service_broadcast(self, webhook_server):
        """Verify broadcast to multiple channels."""
        from codomyrmex.events.notification import (
            ConsoleProvider,
            Notification,
            NotificationChannel,
            NotificationService,
            WebhookProvider,
        )

        service = NotificationService()
        service.register_provider(ConsoleProvider())
        url, received = webhook_server(200)
        service.register_provider(WebhookProvider(url=url))

        notif = Notification(id="broadcast", subject="Test", body="Broadcast test")

        results = service.broadcast(
            notif,
            [NotificationChannel.CONSOLE, NotificationChannel.WEBHOOK],
        )

        assert len(results) == 2
        assert all(r.is_success for r in results)
        assert [r["json"]["id"] for r in received] == ["broadcast_webhook"]

    def test_service_history(self):
        """Verify notification history tracking."""
        from codomyrmex.events.notification import (
            ConsoleProvider,
            Notification,
            NotificationService,
        )

        service = NotificationService()
        service.register_provider(ConsoleProvider())

        service.send(Notification(id="1", subject="Test 1", body="Body"))
        service.send(Notification(id="2", subject="Test 2", body="Body"))

        history = service.history
        assert len(history) == 2

    def test_service_success_count(self):
        """Verify success count tracking."""
        from codomyrmex.events.notification import (
            ConsoleProvider,
            Notification,
            NotificationService,
        )

        service = NotificationService()
        service.register_provider(ConsoleProvider())

        service.send(Notification(id="1", subject="Test", body="Body"))
        service.send(Notification(id="2", subject="Test", body="Body"))

        assert service.success_count == 2


@pytest.mark.unit
class TestBuiltinTemplates:
    """Test suite for built-in templates."""

    def test_alert_template(self):
        """Verify ALERT_TEMPLATE."""
        from codomyrmex.events.notification import ALERT_TEMPLATE, NotificationPriority

        assert ALERT_TEMPLATE.name == "alert"
        assert ALERT_TEMPLATE.default_priority == NotificationPriority.HIGH

        notif = ALERT_TEMPLATE.render(
            id="test",
            severity="CRITICAL",
            title="System Down",
            source="monitoring",
            message="Database unreachable",
        )

        assert "CRITICAL" in notif.subject
        assert "Database unreachable" in notif.body

    def test_info_template(self):
        """Verify INFO_TEMPLATE."""
        from codomyrmex.events.notification import INFO_TEMPLATE

        assert INFO_TEMPLATE.name == "info"

        notif = INFO_TEMPLATE.render(
            id="test",
            title="Status Update",
            message="All systems operational",
        )

        assert notif.subject == "Status Update"

    def test_error_template(self):
        """Verify ERROR_TEMPLATE."""
        from codomyrmex.events.notification import ERROR_TEMPLATE, NotificationPriority

        assert ERROR_TEMPLATE.name == "error"
        assert ERROR_TEMPLATE.default_priority == NotificationPriority.CRITICAL

        notif = ERROR_TEMPLATE.render(
            id="test",
            title="Unhandled Exception",
            details="NullPointerException",
            trace="at line 42...",
        )

        assert "Error" in notif.subject
        assert "NullPointerException" in notif.body
