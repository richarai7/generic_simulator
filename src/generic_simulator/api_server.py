"""Flask API server for simulator control."""

from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import time
from pathlib import Path

from generic_simulator.config_manager import ConfigManager
from generic_simulator.simulator import Simulator

app = Flask(__name__)
CORS(app)

# Global state
simulation_state = {
    "running": False,
    "simulator": None,
    "thread": None,
    "config_id": None,
    "duration": 100.0,
    "current_time": 0.0
}

# Database path
DB_PATH = "configs/simulator.db"

def run_simulation_thread(simulator, duration):
    """Run simulation in a separate thread."""
    global simulation_state
    try:
        simulation_state["running"] = True
        simulator.run(until=duration)
        simulation_state["current_time"] = simulator.env.now
    except Exception as e:
        print(f"Simulation error: {e}")
    finally:
        simulation_state["running"] = False
        simulation_state["simulator"] = None
        simulation_state["thread"] = None


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok"})


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get the current simulation configuration."""
    try:
        manager = ConfigManager(DB_PATH)
        configs = manager.list_configurations()
        
        if not configs:
            return jsonify({"error": "No configurations found"}), 404
        
        # Get the first (and only) configuration
        config = manager.get_configuration(configs[0]["id"])
        return jsonify(config)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/config', methods=['POST'])
def update_config():
    """Update the simulation configuration."""
    try:
        data = request.json
        manager = ConfigManager(DB_PATH)
        
        # Delete all existing configurations
        # For simplicity, we'll recreate the database with the new config
        # In production, you'd want proper update logic
        
        # Create new configuration
        config_id = manager.create_configuration(
            name=data.get("name", "default_config"),
            description=data.get("description", "")
        )
        
        # Add devices
        for device in data.get("devices", []):
            manager.add_device(
                config_id,
                device_name=device["name"],
                device_type=device["type"],
                interval=device["interval"],
                failure_probability=device.get("failure_probability", 0.0),
                config=device.get("config", {})
            )
        
        # Add connections
        for connection in data.get("connections", []):
            manager.add_connection(
                config_id,
                source_device=connection["source"],
                target_device=connection["target"]
            )
        
        return jsonify({"success": True, "config_id": config_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/simulation/start', methods=['POST'])
def start_simulation():
    """Start the simulation."""
    global simulation_state
    
    if simulation_state["running"]:
        return jsonify({"error": "Simulation already running"}), 400
    
    try:
        data = request.json or {}
        duration = data.get("duration", 100.0)
        
        manager = ConfigManager(DB_PATH)
        configs = manager.list_configurations()
        
        if not configs:
            return jsonify({"error": "No configuration found"}), 404
        
        config = manager.get_configuration(configs[0]["id"])
        
        # Create simulator
        simulator = Simulator(config, log_file="logs/web_simulation.json")
        simulation_state["simulator"] = simulator
        simulation_state["config_id"] = configs[0]["id"]
        simulation_state["duration"] = duration
        simulation_state["current_time"] = 0.0
        
        # Start simulation in separate thread
        thread = threading.Thread(
            target=run_simulation_thread,
            args=(simulator, duration)
        )
        thread.daemon = True
        thread.start()
        simulation_state["thread"] = thread
        
        return jsonify({
            "success": True,
            "message": "Simulation started",
            "duration": duration
        })
    except Exception as e:
        simulation_state["running"] = False
        return jsonify({"error": str(e)}), 500


@app.route('/api/simulation/stop', methods=['POST'])
def stop_simulation():
    """Stop the simulation."""
    global simulation_state
    
    if not simulation_state["running"]:
        return jsonify({"error": "No simulation running"}), 400
    
    try:
        # For SimPy, we can't easily stop mid-execution
        # We'll just mark it as stopped and let it complete
        simulation_state["running"] = False
        
        return jsonify({
            "success": True,
            "message": "Simulation stopping"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/simulation/status', methods=['GET'])
def get_simulation_status():
    """Get current simulation status."""
    global simulation_state
    
    status = {
        "running": simulation_state["running"],
        "current_time": simulation_state["current_time"],
        "duration": simulation_state["duration"]
    }
    
    if simulation_state["simulator"]:
        status["current_time"] = simulation_state["simulator"].env.now
        status["device_states"] = simulation_state["simulator"].get_device_states()
    
    return jsonify(status)


def main():
    """Run the Flask server."""
    print("Starting Generic Simulator API Server...")
    print("API available at http://localhost:5000")
    print("Web UI available at http://localhost:3000")
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)


if __name__ == '__main__':
    main()
