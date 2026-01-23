#!/usr/bin/env python3
"""Collaboration Module - Comprehensive Usage Script.

Demonstrates multi-agent coordination with full configurability,
unified logging, and output saving.

Usage:
    python basic_usage.py                          # Run with defaults
    python basic_usage.py --agents 5               # Custom agent count
    python basic_usage.py --verbose                # Verbose output
"""

import sys
import time
from pathlib import Path
from typing import Any, Dict, List

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# Direct import to avoid triggering full codomyrmex package init
import importlib.util
script_base_path = project_root / "src" / "codomyrmex" / "utils" / "script_base.py"
spec = importlib.util.spec_from_file_location("script_base", script_base_path)
script_base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(script_base)
ScriptBase = script_base.ScriptBase
ScriptConfig = script_base.ScriptConfig


class CollaborationScript(ScriptBase):
    """Comprehensive collaboration module demonstration."""

    def __init__(self):
        super().__init__(
            name="collaboration_usage",
            description="Demonstrate and test multi-agent collaboration",
            version="1.0.0",
        )

    def add_arguments(self, parser):
        """Add collaboration-specific arguments."""
        group = parser.add_argument_group("Collaboration Options")
        group.add_argument(
            "--agents", "-a", type=int, default=3,
            help="Number of agents in swarm (default: 3)"
        )
        group.add_argument(
            "--missions", type=int, default=5,
            help="Number of missions to execute (default: 5)"
        )
        group.add_argument(
            "--roles", nargs="+", default=["researcher", "coder", "reviewer"],
            help="Agent roles (default: researcher coder reviewer)"
        )

    def run(self, args, config: ScriptConfig) -> Dict[str, Any]:
        """Execute collaboration demonstrations."""
        results = {
            "tests_run": 0,
            "tests_passed": 0,
            "swarm_stats": {},
            "mission_results": [],
        }

        if config.dry_run:
            self.log_info(f"Would create swarm with {args.agents} agents")
            self.log_info(f"Would execute {args.missions} missions")
            results["dry_run"] = True
            return results

        # Import collaboration module (after dry_run check)
        from codomyrmex.collaboration import SwarmManager, AgentProxy, TaskDecomposer

        # Test 1: SwarmManager creation
        self.log_info(f"\n1. Creating SwarmManager with {args.agents} agents")
        try:
            swarm = SwarmManager()
            agents = []
            for i in range(args.agents):
                role = args.roles[i % len(args.roles)]
                agent = AgentProxy(name=f"agent_{i+1}", role=role)
                swarm.add_agent(agent)
                agents.append({"name": agent.name, "role": agent.role})

            results["swarm_stats"]["agents"] = agents
            results["swarm_stats"]["total"] = len(swarm.agents)
            results["tests_passed"] += 1
            self.log_success(f"Swarm created with {len(swarm.agents)} agents")
        except Exception as e:
            self.log_error(f"Swarm creation failed: {e}")
        results["tests_run"] += 1

        # Test 2: Task decomposition
        self.log_info("\n2. Testing TaskDecomposer")
        try:
            missions = [
                "analyze code and write tests",
                "review documentation and update examples",
                "fix bugs and optimize performance",
            ]
            decomposition_results = []
            for mission in missions:
                subtasks = TaskDecomposer.decompose(mission)
                decomposition_results.append({
                    "mission": mission,
                    "subtasks": subtasks,
                    "count": len(subtasks),
                })

            results["decomposition"] = decomposition_results
            results["tests_passed"] += 1
            self.log_success(f"Decomposed {len(missions)} missions")
        except Exception as e:
            self.log_error(f"Task decomposition failed: {e}")
        results["tests_run"] += 1

        # Test 3: Mission execution
        self.log_info(f"\n3. Executing {args.missions} missions")
        try:
            mission_templates = [
                "analyze codebase structure",
                "implement feature X",
                "optimize database queries",
                "review security protocols",
                "update API documentation",
            ]
            start_time = time.perf_counter()

            for i in range(args.missions):
                mission = mission_templates[i % len(mission_templates)]
                mission_results = swarm.execute(mission)
                results["mission_results"].append({
                    "mission": mission,
                    "results_count": len(mission_results),
                    "agents_responded": list(mission_results.keys()),
                })

            execution_time = time.perf_counter() - start_time
            results["swarm_stats"]["execution_time"] = execution_time
            results["swarm_stats"]["missions_completed"] = args.missions
            results["tests_passed"] += 1
            self.log_success(f"Executed {args.missions} missions in {execution_time:.2f}s")
        except Exception as e:
            self.log_error(f"Mission execution failed: {e}")
        results["tests_run"] += 1

        # Test 4: Consensus voting
        self.log_info("\n4. Testing consensus voting")
        try:
            proposals = [
                "adopt new coding standards",
                "migrate to microservices",
                "implement caching layer",
            ]
            voting_results = []
            for proposal in proposals:
                approved = swarm.consensus_vote(proposal)
                voting_results.append({
                    "proposal": proposal,
                    "approved": approved,
                })

            results["voting"] = voting_results
            results["tests_passed"] += 1
            approved_count = sum(1 for v in voting_results if v["approved"])
            self.log_success(f"Voting complete: {approved_count}/{len(proposals)} proposals approved")
        except Exception as e:
            self.log_error(f"Voting test failed: {e}")
        results["tests_run"] += 1

        # Metrics
        self.add_metric("tests_run", results["tests_run"])
        self.add_metric("tests_passed", results["tests_passed"])
        self.add_metric("agents", len(swarm.agents))
        self.add_metric("missions_completed", args.missions)

        return results


if __name__ == "__main__":
    script = CollaborationScript()
    sys.exit(script.execute())
