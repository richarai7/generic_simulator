# Generic SimPy Simulation Environment

A flexible, config-driven simulation framework for modeling complex process chains with parallel execution support. Built on SimPy, this asset enables users to model any process workflow by simply editing a JSON configuration file—no code changes required.

**⚡ New to this project? Check out the [Quick Start Guide](QUICKSTART.md) to get running in 5 minutes!**

## Overview

This simulation environment is designed with **assetization** in mind, making it easy to:
- Model any process by editing configuration files
- Run what-if scenarios without writing code
- Log all events for downstream analysis
- Scale from proof-of-concept to production asset
- Integrate with web portals and dashboards (future)

## Key Features

### Config-Driven Architecture
- **Zero code changes** needed to model new processes
- All devices, dependencies, and timing parameters defined in JSON
- Extensible to SQLite for enterprise assetization

### Device Modeling
Each device has three wait states:
- **Start**: Minimum wait time before execution begins
- **Execution**: Random duration between min and max values
- **Exit**: Minimum wait time after execution completes

### Staff Utilization
- **Staff resources** shared across devices
- Automatic allocation and release tracking
- **Utilization metrics** calculated automatically
- Bottleneck detection and optimization insights

### Parallel Execution
- Devices execute in parallel when dependencies allow
- Automatic dependency resolution based on device outputs
- SimPy handles all process timing and resource management

### Event Logging
- All device state transitions logged to JSON
- Staff allocation/release events tracked
- Includes timestamps, device IDs, event types, and details
- Ready for downstream processing and visualization

### REST API (Azure Functions)
- **GET /api/events**: Serve event logs to web dashboards and 3D views
- **GET /api/config**: Retrieve process/device configurations
- **POST /api/config**: Save updated configurations from web UI
- Full documentation: [API Documentation](api_function_app/README.md)

### Web Portal (Interactive UI)
- **Configuration Management**: View, create, and edit process configurations
- **Simulation Dashboard**: Metrics, analytics, and event timelines
- **Process Flow Visualizer**: Interactive device dependency diagrams
- **Responsive Design**: Works on desktop, tablet, and mobile
- Full documentation: [Web Portal Guide](web_portal/README.md)

## Installation

```bash
# Clone the repository
git clone https://github.com/richarai7/generic_simulator.git
cd generic_simulator

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

Run a simulation using the provided platelet pooling configuration:

```bash
python main.py --config configs/platelet_pooling.json --output outputs/results.json
```

### Command Line Options

```
usage: main.py [-h] -c CONFIG -o OUTPUT [--max-time MAX_TIME]

Generic SimPy-based Simulation Environment

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Path to the JSON configuration file
  -o OUTPUT, --output OUTPUT
                        Path to the output JSON event log file
  --max-time MAX_TIME   Maximum simulation time (optional). If not set, runs
                        until completion.
