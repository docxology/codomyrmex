"""Vocabulary management for BPE tokenizer.

Provides a standalone Vocabulary class for managing token-to-ID mappings
with built-in special token handling.
"""


class Vocabulary:
    """Token vocabulary with special token handling.

    Maintains bidirectional mappings between token strings and integer IDs.
    Special tokens (<PAD>, <UNK>, <BOS>, <EOS>, <MASK>) are pre-allocated
    at initialization with fixed IDs 0-4.

    Attributes:
        SPECIAL: Class-level dict of special token names to their fixed IDs.
    """

    SPECIAL = {"<PAD>": 0, "<UNK>": 1, "<BOS>": 2, "<EOS>": 3, "<MASK>": 4}

    def __init__(self) -> None:
        self._token_to_id: dict[str, int] = dict(self.SPECIAL)
        self._id_to_token: dict[int, str] = {v: k for k, v in self.SPECIAL.items()}

    def add(self, token: str) -> int:
        """Add a token to the vocabulary and return its ID.

        If the token already exists, returns the existing ID without
        creating a duplicate.

        Args:
            token: The token string to add.

        Returns:
            The integer ID assigned to the token.
        """
        if token not in self._token_to_id:
            idx = len(self._token_to_id)
            self._token_to_id[token] = idx
            self._id_to_token[idx] = token
        return self._token_to_id[token]

    def __len__(self) -> int:
        """Return the total number of tokens in the vocabulary."""
        return len(self._token_to_id)

    def token_to_id(self, token: str) -> int:
        """Look up the integer ID for a token.

        Args:
            token: The token string to look up.

        Returns:
            The integer ID, or the <UNK> ID if the token is not found.
        """
        return self._token_to_id.get(token, self.SPECIAL["<UNK>"])

    def id_to_token_str(self, idx: int) -> str:
        """Look up the token string for an integer ID.

        Args:
            idx: The integer ID to look up.

        Returns:
            The token string, or '<UNK>' if the ID is not found.
        """
        return self._id_to_token.get(idx, "<UNK>")
