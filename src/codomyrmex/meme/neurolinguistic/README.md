# Neurolinguistic Submodule

**Persuasion Engineering**

The `codomyrmex.meme.neurolinguistic` submodule provides tools for analyzing and engineering language at the cognitive level. It focuses on how framing, linguistic patterns, and cognitive biases shape perception and decision-making.

## Key Components

### 1. Data Models (`models.py`)

* **`CognitiveFrame`**: A mental structure that shapes how we reason (e.g., "Tax Relief" vs. "Investment").
* **`LinguisticPattern`**: Specific syntax structures designed to influence (Hypnotic, Clarifying).
* **`BiasInstance`**: Detected occurrences of cognitive bias.
* **`PersuasionAttempt`**: Log of influence operations.

### 2. Framing (`framing.py`)

* **`analyze_frames(text)`**: Identifies active frames in a text.
* **`reframe(content, source, target)`**: Rewrites content to fit a new frame.

### 3. Patterns (`patterns.py`)

* **`milton_model_patterns`**: Hypnotic language patterns (vagueness, mind-reading, cause-effect).
* **`meta_model_patterns`**: Clarifying patterns to challenge vague language.
* **`detect_patterns`**: Scans text for usage of known patterns.

### 4. Engine (`engine.py`)

* **`NeurolinguisticEngine`**: Orchestrator.
  * `audit(text)`: Comprehensive analysis of frames and patterns.
  * `spin(text, target_frame)`: Adjusts the framing of a text.

## Usage

```python
from codomyrmex.meme.neurolinguistic import NeurolinguisticEngine, CognitiveFrame

engine = NeurolinguisticEngine()
frame = CognitiveFrame(name="Innovation", keywords=["new", "disrupt", "future"])
engine.register_frame(frame)

# Audit text
report = engine.audit("This new disruption will change the future.")
print(f"Active Frames: {report['frames']}")
```
