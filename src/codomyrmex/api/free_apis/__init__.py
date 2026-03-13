"""free_apis — Structured index and client for free public APIs.

Pulls the API catalogue from the public-apis project
(https://github.com/public-apis/public-apis) and lets you:

* Browse categories and search entries (:class:`FreeAPIRegistry`)
* Call any listed API over HTTP (:class:`FreeAPIClient`)
* Integrate with the PAI MCP bridge (``mcp_tools`` submodule)

Quick start::

    from codomyrmex.api.free_apis import FreeAPIRegistry, FreeAPIClient

    registry = FreeAPIRegistry()
    registry.fetch()  # loads ~1400 entries
    animals = registry.filter_by_category("Animals")
    print(animals[0].to_dict())

    client = FreeAPIClient()
    result = client.get("https://dog.ceo/api/breeds/list/all")
    print(result.status_code, result.body_text[:120])
"""

from .client import FreeAPIClient
from .models import APICallError, APICallResult, APICategory, APIEntry, APISource
from .registry import FreeAPIRegistry

__all__ = [
    "APICallError",
    "APICallResult",
    "APICategory",
    "APIEntry",
    "APISource",
    "FreeAPIClient",
    "FreeAPIRegistry",
]
