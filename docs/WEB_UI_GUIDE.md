# Web UI User Guide

## Overview

The Generic Simulator Web UI provides an intuitive interface for configuring and controlling simulations. It consists of two main sections:

1. **Simulation Control Panel** - Start/stop simulations and monitor status
2. **Configuration Editor** - Visual editor for device and connection management

## Screenshots and Walkthrough

### 1. Simulation Control Panel

**Status Indicator**
- Green dot (pulsing): Simulation is running
- Gray dot: Simulation is stopped

**Progress Bar**
- Shows simulation progress in real-time
- Displays current time vs. total duration (e.g., "Time: 45.2 / 100")

**Control Buttons**
- **Duration Input**: Set simulation duration (1-10000 time units)
- **Start Simulation**: Begins simulation (disabled when running)
- **Stop Simulation**: Halts simulation (disabled when stopped)

**Device States Grid**
- Real-time display of all device states
- Color-coded states:
  - Green: `running` - Device is actively processing
  - Yellow: `waiting_to_start` - Device initializing
  - Orange: `waiting_to_exit` - Device shutting down
  - Red: `failed` - Device has failed
  - Gray: `exited` - Device has completed
  - Pink: `interrupted` - Device was interrupted

### 2. Configuration Editor

**Configuration Information**
- Displays configuration name and description
- Shows count of devices and connections

**Device Cards**
Each device is displayed in a card with:
- **Device Name**: Editable text field
- **Type**: Dropdown (Sensor, Processor, Actuator)
- **Interval**: Numeric input for processing interval
- **Failure Probability**: 0.0-1.0 range for random failures
- **Remove Button**: Red X button to delete device

**Sensor-Specific Configuration**
- Min Value: Minimum sensor reading
- Max Value: Maximum sensor reading
- Unit: Measurement unit (e.g., "celsius", "psi")

**Connection Management**
- Visual representation: `source → target`
- Dropdowns to select source and target devices
- Remove button for each connection
- "+ Add Connection" button (enabled when 2+ devices exist)

**Action Buttons**
- **Save Configuration**: Commits changes to database
- **Reset Changes**: Reverts to last saved state

**Locked During Simulation**
When a simulation is running, the entire editor is locked with a yellow notice banner: "Configuration is locked while simulation is running"

## Typical Workflow

### Creating a New Configuration

1. **Add Devices**:
   - Click "+ Add Device"
   - Edit the device name (e.g., "temp_sensor")
   - Select device type from dropdown
   - Set interval (e.g., 5.0 for 5 time units)
   - Set failure probability (e.g., 0.05 for 5% chance)
   - For sensors, configure min/max values and unit

2. **Connect Devices**:
   - Click "+ Add Connection"
   - Select source device from first dropdown
   - Select target device from second dropdown
   - Create multiple connections for complex topologies

3. **Save**:
   - Click "Save Configuration"
   - Configuration is stored in SQLite database
   - Confirmation alert appears

### Running a Simulation

1. **Set Duration**:
   - Enter desired simulation time (default: 100)
   - Units are in simulation time steps

2. **Start**:
   - Click "Start Simulation"
   - Status indicator turns green
   - Progress bar appears
   - Device states update every 2 seconds

3. **Monitor**:
   - Watch progress bar advance
   - Observe device states changing
   - See wait states: `waiting_to_start` → `running` → `waiting_to_exit` → `exited`
   - Failed devices turn red

4. **Stop** (if needed):
   - Click "Stop Simulation"
   - Simulation marks as stopping
   - Devices complete current cycle

### Wait State Visualization

The wait states are visible in the Device States grid:

**Start Sequence** (first 0.2 time units):
```
temp_sensor: waiting_to_start
data_processor: waiting_to_start
hvac_actuator: waiting_to_start
    ↓
temp_sensor: running
data_processor: running
hvac_actuator: running
```

**Exit Sequence** (when device fails or sim completes):
```
temp_sensor: failed
    ↓
temp_sensor: waiting_to_exit
    ↓
temp_sensor: exited
```

## Tips and Best Practices

### Configuration Tips
- **Naming**: Use descriptive device names (e.g., "temp_sensor", "main_processor")
- **Intervals**: Shorter intervals = more frequent processing (more events)
- **Failure Probability**: 0.01-0.05 is realistic for stable simulations
- **Connections**: Avoid circular dependencies unless intended

### Simulation Tips
- **Duration**: Start with 50-100 for initial testing
- **Single Simulation**: Only one simulation can run at a time
- **Log Files**: Check `logs/web_simulation.json` for detailed event logs
- **Configuration Lock**: Stop simulation before editing configuration

### Troubleshooting

**Problem**: Configuration not loading
- **Solution**: Ensure database exists at `configs/simulator.db`
- Run `python examples/create_examples.py` to create sample data

**Problem**: API connection errors
- **Solution**: Ensure Flask server is running on port 5000
- Check terminal for API server errors
- Restart with `./start-web-ui.sh`

**Problem**: Can't edit configuration
- **Solution**: Stop any running simulation
- Look for yellow "locked" banner
- Click "Stop Simulation" first

**Problem**: Changes not saving
- **Solution**: Click "Save Configuration" button
- Check browser console for errors
- Verify device names are unique

## Technical Details

### Browser Requirements
- Modern browser with ES6 support
- Chrome 90+, Firefox 88+, Safari 14+, Edge 90+

### API Polling
- Status updates every 2 seconds
- Minimal bandwidth usage (JSON responses)
- Automatic retry on network errors

### State Management
- React state for UI updates
- API calls for persistence
- Optimistic updates for responsiveness

### Security
- CORS enabled for localhost development
- No authentication (development mode)
- Database is local SQLite file

## Advanced Usage

### Custom Device Types
To add custom device types, modify:
1. Backend: `src/generic_simulator/device.py`
2. Frontend: `web-ui/src/components/ConfigurationEditor.js` (type dropdown)

### API Integration
Use the REST API directly for automation:

```bash
# Get current config
curl http://localhost:5000/api/config

# Start simulation
curl -X POST http://localhost:5000/api/simulation/start \
  -H "Content-Type: application/json" \
  -d '{"duration": 100}'

# Check status
curl http://localhost:5000/api/simulation/status
```

### Production Deployment
For production use:
1. Build React app: `cd web-ui && npm run build`
2. Serve static files with Flask
3. Add authentication
4. Use production WSGI server (gunicorn)
5. Configure reverse proxy (nginx)

## Next Steps

- Explore the CLI interface: `generic-simulator --help`
- Read the Architecture documentation: `docs/ARCHITECTURE.md`
- Check detailed usage examples: `docs/USAGE.md`
- Review database schema: `docs/SCHEMA.md`
