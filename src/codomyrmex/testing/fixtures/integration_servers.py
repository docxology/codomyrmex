import threading
from collections.abc import Callable

import uvicorn
from fastapi import FastAPI


class TestServerManager:
    """
    Zero-Mock Integration Testing Server Manager.
    
    Spins up a real FastAPI server on a background thread on localhost to handle
    HTTP requests during test execution. This allows testing network clients
    without relying on external physical infrastructure or using 'unittest.mock'.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 8000):
        self.host = host
        self.port = port
        self.app = FastAPI(title="Codomyrmex Integration Test Server")
        self.server: uvicorn.Server | None = None
        self._thread: threading.Thread | None = None
        self._startup_event = threading.Event()

        # Default health check
        @self.app.get("/health")
        def health_check():
            return {"status": "ok"}

    def add_route(self, path: str, endpoint: Callable, methods: list[str] = ["GET"]):
        """Add a route to the FastAPI application."""
        self.app.add_api_route(path, endpoint, methods=methods)

    def _run_server(self):
        """Run the uvicorn server in the current thread."""
        config = uvicorn.Config(
            app=self.app,
            host=self.host,
            port=self.port,
            log_level="error",
        )
        self.server = uvicorn.Server(config)

        # Override the server's startup to signal our event
        original_startup = self.server.startup

        async def hooked_startup(*args, **kwargs):
            await original_startup(*args, **kwargs)
            self._startup_event.set()

        self.server.startup = hooked_startup
        self.server.run()

    def start(self):
        """Start the server in a background thread."""
        if self._thread is not None and self._thread.is_alive():
            return

        self._startup_event.clear()
        self._thread = threading.Thread(target=self._run_server, daemon=True)
        self._thread.start()

        # Wait for the server to actually start accepting requests
        started = self._startup_event.wait(timeout=5.0)
        if not started:
            raise RuntimeError("Failed to start integration test server within timeout.")

    def stop(self):
        """Stop the background server."""
        if self.server:
            self.server.should_exit = True

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
