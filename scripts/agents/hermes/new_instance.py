#!/usr/bin/env python3
"""Hermes Agent — New Instance Creator.

Creates a fully configured new Hermes agent instance with its own
HERMES_HOME, config.yaml, .env, and optional launchd plist.

Usage:
    python scripts/agents/hermes/new_instance.py --name crescent-city
    python scripts/agents/hermes/new_instance.py --name crescent-city --telegram-token 123:AAxxxx
    python scripts/agents/hermes/new_instance.py --name my-bot --openrouter-key sk-or-v1-xxx --personality "You are a coding expert."
"""

import argparse
import os
import shutil
import sys
from pathlib import Path

# Bootstrap path
try:
    from codomyrmex.utils.cli_helpers import (
        print_error,
        print_info,
        print_success,
        setup_logging,
    )
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "src"))
    from codomyrmex.utils.cli_helpers import (
        print_error,
        print_info,
        print_success,
        setup_logging,
    )


_DEFAULT_MODEL = "nvidia/nemotron-3-super-120b-a12b:free"
_DEFAULT_SUMMARY_MODEL = "google/gemini-3-flash-preview"
_HERMES_SUBDIRS = [
    "cron",
    "sessions",
    "logs",
    "memories",
    "skills",
    "pairing",
    "hooks",
    "image_cache",
    "audio_cache",
    "whatsapp/session",
]


def _generate_config_yaml(
    *,
    model: str,
    personality: str,
    personality_name: str,
    summary_model: str,
    max_turns: int,
    reasoning_effort: str,
) -> str:
    """Generate a config.yaml for a new Hermes instance.

    Args:
        model: LLM model identifier (OpenRouter format).
        personality: Personality system prompt text.
        personality_name: Name for the personality key.
        summary_model: Model for context compression.
        max_turns: Maximum agent turns per session.
        reasoning_effort: Reasoning effort level (low/medium/high).

    Returns:
        YAML content as string.
    """
    return f"""# Hermes Agent Configuration
# Instance created by Codomyrmex new_instance.py
# Docs: https://hermes-agent.nousresearch.com/docs/user-guide/configuration

model: {model}

toolsets:
  - all

agent:
  max_turns: {max_turns}
  verbose: false
  reasoning_effort: {reasoning_effort}
  personality: {personality_name}
  personalities:
    {personality_name}: |
      {personality}

compression:
  enabled: true
  threshold: 0.85
  summary_model: {summary_model}

terminal:
  backend: local
  timeout: 180

telegram:
  require_mention: true
  free_response_channels: ""
"""


def _generate_env_file(
    *,
    openrouter_key: str,
    telegram_token: str,
    telegram_user: str,
) -> str:
    """Generate a .env file for a new Hermes instance.

    Args:
        openrouter_key: OpenRouter API key.
        telegram_token: Telegram bot token (from BotFather).
        telegram_user: Telegram username for access control.

    Returns:
        .env content as string.
    """
    lines = [
        "# Hermes Agent — Environment Variables",
        "# Created by Codomyrmex new_instance.py",
        "",
        "# LLM Provider",
        f"OPENROUTER_API_KEY={openrouter_key}",
    ]
    if telegram_token:
        lines += [
            "",
            "# Telegram Gateway",
            f"TELEGRAM_BOT_TOKEN={telegram_token}",
            f"TELEGRAM_ALLOWED_USERS={telegram_user}",
            f"TELEGRAM_HOME_CHANNEL={telegram_user}",
        ]
    lines += [
        "",
        "# Optional: uncomment to enable",
        "# FIRECRAWL_API_KEY=fc-...",
        "# FAL_KEY=...",
        "# ELEVENLABS_API_KEY=...",
        "# HONCHO_API_KEY=...",
    ]
    return "\n".join(lines) + "\n"


def _generate_launchd_plist(name: str, hermes_home: Path, hermes_bin: str) -> str:
    """Generate a launchd plist for a Hermes gateway instance.

    Args:
        name: Instance name (used in plist label).
        hermes_home: Absolute path to HERMES_HOME directory.
        hermes_bin: Absolute path to the hermes binary.

    Returns:
        XML plist content as string.
    """
    label = f"ai.hermes.gateway.{name}"
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{label}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{hermes_bin}</string>
        <string>gateway</string>
        <string>run</string>
        <string>--replace</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>HERMES_HOME</key>
        <string>{hermes_home}</string>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:{Path.home()}/.local/bin</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>{hermes_home}/logs/gateway.log</string>
    <key>StandardErrorPath</key>
    <string>{hermes_home}/logs/gateway.error.log</string>
    <key>WorkingDirectory</key>
    <string>{hermes_home.parent}</string>
