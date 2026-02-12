# Epistemic Submodule

**Truth & Verification**

The `codomyrmex.meme.epistemic` submodule deals with knowledge, belief, and truth. It provides a rigorous framework for verifying claims, managing evidence, and detecting contradictions or gaslighting.

## Key Components

### 1. Data Models (`models.py`)

* **`Fact`**: A verified unit of truth with a confidence score.
* **`Belief`**: A held conviction (subjective) with emotional investment.
* **`Evidence`**: Data supporting or refuting a claim.
  * `validity`: Reliability of the source.
  * `weight`: Impact on the claim.
* **`EpistemicState`**: The aggregate collection of known facts and beliefs.

### 2. Truth Verification (`truth.py`)

* **`verify_claim`**: Weighs evidence to produce a `Fact`.
  * Penalizes fabricated evidence.
  * Aggregates conflicting data points.
* **`calculate_certainty`**: Measures the stability of a belief system.

### 3. Epistemic Engine (`engine.py`)

* **`EpistemicEngine`**: Orchestrator.
  * `assess_claim(statement, evidence)`: Processes new information.
  * `detect_contradictions()`: Finds conflicts between beliefs and facts.

## Usage

```python
from codomyrmex.meme.epistemic import EpistemicEngine, Evidence, EvidenceType

engine = EpistemicEngine()
evidence = [
    Evidence(content="Photo", source="Camera", evidence_type=EvidenceType.EMPIRICAL, weight=0.9)
]

fact = engine.assess_claim("Event occured", evidence)
print(f"Confidence: {fact.confidence}")
```
