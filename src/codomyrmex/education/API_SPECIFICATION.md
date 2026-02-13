# Education - API Specification

## Introduction

This document specifies the Application Programming Interface (API) for the Education module. The primary purpose of this API is to provide curriculum generation, lesson management, and adaptive learning path visualization for training users and upskilling agents within the Codomyrmex ecosystem.

## Endpoints / Functions / Interfaces

### Enum: `Difficulty`

- **Description**: Enumeration of learning difficulty levels for lessons and curricula.
- **Module**: `codomyrmex.education.curriculum`
- **Values**:
    - `BEGINNER` - Introductory-level content
    - `INTERMEDIATE` - Mid-level content requiring foundational knowledge
    - `ADVANCED` - Complex content for experienced learners
    - `EXPERT` - Mastery-level content

### Class: `Lesson`

- **Description**: Dataclass representing an individual unit of learning within a curriculum. Each lesson has a title, content body, difficulty level, duration, and optional prerequisites.
- **Module**: `codomyrmex.education.curriculum`
- **Parameters/Arguments** (constructor):
    - `title` (str): Title of the lesson
    - `content` (str): Full text content of the lesson
    - `difficulty` (Difficulty): Difficulty level of the lesson
    - `duration_minutes` (int): Estimated time to complete the lesson in minutes
    - `id` (UUID, optional): Unique identifier. Auto-generated via `uuid4()` if not provided
    - `prerequisites` (List[UUID], optional): List of lesson IDs that must be completed before this lesson. Defaults to an empty list

### Class: `Curriculum`

- **Description**: A structured sequence of lessons organized around a topic and target difficulty level. Provides methods for managing lessons and calculating aggregate statistics.
- **Module**: `codomyrmex.education.curriculum`
- **Parameters/Arguments** (constructor):
    - `topic` (str): The subject area of the curriculum
    - `difficulty` (Difficulty): Target difficulty level for the curriculum
- **Attributes**:
    - `topic` (str): The subject area
    - `target_difficulty` (Difficulty): Target difficulty level
    - `lessons` (List[Lesson]): Ordered list of lessons in the curriculum
- **Methods**:
    - `add_lesson(lesson: Lesson) -> None`: Add a lesson to the curriculum.
    - `get_lesson(lesson_id: UUID) -> Optional[Lesson]`: Retrieve a lesson by its UUID. Returns `None` if not found.
    - `total_duration() -> int`: Calculate the total duration of all lessons in minutes.
    - `__repr__() -> str`: Returns a string representation, e.g. `Curriculum(topic='Python Basics', lessons=5)`.

### Function: `render_curriculum_path(curriculum: Curriculum) -> MermaidDiagram`

- **Description**: Generates a Mermaid flowchart diagram showing the lesson dependency graph for a curriculum. Each lesson is a node, and prerequisite relationships are drawn as directed edges.
- **Module**: `codomyrmex.education.visualization`
- **Parameters/Arguments**:
    - `curriculum` (Curriculum): The curriculum to visualize
- **Returns/Response**: `MermaidDiagram` - A Mermaid diagram with title "Curriculum Path" showing the directed graph of lesson dependencies.

## Data Models

### Lesson (dataclass)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `title` | `str` | required | Lesson title |
| `content` | `str` | required | Full text content |
| `difficulty` | `Difficulty` | required | Difficulty level |
| `duration_minutes` | `int` | required | Estimated duration in minutes |
| `id` | `UUID` | auto-generated | Unique identifier |
| `prerequisites` | `List[UUID]` | `[]` | IDs of prerequisite lessons |

## Authentication & Authorization

Not applicable for this internal education module.

## Rate Limiting

Not applicable for this internal education module.

## Versioning

This module follows the general versioning strategy of the Codomyrmex project. API stability is aimed for, with changes documented in the CHANGELOG.md.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
