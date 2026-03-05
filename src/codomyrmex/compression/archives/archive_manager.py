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

    def create_archive(
        self, files: list[Path], output: Path, format: str = "zip"
    ) -> bool:
        """Create an archive containing multiple files.

        Args:
            files: List of file paths to include
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
            logger.error(f"Archive creation error: {e}")
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
                    zf.extractall(output)
                return True
            if archive.suffix in [".tar", ".gz"] or archive.name.endswith(".tar.gz"):
                mode = (
                    "r:gz"
                    if archive.name.endswith(".tar.gz") or archive.suffix == ".gz"
                    else "r"
                )
                with tarfile.open(archive, mode) as tf:
                    # CWE-22: Prevent path traversal during tarfile extraction.
                    # Use data_filter (Python 3.12+) when available for safe extraction.
                    if hasattr(tarfile, "data_filter"):
                        tf.extractall(output, filter="data")
                    else:
                        # Fallback: validate each member path manually
                        for member in tf.getmembers():
                            member_path = Path(output / member.name).resolve()
                            if not str(member_path).startswith(str(output.resolve())):
                                raise CompressionError(
                                    f"Blocked path traversal attempt: {member.name}"
                                )
                        tf.extractall(output)
                return True
            raise ValueError(f"Unknown archive format: {archive.suffix}")
        except Exception as e:
            logger.error(f"Archive extraction error: {e}")
            raise CompressionError(f"Failed to extract archive: {e!s}") from e
