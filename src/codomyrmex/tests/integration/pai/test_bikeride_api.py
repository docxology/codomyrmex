#!/usr/bin/env python3
"""PAI Bike Ride API — Integration Tests.

Tests the Bike Ride email briefing feature via the PAI PM HTTP API.
Requires the PAI PM server running on localhost:8888 with Ollama available.

Run::

    uv run python -m pytest src/codomyrmex/tests/integration/pai/test_bikeride_api.py -v

Or skip if the server is not running::

    uv run python -m pytest src/codomyrmex/tests/integration/pai/test_bikeride_api.py -v -k "not slow"
"""

from __future__ import annotations

import json
import logging
import re
import urllib.error
import urllib.request

import pytest

logger = logging.getLogger(__name__)

PAI_PM_BASE = "http://localhost:8888"
THINKING_PATTERNS = [
    re.compile(r"<think>", re.IGNORECASE),
    re.compile(r"</think>", re.IGNORECASE),
    re.compile(r"^Thinking\.\.\.", re.IGNORECASE | re.MULTILINE),
    re.compile(r"\.{3}done thinking\.", re.IGNORECASE),
    re.compile(r"^Steps:", re.MULTILINE),
    re.compile(r"^Key points:", re.MULTILINE),
    re.compile(r"^Our task:", re.MULTILINE),
]


def _api_get(path: str, timeout: int = 10) -> dict:
    """GET request to PAI PM API."""
    url = f"{PAI_PM_BASE}{path}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def _api_post(path: str, body: dict, timeout: int = 180) -> dict:
    """POST request to PAI PM API."""
    url = f"{PAI_PM_BASE}{path}"
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def _server_available() -> bool:
    """Check if PAI PM server is reachable."""
    try:
        result = _api_get("/api/health", timeout=3)
        return result.get("status") == "ok"
    except (urllib.error.URLError, OSError):
        return False


def _gmail_connected() -> bool:
    """Check if Gmail is authenticated."""
    try:
        result = _api_get("/api/gmail/status", timeout=5)
        return result.get("connected", False)
    except (urllib.error.URLError, OSError):
        return False


requires_server = pytest.mark.skipif(
    not _server_available(),
    reason="PAI PM server not running on localhost:8888",
)

requires_gmail = pytest.mark.skipif(
    not _server_available() or not _gmail_connected(),
    reason="PAI PM server not running or Gmail not connected",
)


def _assert_no_thinking_artifacts(text: str, label: str) -> None:
    """Assert that LLM output is free of chain-of-thought artifacts."""
    for pattern in THINKING_PATTERNS:
        match = pattern.search(text)
        if match:
            snippet = text[max(0, match.start() - 20) : match.end() + 80]
            pytest.fail(
                f"{label} contains thinking artifact matching {pattern.pattern!r}: "
                f"...{snippet}..."
            )


# ── Health & Status ──────────────────────────────────────────────────────


@requires_server
class TestServerHealth:
    """Basic server health and service status checks."""

    def test_health_endpoint(self) -> None:
        result = _api_get("/api/health")
        assert result["status"] == "ok", f"Health check failed: {result}"
        logger.info("Health check passed: %s", result)

    def test_gmail_status(self) -> None:
        result = _api_get("/api/gmail/status")
        assert "connected" in result, f"Gmail status missing 'connected': {result}"
        logger.info(
            "Gmail status: connected=%s, email=%s",
            result.get("connected"),
            result.get("email"),
        )

    def test_agentmail_status(self) -> None:
        result = _api_get("/api/email/agentmail/status")
        assert "connected" in result, f"AgentMail status missing 'connected': {result}"
        logger.info("AgentMail status: connected=%s", result.get("connected"))

    def test_calendar_status(self) -> None:
        result = _api_get("/api/calendar/status")
        assert "authenticated" in result, (
            f"Calendar status missing 'authenticated': {result}"
        )
        logger.info("Calendar status: authenticated=%s", result.get("authenticated"))

    def test_github_status(self) -> None:
        result = _api_get("/api/github/status")
        assert "projects" in result or "linked_count" in result, (
            f"GitHub status unexpected: {result}"
        )
        logger.info("GitHub status: %s", result)


# ── Bike Ride ────────────────────────────────────────────────────────────


