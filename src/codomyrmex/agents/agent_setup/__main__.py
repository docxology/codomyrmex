"""Entry point: ``python -m codomyrmex.agents.agent_setup``."""

import argparse

from codomyrmex.agents.agent_setup.setup_wizard import run_setup_wizard


def main():
    """main ."""
    parser = argparse.ArgumentParser(
        description="Codomyrmex Agent Setup — configure and verify agents",
    )
    parser.add_argument(
        "--config", "-c",
        help="Path to YAML config file (default ~/.codomyrmex/agents.yaml)",
        default=None,
    )
    parser.add_argument(
        "--status-only", "-s",
        action="store_true",
        help="Print status table and exit (no interactive prompts)",
    )
    args = parser.parse_args()

    run_setup_wizard(
        config_path=args.config,
        non_interactive=args.status_only,
    )


if __name__ == "__main__":
    main()
