"""Tests for crypto.steganography.text module."""

from __future__ import annotations

import pytest

from codomyrmex.crypto.exceptions import SteganographyError
from codomyrmex.crypto.steganography.text import (
    ZERO_WIDTH_NON_JOINER,
    ZERO_WIDTH_SPACE,
    embed_in_text,
    extract_from_text,
)


@pytest.mark.unit
@pytest.mark.crypto
class TestEmbedExtractRoundtrip:
    """Tests for embed_in_text and extract_from_text roundtrip."""

    def test_simple_message(self):
        """Verify simple message behavior."""
        cover = "This is a normal sentence."
        secret = "hidden"

        stego = embed_in_text(cover, secret)
        extracted = extract_from_text(stego)
        assert extracted == secret

    def test_empty_secret_message(self):
        """Verify empty secret message behavior."""
        cover = "Hello world"
        secret = ""

        stego = embed_in_text(cover, secret)
        extracted = extract_from_text(stego)
        assert extracted == secret

    def test_longer_secret_message(self):
        """Verify longer secret message behavior."""
        cover = "The weather today is quite pleasant."
        secret = "Meet at the bridge at midnight. Bring the documents."

        stego = embed_in_text(cover, secret)
        extracted = extract_from_text(stego)
        assert extracted == secret

    def test_unicode_secret_message(self):
        """Verify unicode secret message behavior."""
        cover = "Just a regular email."
        secret = "Hello World"

        stego = embed_in_text(cover, secret)
        extracted = extract_from_text(stego)
        assert extracted == secret

    def test_multiline_cover_text(self):
        """Verify multiline cover text behavior."""
        cover = "Line one.\nLine two.\nLine three."
        secret = "secret data"

        stego = embed_in_text(cover, secret)
        extracted = extract_from_text(stego)
        assert extracted == secret


@pytest.mark.unit
@pytest.mark.crypto
class TestCoverTextPreservation:
    """Tests that cover text appears unchanged to human readers."""

    def test_visible_chars_unchanged(self):
        """Verify visible chars unchanged behavior."""
        cover = "This is a test sentence with words."
        secret = "hidden message"

        stego = embed_in_text(cover, secret)

        # Remove zero-width characters to get visible text
        visible_chars = []
        zero_width = {
            ZERO_WIDTH_SPACE, ZERO_WIDTH_NON_JOINER,
            "\u200d", "\u2060",
        }
        for ch in stego:
            if ch not in zero_width:
                visible_chars.append(ch)

        visible_text = "".join(visible_chars)
        assert visible_text == cover

    def test_stego_text_longer_than_cover(self):
        """Verify stego text longer than cover behavior."""
        cover = "Hello world"
        secret = "test"

        stego = embed_in_text(cover, secret)
        # Stego text should be longer due to zero-width chars
        assert len(stego) > len(cover)

    def test_printable_chars_same(self):
        """Verify printable chars same behavior."""
        cover = "Important business communication."
        secret = "buy low sell high"

        stego = embed_in_text(cover, secret)

        # Filter to only printable, non-zero-width chars
        import string

        printable = set(string.printable)
        cover_printable = [c for c in cover if c in printable]
        stego_printable = [c for c in stego if c in printable]
        assert cover_printable == stego_printable


@pytest.mark.unit
@pytest.mark.crypto
class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_cover_text_raises(self):
        """Verify empty cover text raises behavior."""
        with pytest.raises(SteganographyError):
            embed_in_text("", "secret")

    def test_no_hidden_message_raises(self):
        """Verify no hidden message raises behavior."""
        with pytest.raises(SteganographyError):
            extract_from_text("Normal text with no hidden message")

    def test_single_word_cover_text(self):
        """Verify single word cover text behavior."""
        cover = "Hello"
        secret = "test"

        stego = embed_in_text(cover, secret)
        extracted = extract_from_text(stego)
        assert extracted == secret

    def test_special_characters_in_secret(self):
        """Verify special characters in secret behavior."""
        cover = "Regular cover text here."
        secret = "Special: !@#$%^&*()\n\ttabs and newlines"

        stego = embed_in_text(cover, secret)
        extracted = extract_from_text(stego)
        assert extracted == secret
