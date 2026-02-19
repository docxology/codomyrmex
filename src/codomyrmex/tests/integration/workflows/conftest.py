"""Shared fixtures for workflow integration tests.

These fixtures ensure trust state is cleanly reset between tests
and provide common utilities for workflow testing.
"""

import pytest


@pytest.fixture(autouse=True)
def reset_trust_state():
    """Reset the global trust state before and after each test."""
    from codomyrmex.agents.pai import trust_gateway

    # Store original state
    original_level = trust_gateway._trust_level

    yield

    # Restore original state
    trust_gateway._trust_level = trust_gateway.TrustLevel.UNTRUSTED
    trust_gateway._audit_log.clear()
    trust_gateway._pending_confirmations.clear()


@pytest.fixture
def project_root():
    """Project root directory."""
    from pathlib import Path

    return Path(__file__).resolve().parents[5]  # tests/integration/workflows → repo root


@pytest.fixture
def src_codomyrmex():
    """Path to src/codomyrmex."""
    from pathlib import Path

    return Path(__file__).resolve().parents[3]  # tests/integration/workflows → src/codomyrmex
