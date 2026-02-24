"""Governance policy engine module.

Provides PolicyRule, PolicyEngine, and PolicyError for defining
and enforcing governance policies with composable rules.
"""

from collections.abc import Callable
from typing import Any
from uuid import uuid4


class PolicyError(Exception):
    """Exception raised when a policy violation or management error occurs."""
    pass


class PolicyRule:
    """A single evaluatable governance rule.

    Args:
        name: Unique name for this rule.
        condition: Callable that takes a context dict and returns bool.
        action: Description of the enforcement action.
        priority: Higher priority rules are evaluated first (default 0).
    """

    def __init__(
        self,
        name: str,
        condition: Callable[[dict[str, Any]], bool],
        action: str,
        priority: int = 0,
    ) -> None:
        """Execute   Init   operations natively."""
        self.name = name
        self.condition = condition
        self.action = action
        self.priority = priority

    def evaluate(self, context: dict[str, Any]) -> bool:
        """Evaluate the rule against the given context.

        Returns:
            True if the rule passes (condition satisfied), False otherwise.
            Returns False if the condition raises an exception.
        """
        try:
            return bool(self.condition(context))
        except Exception:
            return False

    def __repr__(self) -> str:
        """Execute   Repr   operations natively."""
        return f"PolicyRule(name='{self.name}', priority={self.priority})"




class PolicyEngine:
    """Manages and enforces collections of governance policies.

    Policies are named containers of PolicyRules. Rules within a policy
    are evaluated in descending priority order.
    """

    def __init__(self) -> None:
        """Execute   Init   operations natively."""
        self._policies: dict[str, dict[str, Any]] = {}

    def create_policy(self, name: str, description: str = "") -> dict[str, Any]:
        """Create a new named policy.

        Args:
            name: Unique policy name.
            description: Optional description.

        Returns:
            Dict with 'name', 'id', and 'description'.

        Raises:
            PolicyError: If a policy with that name already exists.
        """
        if name in self._policies:
            raise PolicyError(f"Policy '{name}' already exists")

        policy_id = uuid4().hex[:12]
        self._policies[name] = {
            "id": policy_id,
            "name": name,
            "description": description,
            "rules": [],
        }
        return {"name": name, "id": policy_id, "description": description}

    def add_rule(self, policy_name: str, rule: PolicyRule) -> None:
        """Add a rule to an existing policy.

        Args:
            policy_name: Name of the policy to add the rule to.
            rule: PolicyRule instance.

        Raises:
            PolicyError: If the policy does not exist.
        """
        if policy_name not in self._policies:
            raise PolicyError(f"Policy '{policy_name}' does not exist")
        self._policies[policy_name]["rules"].append(rule)

    def _sorted_rules(self, policy_name: str) -> list[PolicyRule]:
        """Return rules sorted by descending priority."""
        rules = self._policies[policy_name]["rules"]
        return sorted(rules, key=lambda r: r.priority, reverse=True)

    def evaluate(self, policy_name: str, context: dict[str, Any]) -> dict[str, Any]:
        """Evaluate all rules in a policy against the context.

        Args:
            policy_name: Name of the policy.
            context: Context dict to evaluate rules against.

        Returns:
            Dict with 'passed', 'violations', 'total_rules', and 'details'.

        Raises:
            PolicyError: If the policy does not exist.
        """
        if policy_name not in self._policies:
            raise PolicyError(f"Policy '{policy_name}' does not exist")

        rules = self._sorted_rules(policy_name)
        details = []
        violations = 0

        for rule in rules:
            passed = rule.evaluate(context)
            details.append({
                "rule": rule.name,
                "passed": passed,
                "action": rule.action,
                "priority": rule.priority,
            })
            if not passed:
                violations += 1

        return {
            "passed": violations == 0,
            "violations": violations,
            "total_rules": len(rules),
            "details": details,
        }

    def get_violations(
        self, policy_name: str, context: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Return only the rules that failed evaluation.

        Args:
            policy_name: Name of the policy.
            context: Context dict.

        Returns:
            List of dicts with 'rule' and 'action' for each violation.
        """
        result = self.evaluate(policy_name, context)
        return [
            {"rule": d["rule"], "action": d["action"]}
            for d in result["details"]
            if not d["passed"]
        ]

    def enforce(
        self, policy_name: str, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Enforce a policy and return enforcement actions.

        Args:
            policy_name: Name of the policy.
            context: Context dict.

        Returns:
            Dict with 'enforced' (bool), 'actions' (list of action strings),
            and 'violations' count.
        """
        violations = self.get_violations(policy_name, context)
        actions = [v["action"] for v in violations]
        return {
            "enforced": len(violations) > 0,
            "actions": actions,
            "violations": len(violations),
        }

    def list_policies(self) -> list[str]:
        """Return names of all registered policies."""
        return list(self._policies.keys())

    def add_policy(self, policy: PolicyRule) -> None:
        """Add a policy rule directly (wraps in unnamed policy)."""
        self._policies.setdefault("_default", {
            "id": "default",
            "name": "_default",
            "description": "",
            "rules": [],
        })
        self._policies["_default"]["rules"].append(policy)
