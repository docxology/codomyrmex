#!/usr/bin/env python3
"""Thin Orchestration Example — v1.0.4 Quality Gate Demo.

Demonstrates real cross-module integration across 4 Codomyrmex subsystems
without mocks, stubs, or placeholder logic. Each section exercises a
concrete implementation that landed in the v1.0.3→v1.0.4 cycle.

Usage:
    python scripts/examples/orchestration_demo.py
"""

import sys
import tempfile
from pathlib import Path

# Ensure codomyrmex is importable
try:
    import codomyrmex  # noqa: F401
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

# ── 1. Document Conversion ────────────────────────────────────────────
from codomyrmex.documents.transformation.converter import _to_markdown
from codomyrmex.documents.models.document import DocumentFormat

html_input = "<h1>Hello</h1><p>This is a <strong>test</strong> document.</p>"
md_output = _to_markdown(html_input, DocumentFormat.HTML)
print("─── Document Conversion (HTML → Markdown) ───")
print(f"  Input:  {html_input[:60]}…")
print(f"  Output: {md_output.strip()[:80]}")
assert len(md_output.strip()) > 0, "Conversion produced empty output"
print("  ✅ Real conversion — no mocks\n")


# ── 2. Config Change Detection ────────────────────────────────────────
from codomyrmex.config_management.monitoring.config_monitor import ConfigurationMonitor

with tempfile.TemporaryDirectory() as tmpdir:
    monitor = ConfigurationMonitor(workspace_dir=tmpdir)
    monitor.monitoring_dir.mkdir(parents=True, exist_ok=True)

    # Persist a hash
    monitor._persist_hashes({"/etc/app.yaml": "abc123"})

    # Retrieve it
    retrieved = monitor._get_previous_hash("/etc/app.yaml")
    assert retrieved == "abc123", f"Expected abc123, got {retrieved}"

    # Update it
    monitor._persist_hashes({"/etc/app.yaml": "def456"})
    updated = monitor._get_previous_hash("/etc/app.yaml")
    assert updated == "def456", f"Expected def456, got {updated}"

    print("─── Config Change Detection (Hash Persistence) ───")
    print(f"  Stored: abc123 → Retrieved: abc123 ✓")
    print(f"  Updated: def456 → Retrieved: def456 ✓")
    print("  ✅ Real filesystem I/O — no mocks\n")


# ── 3. Patch Generator Parsing ────────────────────────────────────────
from codomyrmex.coding.debugging.error_analyzer import ErrorDiagnosis
from codomyrmex.coding.debugging.patch_generator import PatchGenerator

gen = PatchGenerator(llm_client=None)
diagnosis = ErrorDiagnosis("NameError", "name 'x' is not defined", "app.py", 10, "trace")

# Feed a simulated LLM response with a fenced diff
llm_response = (
    "The fix is to initialize x:\n"
    "```diff\n"
    "--- a/app.py\n"
    "+++ b/app.py\n"
    "@@ -10 +10,2 @@\n"
    "-print(x)\n"
    "+x = 0\n"
    "+print(x)\n"
    "```\n"
)
patches = gen._parse_patches(llm_response, diagnosis)

print("─── Patch Generator (Diff Parsing) ───")
print(f"  Input: {len(llm_response)} chars of LLM response")
print(f"  Extracted: {len(patches)} patch(es)")
print(f"  Confidence: {patches[0].confidence}")
print(f"  Diff snippet: {patches[0].diff[:60]}…")
assert len(patches) == 1
assert patches[0].confidence == 0.9
print("  ✅ Real parsing — no mocks\n")


# ── 4. OllamaClient Session Management ───────────────────────────────
from codomyrmex.agents.llm_client import OllamaClient

client = OllamaClient()
client.create_session("demo_session")

print("─── OllamaClient Session Management ───")
print(f"  Sessions: {list(client.session_manager.keys())}")
assert "demo_session" in client.session_manager

client.close_session("demo_session")
assert "demo_session" not in client.session_manager
print("  Created → Closed demo_session ✓")
print("  ✅ Real state management — no mocks\n")


# ── Summary ───────────────────────────────────────────────────────────
print("═══════════════════════════════════════")
print("  All 4 orchestration checks passed ✅")
print("═══════════════════════════════════════")
