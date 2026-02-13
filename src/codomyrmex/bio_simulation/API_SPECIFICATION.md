# Bio-Simulation - API Specification

## Introduction

This document specifies the Application Programming Interface (API) for the Bio-Simulation module. The primary purpose of this API is to provide a high-fidelity biological simulation engine for ant colony behavior, including individual agent modeling, population-level dynamics, and visualization of colony state.

## Endpoints / Functions / Interfaces

### Enum: `AntState`

- **Description**: Enumeration of possible states for a simulated ant agent.
- **Module**: `codomyrmex.bio_simulation.colony`
- **Values**:
    - `FORAGING` - Ant is searching for food resources
    - `RETURNING` - Ant is returning to the colony
    - `DEFENDING` - Ant is defending the colony
    - `IDLE` - Ant is inactive

### Class: `Ant`

- **Description**: Dataclass representing a single simulated biological agent within the colony. Each ant has a unique identifier, a behavioral state, an energy level, and spatial coordinates.
- **Module**: `codomyrmex.bio_simulation.colony`
- **Parameters/Arguments** (constructor):
    - `id` (int): Unique identifier for the ant
    - `state` (AntState, optional): Current behavioral state. Defaults to `AntState.IDLE`
    - `energy` (float, optional): Energy level of the ant. Defaults to `100.0`
    - `x` (int, optional): X coordinate in the simulation grid. Defaults to `0`
    - `y` (int, optional): Y coordinate in the simulation grid. Defaults to `0`
- **Methods**:
    - `step()`: Perform one simulation step. Decreases energy by 0.1. If the ant is in `FORAGING` state, its position is updated by a random walk (x and y each change by -1, 0, or 1).

### Class: `Colony`

- **Description**: The main simulation environment for an ant colony. Manages a population of `Ant` instances and provides methods to advance the simulation and query colony state.
- **Module**: `codomyrmex.bio_simulation.colony`
- **Parameters/Arguments** (constructor):
    - `population_size` (int): Number of ants to create in the colony
- **Attributes**:
    - `ants` (List[Ant]): List of all ant agents in the colony
    - `tick` (int): Current simulation tick counter, starts at 0
- **Methods**:
    - `step()`: Advance the simulation by one tick. Increments `tick` and calls `step()` on every ant that has energy greater than 0.
    - `get_census() -> dict`: Returns a dictionary mapping each `AntState` to the count of ants currently in that state.

### Function: `render_colony_state(colony: Colony) -> ScatterPlot`

- **Description**: Renders a scatter plot of current ant positions within the colony, using the visualization module's `ScatterPlot` class.
- **Module**: `codomyrmex.bio_simulation.visualization`
- **Parameters/Arguments**:
    - `colony` (Colony): The colony instance to visualize
- **Returns/Response**: `ScatterPlot` - A scatter plot with ant x/y coordinates plotted, titled "Real-time Colony State".

## Data Models

### Ant (dataclass)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `int` | required | Unique agent identifier |
| `state` | `AntState` | `AntState.IDLE` | Current behavioral state |
| `energy` | `float` | `100.0` | Energy level (decreases each step) |
| `x` | `int` | `0` | X position on the grid |
| `y` | `int` | `0` | Y position on the grid |

## Authentication & Authorization

Not applicable for this internal simulation module.

## Rate Limiting

Not applicable for this internal simulation module.

## Versioning

This module follows the general versioning strategy of the Codomyrmex project. API stability is aimed for, with changes documented in the CHANGELOG.md.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
