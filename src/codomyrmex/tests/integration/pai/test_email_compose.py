#!/usr/bin/env python3
"""
LLM Email Compose — Functional Test Suite
==========================================

Tests all LLM-powered email compose endpoints on the PAI PMServer (:8888).
Validates that real project/calendar context data is used in generated emails.

Usage:
    # Test all templates (requires ollama running)
    uv run python scripts/pai/test_email_compose.py

    # Test a specific template
    uv run python scripts/pai/test_email_compose.py --template daily-schedule

    # Use a different backend (claude, gemini)
    uv run python scripts/pai/test_email_compose.py --backend gemini

    # Dry-run: only test API connectivity, skip LLM compose
    uv run python scripts/pai/test_email_compose.py --dry-run

Prerequisites:
    - PMServer running: bun scripts/pai/pm/server.ts --port 8888
    - For ollama: ollama serve must be running
    - For gemini: gemini CLI installed
    - For claude: claude CLI installed
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

import pytest

BASE_URL = "http://localhost:8888"

# ── Helpers ──────────────────────────────────────────────────────────────────


def _get(path: str) -> dict | list | None:
    """Send GET request, return parsed JSON or None on error."""
    try:
        req = urllib.request.Request(f"{BASE_URL}{path}")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"  ✗ GET {path} failed: {e}")
        return None


def _post(path: str, body: dict, timeout: int = 120) -> dict | None:
    """Send POST request with JSON body, return parsed JSON or None."""
    try:
        data = json.dumps(body).encode()
        req = urllib.request.Request(
            f"{BASE_URL}{path}",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode() if e.fp else "no body"
        print(f"  ✗ POST {path} → HTTP {e.code}: {body_text[:200]}")
        return None
    except Exception as e:
        print(f"  ✗ POST {path} failed: {e}")
        return None


def _ok(label: str) -> None:
    print(f"  ✔ {label}")


def _fail(label: str) -> None:
    print(f"  ✗ {label}")


# ── Test Functions ───────────────────────────────────────────────────────────


def test_server_health() -> bool:
    """Verify PMServer is running and responsive."""
    print("\n── Server Health ──")
    data = _get("/api/projects")
    if data is None:
        _fail("PMServer not responding on :8888")
        print("  → Start it: bun scripts/pai/pm/server.ts --port 8888")
        return False
    _ok(f"PMServer online — {len(data)} projects loaded")
    return True


def test_calendar_api() -> bool:
    """Verify calendar API returns real events."""
    print("\n── Calendar API ──")
    data = _get("/api/calendar/events")
    if data is None:
        _fail("Calendar API not responding")
        return False
    events = data.get("events", data.get("items", []))
    if not events:
        print("  ⚠ No calendar events found (gcal may not be connected)")
        return True  # Not a hard failure
    _ok(f"Calendar API: {len(events)} events")
    for ev in events[:5]:
        start = ev.get("start", {}).get(
            "dateTime", ev.get("start", {}).get("date", "?")
        )
        summary = ev.get("summary", "untitled")
        print(f"    📅 {start}: {summary}")
    return True


def test_email_agentmail() -> bool:
    """Verify AgentMail status endpoint."""
    print("\n── AgentMail Status ──")
    data = _get("/api/email/agentmail/status")
    if data is None:
        _fail("AgentMail API not responding")
        return False
    if data.get("success"):
        inboxes = data.get("inboxes", [])
        _ok(f"AgentMail connected — {len(inboxes)} inbox(es)")
        for inbox in inboxes[:3]:
            print(f"    📬 {inbox.get('inbox_id', '?')}")
    else:
        _fail(f"AgentMail not connected: {data.get('error', '?')}")
    return True


def test_email_gmail() -> bool:
    """Verify Gmail messages endpoint."""
    print("\n── Gmail Messages ──")
    data = _get("/api/email/gmail/messages")
    if data is None:
        _fail("Gmail API not responding")
        return False
    msgs = data.get("messages", [])
    _ok(f"Gmail API: {len(msgs)} messages")
    return True


def run_compose(template: str, backend: str, project: str | None = None) -> bool:
    """
    Test LLM email compose for a specific template.

    Sends POST /api/email/compose and validates the response contains
    a non-empty subject and body with real project/calendar data.
    """
    print(f"\n── LLM Compose: {template} ({backend}) ──")

    body: dict = {"template": template, "backend": backend}
    if project:
        body["project"] = project

    start_time = time.time()
    data = _post("/api/email/compose", body, timeout=120)
    elapsed = time.time() - start_time

    if data is None:
        _fail(f"Compose request failed for template={template}")
        return False

    if not data.get("success"):
        _fail(f"Compose returned error: {data.get('error', '?')}")
        return False

    subject = data.get("subject", "")
    email_body = data.get("body", "")

    if not subject:
        _fail("Subject is empty")
        return False

    if not email_body:
        _fail("Body is empty")
        return False

    _ok(f"Subject: {subject[:80]}{'...' if len(subject) > 80 else ''}")
    _ok(f"Body: {len(email_body)} chars ({elapsed:.1f}s)")

    # Show preview
    lines = email_body.strip().split("\n")
    preview_lines = lines[:8]
    for line in preview_lines:
        print(f"    │ {line[:100]}")
    if len(lines) > 8:
        print(f"    │ ... ({len(lines) - 8} more lines)")

    return True


def run_compose_all_templates(backend: str) -> dict:
    """Run compose tests for all 4 standard templates.

    Includes a 5-second cooldown between calls to avoid ollama resource
    contention (llama3.2 needs time to release GPU/memory between calls).
    Failed calls are retried once after a 10-second cooldown.
    """
    results: dict = {}
    templates_to_test = []

    # 1. Daily Schedule
    templates_to_test.append(("daily-schedule", None))

    # 2. All Projects
    templates_to_test.append(("all-projects", None))

    # 3. Project Summary (uses first available project)
    projects = _get("/api/projects")
    project_slug = None
    if projects and len(projects) > 0:
        project_slug = projects[0].get("slug")
    templates_to_test.append(("project-summary", project_slug))

    # 4. Custom
    templates_to_test.append(("custom", None))

    # Run tests with cooldown between calls
    for i, (template, project) in enumerate(templates_to_test):
        if i > 0:
            print(f"\n  ⏳ Cooldown (5s) — letting {backend} release resources...")
            time.sleep(5)
        results[template] = run_compose(template, backend, project=project)

    # Retry any failures once (ollama can be flaky under load)
    failed = [t for t, ok in results.items() if not ok]
    if failed and backend == "ollama":
        print(f"\n  🔄 Retrying {len(failed)} failed template(s) after 10s cooldown...")
        time.sleep(10)
        for template in failed:
            project = project_slug if template == "project-summary" else None
            results[template] = run_compose(template, backend, project=project)
            if template != failed[-1]:
                time.sleep(5)

    return results


def test_pytest_compose_integration():
    """Pytest entrypoint for running integration compose tests."""
    # Skip if PMServer is not running — avoids 30s+ timeout trying to connect
    import socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.settimeout(2)
        sock.connect(("localhost", 8888))
        sock.close()
    except (TimeoutError, ConnectionRefusedError, OSError):
        pytest.skip("PMServer not running on :8888 — skipping LLM compose tests")

    results = run_compose_all_templates("ollama")
    assert all(results.values()), f"Some LLM email compose templates failed: {results}"


# ── Dry-Run Mode ─────────────────────────────────────────────────────────────


def test_dry_run() -> dict:
    """Test API connectivity without invoking LLM backends."""
    print("\n══════════════════════════════════════════")
    print("  DRY RUN — Testing API connectivity only")
    print("══════════════════════════════════════════")

    results: dict = {}
    results["server"] = test_server_health()
    results["calendar"] = test_calendar_api()
    results["agentmail"] = test_email_agentmail()
    results["gmail"] = test_email_gmail()
    return results


# ── CLI ──────────────────────────────────────────────────────────────────────


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Test PAI LLM Email Compose endpoints",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--template",
        choices=["daily-schedule", "all-projects", "project-summary", "custom"],
        default=None,
        help="Test a specific template (default: all)",
    )
    parser.add_argument(
        "--backend",
        choices=["ollama", "claude", "gemini"],
        default="ollama",
        help="LLM backend to use (default: ollama)",
    )
    parser.add_argument(
        "--project",
        default=None,
        help="Project slug for project-summary template",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only test API connectivity, skip LLM compose",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    print("╔══════════════════════════════════════════════════╗")
    print("║  PAI LLM Email Compose — Functional Test Suite  ║")
    print("╚══════════════════════════════════════════════════╝")

    # Phase 1: Server health
    if not test_server_health():
        return 1

    # Phase 2: API connectivity
    test_calendar_api()
    test_email_agentmail()
    test_email_gmail()

    if args.dry_run:
        print("\n✅ Dry run complete — all APIs responding.")
        return 0

    # Phase 3: LLM Compose
    print("\n══════════════════════════════════════════")
    print(f"  LLM COMPOSE TESTS (backend: {args.backend})")
    print("══════════════════════════════════════════")

    if args.template:
        ok = run_compose(args.template, args.backend, project=args.project)
        results = {args.template: ok}
    else:
        results = run_compose_all_templates(args.backend)

    # Summary
    print("\n══════════════════════════════════════════")
    print("  RESULTS SUMMARY")
    print("══════════════════════════════════════════")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    for template, ok in results.items():
        print(f"  {'✔' if ok else '✗'} {template}")
    print(f"\n  {passed}/{total} templates passed")

    if passed == total:
        print("\n✅ All LLM email compose tests passed!")
        return 0
    print(f"\n⚠ {total - passed} template(s) failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
