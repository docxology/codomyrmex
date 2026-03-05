"""MCP tool definitions for the BPE tokenizer module.

Exposes tokenizer_train, tokenizer_encode, and tokenizer_decode as
auto-discoverable MCP tools via the @mcp_tool decorator.
"""

from codomyrmex.model_context_protocol.decorators import mcp_tool

from .bpe import BPETokenizer

_tokenizer: BPETokenizer | None = None


def _get_or_create_tokenizer() -> BPETokenizer:
    """Return the module-level tokenizer instance, creating one if needed."""
    global _tokenizer
    if _tokenizer is None:
        _tokenizer = BPETokenizer(vocab_size=500)
    return _tokenizer


@mcp_tool(category="tokenizer")
def tokenizer_train(texts: list[str], vocab_size: int = 500) -> dict:
    """Train a BPE tokenizer on a list of texts.

    Args:
        texts: List of training strings.
        vocab_size: Target vocabulary size (default 500).

    Returns:
        dict with: status, vocab_size (int), num_merges (int),
        sample_vocab (list of first 20 tokens).
    """
    global _tokenizer
    _tokenizer = BPETokenizer(vocab_size=vocab_size)
    _tokenizer.train(texts, vocab_size=vocab_size)
    return {
        "status": "success",
        "vocab_size": _tokenizer.vocab_size_actual,
        "num_merges": len(_tokenizer.merges),
        "sample_vocab": list(_tokenizer.vocab.keys())[:20],
    }


@mcp_tool(category="tokenizer")
def tokenizer_encode(text: str) -> dict:
    """Encode text to BPE token IDs (must call tokenizer_train first).

    Args:
        text: Input string to tokenize.

    Returns:
        dict with: status, token_ids (list[int]), num_tokens (int).
    """
    tok = _get_or_create_tokenizer()
    if not tok._trained:
        return {"status": "error", "message": "Call tokenizer_train first"}
    ids = tok.encode(text)
    return {"status": "success", "token_ids": ids, "num_tokens": len(ids)}


@mcp_tool(category="tokenizer")
def tokenizer_decode(token_ids: list[int]) -> dict:
    """Decode BPE token IDs back to text.

    Args:
        token_ids: List of integer token IDs.

    Returns:
        dict with: status, text (str).
    """
    tok = _get_or_create_tokenizer()
    if not tok._trained:
        return {"status": "error", "message": "Call tokenizer_train first"}
    text = tok.decode(token_ids)
    return {"status": "success", "text": text}