```

## Configuration File Structure

Configuration files define the entire process workflow in JSON format.

**For complete configuration reference, see [docs/CONFIG_REFERENCE.md](docs/CONFIG_REFERENCE.md)**

Quick overview:

```json
{
  "name": "Process Name",
  "description": "Process description",
  "version": "1.0",
  "staff": {
    "technician": 3,
    "nurse": 2
  },
  "devices": [
    {
      "id": "device_1",
      "type": "device_type",
      "wait_start": 2.0,
      "wait_execution_min": 10.0,
      "wait_execution_max": 20.0,
      "wait_exit": 1.0,
      "fail_prob": 0.01,
      "outputs": ["device_2", "device_3"],
      "staff_required": {
        "technician": 1
      }
    }
  ]
}
```

### Device Configuration Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Unique identifier for the device |
| `type` | string | Device type (for categorization) |
| `wait_start` | float | Minimum wait time before execution (seconds) |
| `wait_execution_min` | float | Minimum execution time (seconds) |
| `wait_execution_max` | float | Maximum execution time (seconds) |
| `wait_exit` | float | Minimum wait time after execution (seconds) |
| `fail_prob` | float | Probability of failure (0.0 to 1.0) |
| `outputs` | array | List of downstream device IDs |
| `staff_required` | object | Staff resources needed (optional) |

### Process Flow

1. **Entry devices** (devices with no upstream dependencies) start automatically
2. Each device waits for all upstream dependencies to complete
3. Device executes through three states: start → execution → exit
4. Random failures can occur based on `fail_prob`
5. Successful completion triggers all downstream devices
6. Process continues until all devices complete or max time is reached

## Output Event Log

The simulation generates a JSON event log with the following structure:

```json
{
  "simulation_metadata": {
    "generated_at": "2026-01-30T06:00:00.000000",
    "total_events": 42
  },
  "events": [
    {
      "timestamp": 0.0,
      "device_id": "device_1",
      "event_type": "start",
      "details": {
        "job_id": 1,
        "state": "start"
      }
    }
  ],
  "staff_utilization": {
    "technician": {
      "count": 3,
      "total_busy_time": 56.95,
      "total_available_time": 530.47,
      "utilization_percentage": 10.74,
      "allocations": 4
    }
  }
}
```

### Event Types

- `simulation_start`: Simulation initialization
- `start`: Device enters start state
- `execution_start`: Device begins execution
- `execution_complete`: Device completes execution
- `exit_start`: Device enters exit state
- `complete`: Device fully completes
- `failure`: Device fails (process stops)
- `staff_allocated`: Staff assigned to device
- `staff_released`: Staff freed from device
- `simulation_end`: Simulation completion

## Example Use Cases

### 1. Platelet Pooling Process
The included `configs/platelet_pooling.json` demonstrates a blood product processing workflow:
- Collection → Quality Check → Temperature Storage → Pooling → Final QC + Labeling → Packaging → Cold Storage

For staff utilization tracking, see `configs/platelet_pooling_with_staff.json`:
- Tracks nurses, technicians, and quality specialists
- Calculates utilization percentages
- Identifies bottlenecks and over-staffing

### 2. Manufacturing Assembly Line
Create a config for manufacturing with parallel assembly stations:
```json
{
  "devices": [
    {"id": "raw_input", "outputs": ["assembly_1", "assembly_2"]},
    {"id": "assembly_1", "outputs": ["merge"]},
    {"id": "assembly_2", "outputs": ["merge"]},
    {"id": "merge", "outputs": ["final_qa"]}
  ]
}
```

### 3. Order Fulfillment Process
Model warehouse operations:
- Order Receipt → Picking → Packing → Shipping Label → Dispatch

## Analyzing Results

### Basic Analysis
Use the built-in analysis script to view device statistics:
```bash
python examples/analyze_log.py outputs/results.json
```

Output includes:
- Device execution times
- Success/failure rates
- **Staff utilization** (if configured)

### Staff Utilization Analysis
For detailed staff insights:
```bash
python examples/analyze_staff_utilization.py outputs/results.json
```

This provides:
- Utilization percentages by staff type
- Allocation counts per device
- **Bottleneck detection** (>70% utilization)
- **Over-staffing alerts** (<20% utilization)
- Optimization recommendations

### Timeline Visualization
View the process timeline:
```bash
python examples/visualize_timeline.py outputs/results.json
```

## Assetization Roadmap

This implementation is designed to evolve from POC to production asset:

### Current (POC)
- ✅ JSON configuration files
- ✅ CLI interface
- ✅ Event logging
- ✅ Parallel execution support
- ✅ Staff utilization tracking
- ✅ Resource bottleneck detection

### Phase 2 (Database Integration)
- 🔲 SQLite/PostgreSQL for configuration storage
- 🔲 Config versioning and history
- 🔲 Multiple simulation runs tracking

### Phase 2.5 (API Layer)
- ✅ Azure Functions API for event data
- ✅ Configuration management endpoints
- ✅ REST API for web frontend integration
- ✅ Comprehensive API documentation

### Phase 3 (Web Portal)
- ✅ Web-based configuration viewer and editor
- ✅ Interactive process flow visualizer
- ✅ Simulation results dashboard
- ✅ Real-time metrics and analytics
- ✅ Modern, responsive UI design
- 🔲 Drag-and-drop process designer (future)

## Future UI/Portal Design

### Configuration Portal Wireframe

```
┌─────────────────────────────────────────────────────────────┐
│  Generic Simulator - Configuration Portal                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Process Configurations                    [+ New Config]    │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Name: Platelet Pooling Process        [Edit] [Run]   │  │
│  │ Description: Lifeblood platelet pooling simulation    │  │
│  │ Devices: 8 | Last Run: 2026-01-30    Status: ✓       │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Name: Manufacturing Assembly Line     [Edit] [Run]   │  │
│  │ Description: Multi-stage assembly process             │  │
│  │ Devices: 12 | Last Run: 2026-01-29   Status: ✓       │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Device Editor Wireframe

