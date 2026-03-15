"""Gateway daemon runner and lifecycle manager."""

import asyncio
import os
import signal
import sys
import time
from pathlib import Path

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class GatewayRunner:
    """Main runner for the Hermes gateway daemon."""

    def __init__(self, replace: bool = False, home_dir: str | None = None) -> None:
        self.replace = replace
        self.home_dir = (
            Path(home_dir) if home_dir else Path.home() / ".codomyrmex" / "hermes"
        )
        self.pid_file = self.home_dir / "gateway.pid"
        self._running = False
        self._stop_event = asyncio.Event()

    def _ensure_home(self) -> None:
        """Ensure the home directory exists."""
        self.home_dir.mkdir(parents=True, exist_ok=True)

    def _check_pid(self) -> None:
        """Check for existing instances via gateway.pid."""
        if not self.pid_file.exists():
            return

        try:
            pid = int(self.pid_file.read_text().strip())
        except ValueError:
            logger.warning("Invalid PID file found. Proceeding as if clear.")
            return

        is_alive = False
        try:
            os.kill(pid, 0)
            is_alive = True
        except ProcessLookupError:
            pass  # Process is dead
        except PermissionError:
            is_alive = True  # Process alive but we don't own it

        if is_alive:
            if not self.replace:
                logger.error(
                    f"Gateway already running at PID {pid}. Refusing to start."
                )
                sys.exit(0)
            else:
                logger.warning(
                    f"Killing existing gateway PID {pid} due to --replace flag."
                )
                try:
                    os.kill(pid, signal.SIGTERM)
                    # Graceful wait
                    for _ in range(50):
                        time.sleep(0.1)
                        try:
                            os.kill(pid, 0)
                        except ProcessLookupError:
                            break
                    else:
                        logger.warning(
                            f"PID {pid} did not exit gracefully. Sending SIGKILL."
                        )
                        os.kill(pid, signal.SIGKILL)
                except Exception as e:
                    logger.error(f"Failed to kill prior instance {pid}: {e}")
                    sys.exit(1)
        elif not self.replace:
            logger.error(
                f"Found stale gateway.pid for {pid}. Refusing to start without --replace."
            )
            sys.exit(0)
        else:
            logger.info(f"Clearing stale gateway.pid {pid}.")

        # Cleanup the old pid file
        try:
            self.pid_file.unlink()
        except FileNotFoundError:
            pass

    def _write_pid(self) -> None:
        """Write current PID to file."""
        self.pid_file.write_text(str(os.getpid()))

    async def _main_loop(self) -> None:
        """The main asynchronous loop."""
        logger.info("Gateway event loop started.")
        self._running = True

        # Initialize platform adapters here in future iterations

        from .cron import CronTicker

        self.cron = CronTicker()
        self.cron.start()

        await self._stop_event.wait()

    def stop(self) -> None:
        """Trigger graceful shutdown."""
        self._running = False
        self._stop_event.set()

    def run(self) -> None:
        """Start the gateway."""
        self._ensure_home()
        self._check_pid()
        self._write_pid()

        logger.info(f"Starting Hermes Gateway on PID {os.getpid()}")
        try:
            asyncio.run(self._main_loop())
        except KeyboardInterrupt:
            logger.info("Gateway shutting down (interrupted).")
        finally:
            self._running = False
            if hasattr(self, "cron"):
                self.cron.stop()
            try:
                if self.pid_file.exists() and self.pid_file.read_text().strip() == str(
                    os.getpid()
                ):
                    self.pid_file.unlink()
            except Exception:
                pass
            logger.info("Gateway shutdown complete.")
