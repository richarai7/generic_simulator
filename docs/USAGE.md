# Usage Examples

This guide provides practical examples of using the Generic Simulator for various scenarios.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Creating Custom Configurations](#creating-custom-configurations)
3. [Programmatic Usage](#programmatic-usage)
4. [Analyzing Simulation Logs](#analyzing-simulation-logs)
5. [Advanced Scenarios](#advanced-scenarios)

## Basic Usage

### 1. Setting Up Examples

First, create the example configurations:

```bash
python examples/create_examples.py
```

### 2. Listing Available Configurations

```bash
generic-simulator list
```

Output:
```
Available configurations in configs/simulator.db:
--------------------------------------------------------------------------------
ID: 1
  Name: simple_chain
  Description: A simple chain of sensor -> processor -> actuator
  Created: 2024-01-30 10:30:00

ID: 2
  Name: multi_sensor
  Description: Multiple sensors feeding into a central processor
  Created: 2024-01-30 10:30:00
```

### 3. Viewing Configuration Details

```bash
generic-simulator show --name simple_chain
```

Output:
```
Configuration: simple_chain
Description: A simple chain of sensor -> processor -> actuator

Devices (3):
--------------------------------------------------------------------------------
  temperature_sensor (sensor)
    Interval: 5.0s
    Failure Probability: 0.05
    Config: {'min_value': 15.0, 'max_value': 30.0, 'unit': 'celsius'}
  
  data_processor (processor)
    Interval: 10.0s
    Failure Probability: 0.02
  
  hvac_actuator (actuator)
    Interval: 15.0s
    Failure Probability: 0.01
    Config: {'action_type': 'adjust_temperature'}

Connections (2):
--------------------------------------------------------------------------------
  temperature_sensor -> data_processor
  data_processor -> hvac_actuator
```

### 4. Running a Simulation

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

## Creating Custom Configurations

### Example: Smart Home Monitoring System

```python
from generic_simulator.config_manager import ConfigManager

# Initialize configuration manager
manager = ConfigManager("configs/simulator.db")

# Create configuration
config_id = manager.create_configuration(
    name="smart_home",
    description="Smart home monitoring and control system"
)

# Add sensors
manager.add_device(
    config_id,
    device_name="living_room_temp",
    device_type="sensor",
    interval=10.0,
    failure_probability=0.02,
    config={
        "min_value": 18.0,
        "max_value": 28.0,
        "unit": "celsius"
    }
)

manager.add_device(
    config_id,
    device_name="bedroom_temp",
    device_type="sensor",
    interval=10.0,
    failure_probability=0.02,
    config={
        "min_value": 18.0,
        "max_value": 28.0,
        "unit": "celsius"
    }
)

manager.add_device(
    config_id,
    device_name="motion_sensor",
    device_type="sensor",
    interval=5.0,
    failure_probability=0.01,
    config={
        "min_value": 0.0,
        "max_value": 1.0,
        "unit": "boolean"
    }
)

# Add central processor
manager.add_device(
    config_id,
    device_name="home_controller",
    device_type="processor",
    interval=15.0,
    failure_probability=0.01,
    config={}
)

# Add actuators
manager.add_device(
    config_id,
    device_name="hvac_system",
    device_type="actuator",
    interval=20.0,
    failure_probability=0.02,
    config={"action_type": "temperature_control"}
)

manager.add_device(
    config_id,
    device_name="lighting_system",
    device_type="actuator",
    interval=5.0,
    failure_probability=0.01,
    config={"action_type": "light_control"}
)

# Create connections
manager.add_connection(config_id, "living_room_temp", "home_controller")
manager.add_connection(config_id, "bedroom_temp", "home_controller")
manager.add_connection(config_id, "motion_sensor", "home_controller")
manager.add_connection(config_id, "home_controller", "hvac_system")
manager.add_connection(config_id, "home_controller", "lighting_system")

print("Smart home configuration created!")
```

Now run it:

```bash
generic-simulator run smart_home --duration 200
```

## Programmatic Usage

### Example: Running Multiple Simulations

```python
from generic_simulator import Simulator, ConfigManager

# Load configuration
manager = ConfigManager("configs/simulator.db")

# Run multiple durations
for duration in [50, 100, 200]:
    config = manager.get_configuration_by_name("simple_chain")
    
    log_file = f"logs/simulation_{duration}.json"
    simulator = Simulator(config, log_file=log_file)
    simulator.run(until=duration)
    
    # Check for failures
    states = simulator.get_device_states()
    failed_devices = [name for name, state in states.items() if state == "failed"]
    
    if failed_devices:
        print(f"Duration {duration}: {len(failed_devices)} devices failed")
    else:
        print(f"Duration {duration}: All devices operational")
```

### Example: Custom Event Processing

```python
from generic_simulator import Simulator, ConfigManager
import json

# Load and run simulation
manager = ConfigManager("configs/simulator.db")
config = manager.get_configuration_by_name("multi_sensor")

simulator = Simulator(config, log_file="logs/custom_analysis.json")
simulator.run(until=100)

# Analyze events
with open("logs/custom_analysis.json", 'r') as f:
    log_data = json.load(f)

events = log_data["simulation_log"]

# Count events by type
event_counts = {}
for event in events:
    event_type = event.get("event_type", "unknown")
    event_counts[event_type] = event_counts.get(event_type, 0) + 1

print("Event Statistics:")
for event_type, count in sorted(event_counts.items()):
    print(f"  {event_type}: {count}")

# Find all failures
failures = [e for e in events if e.get("event_type") == "failed"]
if failures:
    print(f"\nFailures detected: {len(failures)}")
    for failure in failures:
        print(f"  Device: {failure['device']}, Time: {failure['timestamp']}")
```

## Analyzing Simulation Logs

### Example: Processing Sensor Data

```python
import json

# Load simulation log
with open("logs/simulation_simple_chain.json", 'r') as f:
    log_data = json.load(f)

events = log_data["simulation_log"]

# Extract sensor readings
sensor_readings = []
for event in events:
    if (event.get("device") == "temperature_sensor" and 
        event.get("event_type") == "processed" and
        event.get("data", {}).get("output")):
        
        output = event["data"]["output"]
        sensor_readings.append({
            "time": event["timestamp"],
            "value": output.get("value"),
            "unit": output.get("unit")
        })

# Calculate statistics
if sensor_readings:
    values = [r["value"] for r in sensor_readings]
    print(f"Sensor Statistics:")
    print(f"  Readings: {len(values)}")
    print(f"  Min: {min(values):.2f}")
    print(f"  Max: {max(values):.2f}")
    print(f"  Average: {sum(values)/len(values):.2f}")
```

### Example: Device Uptime Analysis

```python
import json

def calculate_uptime(log_file, device_name):
    """Calculate device uptime from simulation log."""
    with open(log_file, 'r') as f:
        log_data = json.load(f)
    
    events = log_data["simulation_log"]
    
    start_time = None
    fail_time = None
    
    for event in events:
        if event.get("device") == device_name:
            if event.get("event_type") == "started":
                start_time = event["timestamp"]
            elif event.get("event_type") == "failed":
                fail_time = event["timestamp"]
                break
    
    # Get simulation end time
    sim_end = events[-1]["timestamp"]
    
    if start_time is not None:
        if fail_time is not None:
            uptime = fail_time - start_time
            uptime_pct = (uptime / sim_end) * 100
            return uptime, uptime_pct, "failed"
        else:
            uptime = sim_end - start_time
            uptime_pct = (uptime / sim_end) * 100
            return uptime, uptime_pct, "operational"
    
    return 0, 0, "unknown"

# Analyze all devices
log_file = "logs/simulation_multi_sensor.json"
devices = ["sensor_1", "sensor_2", "sensor_3", "central_processor", 
           "actuator_1", "actuator_2"]

print("Device Uptime Analysis:")
print("-" * 60)
for device in devices:
    uptime, pct, status = calculate_uptime(log_file, device)
    print(f"{device:20s}: {uptime:6.1f}s ({pct:5.1f}%) - {status}")
```

## Advanced Scenarios

### Example: Parallel Simulation Execution

```python
from concurrent.futures import ProcessPoolExecutor
from generic_simulator import ConfigManager
from generic_simulator.simulator import run_simulation

def run_config(config_name, duration):
    """Run a single simulation configuration."""
    try:
        simulator = run_simulation(
            "configs/simulator.db",
            config_name,
            duration
        )
        states = simulator.get_device_states()
        failed = sum(1 for s in states.values() if s == "failed")
        return config_name, True, failed
    except Exception as e:
        return config_name, False, str(e)

# Run multiple configurations in parallel
configs = ["simple_chain", "multi_sensor", "complex_network"]
duration = 100

with ProcessPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(run_config, cfg, duration) for cfg in configs]
    
    print("Running simulations in parallel...")
    for future in futures:
        config_name, success, result = future.result()
        if success:
            print(f"  {config_name}: Completed ({result} failures)")
        else:
            print(f"  {config_name}: Error - {result}")
```

### Example: Monte Carlo Failure Analysis

```python
from generic_simulator import Simulator, ConfigManager
import statistics

def run_monte_carlo(config_name, num_runs=100, duration=100):
    """Run Monte Carlo simulation to analyze failure rates."""
    manager = ConfigManager("configs/simulator.db")
    config = manager.get_configuration_by_name(config_name)
    
    failure_counts = []
    
    for i in range(num_runs):
        log_file = f"/tmp/mc_simulation_{i}.json"
        simulator = Simulator(config, log_file=log_file)
        simulator.run(until=duration)
        
        states = simulator.get_device_states()
        failures = sum(1 for s in states.values() if s == "failed")
        failure_counts.append(failures)
    
    # Calculate statistics
    mean_failures = statistics.mean(failure_counts)
    std_failures = statistics.stdev(failure_counts)
    max_failures = max(failure_counts)
    
    print(f"Monte Carlo Analysis ({num_runs} runs):")
    print(f"  Mean failures: {mean_failures:.2f}")
    print(f"  Std deviation: {std_failures:.2f}")
    print(f"  Max failures: {max_failures}")
    print(f"  Failure rate: {(mean_failures/len(config['devices']))*100:.1f}%")

# Run analysis
run_monte_carlo("multi_sensor", num_runs=50, duration=200)
```

### Example: Custom Device Type

```python
from generic_simulator.device import Device, DEVICE_TYPES
import random

class WeatherStation(Device):
    """Custom weather station device."""
    
    def process_logic(self):
        """Generate weather data."""
        return {
            "type": "weather_data",
            "temperature": random.uniform(15, 35),
            "humidity": random.uniform(30, 90),
            "pressure": random.uniform(980, 1030),
            "wind_speed": random.uniform(0, 50)
        }

# Register custom device type
DEVICE_TYPES["weather_station"] = WeatherStation

# Now create a configuration using it
manager = ConfigManager("configs/simulator.db")
config_id = manager.create_configuration(
    "weather_network",
    "Weather monitoring network"
)

manager.add_device(
    config_id,
    device_name="station_1",
    device_type="weather_station",
    interval=30.0,
    failure_probability=0.03
)

manager.add_device(
    config_id,
    device_name="data_aggregator",
    device_type="processor",
    interval=60.0
)

manager.add_connection(config_id, "station_1", "data_aggregator")

# Run simulation
from generic_simulator.simulator import run_simulation
run_simulation("configs/simulator.db", "weather_network", 300)
```

## Tips and Best Practices

1. **Start Small**: Begin with simple configurations and gradually add complexity
2. **Monitor Failures**: Set realistic failure probabilities based on real-world data
3. **Analyze Logs**: Use the JSON logs for downstream analysis and visualization
4. **Batch Simulations**: Run multiple scenarios to understand system behavior
5. **Custom Devices**: Extend device types to model specific domain behaviors
6. **Validation**: Verify simulation results match expected behavior before scaling
7. **Performance**: For large simulations, consider increasing device intervals or reducing duration
8. **Logging**: Clean up old log files periodically to save disk space

## Troubleshooting

### Problem: Simulation runs too slowly

**Solution**: 
- Increase device intervals
- Reduce failure probability checks
- Use fewer devices in the configuration

### Problem: Too many log files

**Solution**:
```python
# Specify custom log location
simulator = Simulator(config, log_file="/tmp/simulation.json")
```

### Problem: Database locked

**Solution**:
- Ensure only one process modifies the database at a time
- Close database connections properly
- Use separate databases for parallel simulations

## Next Steps

- Explore the [Architecture Documentation](../docs/ARCHITECTURE.md)
- Review the source code for deeper understanding
- Create custom device types for your domain
- Build analysis tools using the JSON logs
- Contribute to the project!
