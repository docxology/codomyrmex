"""Integration tests for Hermes gateway deep context compression (D2)."""

from typing import Any

from codomyrmex.agents.hermes._provider_router import ContextCompressor


def test_context_compressor_deduplicates_and_truncates() -> None:
    """Ensure ContextCompressor adheres to dynamic payload summarization."""
    # Create an artificially constrained compressor for testing (limit 100 tokens, ~400 chars)
    compressor = ContextCompressor(max_tokens=100, compression_ratio=0.5)

    messages: list[dict[str, Any]] = [
        {"role": "user", "content": "What's up?"},
        {"role": "user", "content": "What's up?"},  # Exact duplicate
        {"role": "assistant", "content": "I see..."},
    ]

    # Add a massive block exceeding 400 chars easily
    huge_block = "A" * 600
    messages.append({"role": "user", "content": huge_block})
    messages.append({"role": "user", "content": "And finally, bye!"})

    # Verify it needs compression
    assert compressor.needs_compression(messages)

    # Run compression
    compressed = compressor.compress(messages)

    # Assertions
    # 1. Deduplication (the second "What's up?" is gone)
    assert len([m for m in compressed if m["content"] == "What's up?"]) == 1

    # 2. Truncation (the massive block should possess the truncated marker)
    huge_compressed = next((m for m in compressed if "A" * 50 in m["content"]), None)
    assert huge_compressed is not None
    assert "[...truncated]" in huge_compressed["content"]
    assert len(huge_compressed["content"]) < 600

    # 3. Overall token size should be safely under limit or significantly reduced
    est_tokens = compressor.estimate_tokens(compressed)
    assert est_tokens < compressor.estimate_tokens(messages)
