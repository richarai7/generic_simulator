# Generic Simulator Architecture

## Overview

The Generic Simulator is a flexible, extensible discrete-event simulation framework built on SimPy, designed to model interconnected devices with configurable behavior and failure characteristics. The system uses SQLite for configuration management and provides comprehensive JSON logging for downstream analysis.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLI Interface                            │
│                    (generic_simulator.cli)                       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Configuration Manager                         │
│                (generic_simulator.config_manager)                │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              SQLite Database Schema                       │  │
│  │  ┌────────────────┐  ┌──────────────┐  ┌─────────────┐  │  │
│  │  │ configurations │  │   devices    │  │ connections │  │  │
│  │  └────────────────┘  └──────────────┘  └─────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Simulator Engine                            │
│                   (generic_simulator.simulator)                  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │               SimPy Environment                           │  │
│  │                                                            │  │
│  │    ┌────────┐    ┌────────┐    ┌────────┐               │  │
│  │    │Device 1│───▶│Device 2│───▶│Device 3│               │  │
│  │    └────────┘    └────────┘    └────────┘               │  │
│  │         │                           │                     │  │
│  │         └───────────────┬───────────┘                     │  │
│  │                         ▼                                 │  │
│  │                    ┌────────┐                             │  │
│  │                    │Device 4│                             │  │
│  │                    └────────┘                             │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Event Logger                                │
│                 (generic_simulator.event_logger)                 │
│                                                                   │
│                    JSON Log File Output                          │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Configuration Manager (`config_manager.py`)

**Responsibility**: Manage simulation configurations in SQLite database

**Key Features**:
- Database schema initialization
- CRUD operations for configurations, devices, and connections
- JSON serialization of device-specific configs
- Configuration retrieval by ID or name

**Database Schema**:

```sql
-- Configurations table
CREATE TABLE configurations (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Devices table
CREATE TABLE devices (
    id INTEGER PRIMARY KEY,
    config_id INTEGER NOT NULL,
    device_name TEXT NOT NULL,
    device_type TEXT NOT NULL,
    interval REAL NOT NULL,
    failure_probability REAL DEFAULT 0.0,
    config_json TEXT,
    FOREIGN KEY (config_id) REFERENCES configurations(id),
    UNIQUE(config_id, device_name)
);

-- Connections table (for output chaining)
CREATE TABLE connections (
    id INTEGER PRIMARY KEY,
    config_id INTEGER NOT NULL,
    source_device TEXT NOT NULL,
    target_device TEXT NOT NULL,
    FOREIGN KEY (config_id) REFERENCES configurations(id)
);
```

### 2. Device Models (`device.py`)

**Responsibility**: Define device behavior and lifecycle

**Class Hierarchy**:

```
Device (Abstract Base Class)
│
├── SensorDevice (generates readings)
├── ProcessorDevice (processes inputs)
└── ActuatorDevice (performs actions)
```

**Device Lifecycle**:

1. **Initialization**: Create device with config parameters
2. **Start**: Begin SimPy process, log start event
3. **Process Loop**:
   - Check for random failure
   - Execute device-specific logic
   - Log processing event
   - Send output to connected devices
   - Wait for next interval
4. **Termination**: Handle failures or interrupts

**Key Features**:
- Random failure simulation based on probability
- Output chaining to multiple devices
- Input buffering (for processors)
- Event logging for all state changes

### 3. Simulator Engine (`simulator.py`)

**Responsibility**: Orchestrate simulation execution

**Workflow**:

1. **Initialization**:
   - Create SimPy environment
   - Instantiate all devices from config
   - Set up connections between devices
   - Initialize event logger

2. **Execution**:
   - Start all device processes
   - Run simulation until specified time
   - Monitor device states

3. **Completion**:
   - Collect final device states
   - Save event log to JSON file
   - Report statistics

**Key Features**:
- Automatic device creation from config
- Connection topology setup
- Event aggregation and logging
- Post-simulation reporting

### 4. Event Logger (`event_logger.py`)

**Responsibility**: Capture and persist simulation events

**Event Structure**:

```json
{
  "timestamp": 10.5,           // Simulation time
  "device": "sensor_1",        // Device name
  "event_type": "processed",   // Event type
  "state": "running",          // Device state
  "data": {                    // Event-specific data
    "output": {
      "type": "sensor_reading",
      "value": 23.45
    }
  },
  "real_timestamp": "2024-01-30T10:30:15.123456"
}
```

