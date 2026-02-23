# Relations - API Specification

## Introduction

This document specifies the Application Programming Interface (API) for the Relations module. The primary purpose of this API is to provide customer relationship management (CRM) capabilities, including contact management, interaction logging, tagging, and social graph visualization.

## Endpoints / Functions / Interfaces

### Enum: `InteractionType`

- **Description**: Types of communication events that can be logged against a contact.
- **Module**: `codomyrmex.relations.crm`
- **Values**:
    - `EMAIL` - Email communication
    - `CALL` - Phone or voice call
    - `MEETING` - In-person or virtual meeting
    - `SOCIAL_MEDIA` - Social media interaction

### Class: `Interaction` (dataclass)

- **Description**: Record of a communication event with a contact.
- **Module**: `codomyrmex.relations.crm`
- **Parameters/Arguments** (constructor):
    - `type` (InteractionType): The type of interaction
    - `summary` (str): Brief description of the interaction
    - `timestamp` (datetime, optional): When the interaction occurred. Defaults to `datetime.now()`
    - `id` (UUID, optional): Unique identifier. Auto-generated via `uuid4()` if not provided

### Class: `Contact` (dataclass)

- **Description**: Represents an external entity (person or organization) in the CRM. Supports tagging for categorization and maintains a history of interactions.
- **Module**: `codomyrmex.relations.crm`
- **Parameters/Arguments** (constructor):
    - `name` (str): Contact name
    - `email` (Optional[str], optional): Email address. Defaults to `None`
    - `phone` (Optional[str], optional): Phone number. Defaults to `None`
    - `tags` (Set[str], optional): Set of tags for categorization. Defaults to empty set
    - `history` (List[Interaction], optional): List of past interactions. Defaults to empty list
    - `id` (UUID, optional): Unique identifier. Auto-generated via `uuid4()` if not provided
- **Methods**:
    - `log_interaction(interaction: Interaction) -> None`: Append an interaction to the contact's history.
    - `add_tag(tag: str) -> None`: Add a tag to the contact's tag set.

### Class: `CRM`

- **Description**: Customer Relationship Management engine. Provides contact storage, search, and retrieval.
- **Module**: `codomyrmex.relations.crm`
- **Parameters/Arguments** (constructor): None
- **Methods**:
    - `add_contact(contact: Contact) -> None`: Add a contact to the CRM.
    - `search(query: str) -> List[Contact]`: Search contacts by name or email (case-insensitive substring match). Returns a list of matching contacts.
    - `get_contact(contact_id: UUID) -> Optional[Contact]`: Retrieve a contact by UUID. Returns `None` if not found.

### Function: `render_social_graph(crm: CRM) -> MermaidDiagram`

- **Description**: Generates a Mermaid diagram showing all contacts in the CRM as nodes in a social graph.
- **Module**: `codomyrmex.relations.visualization`
- **Parameters/Arguments**:
    - `crm` (CRM): The CRM instance to visualize
- **Returns/Response**: `MermaidDiagram` - A top-down Mermaid graph with one node per contact, titled "Social Graph".

## Data Models

### Contact (dataclass)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | `str` | required | Contact name |
| `email` | `Optional[str]` | `None` | Email address |
| `phone` | `Optional[str]` | `None` | Phone number |
| `tags` | `Set[str]` | `set()` | Categorization tags |
| `history` | `List[Interaction]` | `[]` | Interaction history |
| `id` | `UUID` | auto-generated | Unique identifier |

### Interaction (dataclass)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `type` | `InteractionType` | required | Type of communication |
| `summary` | `str` | required | Brief description |
| `timestamp` | `datetime` | `datetime.now()` | When the interaction occurred |
| `id` | `UUID` | auto-generated | Unique identifier |

## Authentication & Authorization

Not applicable for this internal relations module.

## Rate Limiting

Not applicable for this internal relations module.

## Versioning

This module follows the general versioning strategy of the Codomyrmex project. API stability is aimed for, with changes documented in the CHANGELOG.md.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
