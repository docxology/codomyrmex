# Contagion Submodule

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Epidemiological Models of Information**

The `codomyrmex.meme.contagion` submodule provides tools for simulating and analyzing the spread of information using epidemiological models. It treats memes as infectious agents and populations as susceptible hosts.

## Key Components

### 1. Data Models (`models.py`)

* **`ContagionModel`**: Base class for epidemiological simulations.
  * `infection_rate`: Probability of transmission (beta).
  * `recovery_rate`: Probability of recovery/immunity (gamma).
* **`Cascade`**: Represents a specific viral event.
  * `size`: Number of infected nodes.
  * `velocity`: Rate of spread.
  * `cascade_type`: Viral, Organic, Manufactured, Dampened.
* **`PropagationTrace`**: Detailed log of a simulation run.

### 2. Epidemic Models (`epidemic.py`)

* **`SIRModel`**: Susceptible-Infected-Recovered. Classic model for immunity-conferring ideas.
* **`SISModel`**: Susceptible-Infected-Susceptible. For recurring trends or endemic ideas.
* **`SEIRModel`**: Adds an "Exposed" latent period. For complex ideas requiring incubation.

### 3. Cascade Detection (`cascade.py`)

* **`CascadeDetector`**: Identifies viral outbreaks in real-time event streams.
  * `detect(events)`: Returns a list of `Cascade` objects.

### 4. Simulation (`simulation.py`)

* **`run_simulation(model_type, params)`**: Wrapper to execute a contagion simulation.

## Usage

```python
from codomyrmex.meme.contagion import SIRModel, ContagionModel

# Configure model
config = ContagionModel(infection_rate=0.5, recovery_rate=0.1)
model = SIRModel(config)

# Run simulation
trace = model.simulate(steps=100)

print(f"Peak Infections: {trace.peak_infected()}")
```
