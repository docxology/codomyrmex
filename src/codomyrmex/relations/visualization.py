"""Relations visualization — graph rendering, statistics, and text reports.

Provides:
- render_social_graph: Mermaid diagram from CRM contacts
- render_interaction_timeline: timeline view of contact interactions
- contact_heatmap_data: contact activity aggregation by type
- network_summary_text: plain-text summary of the relations network
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Any

from .crm.crm import Contact, ContactManager


def render_social_graph(cm: ContactManager) -> dict[str, Any]:
    """Generate a graph definition from CRM contacts.

    Returns a dictionary with 'title', 'nodes', and 'edge_count'.
    Does not depend on data_visualization to avoid circular imports.
    """
    nodes: list[dict[str, Any]] = []
    for contact in cm._contacts.values():
        safe_name = contact.name.replace(" ", "_")
        nodes.append({
            "id": safe_name,
            "label": contact.name,
            "email": contact.email,
            "tags": list(contact.tags) if hasattr(contact, "tags") else [],
            "interactions": len(contact.interactions),
        })

    return {
        "title": "Social Graph",
        "node_count": len(nodes),
        "nodes": nodes,
    }


def render_interaction_timeline(cm: ContactManager, limit: int = 50) -> list[dict[str, Any]]:
    """Build a timeline of all interactions across contacts.

    Returns a list of dicts sorted by timestamp (newest first),
    each containing contact_name, type, notes, and timestamp.
    """
    events: list[dict[str, Any]] = []
    for contact in cm._contacts.values():
        for ix in contact.interactions:
            events.append({
                "contact_name": contact.name,
                "contact_id": contact.id,
                "type": ix.type,
                "notes": ix.notes,
                "timestamp": ix.timestamp,
            })
    # Sort newest first
    events.sort(key=lambda e: e["timestamp"], reverse=True)
    return events[:limit]


def contact_heatmap_data(cm: ContactManager) -> dict[str, dict[str, int]]:
    """Aggregate interaction counts by contact and type.

    Returns:
        {contact_name: {interaction_type: count}}
    """
    heatmap: dict[str, dict[str, int]] = {}
    for contact in cm._contacts.values():
        counts: dict[str, int] = defaultdict(int)
        for ix in contact.interactions:
            counts[ix.type] += 1
        if counts:
            heatmap[contact.name] = dict(counts)
    return heatmap


def tag_co_occurrence(cm: ContactManager) -> dict[str, dict[str, int]]:
    """Compute tag co-occurrence matrix.

    Returns:
        {tag_a: {tag_b: count}} for contacts sharing both tags.
    """
    matrix: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for contact in cm._contacts.values():
        tags = list(contact.tags) if hasattr(contact, "tags") else []
        for i, t1 in enumerate(tags):
            for t2 in tags[i + 1:]:
                matrix[t1][t2] += 1
                matrix[t2][t1] += 1
    return {k: dict(v) for k, v in matrix.items()}


def network_summary_text(cm: ContactManager) -> str:
    """Generate a plain-text summary of the CRM network.

    Returns:
        Multi-line summary with contact count, interaction totals,
        top tags, and most active contacts.
    """
    contacts = list(cm._contacts.values())
    total_contacts = len(contacts)
    total_interactions = sum(len(c.interactions) for c in contacts)

    # Top contacts by interaction count
    sorted_by_activity = sorted(contacts, key=lambda c: len(c.interactions), reverse=True)
    top_5 = sorted_by_activity[:5]

    # Tag counts
    tag_counts: dict[str, int] = defaultdict(int)
    for c in contacts:
        for tag in (c.tags if hasattr(c, "tags") else []):
            tag_counts[tag] += 1
    top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    lines = [
        f"CRM Network Summary",
        f"  Contacts: {total_contacts}",
        f"  Total interactions: {total_interactions}",
        f"  Avg interactions/contact: {total_interactions / max(total_contacts, 1):.1f}",
    ]
    if top_tags:
        lines.append(f"  Top tags: {', '.join(f'{t}({n})' for t, n in top_tags)}")
    if top_5:
        lines.append(f"  Most active: {', '.join(f'{c.name}({len(c.interactions)})' for c in top_5)}")
    return "\n".join(lines)


def export_contacts_csv(cm: ContactManager) -> str:
    """Export contacts as CSV text."""
    lines = ["name,email,tags,interaction_count"]
    for contact in cm._contacts.values():
        tags_str = "; ".join(contact.tags) if hasattr(contact, "tags") else ""
        lines.append(
            f'"{contact.name}","{contact.email}","{tags_str}",{len(contact.interactions)}'
        )
    return "\n".join(lines)
