"""
Request Batcher

Batches inference requests for efficient processing.
"""

import queue
import threading
import time
from collections.abc import Callable
from concurrent.futures import Future
from typing import Any, Generic, TypeVar

T = TypeVar('T')


class RequestBatcher(Generic[T]):
    """
    Batches inference requests for efficiency.

    Usage:
        batcher = RequestBatcher(
            max_batch_size=16,
            timeout_ms=50,
            processor=batch_inference_fn,
        )

        # Sync usage
        result = batcher.submit_sync(input_data)

        # Async usage
        future = batcher.submit_async(input_data)
        result = future.result()
    """

    def __init__(
        self,
        max_batch_size: int = 32,
        timeout_ms: float = 100.0,
        processor: Callable[[list[T]], list[Any]] | None = None,
    ):
        """Execute   Init   operations natively."""
        self.max_batch_size = max_batch_size
        self.timeout_ms = timeout_ms
        self.processor = processor

        self._queue: queue.Queue = queue.Queue()
        self._pending: dict[str, Future] = {}
        self._counter = 0
        self._lock = threading.Lock()
        self._running = False
        self._thread: threading.Thread | None = None

        # Stats
        self._total_requests = 0
        self._total_batches = 0
        self._batch_sizes: list[int] = []

    def start(self) -> None:
        """Start the batching thread."""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._process_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the batching thread."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)

    def _get_request_id(self) -> str:
        """Generate unique request ID."""
        with self._lock:
            self._counter += 1
            return f"req_{self._counter}"

    def submit_sync(self, input_data: T, timeout: float = 30.0) -> Any:
        """Submit request and wait for result."""
        request_id = self._get_request_id()
        future: Future = Future()

        self._queue.put((request_id, input_data, future))
        self._total_requests += 1

        return future.result(timeout=timeout)

    def submit_async(self, input_data: T) -> Future:
        """Submit request and return future."""
        request_id = self._get_request_id()
        future: Future = Future()

        self._queue.put((request_id, input_data, future))
        self._total_requests += 1

        return future

    def _process_loop(self) -> None:
        """Main processing loop."""
        while self._running:
            batch = self._collect_batch()
            if batch:
                self._process_batch(batch)

    def _collect_batch(self) -> list[tuple]:
        """Collect a batch of requests."""
        batch = []
        deadline = time.time() + (self.timeout_ms / 1000)

        while len(batch) < self.max_batch_size:
            remaining = deadline - time.time()
            if remaining <= 0:
                break

            try:
                item = self._queue.get(timeout=remaining)
                batch.append(item)
            except queue.Empty:
                break

        return batch

    def _process_batch(self, batch: list[tuple]) -> None:
        """Process a collected batch."""
        if not batch or not self.processor:
            return

        request_ids = [item[0] for item in batch]
        inputs = [item[1] for item in batch]
        futures = [item[2] for item in batch]

        try:
            outputs = self.processor(inputs)

            for i, output in enumerate(outputs):
                futures[i].set_result(output)

            self._total_batches += 1
            self._batch_sizes.append(len(batch))

        except Exception as e:
            for future in futures:
                future.set_exception(e)

    @property
    def stats(self) -> dict[str, Any]:
        """Get batching statistics."""
        avg_batch = (
            sum(self._batch_sizes) / len(self._batch_sizes)
            if self._batch_sizes else 0
        )
        return {
            "total_requests": self._total_requests,
            "total_batches": self._total_batches,
            "avg_batch_size": avg_batch,
        }
