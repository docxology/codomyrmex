"""Distributed lock backed by Redis."""

import time
import uuid

import redis
from redis import Redis

from codomyrmex.logging_monitoring.core.logger_config import get_logger

from .distributed_lock import BaseLock

logger = get_logger(__name__)


class RedisLock(BaseLock):
    """Distributed lock using Redis SETNX and TTL."""

    def __init__(self, name: str, redis_client: Redis, ttl: int = 30):
        """Initialize the Redis lock.

        Args:
            name: The name of the lock.
            redis_client: A redis.Redis instance.
            ttl: Time-to-live for the lock in seconds.
        """
        super().__init__(name)
        self.redis = redis_client
        self.ttl = ttl
        self.owner_id = str(uuid.uuid4())
        self.key = f"codomyrmex:lock:{name}"

    def acquire(self, timeout: float = 10.0, retry_interval: float = 0.1) -> bool:
        """Acquire the lock with a given timeout.

        Args:
            timeout: Maximum time to wait in seconds.
            retry_interval: Seconds to wait between retries.

        Returns:
            True if acquired, False otherwise.
        """
        start_time = time.time()
        while True:
            # Atomic set if not exists with PX (milliseconds TTL)
            # EX is seconds, PX is milliseconds. Redis-py handles this.
            if self.redis.set(self.key, self.owner_id, nx=True, ex=self.ttl):
                self.is_held = True
                return True

            if time.time() - start_time >= timeout:
                return False

            time.sleep(retry_interval)

    def release(self) -> None:
        """Release the lock safely."""
        if not self.is_held:
            return

        # Use Lua script for atomic check-and-delete to ensure we only release our own lock
        script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        try:
            # Fallback for fakeredis which might not support eval depending on version/config
            try:
                self.redis.eval(script, 1, self.key, self.owner_id)
            except redis.ResponseError:
                # Minimal fallback: check then delete (non-atomic)
                if (
                    self.redis.get(self.key) == self.owner_id.encode()
                    or self.redis.get(self.key) == self.owner_id
                ):
                    self.redis.delete(self.key)
        except redis.RedisError as e:
            logger.error(f"Error releasing Redis lock '{self.name}': {e}")
        finally:
            self.is_held = False

    def extend(self, additional_ttl: int) -> bool:
        """Extend the lock TTL if still held by this instance.

        Args:
            additional_ttl: New TTL in seconds.

        Returns:
            True if extension succeeded, False otherwise.
        """
        if not self.is_held:
            return False

        script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("expire", KEYS[1], ARGV[2])
        else
            return 0
        end
        """
        try:
            try:
                result = self.redis.eval(
                    script, 1, self.key, self.owner_id, additional_ttl
                )
                return bool(result)
            except redis.ResponseError:
                # Minimal fallback: check then expire (non-atomic)
                if (
                    self.redis.get(self.key) == self.owner_id.encode()
                    or self.redis.get(self.key) == self.owner_id
                ):
                    return bool(self.redis.expire(self.key, additional_ttl))
                return False
        except redis.RedisError as e:
            logger.error(f"Error extending Redis lock '{self.name}': {e}")
            return False

    def is_locked_externally(self) -> bool:
        """Check if the lock is held by anyone (self or other)."""
        return bool(self.redis.exists(self.key))