</dict>
</plist>
"""


def create_instance(args: argparse.Namespace) -> int:
    """Create a new Hermes agent instance.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 success, 1 failure).
    """
    name: str = args.name
    base_dir = Path(args.base_dir).expanduser().resolve() if args.base_dir else Path.home() / f"hermes-{name}"
    hermes_home = base_dir / ".hermes"

    print_info("═" * 60)
    print_info(f"  Creating Hermes Instance: {name}")
    print_info(f"  HERMES_HOME: {hermes_home}")
    print_info("═" * 60)

    # Check if already exists
    if hermes_home.exists() and not args.force:
        print_error(f"\n  ✗ HERMES_HOME already exists: {hermes_home}")
        print_error("  Use --force to overwrite.")
        return 1

    # 1. Create directory structure
    print_info("\n  Creating directory structure...")
    for subdir in _HERMES_SUBDIRS:
        (hermes_home / subdir).mkdir(parents=True, exist_ok=True)
        print_success(f"    ✓ {subdir}/")

    # 2. Generate config.yaml
    print_info("\n  Generating config.yaml...")
    config_content = _generate_config_yaml(
        model=args.model,
        personality=args.personality,
        personality_name=args.personality_name,
        summary_model=args.summary_model,
        max_turns=args.max_turns,
        reasoning_effort=args.reasoning_effort,
    )
    (hermes_home / "config.yaml").write_text(config_content)
    print_success("    ✓ config.yaml")

    # 3. Generate .env
    print_info("\n  Generating .env...")
    env_content = _generate_env_file(
        openrouter_key=args.openrouter_key or "sk-or-v1-your-key-here",
        telegram_token=args.telegram_token or "",
        telegram_user=args.telegram_user or "YourUsername",
    )
    env_path = hermes_home / ".env"
    env_path.write_text(env_content)
    os.chmod(env_path, 0o600)
    print_success("    ✓ .env (chmod 600)")

    # 4. Create SOUL.md (optional personality file)
    if args.soul:
        soul_content = args.soul
    else:
        soul_content = f"# {name.replace('-', ' ').title()}\n\nI am the {name} Hermes agent instance.\n"
    (hermes_home / "SOUL.md").write_text(soul_content)
    print_success("    ✓ SOUL.md")

    # 5. Generate launchd plist (macOS only)
    hermes_bin = shutil.which("hermes") or str(Path.home() / ".local/bin/hermes")
    if sys.platform == "darwin" and args.create_launchd:
        print_info("\n  Generating launchd plist...")
        plist_content = _generate_launchd_plist(name, hermes_home, hermes_bin)
        plist_path = Path.home() / "Library/LaunchAgents" / f"ai.hermes.gateway.{name}.plist"
        plist_path.write_text(plist_content)
        print_success(f"    ✓ {plist_path.name}")
        print_info(f"    Install: launchctl load {plist_path}")
        print_info(f"    Start:   launchctl start ai.hermes.gateway.{name}")

    # Summary
    print_info("\n" + "─" * 60)
    print_success(f"  Instance '{name}' created successfully!")
    print_info("")
    print_info("  Quick test:")
    print_info(f"    HERMES_HOME={hermes_home} hermes status")
    print_info(f"    HERMES_HOME={hermes_home} hermes doctor")
    print_info("")
    print_info("  Start gateway:")
    print_info(f"    HERMES_HOME={hermes_home} hermes gateway run")
    print_info("")
    if args.openrouter_key and args.openrouter_key != "sk-or-v1-your-key-here":
        print_info("  Start chat:")
        print_info(f'    HERMES_HOME={hermes_home} hermes chat -q "Hello!"')
    else:
        print_info("  ⚠ Add your OPENROUTER_API_KEY to .env before using:")
        print_info(f"    {hermes_home}/.env")
    return 0


def main() -> int:
    """Parse arguments and create the instance."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="Create a new Hermes Agent instance with its own HERMES_HOME.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --name crescent-city
  %(prog)s --name my-bot --openrouter-key sk-or-v1-xxx --telegram-token 123:AAxx
  %(prog)s --name researcher --personality "You are a research assistant." --model nousresearch/hermes-3-llama-3.1-405b-moe
        """,
    )
    parser.add_argument("--name", required=True, help="Instance name (e.g., crescent-city)")
    parser.add_argument("--base-dir", help="Base directory (default: ~/hermes-<name>)")
    parser.add_argument("--openrouter-key", help="OpenRouter API key")
    parser.add_argument("--telegram-token", help="Telegram bot token from @BotFather")
    parser.add_argument("--telegram-user", default="", help="Telegram username for access control")
    parser.add_argument("--model", default=_DEFAULT_MODEL, help=f"LLM model (default: {_DEFAULT_MODEL})")
    parser.add_argument("--summary-model", default=_DEFAULT_SUMMARY_MODEL, help="Model for compression")
    parser.add_argument("--personality", default="You are a helpful, intelligent AI assistant.", help="Personality prompt")
    parser.add_argument("--personality-name", default="helpful", help="Personality config key name")
    parser.add_argument("--soul", help="SOUL.md content (global persona)")
    parser.add_argument("--max-turns", type=int, default=150, help="Max agent turns")
    parser.add_argument("--reasoning-effort", choices=["low", "medium", "high"], default="medium", help="Reasoning effort")
    parser.add_argument("--create-launchd", action="store_true", help="Create macOS launchd plist")
    parser.add_argument("--force", action="store_true", help="Overwrite existing instance")
    args = parser.parse_args()
    return create_instance(args)


if __name__ == "__main__":
    sys.exit(main())
