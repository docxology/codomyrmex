#!/usr/bin/env bash
# setup_submodules.sh — Initialize all git submodules and install Python deps where applicable.
# Safe to run multiple times (idempotent).
set -euo pipefail

REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
cd "$REPO_ROOT"

echo "==> Initializing all git submodules..."
git submodule update --init --recursive

echo "==> Setting up hermes-agent-self-evolution with uv..."
HERMES_EVOL="src/codomyrmex/agents/hermes/evolution"
if [ -d "$HERMES_EVOL" ]; then
    cd "$HERMES_EVOL"
    # Remove any existing .venv so uv creates a clean managed one
    if [ -d ".venv" ]; then
        echo "    Removing existing .venv in hermes/evolution..."
        rm -rf .venv
    fi
    # uv sync resolves ALL extras during locking, which fails for the non-PyPI
    # `darwinian-evolver` package in the `darwinian` optional extra.
    # Use `uv venv --seed` (adds pip) + direct pip install to skip lock resolution.
    uv venv --seed
    .venv/bin/pip install -e ".[dev]"
    echo "    hermes/evolution ready."
    cd "$REPO_ROOT"
else
    echo "    WARNING: $HERMES_EVOL not found — submodule may not have been cloned."
fi

echo ""
echo "==> Submodule setup complete."
echo "    gitnexus (Node.js): run 'npm install' in src/codomyrmex/git_analysis/vendor/gitnexus/ if needed."
echo "    vibeship-spawner-skills, dark-pdf, openfang: no Python deps."
