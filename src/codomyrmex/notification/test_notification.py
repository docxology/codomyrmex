"""
Tests for Notification Module
"""

import pytest
import tempfile
import os
from codomyrmex.notification import (
    Notification,
    NotificationChannel,
    NotificationPriority,
    NotificationStatus,
    ConsoleProvider,
    FileProvider,
    WebhookProvider,
    NotificationTemplate,
    NotificationRouter,
    NotificationService,
    ALERT_TEMPLATE,
)


class TestNotification:
    """Tests for Notification dataclass."""
    
    def test_create(self):
        """Should create notification."""
        n = Notification(
            id="test_123",
            subject="Test Subject",
            body="Test body",
        )
        
        assert n.id == "test_123"
        assert n.channel == NotificationChannel.CONSOLE
    
    def test_to_dict(self):
        """Should convert to dict."""
        n = Notification(id="1", subject="S", body="B")
        data = n.to_dict()
        
        assert data["id"] == "1"
        assert data["subject"] == "S"
        assert "created_at" in data


class TestConsoleProvider:
    """Tests for ConsoleProvider."""
    
    def test_send(self, capsys):
        """Should print to console."""
        provider = ConsoleProvider()
        n = Notification(id="1", subject="Test", body="Hello")
        
        result = provider.send(n)
        
        assert result.status == NotificationStatus.SENT
        assert result.is_success
        
        captured = capsys.readouterr()
        assert "Test" in captured.out


class TestFileProvider:
    """Tests for FileProvider."""
    
    def test_send(self):
        """Should write to file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            path = f.name
        
        try:
            provider = FileProvider(path)
            n = Notification(id="1", subject="Test", body="Content")
            
            result = provider.send(n)
            
            assert result.status == NotificationStatus.SENT
            
            with open(path) as f:
                content = f.read()
                assert "Test" in content
        finally:
            os.unlink(path)


class TestWebhookProvider:
    """Tests for WebhookProvider."""
    
    def test_send(self):
        """Should simulate webhook send."""
        provider = WebhookProvider("https://example.com/hook")
        n = Notification(id="1", subject="Test", body="Body")
        
        result = provider.send(n)
        
        assert result.status == NotificationStatus.SENT
        assert len(provider._sent) == 1


class TestNotificationTemplate:
    """Tests for NotificationTemplate."""
    
    def test_render(self):
        """Should render template."""
        template = NotificationTemplate(
            name="test",
            subject_template="Hello {name}",
            body_template="Welcome {name}! Your code is {code}.",
        )
        
        n = template.render(id="1", name="Alice", code="ABC123")
        
        assert n.subject == "Hello Alice"
        assert "ABC123" in n.body
    
    def test_with_priority(self):
        """Should respect default priority."""
        template = NotificationTemplate(
            name="urgent",
            subject_template="{msg}",
            body_template="{msg}",
            default_priority=NotificationPriority.CRITICAL,
        )
        
        n = template.render(id="1", msg="Alert")
        
        assert n.priority == NotificationPriority.CRITICAL


class TestNotificationRouter:
    """Tests for NotificationRouter."""
    
    def test_route_by_priority(self):
        """Should route based on priority."""
        router = NotificationRouter()
        router.add_rule(
            lambda n: n.priority == NotificationPriority.CRITICAL,
            NotificationChannel.SLACK,
        )
        router.add_default(NotificationChannel.CONSOLE)
        
        critical = Notification(id="1", subject="S", body="B", priority=NotificationPriority.CRITICAL)
        normal = Notification(id="2", subject="S", body="B", priority=NotificationPriority.LOW)
        
        assert router.route(critical) == NotificationChannel.SLACK
        assert router.route(normal) == NotificationChannel.CONSOLE


class TestNotificationService:
    """Tests for NotificationService."""
    
    def test_send(self, capsys):
        """Should send notification."""
        service = NotificationService()
        service.register_provider(ConsoleProvider())
        
        n = Notification(id="1", subject="Test", body="Hello")
        result = service.send(n)
        
        assert result.is_success
    
    def test_send_from_template(self, capsys):
        """Should send from template."""
        service = NotificationService()
        service.register_provider(ConsoleProvider())
        service.register_template(ALERT_TEMPLATE)
        
        result = service.send_from_template(
            "alert",
            id="1",
            severity="HIGH",
            title="CPU Alert",
            source="monitoring",
            message="CPU at 95%",
        )
        
        assert result.is_success
    
    def test_no_provider(self):
        """Should fail if no provider."""
        service = NotificationService()
        
        n = Notification(id="1", subject="S", body="B", channel=NotificationChannel.EMAIL)
        result = service.send(n)
        
        assert result.status == NotificationStatus.FAILED
        assert "No provider" in result.error
    
    def test_broadcast(self, capsys):
        """Should broadcast to multiple channels."""
        service = NotificationService()
        service.register_provider(ConsoleProvider())
        
        n = Notification(id="1", subject="S", body="B")
        results = service.broadcast(n, [NotificationChannel.CONSOLE])
        
        assert len(results) == 1
        assert results[0].is_success
    
    def test_history(self):
        """Should track history."""
        service = NotificationService()
        service.register_provider(ConsoleProvider())
        
        for i in range(3):
            service.send(Notification(id=str(i), subject="S", body="B"))
        
        assert len(service.history) == 3
        assert service.success_count == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
