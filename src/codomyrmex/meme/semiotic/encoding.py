"""Semiotic encoding — meaning-level steganography."""

from __future__ import annotations

from typing import Dict, List


class SemioticEncoder:
    """Encode and decode meaning within meaning.

    Uses synonym substitution patterns to embed hidden
    semiotic payloads within carrier text. This implements
    a form of linguistic steganography.
    """

    _SYNONYM_MAP: Dict[str, List[str]] = {
        "good": ["fine", "great", "excellent", "superb"],
        "bad": ["poor", "terrible", "awful", "dreadful"],
        "big": ["large", "huge", "enormous", "vast"],
        "small": ["tiny", "little", "minute", "compact"],
        "fast": ["quick", "rapid", "swift", "speedy"],
        "slow": ["gradual", "sluggish", "unhurried", "leisurely"],
        "happy": ["glad", "joyful", "cheerful", "content"],
        "sad": ["unhappy", "sorrowful", "glum", "downcast"],
    }

    def encode(self, carrier: str, payload: str) -> str:
        """Encode a payload message into carrier text via synonym selection.

        The payload string is hashed/converted to bits to drive selection.
        This Proof-of-Concept uses simple mod-based selection index.

        Args:
            carrier: The cover text to hide the payload in.
            payload: The secret message to embed.

        Returns:
            Modified carrier text containing the payload.
        """
        payload_bits = self._to_bits(payload)
        words = carrier.split()
        bit_idx = 0
        result: List[str] = []

        for word in words:
            clean = word.lower().strip(".,!?")
            # If word is a recognized key for synonyms
            if clean in self._SYNONYM_MAP and bit_idx < len(payload_bits):
                synonyms = self._SYNONYM_MAP[clean]
                # Use payload bit to select specific synonym
                idx = payload_bits[bit_idx] % len(synonyms)
                # Ideally, preserve original capitalization/punctuation
                # (omitted here for clarity)
                result.append(synonyms[idx])
                bit_idx += 1
            else:
                result.append(word)

        return " ".join(result)

    def decode(self, encoded: str) -> List[int]:
        """Extract embedded bit pattern from encoded text.

        Args:
            encoded: Text containing hidden payload.

        Returns:
            List of integers representing payload bits.
        """
        words = encoded.split()
        bits: List[int] = []

        for word in words:
            clean = word.lower().strip(".,!?")
            for base, synonyms in self._SYNONYM_MAP.items():
                if clean in synonyms:
                    bits.append(synonyms.index(clean))
                    break
        return bits

    def _to_bits(self, text: str) -> List[int]:
        """Convert text to a list of small integers for encoding."""
        # Simple transform for demo purposes
        return [b % 4 for b in text.encode("utf-8")]
