"""Perplexity client submodule.

Exports the PerplexityClient and PerplexityError for integration into
the agent framework. Allows using the Perplexity online LLM for search-augmented
queries.
"""

from .perplexity_client import PerplexityClient, PerplexityError

__all__ = ["PerplexityClient", "PerplexityError"]
