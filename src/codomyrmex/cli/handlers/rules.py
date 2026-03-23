"""CLI handlers for the rules subcommand group."""

from __future__ import annotations


def handle_rules_list() -> int:
    """list all rules with their priority and module."""
    from codomyrmex.agentic_memory.rules import RuleEngine

    engine = RuleEngine()
    rules = engine.list_all_rules()

    if not rules:
        print("No rules found.")
        return 0

    # Column widths
    name_w = max(len(r.name) for r in rules)
    prio_w = max(len(r.priority.name) for r in rules)
    header = f"{'NAME':<{name_w}}  {'PRIORITY':<{prio_w}}  FILE"
    print(header)
    print("-" * len(header))
    for r in rules:
        print(f"{r.name:<{name_w}}  {r.priority.name:<{prio_w}}  {r.file_path}")

    print(f"\n{len(rules)} rules total.")
    return 0


def handle_rules_check(file: str) -> int:
    """Check applicable rules for a given file path."""
    from codomyrmex.agentic_memory.rules import RuleEngine

    engine = RuleEngine()
    rule_set = engine.get_applicable_rules(file_path=file)
    resolved = rule_set.resolved()

    if not resolved:
        print(f"No rules applicable for: {file}")
        return 0

    print(f"Rules applicable to: {file}")
    print()
    for r in resolved:
        print(f"  [{r.priority.name}] {r.name}")
    print(f"\n{len(resolved)} rules apply (highest priority first).")
    return 0
