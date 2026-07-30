# OpenGauss integration

OpenGauss is included at
[`src/codomyrmex/agents/open_gauss/`](https://github.com/math-inc/OpenGauss/tree/f87633900ae185b8037bf451a914fe7eeae1eb08)
as the `math-inc/OpenGauss` Git submodule. It provides the `gauss` command and
project-scoped Lean workflows. Codomyrmex does not maintain a separate
`open_gauss_client.py` wrapper; the checked-out submodule and its own
documentation are authoritative. Upstream links on this page target the
superproject's recorded submodule commit so they also work before initialization.

## Boundary

- `.gitmodules` defines the upstream repository.
- The superproject records the submodule commit used by a Codomyrmex checkout.
- The submodule's
  [`pyproject.toml`](https://github.com/math-inc/OpenGauss/blob/f87633900ae185b8037bf451a914fe7eeae1eb08/pyproject.toml)
  defines its version, dependencies, and console entry points.
- The upstream
  [README](https://github.com/math-inc/OpenGauss/blob/f87633900ae185b8037bf451a914fe7eeae1eb08/README.md) and
  [Start Here guide](https://github.com/math-inc/OpenGauss/blob/f87633900ae185b8037bf451a914fe7eeae1eb08/website/docs/getting-started/start-here.md)
  define installation and operational behavior.
- Changes inside the submodule belong to its own repository and must not be
  silently folded into a Codomyrmex documentation or formatting pass.

## Initialize

From the Codomyrmex repository root:

```bash
git submodule update --init --recursive src/codomyrmex/agents/open_gauss
git submodule status src/codomyrmex/agents/open_gauss
```

The update command changes checkout state. Inspect `git status` first and do not
run it over concurrent or uncommitted submodule work.

## Install and run

Follow the submodule's installer rather than invoking internal Python files:

```bash
cd src/codomyrmex/agents/open_gauss
./scripts/install.sh
gauss-open-guide
gauss
```

The installed `gauss` console script maps to `gauss_cli.main:main`. Additional
entry points are declared in the submodule's `pyproject.toml`; their presence
depends on the selected installation extras.

Inside `gauss`, select or initialize a Lean project before launching workflows:

```text
/chat
/project init
/prove
/swarm
```

Available workflows and backend requirements can change with the pinned
submodule revision. Verify them against the checked-out upstream README instead
of copying a fixed command count into Codomyrmex documentation.

## Validate

These read-only checks confirm integration shape without changing the submodule:

```bash
git submodule status src/codomyrmex/agents/open_gauss
uv run --locked python scripts/doc_inventory.py
```

Run OpenGauss's own test instructions from within the submodule when validating
its implementation. Codomyrmex package test totals are not evidence for the
submodule, and upstream test totals must not be hard-coded here.

## Navigation

- [Agent documentation index](../README.md)
- [Repository agent contract](../../../AGENTS.md)
- [Submodule source](https://github.com/math-inc/OpenGauss/tree/f87633900ae185b8037bf451a914fe7eeae1eb08)
- [Submodule README](https://github.com/math-inc/OpenGauss/blob/f87633900ae185b8037bf451a914fe7eeae1eb08/README.md)
- [Git submodules](../../../.gitmodules)
