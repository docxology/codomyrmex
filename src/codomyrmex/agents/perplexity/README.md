# Perplexity API Submodule

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The `perplexity` submodule provides an `APIAgentBase` client to interface with the [Perplexity API](https://docs.perplexity.ai/), giving Codomyrmex the ability to perform search-augmented LLM completions.

## Usage

```python
from codomyrmex.agents.core import AgentRequest
from codomyrmex.agents.perplexity import PerplexityClient

client = PerplexityClient()
request = AgentRequest(prompt="What is the latest version of Python?")
response = client.execute(request)

if response.is_success():
    print(response.content)
    # response.metadata typically contains citation URLs
else:
    print(response.error)
```

## Setup

Set `PERPLEXITY_API_KEY` in your environment or use the `agent_setup` wizard.
