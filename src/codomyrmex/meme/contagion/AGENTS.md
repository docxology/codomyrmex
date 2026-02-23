# Agents Guide: Contagion

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Operational Directives**

Use the `contagion` submodule to model the spread of information and detect viral events.

## Capabilities

1. **Simulation**:
    * Use `SIRModel` to predict the trajectory of a new meme. Estimate when "herd immunity" (saturation) will be reached.
    * Use `SEIRModel` for complex, high-effort memes that require "incubation" time before re-transmission.

2. **Detection**:
    * Monitor social feeds for rapid spikes in keyword usage.
    * Use `CascadeDetector` to classify events. `CascadeType.MANUFACTURED` indicates bot activity or coordinated campaigns; `CascadeType.VIRAL` suggests organic spread.

## Constraints

* **Parameter Sensitivity**: Small changes in `infection_rate` (beta) can drastically alter outcomes. Always run sensitivity analyses.
* **Network Topology**: Real social networks are not perfectly mixed (mean-field). Use `rhizome` for more accurate network-based simulations.

## Integration

* **With Swarm**: Use `contagion` dynamics to set parameters for swarm behavior (e.g., panic thresholds).
* **With Cultural Dynamics**: Use cascade data to feed `cultural_dynamics.Zeitgeist` tracking.
