"""Main simulator engine."""

import simpy
from typing import Dict, Any, Optional
from pathlib import Path

from .config_manager import ConfigManager
from .device import create_device, Device
from .event_logger import EventLogger


class Simulator:
    """Main simulation engine."""

    def __init__(self, config: Dict[str, Any], log_file: Optional[str] = None):
        """Initialize simulator.
        
        Args:
            config: Configuration dictionary from ConfigManager
            log_file: Optional path to JSON log file
        """
        self.config = config
        self.env = simpy.Environment()
        self.devices: Dict[str, Device] = {}
        
        # Setup event logger
        if log_file is None:
            log_file = f"logs/simulation_{config['name']}.json"
        self.logger = EventLogger(log_file)
        
        # Build simulation from config
        self._build_simulation()

    def _build_simulation(self):
        """Build simulation from configuration."""
        # Create all devices
        for device_config in self.config["devices"]:
            device = create_device(
                device_type=device_config["type"],
                env=self.env,
                name=device_config["name"],
                interval=device_config["interval"],
                failure_probability=device_config.get("failure_probability", 0.0),
                config=device_config.get("config", {}),
                logger=self.logger.log
            )
            self.devices[device_config["name"]] = device

        # Setup connections
        for connection in self.config.get("connections", []):
            source_device = self.devices.get(connection["source"])
            target_device = self.devices.get(connection["target"])
            
            if source_device and target_device:
                source_device.add_output(target_device)
            else:
                print(f"Warning: Connection {connection['source']} -> {connection['target']} "
                      f"references unknown device(s)")

    def run(self, until: float = 100.0):
        """Run simulation.
        
        Args:
            until: Simulation time to run until
        """
        print(f"Starting simulation: {self.config['name']}")
        print(f"Devices: {len(self.devices)}")
        print(f"Running until time: {until}")
        
        # Log simulation start
        self.logger.log({
            "timestamp": self.env.now,
            "event_type": "simulation_start",
            "config_name": self.config["name"],
            "device_count": len(self.devices)
        })
        
        # Run simulation
        self.env.run(until=until)
        
        # Log simulation end
        self.logger.log({
            "timestamp": self.env.now,
            "event_type": "simulation_end",
            "config_name": self.config["name"]
        })
        
        print(f"Simulation completed at time: {self.env.now}")
        print(f"Events logged: {len(self.logger.get_events())}")
        
        # Save logs
        self.logger.save()
        print(f"Logs saved to: {self.logger.log_file}")

    def get_device_states(self) -> Dict[str, str]:
        """Get current state of all devices.
        
        Returns:
            Dictionary mapping device names to their states
        """
        return {name: device.state for name, device in self.devices.items()}


def run_simulation(config_path: str, config_name: str, duration: float = 100.0):
    """Run a simulation from database configuration.
    
    Args:
        config_path: Path to SQLite database
        config_name: Name of configuration to run
        duration: Simulation duration
    """
    # Load configuration
    manager = ConfigManager(config_path)
    config = manager.get_configuration_by_name(config_name)
    
    # Create and run simulator
    simulator = Simulator(config)
    simulator.run(until=duration)
    
    return simulator
