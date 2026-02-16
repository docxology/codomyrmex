"""Policy engine with rule evaluation, violation detection, and enforcement.

Policies are named collections of rules.  Each rule has a callable condition
that receives a context dict and returns ``True`` (pass) or ``False`` (fail).
The engine can evaluate policies to find violations and optionally enforce
corrective actions.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class PolicyError(Exception):
    """Raised when a policy operation fails."""


class PolicyRule:
    """A single evaluable governance rule.

    Attributes:
        name: Short name for the rule.
        condition: A callable that receives a context dict and returns bool.
        action: Description of the enforcement action when the rule is violated.
        priority: Numeric priority (higher = more important, evaluated first).
    """

    def __init__(
        self,
        name: str,
        condition: Callable[[dict], bool],
        action: str,
        priority: int = 0,
    ) -> None:
        self.name = name
        self.condition = condition
        self.action = action
        self.priority = priority

    def evaluate(self, context: dict) -> bool:
        """Evaluate this rule against a context.

        Args:
            context: Arbitrary dict of state to check against the condition.

        Returns:
            ``True`` if the rule passes, ``False`` if it is violated.
        """
        try:
            return bool(self.condition(context))
        except Exception as exc:
            logger.warning("Rule '%s' raised during evaluation: %s", self.name, exc)
            return False

    def __repr__(self) -> str:
        return f"PolicyRule(name={self.name!r}, priority={self.priority})"


class PolicyEngine:
    """Manages named policies, each containing an ordered list of rules.

    Usage::

        engine = PolicyEngine()
        engine.create_policy("budget", "Enforce spending limits")

        engine.add_rule("budget", PolicyRule(
            name="max_spend",
            condition=lambda ctx: ctx.get("amount", 0) <= 10_000,
            action="Reject transaction exceeding $10,000",
            priority=10,
        ))

        result = engine.evaluate("budget", {"amount": 5_000})
        # result["passed"] == True

        violations = engine.get_violations("budget", {"amount": 15_000})
        # violations == [{"rule": "max_spend", ...}]
    """

    def __init__(self) -> None:
        # policy_name -> {"id", "name", "description", "rules", "created_at"}
        self._policies: dict[str, dict] = {}

    def create_policy(self, name: str, description: str = "") -> dict:
        """Create a new named policy.

        Args:
            name: Unique policy name.
            description: Human-readable purpose of the policy.

        Returns:
            The policy metadata dict.

        Raises:
            PolicyError: If a policy with the same name already exists.
        """
        if name in self._policies:
            raise PolicyError(f"Policy '{name}' already exists.")

        policy = {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": description,
            "rules": [],
            "created_at": datetime.now().isoformat(),
        }
        self._policies[name] = policy
        logger.info("Created policy '%s'", name)
        return {k: v for k, v in policy.items() if k != "rules"}

    def add_rule(self, policy_name: str, rule: PolicyRule) -> None:
        """Add a rule to an existing policy.

        Rules are kept sorted by descending priority so higher-priority rules
        evaluate first.

        Args:
            policy_name: Name of the target policy.
            rule: The rule to add.

        Raises:
            PolicyError: If the policy does not exist.
        """
        policy = self._get_policy(policy_name)
        policy["rules"].append(rule)
        policy["rules"].sort(key=lambda r: r.priority, reverse=True)
        logger.info("Added rule '%s' to policy '%s'", rule.name, policy_name)

    def evaluate(self, policy_name: str, context: dict) -> dict:
        """Evaluate all rules in a policy against the given context.

        Args:
            policy_name: Name of the policy to evaluate.
            context: State dict passed to every rule's condition.

        Returns:
            A dict with:
                - ``passed`` (bool): ``True`` if all rules passed.
                - ``total_rules`` (int): Number of rules evaluated.
                - ``violations`` (int): Number of failed rules.
                - ``details`` (list[dict]): Per-rule results.
        """
        policy = self._get_policy(policy_name)
        details: list[dict] = []
        violations = 0

        for rule in policy["rules"]:
            passed = rule.evaluate(context)
            if not passed:
                violations += 1
            details.append({
                "rule": rule.name,
                "priority": rule.priority,
                "passed": passed,
                "action": rule.action if not passed else None,
            })

        return {
            "policy": policy_name,
            "passed": violations == 0,
            "total_rules": len(policy["rules"]),
            "violations": violations,
            "details": details,
        }

    def get_violations(self, policy_name: str, context: dict) -> list[dict]:
        """Return only the violated rules for a policy and context.

        Args:
            policy_name: Policy to check.
            context: State dict.

        Returns:
            A list of dicts, each with ``rule``, ``priority``, and ``action``.
        """
        result = self.evaluate(policy_name, context)
        return [
            {
                "rule": d["rule"],
                "priority": d["priority"],
                "action": d["action"],
            }
            for d in result["details"]
            if not d["passed"]
        ]

    def enforce(self, policy_name: str, context: dict) -> dict:
        """Evaluate the policy and return enforcement recommendations.

        This is a higher-level wrapper around :meth:`evaluate` that adds
        an ``actions`` list of recommended enforcement steps and an
        ``enforced`` flag indicating whether any action was triggered.

        Args:
            policy_name: Policy to enforce.
            context: State dict.

        Returns:
            A dict extending the :meth:`evaluate` result with ``actions``
            (list of action strings) and ``enforced`` (bool).
        """
        result = self.evaluate(policy_name, context)
        actions = [
            d["action"]
            for d in result["details"]
            if not d["passed"] and d["action"]
        ]
        result["actions"] = actions
        result["enforced"] = len(actions) > 0
        return result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_policy(self, name: str) -> dict:
        if name not in self._policies:
            raise PolicyError(f"Policy '{name}' does not exist.")
        return self._policies[name]

    def list_policies(self) -> list[str]:
        """Return names of all registered policies."""
        return list(self._policies.keys())
