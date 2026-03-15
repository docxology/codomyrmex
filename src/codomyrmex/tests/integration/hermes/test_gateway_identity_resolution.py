"""Integration tests for Cross-Platform Identity Resolution (D1)."""

from pathlib import Path


from codomyrmex.agents.hermes.gateway.identity import IdentityResolver


async def test_identity_resolution_handshake(tmp_path: Path) -> None:
    """Ensure arbitrary cross-platform IDs route safely into unified UUIDs."""
    db_file = tmp_path / "identities.json"
    resolver = IdentityResolver(db_file)
    await resolver.initialize()

    # 1. Telegram generic load
    global_id_1 = await resolver.resolve("telegram", "tele_999", "Alpha User")
    assert global_id_1.startswith("usr_")

    # 2. Assert stability caching
    global_id_2 = await resolver.resolve("telegram", "tele_999", "Alpha User")
    assert global_id_1 == global_id_2

    # 3. Explicit cross-linking (Imagine a user authenticates Discord inside the telegram bot)
    success = await resolver.link_identity(global_id_1, "discord", "disc_888")
    assert success is True

    # 4. Now if they talk to the Discord bot natively, it should yield the exact same DB namespace
    global_id_3 = await resolver.resolve("discord", "disc_888", "Discord Alpha")
    assert global_id_3 == global_id_1

    # 5. Clean fresh user entirely
    global_id_independent = await resolver.resolve("whatsapp", "wa_777", "Beta User")
    assert global_id_independent != global_id_1
    assert global_id_independent.startswith("usr_")

    # Verify disk structure
    verify = IdentityResolver(db_file)
    await verify.initialize()

    assert global_id_1 in verify._profiles
    assert verify._profiles[global_id_1]["platforms"]["discord"] == "disc_888"
