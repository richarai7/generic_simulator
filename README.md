# Generic Simulator

A flexible, extensible device simulator framework built on SimPy, featuring SQLite-based configuration management and comprehensive event logging.

## Features

- **SimPy-based simulation**: Discrete-event simulation using the powerful SimPy library
- **SQLite configuration**: Store device configurations, topologies, and connections in a structured database
- **Device models**: Extensible device types (sensors, processors, actuators)
- **Output chaining**: Connect devices to create complex data flow topologies
- **Failure simulation**: Configurable random failure probability for each device
- **Event logging**: Real-time JSON logging of all events, state changes, and outputs
- **CLI interface**: Easy-to-use command-line interface for managing and running simulations
- **Extensible design**: Plugin-ready architecture for custom device types and future enhancements

## Installation

### From source

```bash
# Clone the repository
git clone https://github.com/richarai7/generic_simulator.git
cd generic_simulator

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

## Quick Start

### 1. Create example configurations

```bash
# Create example configurations in the database
python examples/create_examples.py
```

This creates three example configurations:
- `simple_chain`: A basic sensor → processor → actuator chain
- `multi_sensor`: Multiple sensors feeding a central processor
- `complex_network`: Complex network with parallel processing paths

### 2. List available configurations

```bash
generic-simulator list
```

### 3. View configuration details

```bash
generic-simulator show --name simple_chain
```

### 4. Run a simulation

```bash
generic-simulator run simple_chain --duration 100
```

The simulation will:
- Create devices according to the configuration
- Run for 100 time units
- Log all events to `logs/simulation_simple_chain.json`
- Display final device states

## Usage

### CLI Commands

```bash
# List all configurations
generic-simulator list

# Show configuration details
generic-simulator show --name <config_name>
generic-simulator show --config-id <id>

# Run a simulation
generic-simulator run <config_name> [--duration <time>]

# Use custom database path
generic-simulator --config-db path/to/database.db list
```

### Database Schema

The simulator uses SQLite with three main tables:

#### Configurations Table
```sql
CREATE TABLE configurations (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP
)
```

#### Devices Table
```sql
CREATE TABLE devices (
    id INTEGER PRIMARY KEY,
    config_id INTEGER,
    device_name TEXT NOT NULL,
    device_type TEXT NOT NULL,
    interval REAL NOT NULL,
    failure_probability REAL DEFAULT 0.0,
    config_json TEXT,
    FOREIGN KEY (config_id) REFERENCES configurations(id)
)
```

#### Connections Table
```sql
CREATE TABLE connections (
    id INTEGER PRIMARY KEY,
    config_id INTEGER,
    source_device TEXT NOT NULL,
    target_device TEXT NOT NULL,
    FOREIGN KEY (config_id) REFERENCES configurations(id)
)
```

### Creating Custom Configurations

```python
from generic_simulator.config_manager import ConfigManager

manager = ConfigManager("configs/simulator.db")

# Create configuration
config_id = manager.create_configuration(
    name="my_config",
    description="My custom configuration"
)

# Add devices
manager.add_device(
    config_id,
    device_name="sensor1",
    device_type="sensor",
    interval=5.0,
    failure_probability=0.05,
    config={"min_value": 0, "max_value": 100, "unit": "celsius"}
)

manager.add_device(
    config_id,
    device_name="processor1",
    device_type="processor",
    interval=10.0,
    failure_probability=0.01
)

# Add connection
manager.add_connection(config_id, "sensor1", "processor1")
```

### Programmatic Usage

```python
from generic_simulator import Simulator, ConfigManager

# Load configuration
manager = ConfigManager("configs/simulator.db")
config = manager.get_configuration_by_name("simple_chain")

# Create and run simulator
simulator = Simulator(config, log_file="logs/my_simulation.json")
simulator.run(until=100.0)

# Check device states
states = simulator.get_device_states()
print(states)
```

## Device Types

### Sensor
Generates periodic readings with configurable ranges:
- `min_value`: Minimum sensor value
- `max_value`: Maximum sensor value
- `unit`: Measurement unit

### Processor
Processes inputs from connected devices:
- Buffers incoming data
- Processes on each interval
- Outputs aggregated results

### Actuator
Performs actions based on inputs:
- `action_type`: Type of action to perform
- Tracks number of actions performed

## Event Logging

All simulation events are logged to JSON files with the following structure:

```json
{
  "simulation_log": [
    {
      "timestamp": 0,
      "device": "temperature_sensor",
      "event_type": "started",
      "state": "running",
      "data": {},
      "real_timestamp": "2024-01-30T10:30:00.123456"
    },
    {
      "timestamp": 5.0,
      "device": "temperature_sensor",
      "event_type": "processed",
      "state": "running",
      "data": {
        "output": {
          "type": "sensor_reading",
          "value": 23.45,
          "unit": "celsius"
        }
      },
      "real_timestamp": "2024-01-30T10:30:05.234567"
    }
  ],
  "event_count": 125,
  "generated_at": "2024-01-30T10:32:30.123456"
}
```

## Extending the Simulator

### Adding Custom Device Types

```python
from generic_simulator.device import Device

class CustomDevice(Device):
    def process_logic(self):
        # Implement custom logic
        return {"type": "custom_output", "data": "custom_data"}

# Register the device type
from generic_simulator.device import DEVICE_TYPES
DEVICE_TYPES["custom"] = CustomDevice
```

### Future Extensions

The architecture supports:
- **Plugin system**: Load custom device types dynamically
- **Web API**: REST API for simulation control
- **Real-time dashboard**: Web-based monitoring interface
- **Digital twin integration**: Connect to real-world IoT devices
- **Distributed simulation**: Run simulations across multiple nodes
- **Advanced analytics**: Built-in analysis and visualization tools

## Architecture

```
generic_simulator/
├── src/generic_simulator/
│   ├── __init__.py          # Package initialization
│   ├── config_manager.py    # SQLite configuration management
│   ├── device.py            # Device base class and implementations
│   ├── simulator.py         # Main simulation engine
│   ├── event_logger.py      # JSON event logging
│   └── cli.py               # Command-line interface
├── examples/
│   └── create_examples.py   # Example configuration generator
├── tests/                   # Test suite
├── configs/                 # SQLite databases
├── logs/                    # Simulation logs (generated)
├── setup.py                 # Package setup
└── requirements.txt         # Dependencies
```

## Requirements

- Python 3.8+
- SimPy 4.0.1+

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## Support

For questions and support, please open an issue on the GitHub repository.
