from typing import Callable, Any, Dict, List

class PolicyError(Exception):
    """Exception raised when a policy violation occurs."""
    pass

class Policy:
    """Executable governance rule."""
    
    def __init__(self, name: str, rule: Callable[[Dict[str, Any]], bool], error_message: str):
        self.name = name
        self.rule = rule
        self.error_message = error_message

    def check(self, context: Dict[str, Any]) -> None:
        """
        Evaluate the rule against the context.
        Raises PolicyError if the rule evaluates to False.
        """
        try:
            result = self.rule(context)
        except Exception as e:
            raise PolicyError(f"Policy '{self.name}' execution failed: {e}")
        
        if not result:
            raise PolicyError(f"Policy '{self.name}' violation: {self.error_message}")

class PolicyEngine:
    """Manages and enforces a collection of policies."""
    
    def __init__(self):
        self._policies: List[Policy] = []

    def add_policy(self, policy: Policy) -> None:
        self._policies.append(policy)

    def enforce(self, context: Dict[str, Any]) -> None:
        """Run all policies against the context."""
        errors = []
        for policy in self._policies:
            try:
                policy.check(context)
            except PolicyError as e:
                errors.append(str(e))
        
        if errors:
            raise PolicyError("\n".join(errors))
