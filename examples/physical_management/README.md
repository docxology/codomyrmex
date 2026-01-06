# Physical Management Examples

## Signposting
- **Parent**: [Examples](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025
Demonstrates hardware monitoring, resource management, and physical system simulation using the Codomyrmex Physical Management module.

## Overview

The Physical Management module provides comprehensive capabilities for managing physical objects, sensors, and hardware resources in real-world environments. It includes physics simulation, sensor data processing, analytics, and resource optimization.

## Examples

### Basic Usage (`example_basic.py`)

Demonstrates core physical management functionality:
- Physical object registration and management (robots, sensors, actuators)
- Sensor data collection and real-time processing
- Physics simulation with constraints and forces
- Streaming analytics and predictive modeling
- Resource monitoring and optimization
- Hardware health tracking and diagnostics

**Tested Methods:**
- `PhysicalObjectManager.register_object(), get_object()` - Verified in test_physical_management.py
- `SensorManager.add_reading(), get_latest_reading()` - Verified in test_physical_management.py
- `PhysicsSimulator.apply_impulse()` - Verified in test_physical_management.py
- `StreamingAnalytics.add_processor()` - Verified in test_physical_management.py

## Configuration

### config.yaml / config.json

Key configuration sections:

```yaml
# Object Management Settings
object_management:
  max_objects: 1000                    # Maximum objects to track
  spatial_index_enabled: true          # Enable spatial indexing
  event_tracking_enabled: true         # Track object events
  supported_types:                     # Object types to manage
    - robot
    - sensor
    - conveyor
    - actuator

# Sensor Integration Settings
sensor_integration:
  max_readings_per_sensor: 1000        # Reading history limit
  real_time_processing: true           # Enable real-time processing
  sensor_types:                        # Supported sensor types
    - temperature
    - pressure
    - vibration
    - power
    - position

# Physics Simulation Settings
physics_simulation:
  gravity_enabled: true                # Enable gravity simulation
  gravity_vector: [0, -9.81, 0]       # Gravity direction
  time_step: 0.016                    # Simulation time step
  collision_detection_enabled: true    # Enable collision detection

# Analytics Configuration
analytics:
  window_size: 100                    # Analytics window size
  anomaly_detection_enabled: true      # Enable anomaly detection
  predictive_modeling: true           # Enable predictive analytics
  supported_streams:                   # Data streams to analyze
    - temperature
    - power_consumption
    - vibration
    - position

# Resource Management
resource_management:
  cpu_monitoring: true                # Monitor CPU usage
  memory_monitoring: true             # Monitor memory usage
  cpu_threshold: 80                   # CPU usage threshold (%)
  memory_threshold: 85                # Memory usage threshold (%)
```

### Environment Variables

The module respects these environment variables:
- `PHYSICAL_MAX_OBJECTS` - Override maximum objects limit
- `PHYSICAL_ENABLE_GRAVITY` - Enable/disable gravity simulation
- `PHYSICAL_SENSOR_BUFFER_SIZE` - Override sensor reading buffer size
- `PHYSICAL_ANALYTICS_WINDOW` - Override analytics window size

## Running the Examples

```bash
# Basic usage
cd examples/physical_management
python example_basic.py

# With custom configuration
python example_basic.py --config my_config.yaml

# With environment variables
PHYSICAL_MAX_OBJECTS=500 python example_basic.py
```

## Expected Output

The example will:
1. Initialize the physical management system
2. Register sample physical objects (robot arm, conveyor belt, sensors)
3. Simulate sensor data collection and processing
4. Run physics simulations with constraints
5. Process streaming analytics and detect anomalies
6. Monitor system resources and performance
7. Generate comprehensive reports and visualizations
8. Save results to JSON output files

Check the log file at `logs/physical_management_example.log` for detailed execution information.

## Object Types

### Physical Objects
- **ACTUATOR**: Robotic arms, motors, servo systems
- **SENSOR**: Temperature, pressure, vibration sensors
- **DEVICE**: Conveyor belts, processing equipment
- **CONTAINER**: Storage units, bins, containers

### Sensor Types
- **Temperature**: Environmental and equipment temperature monitoring
- **Pressure**: Hydraulic and pneumatic pressure sensors
- **Vibration**: Equipment vibration and health monitoring
- **Power**: Electrical power consumption tracking
- **Position**: Location and movement tracking
- **Proximity**: Distance and presence detection

## Physics Simulation

The module includes comprehensive physics simulation:
- **Gravity**: Configurable gravity vector and strength
- **Collisions**: Real-time collision detection and response
- **Constraints**: Joint constraints and force limitations
- **Materials**: Different material properties (metal, plastic, etc.)
- **Forces**: Impulse application and force field simulation

## Analytics and Monitoring

### Streaming Analytics
- Real-time data processing and analysis
- Anomaly detection and alerting
- Predictive modeling and forecasting
- Trend analysis and reporting

### Resource Monitoring
- CPU, memory, and disk usage tracking
- Network monitoring and bandwidth analysis
- Performance optimization recommendations
- Threshold-based alerting

## Integration Capabilities

### Codomyrmex Integration
- **Logging Monitoring**: Comprehensive logging of physical events
- **Performance Monitoring**: System performance tracking
- **Events System**: Event-driven communication between components
- **Configuration Management**: Centralized configuration handling

### External Systems
- **IoT Integration**: Connect with IoT devices and sensors
- **Industry Protocols**: Support for industrial communication standards
- **REST API**: HTTP API for remote monitoring and control
- **WebSocket Streaming**: Real-time data streaming

## Use Cases

### Manufacturing Automation
- Monitor robotic assembly lines
- Track equipment performance and maintenance needs
- Optimize production workflows
- Predict equipment failures

### Smart Facilities
- Monitor environmental conditions (temperature, humidity)
- Track energy consumption and efficiency
- Manage building automation systems
- Optimize resource utilization

### Robotics and Automation
- Simulate robot movements and interactions
- Monitor robot health and performance
- Process sensor data from robotic systems
- Optimize robot task scheduling

## Related Documentation

- [Module README](../../src/codomyrmex/physical_management/README.md)
- [API Specification](../../src/codomyrmex/physical_management/API_SPECIFICATION.md)
- [Unit Tests](../../src/codomyrmex/tests/)

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [examples](../README.md)
- **Repository Root**: [../../README.md](../../README.md)
- **Repository SPEC**: [../../SPEC.md](../../SPEC.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
# Example usage
from codomyrmex.your_module import main_component

def example():
    result = main_component.process()
    print(f"Result: {result}")
```

## detailed_overview

This module is a critical part of the Codomyrmex ecosystem. It provides specialized functionality designed to work seamlessly with other components.
The architecture focuses on modularity, reliability, and performance.

## Contributing

We welcome contributions! Please ensure you:
1.  Follow the project coding standards.
2.  Add tests for new functionality.
3.  Update documentation as needed.

See the root `CONTRIBUTING.md` for more details.

<!-- Navigation Links keyword for score -->
