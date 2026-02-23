# Narrative Submodule

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Computational Narratology**

The `codomyrmex.meme.narrative` submodule provides tools for analyzing, generating, and restructuring narratives. It uses structuralist theory (Campbell, Propp) to manipulate story arcs and archetypes.

## Key Components

### 1. Data Models (`models.py`)

* **`Narrative`**: A structured story entity.
  * `arc`: The structural trajectory (e.g., Hero's Journey).
  * `characters`: Agents filling archetypal roles.
* **`NarrativeArc`**: Defines the stages of a story (e.g., Call to Adventure, Ordeal, Return).
* **`Archetype`**: Enum of classic roles (Hero, Shadow, Mentor, Trickster).

### 2. Structure (`structure.py`)

* **`heros_journey_arc`**: Campbell's monomyth template.
* **`freytag_pyramid_arc`**: Classic dramatic structure (Exposition -> Climax -> Denouement).
* **`fichtean_curve_arc`**: Series of crises leading to a climax.

### 3. Myth Synthesis (`myth.py`)

* **`synthesize_myth(domain, archetype_map)`**: Generates a skeletal narrative for a given domain (e.g., "Tech Startup", "Political Campaign").

### 4. Narrative Engine (`engine.py`)

* **`NarrativeEngine`**: Orchestrator.
  * `analyze(text)`: Deconstructs a story into its components.
  * `generate(template)`: Creates a new narrative from a template.

## Usage

```python
from codomyrmex.meme.narrative import NarrativeEngine, Archetype

engine = NarrativeEngine()

# Generate a Tech Myth
myth = engine.generate_myth(
    subject="The Founder",
    archetype=Archetype.HERO,
    domain="Silicon Valley"
)

print(f"Title: {myth.title}")
# Output: "The Founder's Journey to the Unicorn"
```
