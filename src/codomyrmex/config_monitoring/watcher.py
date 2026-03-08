"""Hot-reloading configuration watcher."""

import threading
from collections.abc import Callable
from pathlib import Path

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class ConfigWatcher:
    """Watches a configuration file for changes and triggers a callback."""

    def __init__(
        self, file_path: str | Path, callback: Callable[[], None], interval: float = 5.0
    ):
        """Initialize the watcher.

        Args:
            file_path: Path to the file to watch
            callback: Function to call when change is detected
            interval: Polling interval in seconds

        """
        self.file_path = Path(file_path).absolute()
        self.callback = callback
        self.interval = interval
        self._last_mtime = self._get_mtime()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()

    def _get_mtime(self) -> float:
        """Get modification time of the file."""
        try:
            if self.file_path.is_file():
                return self.file_path.stat().st_mtime
        except (OSError, AttributeError):
            pass
        return 0.0

    def start(self) -> None:
        """Start the watcher thread."""
        with self._lock:
            if self._thread and self._thread.is_alive():
                logger.debug("Watcher already running for %s", self.file_path)
                return
            self._stop_event.clear()
            self._thread = threading.Thread(
                target=self._run,
                name=f"ConfigWatcher-{self.file_path.name}",
                daemon=True,
            )
            self._thread.start()
            logger.info("Started watching %s (interval=%ss)", self.file_path, self.interval)

    def stop(self) -> None:
        """Stop the watcher thread."""
        self._stop_event.set()
        with self._lock:
            if self._thread:
                self._thread.join(timeout=min(self.interval * 2, 5.0))
                self._thread = None
                logger.info("Stopped watching %s", self.file_path)

    def _run(self) -> None:
        """Run the polling loop to check for file changes."""
        while not self._stop_event.is_set():
            try:
                current_mtime = self._get_mtime()
                if current_mtime > self._last_mtime:
                    logger.info("Config file changed: %s", self.file_path)
                    self._last_mtime = current_mtime
                    try:
                        self.callback()
                    except Exception as e:
                        logger.error("Error in ConfigWatcher callback for %s: %s", self.file_path, e)
                elif current_mtime < self._last_mtime and current_mtime == 0:
                    # File disappeared
                    logger.warning("Watched file disappeared: %s", self.file_path)
                    self._last_mtime = 0
            except Exception as e:
                logger.error("Unexpected error in ConfigWatcher loop for %s: %s", self.file_path, e)

            # Wait for interval, but wake up quickly if stop_event is set
            self._stop_event.wait(self.interval)

    @property
    def is_alive(self) -> bool:
        """Check if the watcher thread is alive."""
        with self._lock:
            return self._thread is not None and self._thread.is_alive()
