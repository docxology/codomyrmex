# agents.hermes.provider_router_pkg

LiteLLM provider routing, compression, and model context registry.

Import via `codomyrmex.agents.hermes.provider_router_pkg`.

`ProviderRouter` accepts explicit `env_path` and keyword-only `rotation_path`
before credential loading and rotation-template creation. Defaults follow
`HERMES_HOME` when set and otherwise use `~/.hermes`. Explicit paths take
precedence, so tests can keep credentials and generated rotation files in
temporary directories. Model dispatch remains a separate provider operation.
