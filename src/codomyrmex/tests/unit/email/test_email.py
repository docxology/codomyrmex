"""Tests for email module."""



# Coverage push — email/agentmail
class TestAgentMailProvider:
    """Tests for AgentMail email provider."""

    def test_import(self):
        from codomyrmex.email.agentmail.provider import AgentMailProvider
        assert AgentMailProvider is not None