**Event Types**:
- `simulation_start`: Simulation begins
- `simulation_end`: Simulation completes
- `started`: Device starts running
- `processed`: Device completes processing cycle
- `received_input`: Device receives input from another device
- `failed`: Device fails
- `interrupted`: Device interrupted

### 5. CLI Interface (`cli.py`)

**Responsibility**: Provide command-line access to simulator

**Commands**:

```bash
# List configurations
generic-simulator list

# Show configuration details
generic-simulator show --name <name>

# Run simulation
generic-simulator run <name> --duration <time>
```

## Data Flow

### Typical Simulation Flow

```
1. User runs CLI command
   └─> CLI parses arguments
   
2. ConfigManager loads configuration
   └─> Queries SQLite database
   └─> Returns config dictionary
   
3. Simulator initializes
   └─> Creates SimPy environment
   └─> Instantiates devices using factory
   └─> Sets up connections
   └─> Initializes event logger
   
4. Simulation runs
   └─> Each device runs as SimPy process
   └─> Devices process at their intervals
   └─> Outputs chain to connected devices
   └─> Random failures occur
   └─> All events logged
   
5. Simulation completes
   └─> Event log saved to JSON
   └─> Final states reported
   └─> Statistics displayed
```

### Device Communication Flow

```
Sensor (interval=5s)
  │
  ├─> Generates reading at t=0, 5, 10, 15...
  │
  └─> Sends output to Processor
      │
      └─> Processor receives input
          │
          ├─> Buffers input
          │
          └─> Processes at t=0, 10, 20, 30...
              │
              └─> Sends aggregated output to Actuator
                  │
                  └─> Actuator receives input
                      │
                      └─> Performs action at t=0, 15, 30...
```

## Extensibility Points

### 1. Custom Device Types

```python
from generic_simulator.device import Device, DEVICE_TYPES

class CustomDevice(Device):
    def process_logic(self):
        # Implement custom logic
        return {"custom": "output"}

# Register device type
DEVICE_TYPES["custom"] = CustomDevice
```

### 2. Plugin System (Future)

```python
# Plugin interface
class SimulatorPlugin:
    def on_simulation_start(self, simulator):
        pass
    
    def on_device_event(self, event):
        pass
    
    def on_simulation_end(self, simulator):
        pass
```

### 3. Web API (Future)

```
GET  /api/configurations          - List configurations
GET  /api/configurations/:id      - Get configuration
POST /api/configurations          - Create configuration
POST /api/simulations             - Start simulation
GET  /api/simulations/:id         - Get simulation status
GET  /api/simulations/:id/events  - Get simulation events
```

### 4. Digital Twin Integration (Future)

```python
class DigitalTwinDevice(Device):
    def __init__(self, *args, iot_endpoint=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.iot_endpoint = iot_endpoint
    
    def process_logic(self):
        # Fetch real-time data from IoT device
        real_data = self.fetch_from_iot()
        # Process and return
        return real_data
```

## Performance Considerations

### Scalability

- **Device Count**: SimPy can handle thousands of concurrent processes
- **Event Logging**: In-memory buffering with periodic flush for large simulations
- **Database**: SQLite is lightweight but single-writer; consider PostgreSQL for concurrent access

### Optimization Strategies

1. **Event Batching**: Buffer events and write in batches
2. **Selective Logging**: Configure log levels per device
3. **Parallel Simulations**: Run multiple configurations in separate processes
4. **Database Indexing**: Add indexes on frequently queried columns

## Security Considerations

1. **Input Validation**: Validate all configuration inputs
2. **SQL Injection**: Use parameterized queries (already implemented)
3. **Resource Limits**: Set maximum simulation duration and device count
4. **File Access**: Validate log file paths to prevent path traversal

## Testing Strategy

### Unit Tests

- `test_config_manager.py`: Database operations
- `test_device.py`: Device behavior and lifecycle
- `test_simulator.py`: Simulation execution and logging

### Integration Tests

- End-to-end simulation workflows
- Multi-device communication
- Failure scenarios

### Performance Tests

- Large-scale simulations (1000+ devices)
- Long-running simulations
- High-frequency device intervals

## Future Enhancements

1. **Real-time Visualization**: Web dashboard showing live simulation state
2. **Advanced Analytics**: Built-in metrics, statistics, and visualization
3. **Distributed Simulation**: Multi-node parallel execution
4. **Machine Learning Integration**: Predictive failure models, optimization
5. **Cloud Deployment**: Containerized deployment with orchestration
6. **API Gateway**: RESTful API with authentication and rate limiting
7. **Plugin Marketplace**: Community-contributed device types and extensions
8. **Digital Twin Integration**: Bidirectional sync with real IoT devices
