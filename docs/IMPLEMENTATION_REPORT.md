# React Web UI Implementation - Complete

## Summary

Successfully implemented a React-based web interface for the Generic Simulator with full configuration editing and simulation control capabilities.

## What Was Implemented

### 1. Flask REST API Server (`api_server.py`)

**Endpoints:**
```
GET  /api/health              - Health check
GET  /api/config              - Get current configuration  
POST /api/config              - Update configuration
POST /api/simulation/start    - Start simulation (with duration)
POST /api/simulation/stop     - Stop simulation
GET  /api/simulation/status   - Get real-time status
```

**Features:**
- Thread-safe simulation execution
- Single simulation enforcement (only 1 at a time)
- Real-time status updates with device states
- CORS enabled for local development
- Graceful error handling

### 2. React Frontend (`web-ui/`)

**Components:**

**SimulationControl.js**
- Start/Stop buttons with duration input
- Real-time status indicator (green=running, gray=stopped)
- Progress bar showing simulation progress
- Live device states grid with color coding
- Automatic status polling (every 2 seconds)

**ConfigurationEditor.js**
- Visual device editor with add/remove
- Device type selector (Sensor/Processor/Actuator)
- Configurable parameters: interval, failure_probability
- Sensor-specific config: min/max values, unit
- Connection management with visual arrows
- Save/Reset functionality
- Locked state when simulation running

**App.js**
- Main application shell
- API integration layer
- Error handling and display
- State management

### 3. Device Wait States

Modified `device.py` to support two wait states:

**waiting_to_start** (0.1 time units)
- Device enters this state before running
- Logged as event: `{"event_type": "waiting_to_start"}`
- Visible in UI with yellow color

**waiting_to_exit** (0.1 time units)  
- Device enters before final exit
- Triggered on failure or interrupt
- Logged as event: `{"event_type": "waiting_to_exit"}`
- Visible in UI with orange color

**State Progression:**
```
waiting_to_start (0.0-0.1) 
  → running (0.1+)
    → [on failure/end]
      → waiting_to_exit
        → exited
```

## Requirements Met

✅ **React page for configuration editing**
- Full CRUD operations on devices and connections
- Visual interface with form validation
- Real-time updates

✅ **Start and stop simulation from UI**
- Start button with duration input
- Stop button to halt simulation
- Status indicators and progress bar

✅ **Only 1 simulation at a time**
- Enforced in API server
- Start button disabled when running
- Error returned if trying to start while running

✅ **Single simulation configuration**
- UI works with one active configuration
- Configuration locked during simulation
- Changes saved to single config in database

✅ **2 wait states: start execution and exit**
- `waiting_to_start`: 0.1s delay before running
- `waiting_to_exit`: 0.1s delay before exit
- Both logged and visible in UI

## File Structure

```
generic_simulator/
├── src/generic_simulator/
│   ├── api_server.py          # Flask REST API (new)
│   └── device.py               # Updated with wait states
├── web-ui/                     # React app (new)
│   ├── package.json
│   ├── public/
│   │   └── index.html
│   └── src/
│       ├── App.js
│       ├── App.css
│       ├── index.js
│       ├── index.css
│       └── components/
│           ├── SimulationControl.js
│           ├── SimulationControl.css
│           ├── ConfigurationEditor.js
│           └── ConfigurationEditor.css
├── docs/
│   ├── WEB_UI_GUIDE.md         # User guide (new)
│   └── UI_MOCKUP.txt           # Visual mockup (new)
├── requirements-web.txt         # Flask dependencies (new)
├── start-web-ui.sh             # Startup script (new)
└── README.md                   # Updated with Web UI section
```

## Testing Results

### Unit Tests
```
Ran 20 tests in 0.102s
OK
```

All existing tests pass with wait state modifications.

