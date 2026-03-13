"""Bi-directional sync between Obsidian Vault and Agentic Memory."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from codomyrmex.agentic_memory.models import MemoryImportance, MemoryType
from codomyrmex.agentic_memory.obsidian.crud import (
    create_note,
    set_frontmatter,
)
from codomyrmex.logging_monitoring import get_logger

if TYPE_CHECKING:
    from codomyrmex.agentic_memory.memory import VectorStoreMemory
    from codomyrmex.agentic_memory.obsidian.vault import ObsidianVault

logger = get_logger(__name__)


class ObsidianMemoryBridge:
    """Synchronizes an Obsidian Vault with an Agentic Memory VectorStore.

    This bridge allows parsing Obsidian notes into semantic memories,
    tagging the markdown files with an `agentic_id` to track the connection,
    and also exporting raw abstract memories back into Obsidian as Markdown.
    """

    def __init__(
        self,
        vault: ObsidianVault,
        memory: VectorStoreMemory,
        export_folder: str = "Memories",
    ):
        self.vault = vault
        self.memory = memory
        self.export_folder = export_folder.strip("/")

    def ingest_vault(self) -> dict[str, Any]:
        """Scan the vault and ingest notes into agentic memory.

        Notes with an `agentic_id` in their frontmatter are matched against
        the store. If the memory content is out-of-sync with the note, or if
        it does not exist, it is updated.
        """
        stats = {"added": 0, "updated": 0, "skipped": 0, "errors": 0}

        self.vault.refresh()

        for name in self.vault.list_notes():
            try:
                note = self.vault.get_note(name)
                if not note:
                    stats["errors"] += 1
                    continue

                frontmatter = note.frontmatter
                agentic_id = frontmatter.get("agentic_id")

                content = note.content.strip()
                if not content:
                    stats["skipped"] += 1
                    continue

                imp_str = str(frontmatter.get("importance", "medium")).upper()
                try:
                    importance = MemoryImportance[imp_str]
                except KeyError:
                    importance = MemoryImportance.MEDIUM

                meta = {"source": "obsidian", "path": name, "title": note.title}

                if agentic_id:
                    # Check if memory exists
                    mem = self.memory.store.get(agentic_id)
                    if mem:
                        # If content differs, update memory
                        if mem.content != content:
                            mem.content = content
                            mem.importance = importance
                            mem.metadata.update(meta)
                            self.memory.store.save(mem)

                            # Update vector if applicable
                            if self.memory.vector_store and self.memory._embedder:
                                embedding = self.memory._embedder.encode(
                                    content
                                ).tolist()
                                self.memory.vector_store.add(
                                    id=mem.id,
                                    embedding=embedding,
                                    metadata={
                                        "importance": mem.importance.value,
                                        "type": mem.memory_type.value,
                                    },
                                )
                            stats["updated"] += 1
                        else:
                            stats["skipped"] += 1
                    else:
                        # Agentic ID is present but memory is gone. We re-create it but we
                        # cannot force the ID cleanly via VectorStoreMemory.remember unless we modify the store directly.
                        # It's safer to just let remember() generate a new one and update the frontmatter.
                        new_mem = self.memory.remember(
                            content,
                            memory_type=MemoryType.SEMANTIC,
                            importance=importance,
                            metadata=meta,
                        )
                        set_frontmatter(self.vault, name, {"agentic_id": new_mem.id})
                        stats["added"] += 1
                else:
                    # New ingest
                    new_mem = self.memory.remember(
                        content,
                        memory_type=MemoryType.SEMANTIC,
                        importance=importance,
                        metadata=meta,
                    )
                    set_frontmatter(self.vault, name, {"agentic_id": new_mem.id})
                    stats["added"] += 1

            except Exception as e:
                logger.error("Failed to ingest note %s: %s", name, e)
                stats["errors"] += 1

        return stats

    def export_memories(self) -> dict[str, Any]:
        """Export raw agentic memories to the vault.

        Memories that do not have `source: obsidian` and match the criteria
        are written as new markdown files in the `export_folder`.
        """
        stats = {"created": 0, "skipped": 0, "errors": 0}

        all_mems = self.memory.store.list_all()

        # Build inverted index of agentic_id -> note path
        self.vault.refresh()
        id_to_path = {}
        for name in self.vault.list_notes():
            note = self.vault.get_note(name)
            if note and "agentic_id" in note.frontmatter:
                id_to_path[note.frontmatter["agentic_id"]] = name

        for mem in all_mems:
            try:
                if mem.id in id_to_path:
                    # Already tracked by a note
                    stats["skipped"] += 1
                    continue

                # Do not export if it's already recorded as coming from obsidian
                # (but somehow we couldn't find the file - maybe it was deleted outside Obsidian)
                if mem.metadata.get("source") == "obsidian":
                    stats["skipped"] += 1
                    continue

                # Not tracked, let's export it
                # Create a title
                # We can use the first few words or ID if too short
                words = mem.content.split()[:5]
                if words:
                    title_slug = (
                        "-".join(w.lower() for w in words)
                        .replace(".", "")
                        .replace(",", "")
                    )
                    safe_title = f"{title_slug}-{mem.id[:6]}"
                else:
                    safe_title = f"Memory-{mem.id[:8]}"

                path = f"{self.export_folder}/{safe_title}.md"

                fm = {
                    "agentic_id": mem.id,
                    "importance": mem.importance.value,
                    "memory_type": mem.memory_type.value,
                    "source": "agentic_memory",
                }

                # Tags
                if mem.tags:
                    fm["tags"] = mem.tags

                # Additional metadata properties
                for k, v in mem.metadata.items():
                    if k not in fm and isinstance(v, (str, int, float, bool, list)):
                        fm[k] = v

                create_note(self.vault, path, content=mem.content, frontmatter=fm)
                stats["created"] += 1

            except Exception as e:
                logger.error("Failed to export memory %s: %s", mem.id, e)
                stats["errors"] += 1

        return stats

    def sync(self) -> dict[str, dict[str, Any]]:
        """Run bidirectional sync.

        First exports new agentic memories to Obsidian.
        Then ingests Obsidian notes (and their changes) back to memory.
        """
        export_stats = self.export_memories()

        self.vault.refresh()
        ingest_stats = self.ingest_vault()

        return {"export": export_stats, "ingest": ingest_stats}
