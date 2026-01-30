"""
Generic SimPy-based Simulation Engine
Supports config-driven device modeling with parallel execution.
"""

import simpy
import random
import json
from typing import Dict, List, Any, Optional
from datetime import datetime


class Device:
    """
    Represents a generic device in the simulation with three wait states:
    - Start: minimum wait time before execution
    - Execution: random wait time between min and max
    - Exit: minimum wait time after execution
    """
    
    def __init__(
        self,
        device_id: str,
        device_type: str,
        wait_start: float,
        wait_execution_min: float,
        wait_execution_max: float,
        wait_exit: float,
        fail_prob: float,
        outputs: List[str]
    ):
        self.device_id = device_id
        self.device_type = device_type
        self.wait_start = wait_start
        self.wait_execution_min = wait_execution_min
        self.wait_execution_max = wait_execution_max
        self.wait_exit = wait_exit
        self.fail_prob = fail_prob
        self.outputs = outputs
        
    def __repr__(self):
        return f"Device({self.device_id}, {self.device_type})"


class EventLogger:
    """Logs all device events to a structured format."""
    
    def __init__(self):
        self.events: List[Dict[str, Any]] = []
        
    def log_event(
        self,
        timestamp: float,
        device_id: str,
        event_type: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log an event with timestamp and details."""
        event = {
            "timestamp": timestamp,
            "device_id": device_id,
            "event_type": event_type,
            "details": details or {}
        }
        self.events.append(event)
        
    def save_to_file(self, filepath: str):
        """Save all logged events to a JSON file."""
        output = {
            "simulation_metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_events": len(self.events)
            },
            "events": self.events
        }
        
        with open(filepath, 'w') as f:
            json.dump(output, f, indent=2)


class Simulator:
    """
    Generic simulation engine that loads config and executes device processes.
    Supports parallel execution and dependency management.
    """
    
    def __init__(self, config: Dict[str, Any], random_seed: Optional[int] = None):
        self.config = config
        self.devices: Dict[str, Device] = {}
        self.event_logger = EventLogger()
        self.env = simpy.Environment()
        self.device_resources: Dict[str, simpy.Resource] = {}
        self.device_completion_events: Dict[str, simpy.Event] = {}
        self.upstream_dependencies: Dict[str, List[str]] = {}
        self.device_started: Dict[str, bool] = {}
        
        # Set random seed if provided
        if random_seed is not None:
            random.seed(random_seed)
        
        # Load devices from config
        self._load_devices()
        self._validate_config()
        self._build_dependency_graph()
        
    def _load_devices(self):
        """Load all devices from configuration."""
        for device_config in self.config.get("devices", []):
            device_id = device_config["id"]
            
            # Check for duplicate device IDs
            if device_id in self.devices:
                raise ValueError(f"Duplicate device ID found: {device_id}")
            
            # Validate timing parameters
            wait_execution_min = device_config.get("wait_execution_min", 0)
            wait_execution_max = device_config.get("wait_execution_max", 0)
            if wait_execution_max < wait_execution_min:
                raise ValueError(
                    f"Device {device_id}: wait_execution_max ({wait_execution_max}) "
                    f"must be >= wait_execution_min ({wait_execution_min})"
                )
            
            device = Device(
                device_id=device_id,
                device_type=device_config["type"],
                wait_start=device_config.get("wait_start", 0),
                wait_execution_min=wait_execution_min,
                wait_execution_max=wait_execution_max,
                wait_exit=device_config.get("wait_exit", 0),
                fail_prob=device_config.get("fail_prob", 0.0),
                outputs=device_config.get("outputs", [])
            )
            self.devices[device.device_id] = device
            self.device_started[device.device_id] = False
            
            # Create a resource for each device (capacity = 1 means one job at a time)
            self.device_resources[device.device_id] = simpy.Resource(self.env, capacity=1)
            
            # Create completion event for each device
            self.device_completion_events[device.device_id] = self.env.event()
    
    def _validate_config(self):
        """Validate that all output IDs reference existing devices."""
        for device in self.devices.values():
            for output_id in device.outputs:
                if output_id not in self.devices:
                    raise ValueError(
                        f"Device {device.device_id} references non-existent output device: {output_id}"
                    )
    
    def _build_dependency_graph(self):
        """Build the upstream dependency graph for efficient lookup."""
        # Initialize empty lists for all devices
        for device_id in self.devices:
            self.upstream_dependencies[device_id] = []
        
        # Build the graph
        for device in self.devices.values():
            for output_id in device.outputs:
                self.upstream_dependencies[output_id].append(device.device_id)
    
    def _device_process(self, device: Device, job_id: int):
        """
        SimPy process for a single device execution.
        Handles the three wait states and failure probability.
        """
        # Wait for upstream dependencies to complete
        upstream_deps = self.upstream_dependencies.get(device.device_id, [])
        for dep_id in upstream_deps:
            if dep_id in self.device_completion_events:
                yield self.device_completion_events[dep_id]
        
        # Request the device resource
        with self.device_resources[device.device_id].request() as request:
            yield request
            
            # START state
            self.event_logger.log_event(
                self.env.now,
                device.device_id,
                "start",
                {"job_id": job_id, "state": "start"}
            )
            yield self.env.timeout(device.wait_start)
            
            # EXECUTION state (random duration between min and max)
            execution_time = random.uniform(
                device.wait_execution_min,
                device.wait_execution_max
            )
            self.event_logger.log_event(
                self.env.now,
                device.device_id,
                "execution_start",
                {"job_id": job_id, "state": "execution", "duration": execution_time}
            )
            yield self.env.timeout(execution_time)
            
            # Check for failure
            if random.random() < device.fail_prob:
                self.event_logger.log_event(
                    self.env.now,
                    device.device_id,
                    "failure",
                    {"job_id": job_id, "reason": "random_failure"}
                )
                return  # Stop processing on failure
            
            self.event_logger.log_event(
                self.env.now,
                device.device_id,
                "execution_complete",
                {"job_id": job_id, "state": "execution"}
            )
            
            # EXIT state
            self.event_logger.log_event(
                self.env.now,
                device.device_id,
                "exit_start",
                {"job_id": job_id, "state": "exit"}
            )
            yield self.env.timeout(device.wait_exit)
            
            self.event_logger.log_event(
                self.env.now,
                device.device_id,
                "complete",
                {"job_id": job_id, "state": "exit"}
            )
            
        # Mark device as complete and trigger downstream processes
        if not self.device_completion_events[device.device_id].triggered:
            self.device_completion_events[device.device_id].succeed()
        
        # Trigger downstream devices (only if not already started)
        for output_id in device.outputs:
            if output_id in self.devices and not self.device_started[output_id]:
                # Check if all upstream dependencies are complete
                all_deps_complete = all(
                    self.device_completion_events[dep_id].triggered
                    for dep_id in self.upstream_dependencies[output_id]
                )
                
                if all_deps_complete:
                    # Mark as started and create process
                    self.device_started[output_id] = True
                    self.env.process(self._device_process(self.devices[output_id], job_id))
    
    def run(self, max_time: Optional[float] = None):
        """
        Run the simulation.
        
        Args:
            max_time: Maximum simulation time. If None, runs until all processes complete.
        """
        # Find entry point devices (devices with no upstream dependencies)
        entry_devices = []
        for device_id in self.devices:
            if not self.upstream_dependencies[device_id]:
                entry_devices.append(device_id)
        
        self.event_logger.log_event(
            0,
            "SYSTEM",
            "simulation_start",
            {
                "entry_devices": entry_devices,
                "total_devices": len(self.devices)
            }
        )
        
        # Start processes for entry point devices
        job_id = 1
        for device_id in entry_devices:
            device = self.devices[device_id]
            self.device_started[device_id] = True
            self.env.process(self._device_process(device, job_id))
        
        # Run the simulation
        if max_time:
            self.env.run(until=max_time)
        else:
            self.env.run()
        
        self.event_logger.log_event(
            self.env.now,
            "SYSTEM",
            "simulation_end",
            {"simulation_time": self.env.now}
        )
    
    def save_events(self, filepath: str):
        """Save event log to file."""
        self.event_logger.save_to_file(filepath)


def load_config(config_path: str) -> Dict[str, Any]:
    """Load simulation configuration from JSON file."""
    with open(config_path, 'r') as f:
        return json.load(f)
