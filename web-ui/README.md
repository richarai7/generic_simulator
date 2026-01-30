# Generic Simulator Web UI

React-based web interface for configuring and controlling the Generic Simulator.

## Features

- **Configuration Editor**: Visual editor for simulation configuration
  - Add/remove devices (sensors, processors, actuators)
  - Configure device parameters (interval, failure probability)
  - Manage device connections (output chaining)
- **Simulation Control**: Start and stop simulations from the UI
  - Real-time status indicator
  - Progress bar showing simulation progress
  - Device state monitoring
- **Single Simulation**: Only one simulation can run at a time
- **Wait States**: Devices support start_execution and exit wait states

## Installation

### Prerequisites

- Node.js 14+ and npm
- Python backend API server running

### Setup

```bash
# Navigate to web-ui directory
cd web-ui

# Install dependencies
npm install

# Start development server
npm start
```

The app will open at http://localhost:3000

## Usage

### Starting the Backend

First, start the Flask API server:

```bash
# From the project root
pip install -r requirements-web.txt
python -m generic_simulator.api_server
```

The API will be available at http://localhost:5000

### Using the Web UI

1. **View Configuration**: The current configuration is loaded automatically
2. **Edit Configuration**: 
   - Click on fields to edit device parameters
   - Use "+ Add Device" to add new devices
   - Use "+ Add Connection" to create output chains
   - Click "Save Configuration" when done
3. **Start Simulation**:
   - Set the duration (in time units)
   - Click "Start Simulation"
   - Watch the progress bar and device states update in real-time
4. **Stop Simulation**: Click "Stop Simulation" to halt a running simulation

## Configuration Locked During Simulation

When a simulation is running, the configuration editor is locked to prevent conflicts. Stop the simulation before making changes.

## Architecture

### Frontend (React)

- `App.js`: Main application component
- `components/SimulationControl.js`: Simulation start/stop controls
- `components/ConfigurationEditor.js`: Visual configuration editor

### Backend (Flask)

- `src/generic_simulator/api_server.py`: REST API server
  - `GET /api/config`: Get configuration
  - `POST /api/config`: Update configuration
  - `POST /api/simulation/start`: Start simulation
  - `POST /api/simulation/stop`: Stop simulation
  - `GET /api/simulation/status`: Get simulation status

## Development

### Build for Production

```bash
npm run build
```

This creates an optimized production build in the `build/` directory.

### Testing

```bash
npm test
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Troubleshooting

**Problem**: API connection errors

**Solution**: Ensure the Flask backend is running on port 5000

---

**Problem**: Configuration not loading

**Solution**: Make sure the database exists at `configs/simulator.db`. Run `python examples/create_examples.py` to create sample configurations.

---

**Problem**: Can't edit configuration

**Solution**: Stop any running simulation first. The editor is locked during simulation execution.
