"""Integration tests for the concurrent JSON directory sync mechanism."""

import asyncio
from pathlib import Path

from codomyrmex.agents.hermes.gateway.directory import ChannelDirectorySync


async def test_channel_directory_sync_concurrent(tmp_path: Path) -> None:
    """Ensure the async lock prevents concurrent JSON write corruption."""
    db_file = tmp_path / "channel_directory.json"
    sync = ChannelDirectorySync(db_file)
    await sync.initialize()

    async def worker(platform: str, count: int) -> None:
        for i in range(count):
            await sync.register_channel(
                platform, f"uid_{i}", {"name": f"User {i}", "chat_id": str(i * 100)}
            )
            # Yield to force switching
            await asyncio.sleep(0.001)

    # Launch 3 platform workers trying to write 50 updates each back to the same JSON file
    tasks = [
        worker("telegram", 50),
        worker("whatsapp", 50),
        worker("discord", 50),
    ]

    await asyncio.gather(*tasks)

    # Reload purely from disk using a fresh instance
    verify_sync = ChannelDirectorySync(db_file)
    await verify_sync.initialize()

    tree = await verify_sync.get_directory()

    assert "telegram" in tree
    assert "whatsapp" in tree
    assert "discord" in tree

    assert len(tree["telegram"]) == 50
    assert len(tree["discord"]) == 50

    # Spot check final element metadata
    assert tree["telegram"]["uid_49"]["name"] == "User 49"
