"""Hot-reloading configuration watcher."""

import os
import threading
import time
from collections.abc import Callable

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)

class ConfigWatcher:
    """Watches a configuration file for changes and triggers a callback."""

    def __init__(self, file_path: str, callback: Callable[[], None], interval: int = 5):
        self.file_path = file_path
        self.callback = callback
        self.interval = interval
        self._last_mtime = os.path.getmtime(file_path) if os.path.exists(file_path) else 0
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self):
        """Start the watcher thread."""
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the watcher thread."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)

    def _run(self):
        """Run the operation."""
        while not self._stop_event.is_set():
            try:
                if os.path.exists(self.file_path):
                    current_mtime = os.path.getmtime(self.file_path)
                    if current_mtime > self._last_mtime:
                        logger.info(f"Config file changed: {self.file_path}")
                        self._last_mtime = current_mtime
                        self.callback()
            except Exception as e:
                logger.error(f"Error watching config file: {e}")

            time.sleep(self.interval)
