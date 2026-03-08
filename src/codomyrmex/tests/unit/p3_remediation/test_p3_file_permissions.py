"""
TDD regression tests for P3 CodeQL overly-permissive chmod remediation.

Verifies that ``synthesize_build_artifact`` produces files with owner-only
permissions (0o700) instead of overly permissive (0o755).

Zero-Mock compliant — uses real file operations.
"""

import stat

import pytest

from codomyrmex.ci_cd_automation.build.pipeline.build_orchestrator import (
    synthesize_build_artifact,
)


@pytest.mark.unit
class TestBuildArtifactPermissions:
    """Verify synthesized build artifacts have secure permissions."""

    def test_synthesized_artifact_has_owner_only_permissions(self, tmp_path):
        """Synthesized artifact must have mode 0o700 (owner rwx only)."""
        source = tmp_path / "source.py"
        source.write_text("print('hello')\n")

        output = tmp_path / "artifact.py"
        result = synthesize_build_artifact(str(source), str(output))

        assert result is True, "Build artifact synthesis should succeed"
        assert output.exists(), "Output file must exist"

        # Extract permission bits (last 9 bits)
        mode = output.stat().st_mode & 0o777
        assert mode == 0o700, (
            f"Artifact permissions should be 0o700 (owner-only), got {oct(mode)}"
        )

    def test_synthesized_artifact_not_world_executable(self, tmp_path):
        """Synthesized artifact must NOT be world-executable."""
        source = tmp_path / "source.py"
        source.write_text("x = 1\n")

        output = tmp_path / "artifact2.py"
        synthesize_build_artifact(str(source), str(output))

        mode = output.stat().st_mode
        # Check that 'others' have NO permissions at all
        assert not (mode & stat.S_IROTH), "Others should not have read permission"
        assert not (mode & stat.S_IWOTH), "Others should not have write permission"
        assert not (mode & stat.S_IXOTH), "Others should not have execute permission"

    def test_synthesized_artifact_not_group_executable(self, tmp_path):
        """Synthesized artifact must NOT be group-readable/executable."""
        source = tmp_path / "source.py"
        source.write_text("y = 2\n")

        output = tmp_path / "artifact3.py"
        synthesize_build_artifact(str(source), str(output))

        mode = output.stat().st_mode
        assert not (mode & stat.S_IRGRP), "Group should not have read permission"
        assert not (mode & stat.S_IWGRP), "Group should not have write permission"
        assert not (mode & stat.S_IXGRP), "Group should not have execute permission"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