@requires_gmail
class TestBikeRideLoad:
    """Test the Bike Ride load endpoint with real LLM (Ollama gemma3:4b)."""

    @pytest.mark.slow
    def test_load_returns_threads(self) -> None:
        """Load bike ride threads — verifies summary and drafts are generated."""
        result = _api_post(
            "/api/bikeride/load",
            {
                "backend": "ollama",
                "model": "gemma3:4b",
            },
            timeout=300,
        )
        assert result.get("success") is True, f"Bike ride load failed: {result}"
        threads = result.get("threads", [])
        logger.info("Bike ride loaded %d threads", len(threads))

        for thread in threads:
            subject = thread.get("subject", "(no subject)")

            # Verify summary exists and is clean
            summary = thread.get("summary", "")
            assert len(summary) > 10, f"Summary too short for '{subject}': {summary!r}"
            assert len(summary) < 1000, (
                f"Summary too verbose for '{subject}' ({len(summary)} chars). "
                f"Should be 2-3 sentences."
            )
            _assert_no_thinking_artifacts(summary, f"Summary for '{subject}'")
            logger.info(
                "Thread '%s' summary (%d chars): %s",
                subject,
                len(summary),
                summary[:120],
            )

            # Verify drafts exist and are clean
            drafts = thread.get("drafts", [])
            assert len(drafts) == 3, (
                f"Expected 3 drafts (A/B/C) for '{subject}', got {len(drafts)}"
            )
            for draft in drafts:
                label = draft.get("label", "?")
                title = draft.get("title", "?")
                text = draft.get("text", "")
                assert len(text) > 10, f"Draft {label} ({title}) too short: {text!r}"
                _assert_no_thinking_artifacts(
                    text, f"Draft {label} ({title}) for '{subject}'"
                )
                logger.info(
                    "Draft %s (%s, %d chars): %s", label, title, len(text), text[:80]
                )


@requires_server
class TestBikeRideTTS:
    """Test the text-to-speech endpoint (macOS only)."""

    def test_tts_produces_audio(self) -> None:
        """Convert a short text to audio and verify base64 response."""
        result = _api_post(
            "/api/bikeride/tts",
            {
                "text": "Hello, this is a test of the text to speech system.",
            },
            timeout=30,
        )
        assert result.get("success") is True, f"TTS failed: {result}"
        audio_url = result.get("audioUrl", "")
        assert audio_url.startswith("data:audio/"), (
            f"Audio URL format unexpected: {audio_url[:60]}"
        )
        # Verify base64 data is non-trivial (at least 1KB)
        base64_data = audio_url.split(",", 1)[1] if "," in audio_url else ""
        assert len(base64_data) > 1000, (
            f"Audio data too small ({len(base64_data)} chars)"
        )
        logger.info("TTS produced %d bytes of audio", len(base64_data))


# ── GitHub Integration ───────────────────────────────────────────────────


@requires_server
class TestGitHubIntegration:
    """Test GitHub sync API endpoints."""

    def test_repos_list(self) -> None:
        """list repos for the default owner."""
        result = _api_get("/api/github/repos?owner=docxology")
        assert isinstance(result, list), f"Expected list of repos, got {type(result)}"
        assert len(result) > 0, "No repos returned for docxology"
        logger.info("GitHub repos listed: %d", len(result))

    def test_sync_status(self) -> None:
        """Check GitHub sync status shows linked projects."""
        result = _api_get("/api/github/status")
        assert "projects" in result, f"Missing 'projects' in status: {result}"
        linked = [p for p in result["projects"] if p.get("linked")]
        logger.info("GitHub sync status: %d linked projects", len(linked))


# ── Project & Mission CRUD ───────────────────────────────────────────────


@requires_server
class TestProjectMissionCRUD:
    """Test project and mission listing endpoints."""

    def test_list_projects(self) -> None:
        result = _api_get("/api/projects")
        assert isinstance(result, list), (
            f"Expected list of projects, got {type(result)}"
        )
        logger.info("Projects listed: %d", len(result))

    def test_list_missions(self) -> None:
        result = _api_get("/api/missions")
        assert isinstance(result, list), (
            f"Expected list of missions, got {type(result)}"
        )
        logger.info("Missions listed: %d", len(result))

    def test_awareness_endpoint(self) -> None:
        result = _api_get("/api/awareness")
        assert isinstance(result, dict), (
            f"Expected dict from awareness, got {type(result)}"
        )
        logger.info("Awareness keys: %s", list(result.keys())[:10])


# ── Entry-point ──────────────────────────────────────────────────────────


def main() -> int:
    """CLI entry point for direct execution."""
    import sys

    return pytest.main(
        [__file__, "-v", "--tb=short", "--log-cli-level=INFO", *sys.argv[1:]]
    )


if __name__ == "__main__":
    raise SystemExit(main())
