# Quick Start Guide

Get up and running with the Generic Simulator in 5 minutes!

## Installation

```bash
# Clone the repository
git clone https://github.com/richarai7/generic_simulator.git
cd generic_simulator

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

## 5-Minute Tutorial

### Step 1: Create Example Configurations (30 seconds)

```bash
python examples/create_examples.py
```

This creates three example configurations in `configs/simulator.db`:
- `simple_chain`: Basic sensor → processor → actuator
- `multi_sensor`: Multiple sensors feeding one processor
- `complex_network`: Complex topology with parallel paths

### Step 2: List Configurations (10 seconds)

```bash
generic-simulator list
```

You should see:
```
Available configurations in configs/simulator.db:
--------------------------------------------------------------------------------
ID: 1
  Name: simple_chain
  Description: A simple chain of sensor -> processor -> actuator
  Created: 2024-01-30 10:30:00
...
```

### Step 3: View Configuration Details (10 seconds)

```bash
generic-simulator show --name simple_chain
```

This displays all devices and their connections.

### Step 4: Run Your First Simulation (30 seconds)

```bash
generic-simulator run simple_chain --duration 100
```

Output:
```
Running configuration: simple_chain
Duration: 100.0 time units

Starting simulation: simple_chain
Devices: 3
Running until time: 100.0
Simulation completed at time: 100.0
Events logged: 71
Logs saved to: logs/simulation_simple_chain.json

Device Final States:
--------------------------------------------------------------------------------
  data_processor: running
  hvac_actuator: running
  temperature_sensor: running
```

### Step 5: Examine the Results (1 minute)

```bash
# View the first few events
head -n 50 logs/simulation_simple_chain.json

# Count events by type
python -c "
import json
data = json.load(open('logs/simulation_simple_chain.json'))
events = data['simulation_log']
types = {}
for e in events:
    t = e.get('event_type', 'unknown')
    types[t] = types.get(t, 0) + 1
for t, c in sorted(types.items()):
    print(f'{t}: {c}')
"
```

## What's Next?

### Try Different Configurations

```bash
# Run the multi-sensor configuration
generic-simulator run multi_sensor --duration 100

# Run the complex network
generic-simulator run complex_network --duration 150
```

### Create Your Own Configuration

Create a Python script:

```python
from generic_simulator.config_manager import ConfigManager

# Initialize manager
manager = ConfigManager("configs/simulator.db")

# Create new configuration
config_id = manager.create_configuration(
    name="my_first_config",
    description="My first custom configuration"
)

# Add a sensor
manager.add_device(
    config_id,
    device_name="my_sensor",
    device_type="sensor",
    interval=5.0,
    failure_probability=0.01,
    config={"min_value": 0, "max_value": 100, "unit": "units"}
)

# Add a processor
manager.add_device(
    config_id,
    device_name="my_processor",
    device_type="processor",
    interval=10.0,
    failure_probability=0.01
)

# Connect them
manager.add_connection(config_id, "my_sensor", "my_processor")

print("Configuration created! Run with:")
print("generic-simulator run my_first_config --duration 100")
```

### Analyze Simulation Results

```python
import json

# Load simulation log
with open("logs/simulation_simple_chain.json") as f:
    data = json.load(f)

events = data["simulation_log"]

# Find all sensor readings
sensor_data = [
    e for e in events 
    if e.get("device") == "temperature_sensor" 
    and e.get("event_type") == "processed"
]

print(f"Total sensor readings: {len(sensor_data)}")

# Check for failures
failures = [e for e in events if e.get("event_type") == "failed"]
if failures:
    print(f"Failures detected: {len(failures)}")
    for f in failures:
        print(f"  - {f['device']} failed at time {f['timestamp']}")
else:
    print("No failures during simulation")
```

### Run Tests

```bash
# Run all tests
python -m unittest discover tests -v

# Run specific test file
python -m unittest tests.test_device -v
```

## Common Commands

```bash
# List all configurations
generic-simulator list

# Show configuration details
generic-simulator show --name <config_name>
generic-simulator show --config-id <id>

# Run simulation
generic-simulator run <config_name> --duration <seconds>

# Use different database
generic-simulator --config-db my_configs.db list
```

## Directory Structure

```
generic_simulator/
├── configs/              # SQLite databases
├── logs/                # Simulation output logs
├── examples/            # Example scripts
├── docs/               # Documentation
├── src/                # Source code
│   └── generic_simulator/
├── tests/              # Test suite
├── README.md           # Main documentation
└── requirements.txt    # Dependencies
```

## Key Concepts

**Configuration**: A named simulation setup with devices and connections

**Device**: A simulated component that processes at regular intervals
- **Sensor**: Generates data
- **Processor**: Processes inputs
- **Actuator**: Performs actions

**Connection**: Output link from one device to another

**Event**: A logged occurrence (start, process, input, output, failure)

**Interval**: How often a device processes (in simulation time units)

**Failure Probability**: Chance of device failing on each cycle (0.0-1.0)

## Troubleshooting

**Problem**: `generic-simulator` command not found

**Solution**: Make sure you installed with `pip install -e .` and your PATH includes pip's bin directory

---

**Problem**: Database file not found

**Solution**: Run `python examples/create_examples.py` first to create the database

---

**Problem**: Import errors

**Solution**: Make sure you're running from the project root or have installed the package

---

## Learn More

- [README.md](../README.md) - Full documentation
- [ARCHITECTURE.md](../docs/ARCHITECTURE.md) - System architecture
- [USAGE.md](../docs/USAGE.md) - Detailed usage examples
- [SCHEMA.md](../docs/SCHEMA.md) - Database schema reference

## Getting Help

- Check the documentation in the `docs/` directory
- Review example configurations in `examples/`
- Look at the test files in `tests/` for code examples
- Open an issue on GitHub

Happy simulating! 🚀
