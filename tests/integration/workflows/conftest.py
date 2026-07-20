"""Shared fixtures for workflow integration tests.

These fixtures ensure trust state is cleanly reset between tests
and provide common utilities for workflow testing.
"""

import pytest

from tests.support.repo_paths import PACKAGE_ROOT, REPO_ROOT


@pytest.fixture(autouse=True)
def reset_trust_state():
    """Reset the global trust state before and after each test."""
    from codomyrmex.agents.pai import trust_gateway

    # Store original state

    yield

    # Restore original state
    trust_gateway._trust_level = trust_gateway.TrustLevel.UNTRUSTED
    trust_gateway._audit_log.clear()
    trust_gateway._pending_confirmations.clear()


@pytest.fixture
def project_root():
    """Project root directory."""
    from pathlib import Path

    return REPO_ROOT  # tests/integration/workflows → repo root


@pytest.fixture
def src_codomyrmex():
    """Path to src/codomyrmex."""
    from pathlib import Path

    return PACKAGE_ROOT  # tests/integration/workflows → src/codomyrmex