```
┌─────────────────────────────────────────────────────────────┐
│  Edit Device - "collection"                                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Device ID:    [collection___________]                       │
│  Device Type:  [collection_station___]                       │
│                                                               │
│  ┌─ Timing Parameters ──────────────────────────────────┐   │
│  │ Start Wait (min):      [2.0_]  seconds               │   │
│  │ Execution Min:         [15.0]  seconds               │   │
│  │ Execution Max:         [30.0]  seconds               │   │
│  │ Exit Wait (min):       [1.0_]  seconds               │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─ Reliability ─────────────────────────────────────────┐  │
│  │ Failure Probability:   [0.01] (1%)                    │  │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─ Outputs (Downstream Devices) ───────────────────────┐  │
│  │ [quality_check_1]                          [Remove]  │  │
│  │                                            [+ Add]    │  │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│                              [Cancel]  [Save]                │
└─────────────────────────────────────────────────────────────┘
```

### Process Visualizer Wireframe

```
┌─────────────────────────────────────────────────────────────┐
│  Process Flow - Platelet Pooling                             │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│    ┌──────────┐      ┌──────────┐      ┌──────────┐        │
│    │Collection│─────→│Quality   │─────→│ Storage  │        │
│    │          │      │ Check 1  │      │   Temp   │        │
│    └──────────┘      └──────────┘      └──────────┘        │
│                                              │               │
│                                              ↓               │
│                                         ┌──────────┐        │
│                                         │ Pooling  │        │
│                                         └──────────┘        │
│                                          │        │          │
│                               ┌──────────┘        └─────┐   │
│                               ↓                         ↓   │
│                         ┌──────────┐            ┌──────────┐│
│                         │Quality   │            │ Labeling ││
│                         │ Check 2  │            │          ││
│                         └──────────┘            └──────────┘│
│                               │                         │   │
│                               └──────────┬──────────────┘   │
│                                          ↓                   │
│                                     ┌──────────┐            │
│                                     │Packaging │            │
│                                     └──────────┘            │
│                                          │                   │
│                                          ↓                   │
│                                     ┌──────────┐            │
│                                     │  Final   │            │
│                                     │ Storage  │            │
│                                     └──────────┘            │
│                                                               │
│  [Run Simulation]  [Export Config]  [View Results]          │
└─────────────────────────────────────────────────────────────┘
```

### Simulation Dashboard Wireframe

```
┌─────────────────────────────────────────────────────────────┐
│  Simulation Dashboard                                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Run: Platelet Pooling - 2026-01-30 06:00:00                │
│  Status: ✓ Completed | Duration: 156.3s | Events: 42        │
│                                                               │
│  ┌─ Performance Metrics ────────────────────────────────┐   │
│  │  Device           | Avg Time | Success | Failures    │   │
│  │  Collection       | 22.5s    | 100%    | 0           │   │
│  │  Quality Check 1  | 4.2s     | 95%     | 5%          │   │
│  │  Storage Temp     | 89.3s    | 98%     | 2%          │   │
│  │  Pooling          | 14.7s    | 97%     | 3%          │   │
│  │  ...                                                  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─ Event Timeline ─────────────────────────────────────┐   │
│  │  [Timeline visualization showing device states]      │   │
│  │  ████▓▓▓░░░████▓▓░░░████▓▓░░░                        │   │
│  │  Time (s): 0────50────100───150                      │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  [Download Event Log]  [Compare Runs]  [Export Report]      │
└─────────────────────────────────────────────────────────────┘
```