### API Tests
```bash
# Health check
$ curl http://localhost:5000/api/health
{"status": "ok"}

# Get configuration
$ curl http://localhost:5000/api/config
{
  "name": "simple_chain",
  "devices": [...],
  "connections": [...]
}

# Start simulation
$ curl -X POST http://localhost:5000/api/simulation/start \
  -H "Content-Type: application/json" \
  -d '{"duration": 30}'
{"success": true, "message": "Simulation started"}

# Check status
$ curl http://localhost:5000/api/simulation/status
{
  "running": true,
  "current_time": 15.2,
  "duration": 30,
  "device_states": {
    "temperature_sensor": "running",
    "data_processor": "running",
    "hvac_actuator": "running"
  }
}
```

### Wait State Verification
```python
# Test output showing wait states
Events logged:
  0: waiting_to_start - waiting_to_start
  0.1: started - running
  0.1: failed - failed
  0.1: waiting_to_exit - waiting_to_exit
  0.2: exited - exited
```

## Usage Instructions

### Quick Start

1. **Start API Server:**
```bash
./start-web-ui.sh
# Server starts on http://localhost:5000
```

2. **Start React App:**
```bash
cd web-ui
npm install  # First time only
npm start
# App opens at http://localhost:3000
```

3. **Use the UI:**
- Configure devices in the editor
- Click "Save Configuration"
- Set duration and click "Start Simulation"
- Watch real-time progress and device states
- Click "Stop Simulation" when needed

### Configuration Workflow

1. **Add Device**: Click "+ Add Device"
2. **Edit Properties**: Name, type, interval, failure probability
3. **Add Connections**: Click "+ Add Connection", select source → target
4. **Save**: Click "Save Configuration"

### Simulation Workflow

1. **Set Duration**: Enter time units (e.g., 100)
2. **Start**: Click "Start Simulation"
3. **Monitor**: Watch progress bar and device states
4. **Observe Wait States**: See devices transition through:
   - `waiting_to_start` (yellow)
   - `running` (green)
   - `waiting_to_exit` (orange) if failure/complete
   - `exited` (gray)

## Technical Details

### State Management
- **Backend**: Global `simulation_state` dict
- **Frontend**: React hooks (useState, useEffect)
- **Polling**: 2-second interval for status updates
- **Thread Safety**: Python threading for simulation execution

### Single Simulation Enforcement
- Global flag: `simulation_state["running"]`
- API rejects start requests when running
- UI disables start button when running
- Configuration locked when running

### Wait State Implementation
- Both wait states use `yield self.env.timeout(0.1)`
- Implemented in device `run()` method
- Logged as events with timestamps
- Visible in device state display

### Color Coding
- 🟢 Green: `running`
- 🟡 Yellow: `waiting_to_start`
- 🟠 Orange: `waiting_to_exit`
- 🔴 Red: `failed`
- ⚪ Gray: `exited`
- 🩷 Pink: `interrupted`

## Future Enhancements

### Potential Additions
- [ ] Authentication and user management
- [ ] Multiple configuration support (tabs/selector)
- [ ] Real-time event stream (WebSocket)
- [ ] Visual topology diagram
- [ ] Historical simulation logs browser
- [ ] Export/import configurations
- [ ] Simulation replay feature
- [ ] Advanced analytics dashboard

### Production Deployment
- Build React app: `npm run build`
- Serve with production WSGI server (gunicorn)
- Add reverse proxy (nginx)
- Enable HTTPS
- Add authentication layer

## Known Limitations

1. **Single Configuration**: UI only works with one configuration at a time
2. **No WebSocket**: Status updates via polling (2s interval)
3. **No Authentication**: Development mode only
4. **Limited Validation**: Basic client-side validation only
5. **No Undo/Redo**: Configuration changes are immediate on save

## Conclusion

The React Web UI successfully provides:
- ✅ Visual configuration editing
- ✅ Real-time simulation control  
- ✅ Live status monitoring
- ✅ Wait state visualization
- ✅ Single simulation enforcement
- ✅ Intuitive user experience

All requirements met and verified through testing. Ready for demonstration and further development.
