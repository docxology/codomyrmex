# Semiotics Submodule

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**The Science of Meaning**

The `codomyrmex.meme.semiotic` submodule deals with signs, signifiers, and the construction of meaning. It ensures that memes are not just strings of text, but carriers of semantic value.

## Key Components

### 1. Data Models (`models.py`)

* **`Sign`**: Represents the dyadic (Saussure) or triadic (Peirce) unit of meaning.
  * `signifier`: The form (word, image).
  * `signified`: The concept it represents.
* **`SignType`**: Classification (Icon, Index, Symbol).
* **`SemanticTerritory`**: A mapped space of related concepts.
* **`DriftReport`**: Analysis of how a sign's meaning has shifted.

### 2. Analysis (`analyzer.py`)

* **`SemioticAnalyzer`**: Tools for decoding signs.
  * `decode(signifier)`: Retrieves the signified concept.
  * `measure_drift(sign, corpus_a, corpus_b)`: Quantifies meaning shift.

### 3. Encoding (`encoding.py`)

* **`SemioticEncoder`**: Steganography and encoding.
  * `encode(payload, cover_text)`: Hides a message within a larger text using synonym substitution or structural mapping.
  * `decode(stego_text)`: Retrieves the hidden payload.

### 4. Mnemonics (`mnemonics.py`)

* **`build_memory_palace(items)`**: Constructs a "Method of Loci" structure to aid retention of information.

## Usage

```python
from codomyrmex.meme.semiotic import SemioticAnalyzer, Sign

analyzer = SemioticAnalyzer()
sign = Sign(signifier="Apple", signified="Technology Company")

# Check meaning in different contexts
drift = analyzer.measure_drift(sign, corpus_tech, corpus_fruit)
print(f"Distance: {drift.distance}")
```