## UI/Portal Flow

### User Journey for Configuration and Simulation

1. **Access Portal** → User logs into web portal
2. **Select/Create Config** → Choose existing config or create new
3. **Edit Devices** → 
   - Add/remove devices
   - Configure timing parameters
   - Set failure probabilities
   - Define device dependencies (outputs)
4. **Visualize Process** → See graphical representation of workflow
5. **Run Simulation** → Click "Run" button
6. **Monitor Progress** → Real-time status updates
7. **View Results** → Dashboard with metrics and event timeline
8. **Download/Export** → Get event log for further analysis
9. **Compare Scenarios** → Run what-if analyses with different configs

### Portal Features (Future)

- **Azure Functions API**: REST API for event data and config management (✅ **Available Now!** - See [API Documentation](api_function_app/README.md))
- **Drag-and-Drop Process Designer**: Visual interface to create device workflows
- **Parameter Sliders**: Interactive controls for timing and probability adjustments
- **Real-time Validation**: Immediate feedback on config errors
- **Template Library**: Pre-built process templates for common scenarios
- **Collaboration**: Share configs between team members
- **Version Control**: Track config changes over time
- **Batch Simulation**: Run multiple scenarios automatically

## Extending the Asset

### Adding New Device Types

Simply add a new device entry to your config:

```json
{
  "id": "new_device",
  "type": "custom_processor",
  "wait_start": 1.0,
  "wait_execution_min": 5.0,
  "wait_execution_max": 10.0,
  "wait_exit": 0.5,
  "fail_prob": 0.02,
  "outputs": ["next_device"]
}
```

### Creating Complex Workflows

- **Sequential**: Each device has one output
- **Parallel**: One device has multiple outputs
- **Convergent**: Multiple devices point to same output
- **Branching**: Combine all patterns for complex flows

### Integration Points

The event log JSON can be consumed by:
- BI tools (Power BI, Tableau)
- Python analytics scripts
- Dashboard applications
- Data warehouses
- ML/AI pipelines

## Technical Architecture

### Core Components

1. **simulator.py**: Core simulation engine
   - Device class: Represents individual process devices
   - EventLogger: Captures all events
   - Simulator: Orchestrates the entire simulation

2. **main.py**: CLI interface
   - Argument parsing
   - Config loading
   - Simulation execution
   - Error handling

3. **configs/**: Configuration files
   - JSON format
   - Extensible to SQLite

4. **outputs/**: Event logs
   - JSON format
   - Timestamped events

### Design Principles

- **Separation of Concerns**: Config, logic, and output are separated
- **Single Responsibility**: Each class has one clear purpose
- **Open/Closed**: Easy to extend without modifying core code
- **Dependency Injection**: Config drives behavior
- **Event Sourcing**: All state changes logged

## Troubleshooting

### Common Issues

**Issue**: "Config file not found"
- **Solution**: Verify the path to your config file is correct

**Issue**: "Circular dependency detected"
- **Solution**: Check device outputs don't create loops

**Issue**: "Simulation never completes"
- **Solution**: Use `--max-time` parameter to set a time limit

## Contributing

This asset is designed to be extended. Potential enhancements:

- Additional device state types
- Resource constraints (limited capacity)
- Batch processing support
- Priority queues
- Cost modeling
- Energy consumption tracking

## License

[Specify your license here]

## Support

For questions or issues, please open an issue on GitHub.

---

**Version**: 1.0  
**Last Updated**: 2026-01-30  
**Maintainer**: [Your name/team]
