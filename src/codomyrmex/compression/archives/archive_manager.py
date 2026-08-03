import stat
import tarfile
import zipfile
from pathlib import Path

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring import get_logger

"""Archive management for creating and extracting archives."""


logger = get_logger(__name__)


class CompressionError(CodomyrmexError):
    """Raised when compression operations fail."""


class ArchiveManager:
    """Manager for archive operations."""

    @staticmethod
    def _validate_member_path(output: Path, member_name: str) -> Path:
        """Return a safe extraction path for an archive member.

        Archive member names are untrusted input.  Resolving the candidate and
        checking its relationship to the resolved output directory avoids the
        string-prefix bypass where ``/tmp/out_evil`` incorrectly matched
        ``/tmp/out``.
        """
        output_root = output.resolve()
        member_path = (output_root / member_name).resolve()
        try:
            member_path.relative_to(output_root)
        except ValueError as exc:
            raise CompressionError(
                f"Blocked path traversal attempt: {member_name}"
            ) from exc
        return member_path

    def create_archive(
        self, files: list[Path], output: Path, format: str = "zip"
    ) -> bool:
        """Create an archive containing multiple files.

        Args:
            files: list of file paths to include
            output: Output archive path
            format: Archive format (zip, tar, tar.gz)

        Returns:
            True if successful

        Raises:
            CompressionError: If archive creation fails
        """
        try:
            if format == "zip":
                with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
                    for file_path in files:
                        if file_path.exists():
                            zf.write(file_path, file_path.name)
                return True
            if format in ["tar", "tar.gz"]:
                mode = "w:gz" if format == "tar.gz" else "w"
                with tarfile.open(output, mode) as tf:
                    for file_path in files:
                        if file_path.exists():
                            tf.add(file_path, arcname=file_path.name)
                return True
            raise ValueError(f"Unknown format: {format}")
        except Exception as e:
            logger.error("Archive creation error: %s", e)
            raise CompressionError(f"Failed to create archive: {e!s}") from e

    def extract_archive(self, archive: Path, output: Path) -> bool:
        """Extract files from an archive.

        Args:
            archive: Archive file path
            output: Output directory path

        Returns:
            True if successful

        Raises:
            CompressionError: If extraction fails
        """
        try:
            output.mkdir(parents=True, exist_ok=True)

            if archive.suffix == ".zip":
                with zipfile.ZipFile(archive, "r") as zf:
                    for member in zf.infolist():
                        ArchiveManager._validate_member_path(output, member.filename)
                        mode = (member.external_attr >> 16) & 0o170000
                        if stat.S_ISLNK(mode):
                            raise CompressionError(
                                f"Blocked unsafe symbolic link: {member.filename}"
                            )
                    zf.extractall(output)  # nosec B202 - members were preflight-validated
                return True
            if archive.suffix in [".tar", ".gz"] or archive.name.endswith(".tar.gz"):
                mode = (
                    "r:gz"
                    if archive.name.endswith(".tar.gz") or archive.suffix == ".gz"
                    else "r"
                )
                with tarfile.open(archive, mode) as tf:
                    # CWE-22: Prevent path traversal during tarfile extraction.
                    # Validate paths and reject links before any extraction.
                    for member in tf.getmembers():
                        ArchiveManager._validate_member_path(output, member.name)
                        if member.issym() or member.islnk():
                            raise CompressionError(
                                f"Blocked unsafe archive link: {member.name}"
                            )

                    # Use data_filter (Python 3.12+) as defense in depth;
                    # retain the explicit validation for Python 3.11.
                    if hasattr(tarfile, "data_filter"):
                        tf.extractall(output, filter="data")  # nosec B202 - preflight validation plus data filter
                    else:
                        tf.extractall(output)  # nosec B202 - explicit Python 3.11 preflight validation
                return True
            raise ValueError(f"Unknown archive format: {archive.suffix}")
        except Exception as e:
            logger.error("Archive extraction error: %s", e)
            raise CompressionError(f"Failed to extract archive: {e!s}") from e
