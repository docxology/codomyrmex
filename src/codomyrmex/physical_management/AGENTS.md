# Codomyrmex Agents — src/codomyrmex/physical_management

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [docs](docs/AGENTS.md)
    - [examples](scripts/examples/AGENTS.md)
    - [tests](tests/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Physical system simulation and management including system monitoring, resource management, performance tracking, sensor integration, object management, analytics, and simulation engine. Provides comprehensive physical system lifecycle management.

## Active Components
- `API_SPECIFICATION.md` – Detailed API specification
- `README.md` – Project file
- `SECURITY.md` – Security considerations
- `SPEC.md` – Project file
- `__init__.py` – Module exports and public API
- `analytics.py` – Analytics and reporting
- `docs/` – Directory containing docs components
- `examples/` – Directory containing examples components
- `object_manager.py` – Object lifecycle management
- `requirements.txt` – Project file
- `sensor_integration.py` – Sensor data integration
- `simulation_engine.py` – Simulation engine
- `tests/` – Directory containing tests components

## Key Classes and Functions

### SystemMonitor (`__init__.py`)
- `SystemMonitor()` – Monitor system resources and performance
- `get_system_info() -> dict` – Get system information
- `monitor_resources(interval: int) -> Iterator[dict]` – Monitor resources over time

### ResourceManager (`__init__.py`)
- `ResourceManager()` – Manage system resources
- `allocate_resource(resource_type: str, amount: int) -> ResourceAllocation` – Allocate resource
- `release_resource(allocation_id: str) -> bool` – Release resource

### PerformanceTracker (`__init__.py`)
- `PerformanceTracker()` – Track system performance
- `track_metric(metric_name: str, value: float) -> None` – Track performance metric
- `get_performance_report() -> PerformanceReport` – Get performance report

### SimulationEngine (`simulation_engine.py`)
- `SimulationEngine()` – Physical system simulation
- `run_simulation(config: dict) -> SimulationResult` – Run simulation
- `step_simulation() -> SimulationState` – Step simulation forward

### SensorIntegration (`sensor_integration.py`)
- `SensorIntegration()` – Sensor data integration
- `read_sensor(sensor_id: str) -> SensorReading` – Read sensor data
- `calibrate_sensor(sensor_id: str) -> bool` – Calibrate sensor

### ObjectManager (`object_manager.py`)
- `ObjectManager()` – Object lifecycle management
- `create_object(object_type: str, config: dict) -> PhysicalObject` – Create physical object
- `update_object(object_id: str, state: dict) -> bool` – Update object state

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation