"""Unit tests for honeytoken activation in defense/active.py.

Validates the full honeytoken lifecycle: create → embed → detect → report.
"""

import pytest


class TestHoneytokenActivation:
    """Tests for the honeytoken subsystem."""

    def test_create_honeytoken(self):
        """create_honeytoken returns a token string."""
        from codomyrmex.defense.active import ActiveDefense

        defense = ActiveDefense()
        token = defense.create_honeytoken(label="test-token")
        assert token.startswith("HT-")
        assert len(token) == 15  # "HT-" + 12 hex chars

    def test_check_honeytoken_detects_planted_token(self):
        """check_honeytoken detects a planted token in text."""
        from codomyrmex.defense.active import ActiveDefense

        defense = ActiveDefense()
        token = defense.create_honeytoken(label="canary")

        # Simulate the token appearing in exfiltrated data
        evil_text = f"The secret data is {token} and more..."
        triggered = defense.check_honeytoken(evil_text)

        assert len(triggered) == 1
        assert triggered[0] == token

    def test_check_honeytoken_no_false_positive(self):
        """check_honeytoken returns empty for clean text."""
        from codomyrmex.defense.active import ActiveDefense

        defense = ActiveDefense()
        defense.create_honeytoken(label="canary")

        clean_text = "This is perfectly normal text without any tokens."
        triggered = defense.check_honeytoken(clean_text)
        assert triggered == []

    def test_honeytoken_trigger_count(self):
        """Repeated triggers increment the counter."""
        from codomyrmex.defense.active import ActiveDefense

        defense = ActiveDefense()
        token = defense.create_honeytoken(label="counter-test")

        defense.check_honeytoken(f"text with {token}")
        defense.check_honeytoken(f"another text with {token}")

        tokens = defense.list_honeytokens()
        assert tokens[token]["trigger_count"] == 2

    def test_threat_report_includes_honeytokens(self):
        """Threat report includes honeytoken metrics."""
        from codomyrmex.defense.active import ActiveDefense

        defense = ActiveDefense()
        token = defense.create_honeytoken(label="report-test")
        defense.check_honeytoken(f"leak: {token}")

        report = defense.get_threat_report()
        assert report["honeytokens_active"] == 1
        assert report["honeytokens_triggered"] == 1

    def test_multiple_honeytokens(self):
        """Multiple honeytokens can be planted and detected independently."""
        from codomyrmex.defense.active import ActiveDefense

        defense = ActiveDefense()
        t1 = defense.create_honeytoken(label="token-1")
        t2 = defense.create_honeytoken(label="token-2")
        t3 = defense.create_honeytoken(label="token-3")

        # Only t1 and t3 appear in the text
        text = f"found {t1} and {t3} but not the other"
        triggered = defense.check_honeytoken(text)

        assert set(triggered) == {t1, t3}
        assert t2 not in triggered
