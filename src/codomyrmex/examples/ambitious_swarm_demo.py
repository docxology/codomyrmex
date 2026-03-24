#!/usr/bin/env python3
"""Ambitious Swarm Demonstration.

This script demonstrates spinning up a mega-swarm of heterogeneous AI agents
(Jules, Paperclip, Hermes, and Perplexity) and gathering their individual
deliverables for a complex request.

Usage:
    uv run python src/codomyrmex/examples/ambitious_swarm_demo.py
"""

import sys

from codomyrmex.agents.core import AgentRequest
from codomyrmex.agents.generic import AgentOrchestrator
from codomyrmex.agents.hermes import HermesClient
from codomyrmex.agents.jules import JulesClient
from codomyrmex.agents.paperclip import PaperclipClient
from codomyrmex.agents.perplexity import PerplexityClient
from codomyrmex.logging_monitoring import get_logger, setup_logging

logger = get_logger(__name__)


def main():
    setup_logging({"level": "INFO"})
    logger.info("Initializing Ambitious Swarm...")

    # Instantiate diverse agents. Some may use live keys, some may fall back.
    # The swarm handles failures gracefully.
    try:
        jules = JulesClient()
    except Exception:
        jules = None

    try:
        paperclip = PaperclipClient()
    except Exception:
        paperclip = None

    try:
        hermes = HermesClient()
    except Exception:
        hermes = None

    try:
        perplexity = PerplexityClient()
    except Exception:
        perplexity = None

    swarm_agents = []
    for a in [jules, paperclip, hermes, perplexity]:
        if a is not None:
            try:
                # Only use agents that have their underlying CLI or API key configured locally
                if hasattr(a, "test_connection") and a.test_connection():
                    swarm_agents.append(a)
                else:
                    logger.warning(
                        f"Skipping {a.name} because its CLI or API Key is unavailable on this machine."
                    )
            except Exception as e:
                logger.warning(f"Error checking {a.name}: {e}")

    if not swarm_agents:
        logger.error("No agents could be initialized. Exiting.")
        sys.exit(1)

    orchestrator = AgentOrchestrator(swarm_agents)
    logger.info(
        f"Swarm assembled with {len(swarm_agents)} agents: {[a.name for a in swarm_agents]}"
    )

    request = AgentRequest(
        prompt="Propose a 3-step high-level architectural plan for integrating a new physics engine into an existing codebase.",
        context={"model": "sonar"},  # specifically for perplexity
    )

    logger.info("Executing swarm in PARALLEL...")
    deliverables = orchestrator.execute_parallel(request)

    print("\n" + "=" * 50)
    print("AMBITIOUS SWARM DELIVERABLES")
    print("=" * 50)

    for i, response in enumerate(deliverables):
        agent_name = response.metadata.get("agent", swarm_agents[i].name)
        status = "SUCCESS" if response.is_success() else "FAILED"
        print(f"\n--- [ {agent_name.upper()} | {status} ] ---")
        if response.is_success():
            print(response.content.strip())
        else:
            print(f"Error: {response.error}")
        print("-" * 50)

    logger.info("Swarm demonstration complete.")


if __name__ == "__main__":
    main()
