"""Real-clock capacity, expiry, and concurrent acquisition controls."""

import asyncio

import pytest

from codomyrmex.concurrency.workers.rate_limiter import AsyncSlidingWindow


@pytest.mark.asyncio
async def test_expired_requests_release_capacity_for_concurrent_callers():
    window = AsyncSlidingWindow(max_requests=2, window_seconds=0.2)
    assert await window.acquire(timeout=1.0)
    assert await window.acquire(timeout=1.0)
    assert not await window.acquire(timeout=0.05)
    await asyncio.sleep(0.25)
    results = await asyncio.gather(*(window.acquire(timeout=0.05) for _ in range(3)))
    assert results.count(True) == 2
    assert results.count(False) == 1
