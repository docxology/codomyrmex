"""Memory adapter for syncing Hermes sessions to long-term Obsidian Vaults."""

import os
from pathlib import Path

from codomyrmex.agentic_memory.obsidian import ObsidianVault, create_note
from codomyrmex.agents.hermes.session import HermesSession
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


def sync_session_to_vault(session: HermesSession, vault_path: str | Path) -> None:
    """Sync a HermesSession into an Obsidian vault cleanly.

    Args:
        session: The active HermesSession containing messages and metadata.
        vault_path: Path to the root of the local Obsidian Vault.
    """
    try:
        # Expand user and ensure absolute path
        expanded_path = Path(os.path.expanduser(str(vault_path))).resolve()

        # We assume the library guarantees directory existence but we'll try to
        # ensure the root vault dir is ready
        expanded_path.mkdir(parents=True, exist_ok=True)

        vault = ObsidianVault(expanded_path)

        content_lines = []
        for msg in session.messages:
            role = msg.get("role", "unknown").capitalize()
            content = msg.get("content", "")
            content_lines.append(f"### {role}\n{content}\n")

        content_str = "\n".join(content_lines)

        # Place sessions neatly into a Sessions/ subfolder in Obsidian
        name = f"Sessions/{session.name or session.session_id}"

        frontmatter = {
            "session_id": session.session_id,
            "type": "hermes_session",
            "updated_at": session.updated_at,
        }
        if session.parent_session_id:
            frontmatter["parent"] = session.parent_session_id

        create_note(
            vault=vault,
            name=name,
            content=content_str,
            frontmatter=frontmatter,
            overwrite=True,
        )
        logger.debug(
            "Synced session %s to Obsidian vault at %s",
            session.session_id,
            expanded_path,
        )
    except Exception as e:
        logger.error("Failed to sync session %s to vault: %s", session.session_id, e)
