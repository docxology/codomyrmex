#!/usr/bin/env python3
"""Maximum Verified Paperclip Orchestration Demo.

This script demonstrates programmatically spinning up a mission
and delegating it to an active Paperclip company via the
PaperclipClient.
"""

import json

from codomyrmex.logging_monitoring.logger import get_logger

from codomyrmex.agents.paperclip.paperclip_client import PaperclipClient

logger = get_logger(__name__)


def main() -> None:
    """Bootstrap a maximum paperclip orchestration mission."""
    logger.info("Initializing Maximum Verified Paperclip Orchestration...")

    client = PaperclipClient()

    # Step 1: Ensure Paperclip CLI is available
    version_info = client.get_version()
    if not version_info.get("available"):
        logger.error("Paperclip CLI not found. Please install it first.")
        return

    logger.info(f"Connected to Paperclip CLI: {version_info.get('version')}")

    # Step 2: List Companies to find the target company
    companies_res = client.list_companies()
    if not companies_res.get("success"):
        logger.error(f"Failed to list companies: {companies_res.get('error')}")
        return

    try:
        companies_data = json.loads(companies_res.get("output", "[]"))
        if not companies_data:
            logger.warning("No companies found to orchestrate.")
            return
        company = companies_data[0]
        company_id = company.get("id")
        logger.info(f"Targeting Company [ID: {company_id}]")
    except json.JSONDecodeError:
        logger.error("Failed to parse company list JSON.")
        return

    # Step 3: Find the CEO Agent to trigger
    agents_res = client.list_agents(company_id)
    if not agents_res.get("success"):
        logger.error("Failed to list agents.")
        return

    try:
        agents_data = json.loads(agents_res.get("output", "[]"))
        ceo_agent = None
        for agent in agents_data:
            sys_prompt = agent.get("systemPrompt", "")
            agent_name = agent.get("name", "")
            if sys_prompt.startswith("You are the CEO") or "CEO" in agent_name:
                ceo_agent = agent
                break

        if not ceo_agent:
            if agents_data:
                ceo_agent = agents_data[0]
            else:
                logger.error("No agents found in company.")
                return

        ceo_agent_id = ceo_agent.get("id")
        logger.info(f"Selected orchestrating Agent [ID: {ceo_agent_id}]")
    except json.JSONDecodeError:
        logger.error("Failed to parse agent list JSON.")
        return

    # Step 4: Bootstrap the Programmatic Mission
    mission_title = "Programmatic Swarm Defense Mission"
    mission_desc = "Autonomously review the latest security threats against the swarm and propose resilient architecture upgrades."

    logger.info(f"Bootstrapping mission: '{mission_title}'")

    boot_res = client.bootstrap_mission(
        company_id=company_id,
        title=mission_title,
        description=mission_desc,
        trigger_agent_id=ceo_agent_id,
    )

    if boot_res.get("success"):
        logger.info("Mission successfully bootstrapped and CEO dispatched!")
        logger.info(f"Execution Output: {boot_res.get('output')}")
    else:
        logger.error(f"Failed to bootstrap mission: {boot_res.get('error')}")


if __name__ == "__main__":
    main()
