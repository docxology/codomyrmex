#!/usr/bin/env python3
"""
Artifact Inspector for Antigravity
Lists and inspects all artifacts in the current conversation.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

# Ensure project root is in path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from codomyrmex.ide.antigravity import AntigravityClient

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("antigravity.inspector")


def inspect_artifacts():
    client = AntigravityClient()

    if not client.connect():
        logger.error("❌ Not connected to Antigravity.")
        return False

    logger.info(f"🔍 Inspecting Conversation: {client.get_conversation_id()}")

    artifacts = client.list_artifacts()
    logger.info(f"Found {len(artifacts)} artifacts.\n")

    for i, art in enumerate(artifacts, 1):
        modified_time = datetime.fromtimestamp(art["modified"]).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        logger.info(f"[{i}] {art['name']} ({art['type']})")
        logger.info(f"    Path: {art['path']}")
        logger.info(f"    Size: {art['size']} bytes")
        logger.info(f"    Modified: {modified_time}")
        logger.info("-" * 40)

    return True

    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml

    config_path = (
        Path(__file__).resolve().parent.parent.parent / "config" / "ide" / "config.yaml"
    )
    if config_path.exists():
        with open(config_path) as f:
            yaml.safe_load(f) or {}
            print("Loaded config from config/ide/config.yaml")


if __name__ == "__main__":
    inspect_artifacts()
