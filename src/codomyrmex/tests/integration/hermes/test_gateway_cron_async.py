"""Integration tests for the Hermes gateway async cron ticker."""

import asyncio
import time

import pytest

from codomyrmex.agents.hermes.gateway.cron import CronTicker


async def test_cron_ticker_async_fire_and_forget() -> None:
    """Ensure the CronTicker does not block the main loop when executing jobs."""
    ticker = CronTicker(interval=0.1)

    slow_job_started = asyncio.Event()
    slow_job_completed = asyncio.Event()

    async def slow_job() -> None:
        slow_job_started.set()
        await asyncio.sleep(0.5)
        slow_job_completed.set()

    ticker.register_job(slow_job)
    ticker.start()

    # Wait for the first tick to fire the job
    await asyncio.wait_for(slow_job_started.wait(), timeout=1.0)

    # The ticker should have immediately returned to its wait loop (not blocked by the 0.5s sleep)
    tick_start = time.time()
    await asyncio.sleep(0.1) # Simulate main loop doing other things
    tick_elapsed = time.time() - tick_start

    # If the ticker had blocked us, tick_elapsed would be > 0.5s.
    assert tick_elapsed < 0.2

    # The job is still running in the background... wait for it to finish gracefully
    await asyncio.wait_for(slow_job_completed.wait(), timeout=1.0)

    ticker.stop()
