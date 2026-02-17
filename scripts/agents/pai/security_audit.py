#!/usr/bin/env python3
"""
PAI Security Audit

Deep security analysis of the PAI integration: security config, TELOS files,
destructive tool classification, environment variables, and trust boundaries.

Usage:
    python scripts/agents/pai/security_audit.py                         # Full audit
    python scripts/agents/pai/security_audit.py --section classification # Tool classification only
    python scripts/agents/pai/security_audit.py --json                   # JSON output

Upstream: https://github.com/danielmiessler/Personal_AI_Infrastructure
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.agents.pai import (
    PAIBridge,
    TrustLevel,
    SAFE_TOOLS,
    DESTRUCTIVE_TOOLS,
    SAFE_TOOL_COUNT,
    DESTRUCTIVE_TOOL_COUNT,
    get_trust_report,
)
from codomyrmex.utils.cli_helpers import (
    setup_logging, print_info, print_success, print_warning, print_error,
)

SECTIONS = ["security", "telos", "classification", "env", "trust"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="PAI Security Audit — security config, TELOS, tool classification",
    )
    parser.add_argument("--section", "-s", choices=SECTIONS, help="Show specific section")
    parser.add_argument("--json", "-j", action="store_true", dest="json_output", help="JSON output")
    return parser.parse_args()


def _header(title: str) -> None:
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}")


def section_security(bridge: PAIBridge) -> dict:
    """Security system configuration."""
    config = bridge.get_security_config()
    _header("Security System Configuration")
    if not config:
        print_warning("  No security configuration found.")
        return {"security": {}}
    for key, val in config.items():
        print(f"  {key:30s}  {val}")
    return {"security": config}


def section_telos(bridge: PAIBridge) -> dict:
    """TELOS identity and mission files."""
    files = bridge.get_telos_files()
    _header(f"TELOS Identity ({len(files)} files)")
    if not files:
        print_warning("  No TELOS files found.")
        return {"telos": [], "count": 0}
    for f in sorted(files):
        print(f"  📄 {f}")
    print(f"\n  Total: {len(files)} identity files")
    return {"telos": files, "count": len(files)}


def section_classification() -> dict:
    """Tool classification: safe vs destructive."""
    _header("Tool Classification")

    print(f"  Trust levels: {', '.join(t.value for t in TrustLevel)}")
    print()

    # Destructive tools
    destructive = sorted(DESTRUCTIVE_TOOLS) if DESTRUCTIVE_TOOLS else []
    print(f"  🔴 DESTRUCTIVE tools ({DESTRUCTIVE_TOOL_COUNT}):")
    for t in destructive:
        print(f"    ⚠️  {t}")

    # Safe tools (may be a lazy proxy — try to iterate)
    print(f"\n  🟢 SAFE tools ({SAFE_TOOL_COUNT}):")
    try:
        safe = sorted(SAFE_TOOLS)
        for t in safe[:15]:
            print(f"    ✅ {t}")
        if len(safe) > 15:
            print(f"    ... and {len(safe) - 15} more")
    except Exception:
        print(f"    (lazy-evaluated, {SAFE_TOOL_COUNT} total)")

    print(f"\n  Total classified: {SAFE_TOOL_COUNT} safe + {DESTRUCTIVE_TOOL_COUNT} destructive")

    return {
        "destructive_count": int(DESTRUCTIVE_TOOL_COUNT),
        "safe_count": int(SAFE_TOOL_COUNT),
        "destructive_tools": destructive,
    }


def section_env(bridge: PAIBridge) -> dict:
    """Settings and environment variables."""
    settings = bridge.get_settings()
    env = bridge.get_pai_env()
    _header("Settings & Environment")

    if settings:
        print(f"  settings.json keys: {list(settings.keys())}")
        # Highlight security-relevant keys (don't show values)
        security_keys = [k for k in settings if any(s in k.lower() for s in ["key", "token", "secret", "auth"])]
        if security_keys:
            print(f"  ⚠️  Security-sensitive keys detected: {security_keys}")
            print(f"     (values hidden for security)")
    else:
        print_info("  settings.json: not found")

    print(f"\n  PAI environment variables ({len(env)}):")
    for k, v in list(env.items())[:8]:
        # Mask potential secrets
        if any(s in k.lower() for s in ["key", "token", "secret"]):
            display = "***MASKED***"
        else:
            display = v if len(v) < 50 else v[:47] + "..."
        print(f"    {k} = {display}")
    if len(env) > 8:
        print(f"    ... and {len(env) - 8} more")

    return {
        "settings_keys": list((settings or {}).keys()),
        "env_count": len(env),
        "has_sensitive_keys": bool([k for k in (settings or {}) if "key" in k.lower()]),
    }


def section_trust() -> dict:
    """Current trust state report."""
    _header("Trust State Report")
    report = get_trust_report()

    if not report:
        print_warning("  No trust report available.")
        return {"trust": {}}

    by_level = report.get("by_level", {})
    counts = report.get("counts", {})

    for level, tools in by_level.items():
        count = len(tools) if isinstance(tools, list) else tools
        print(f"  {level:15s}: {count}")

    print(f"\n  Summary: {counts}")
    return {"trust": report}


def main() -> int:
    args = parse_args()
    setup_logging()

    bridge = PAIBridge()
    if not bridge.is_installed():
        print_warning("PAI is not installed. Showing empty results.")

    results: dict = {}
    fns = {
        "security": lambda: section_security(bridge),
        "telos": lambda: section_telos(bridge),
        "classification": section_classification,
        "env": lambda: section_env(bridge),
        "trust": section_trust,
    }

    if args.section:
        results[args.section] = fns[args.section]()
    else:
        for name, fn in fns.items():
            results[name] = fn()

    if args.json_output:
        print("\n" + json.dumps(results, indent=2, default=str))

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
