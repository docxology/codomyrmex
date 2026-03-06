"""CacheWarmer: pre-populate caches via batch, parallel, or scheduled strategies."""

import concurrent.futures
import threading
import time
from datetime import datetime
from typing import Generic, TypeVar

from codomyrmex.logging_monitoring import get_logger

from .loaders import BatchValueLoader, ValueLoader
from .models import WarmingConfig, WarmingStats
from .providers import KeyProvider

logger = get_logger(__name__)

K = TypeVar("K")
V = TypeVar("V")


class CacheWarmer(Generic[K, V]):
    """
    Cache warmer for pre-populating caches.

    Usage:
        warmer = CacheWarmer(cache=my_cache, key_provider=keys, value_loader=loader)
        stats = warmer.warm()
    """

    def __init__(
        self,
        cache: dict[K, V],
        key_provider: KeyProvider[K],
        value_loader: ValueLoader[K, V],
        config: WarmingConfig | None = None,
    ):
        self.cache = cache
        self.key_provider = key_provider
        self.value_loader = value_loader
        self.config = config or WarmingConfig()
        self._stats = WarmingStats()
        self._warming = False
        self._lock = threading.Lock()
        self._scheduler_thread: threading.Thread | None = None
        self._stop_scheduler = threading.Event()

    @property
    def stats(self) -> WarmingStats:
        return self._stats

    @property
    def is_warming(self) -> bool:
        return self._warming

    def warm(self, keys: list[K] | None = None) -> WarmingStats:
        """Warm the cache synchronously."""
        with self._lock:
            if self._warming:
                return self._stats
            self._warming = True

        start = time.time()
        stats = WarmingStats()
        try:
            target = keys if keys is not None else self.key_provider.get_keys()
            stats = (
                self._warm_batch(target)
                if isinstance(self.value_loader, BatchValueLoader)
                else self._warm_parallel(target)
            )
            stats.total_time_ms = (time.time() - start) * 1000
            stats.last_warming = datetime.now()
        finally:
            with self._lock:
                self._warming = False
                self._stats = stats

        return stats

    def _warm_batch(self, keys: list[K]) -> WarmingStats:
        """Warm using batch loading."""
        stats = WarmingStats()
        loader = self.value_loader
        if not isinstance(loader, BatchValueLoader):
            return stats

        for i in range(0, len(keys), self.config.batch_size):
            batch = keys[i : i + self.config.batch_size]
            try:
                for key, value in loader.load_batch(batch).items():
                    self.cache[key] = value
                    stats.keys_warmed += 1
            except Exception as e:
                stats.keys_failed += len(batch)
                stats.errors.append(str(e))

        return stats

    def _load_key_with_retry(self, key: K) -> tuple:
        """Load one key with exponential-backoff retries."""
        for attempt in range(self.config.max_retries + 1):
            try:
                return (key, self.value_loader.load(key), None)
            except Exception as e:
                if attempt == self.config.max_retries or not self.config.retry_on_failure:
                    return (key, None, str(e))
                time.sleep(0.1 * (2**attempt))
        return (key, None, "Max retries exceeded")

    def _warm_parallel(self, keys: list[K]) -> WarmingStats:
        """Warm using parallel loading with ThreadPoolExecutor."""
        stats = WarmingStats()
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.max_workers) as ex:
            futures = {ex.submit(self._load_key_with_retry, key): key for key in keys}
            for future in concurrent.futures.as_completed(futures, timeout=self.config.warmup_timeout_s):
                key, value, error = future.result()
                if error:
                    stats.keys_failed += 1
                    stats.errors.append(f"{key}: {error}")
                else:
                    self.cache[key] = value
                    stats.keys_warmed += 1
        return stats

    def warm_async(self, keys: list[K] | None = None) -> concurrent.futures.Future:
        """Warm the cache asynchronously."""
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        return executor.submit(self.warm, keys)

    def warm_key(self, key: K) -> bool:
        """Warm a single key. Returns True on success."""
        try:
            self.cache[key] = self.value_loader.load(key)
            return True
        except Exception as e:
            logger.warning("Failed to warm cache key %r: %s", key, e)
            return False

    def start_scheduler(self) -> None:
        """Start background scheduled warming."""
        if self._scheduler_thread and self._scheduler_thread.is_alive():
            return
        self._stop_scheduler.clear()

        def _loop():
            while not self._stop_scheduler.wait(self.config.refresh_interval_s):
                self.warm()

        self._scheduler_thread = threading.Thread(target=_loop, daemon=True)
        self._scheduler_thread.start()

    def stop_scheduler(self) -> None:
        """Stop background scheduled warming."""
        self._stop_scheduler.set()
        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=5.0)
