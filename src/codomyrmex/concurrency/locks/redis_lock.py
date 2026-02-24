"""Distributed lock backed by Redis."""

import logging
import time
import uuid

import redis

from .distributed_lock import BaseLock

logger = logging.getLogger(__name__)

class RedisLock(BaseLock):
    """Distributed lock using Redis SETNX and TTL."""

    def __init__(self, name: str, redis_client: redis.Redis, ttl: int = 30):
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
        """Execute Acquire operations natively."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            # Atomic set if not exists with PX (milliseconds TTL)
            if self.redis.set(self.key, self.owner_id, nx=True, ex=self.ttl):
                self.is_held = True
                return True
            time.sleep(retry_interval)
        return False

    def release(self) -> None:
        """Execute Release operations natively."""
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
        self.redis.eval(script, 1, self.key, self.owner_id)
        self.is_held = False

    def extend(self, additional_ttl: int) -> bool:
        """Extend the lock TTL if held."""
        if not self.is_held:
            return False

        script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("expire", KEYS[1], ARGV[2])
        else
            return 0
        end
        """
        result = self.redis.eval(script, 1, self.key, self.owner_id, additional_ttl)
        return bool(result)
