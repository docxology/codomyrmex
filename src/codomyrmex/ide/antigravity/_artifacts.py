"""Artifact management mixin for Antigravity IDE client.

Extracted from client.py.
"""

from __future__ import annotations

from typing import Any

from .models import Artifact, ArtifactError, ConversationContext


class AntigravityArtifactsMixin:
    """Mixin for managing Antigravity artifacts and context."""

    # Note: Requires self._conversation_id, self.artifact_dir, self.emit_event, self._connected

    def get_context(self) -> ConversationContext | None:
        """Get the current conversation context.

        Returns:
            ConversationContext or None if not connected.
        """
        return self._context

    def _load_context(self) -> ConversationContext | None:
        """Load conversation context from artifacts."""
        if not self._conversation_id:
            return None

        context = ConversationContext(conversation_id=self._conversation_id)
        context.artifacts = self._scan_artifacts()

        # Try to load task.md for task info
        task_artifact = self._get_artifact_by_name("task")
        if task_artifact:
            context.task_name = "Current Task"
            context.task_status = "Active"

        return context

    def _scan_artifacts(self) -> list[Artifact]:
        """Scan the conversation directory for artifacts."""
        artifacts = []
        if not self._conversation_id:
            return artifacts

        conversation_dir = self.artifact_dir / self._conversation_id
        if not conversation_dir.exists():
            return artifacts

        for item in conversation_dir.iterdir():
            if item.is_file() and item.suffix == ".md":
                # Determine artifact type from name
                artifact_type = "other"
                if item.stem == "task":
                    artifact_type = "task"
                elif "implementation" in item.stem.lower():
                    artifact_type = "implementation_plan"
                elif "walkthrough" in item.stem.lower():
                    artifact_type = "walkthrough"

                artifacts.append(
                    Artifact(
                        name=item.stem,
                        path=str(item),
                        artifact_type=artifact_type,
                        size=item.stat().st_size,
                        modified=item.stat().st_mtime,
                    )
                )

        return artifacts

    def _get_artifact_by_name(self, name: str) -> Artifact | None:
        """Get an artifact by name."""
        if not self._context:
            return None
        for artifact in self._context.artifacts:
            if artifact.name == name:
                return artifact
        return None

    def list_artifacts(self) -> list[dict[str, Any]]:
        """list conversation artifacts.

        Returns:
            list of artifact metadata dictionaries.
        """
        if not self._connected or not self._conversation_id:
            return []

        # Always refresh artifacts on list
        self._context = self._load_context()
        if not self._context:
            return []

        return [a.to_dict() for a in self._context.artifacts]

    def get_artifact(self, name: str) -> dict[str, Any] | None:
        """Get a specific artifact by name.

        Args:
            name: Artifact name (without extension).

        Returns:
            dict with artifact data including content.
        """
        if not self._connected or not self._conversation_id:
            return None

        conversation_dir = self.artifact_dir / self._conversation_id
        artifact_path = conversation_dir / f"{name}.md"

        if not artifact_path.exists():
            return None

        try:
            content = artifact_path.read_text()
            return {
                "name": name,
                "path": str(artifact_path),
                "content": content,
                "size": len(content),
                "modified": artifact_path.stat().st_mtime,
            }
        except Exception as e:
            return {"error": str(e)}

    def create_artifact(
        self, name: str, content: str, artifact_type: str = "other"
    ) -> dict[str, Any]:
        """Create a new artifact.

        Args:
            name: Artifact name (without extension).
            content: Artifact content.
            artifact_type: Type of artifact (task, implementation_plan, walkthrough, other).

        Returns:
            dict with artifact metadata.

        Raises:
            ArtifactError: If artifact creation fails.
        """
        if not self._connected or not self._conversation_id:
            raise ArtifactError("Not connected to Antigravity session")

        if artifact_type not in self.ARTIFACT_TYPES:
            raise ArtifactError(f"Invalid artifact type: {artifact_type}")

        conversation_dir = self.artifact_dir / self._conversation_id
        try:
            conversation_dir.mkdir(parents=True, exist_ok=True)

            artifact_path = conversation_dir / f"{name}.md"
            artifact_path.write_text(content)

            # Refresh context
            self._context = self._load_context()

            self.emit_event("artifact_created", {"name": name, "type": artifact_type})

            return {
                "name": name,
                "path": str(artifact_path),
                "type": artifact_type,
                "size": len(content),
                "created": True,
            }
        except Exception as e:
            raise ArtifactError(f"Failed to create artifact: {e}") from e

    def update_artifact(self, name: str, content: str) -> dict[str, Any]:
        """Update an existing artifact.

        Args:
            name: Artifact name (without extension).
            content: New artifact content.

        Returns:
            dict with artifact metadata.

        Raises:
            ArtifactError: If artifact doesn't exist or update fails.
        """
        if not self._connected or not self._conversation_id:
            raise ArtifactError("Not connected to Antigravity session")

        conversation_dir = self.artifact_dir / self._conversation_id
        artifact_path = conversation_dir / f"{name}.md"

        if not artifact_path.exists():
            raise ArtifactError(f"Artifact not found: {name}")

        try:
            artifact_path.write_text(content)

            # Refresh context
            self._context = self._load_context()

            self.emit_event("artifact_updated", {"name": name})

            return {
                "name": name,
                "path": str(artifact_path),
                "size": len(content),
                "updated": True,
            }
        except Exception as e:
            raise ArtifactError(f"Failed to update artifact: {e}") from e

    def delete_artifact(self, name: str) -> bool:
        """Delete an artifact.

        Args:
            name: Artifact name (without extension).

        Returns:
            bool: True if deleted successfully.

        Raises:
            ArtifactError: If artifact doesn't exist.
        """
        if not self._connected or not self._conversation_id:
            raise ArtifactError("Not connected to Antigravity session")

        conversation_dir = self.artifact_dir / self._conversation_id
        artifact_path = conversation_dir / f"{name}.md"

        if not artifact_path.exists():
            raise ArtifactError(f"Artifact not found: {name}")

        try:
            artifact_path.unlink()

            # Refresh context
            self._context = self._load_context()

            self.emit_event("artifact_deleted", {"name": name})

            return True
        except Exception as e:
            raise ArtifactError(f"Failed to delete artifact: {e}") from e
