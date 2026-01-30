"""Base device model and implementations."""

import simpy
import random
from typing import Dict, Any, List, Optional, Callable
from abc import ABC, abstractmethod


class Device(ABC):
    """Base class for all simulated devices."""

    def __init__(
        self,
        env: simpy.Environment,
        name: str,
        interval: float,
        failure_probability: float = 0.0,
        config: Optional[Dict[str, Any]] = None,
        logger: Optional[Callable] = None
    ):
        """Initialize device.
        
        Args:
            env: SimPy environment
            name: Device name
            interval: Processing interval in seconds
            failure_probability: Probability of failure (0.0-1.0)
            config: Device-specific configuration
            logger: Optional logging function
        """
        self.env = env
        self.name = name
        self.interval = interval
        self.failure_probability = failure_probability
        self.config = config or {}
        self.logger = logger
        self.state = "initialized"
        self.outputs: List['Device'] = []
        self.failed = False
        
        # Start the device process
        self.process = env.process(self.run())

    def add_output(self, device: 'Device'):
        """Add an output device for chaining.
        
        Args:
            device: Target device to send output to
        """
        self.outputs.append(device)

    def log_event(self, event_type: str, data: Optional[Dict[str, Any]] = None):
        """Log an event.
        
        Args:
            event_type: Type of event
            data: Optional event data
        """
        if self.logger:
            event_data = {
                "timestamp": self.env.now,
                "device": self.name,
                "event_type": event_type,
                "state": self.state,
                "data": data or {}
            }
            self.logger(event_data)

    def check_failure(self) -> bool:
        """Check if device fails based on failure probability.
        
        Returns:
            True if device fails, False otherwise
        """
        if self.failure_probability > 0 and random.random() < self.failure_probability:
            return True
        return False

    def run(self):
        """Main device process."""
        self.state = "running"
        self.log_event("started")
        
        try:
            while True:
                # Check for failure
                if self.check_failure():
                    self.failed = True
                    self.state = "failed"
                    self.log_event("failed", {"reason": "random_failure"})
                    break
                
                # Process device logic
                output_data = self.process_logic()
                
                # Log processing
                self.log_event("processed", {"output": output_data})
                
                # Send output to connected devices
                if output_data is not None:
                    self.send_output(output_data)
                
                # Wait for next interval
                yield self.env.timeout(self.interval)
                
        except simpy.Interrupt:
            self.state = "interrupted"
            self.log_event("interrupted")

    @abstractmethod
    def process_logic(self) -> Optional[Any]:
        """Device-specific processing logic.
        
        Returns:
            Output data to send to connected devices
        """
        pass

    def send_output(self, data: Any):
        """Send output to all connected devices.
        
        Args:
            data: Data to send
        """
        for output_device in self.outputs:
            output_device.receive_input(data, self.name)

    def receive_input(self, data: Any, source: str):
        """Receive input from another device.
        
        Args:
            data: Input data
            source: Source device name
        """
        self.log_event("received_input", {"source": source, "data": data})


class SensorDevice(Device):
    """Generic sensor device that generates readings."""

    def process_logic(self) -> Optional[Any]:
        """Generate sensor reading."""
        # Generate random reading based on config
        min_value = self.config.get("min_value", 0)
        max_value = self.config.get("max_value", 100)
        value = random.uniform(min_value, max_value)
        
        return {
            "type": "sensor_reading",
            "value": value,
            "unit": self.config.get("unit", "units")
        }


class ProcessorDevice(Device):
    """Generic processor device that processes inputs."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.input_buffer: List[Any] = []

    def receive_input(self, data: Any, source: str):
        """Store input in buffer."""
        super().receive_input(data, source)
        self.input_buffer.append({"source": source, "data": data, "time": self.env.now})

    def process_logic(self) -> Optional[Any]:
        """Process buffered inputs."""
        if self.input_buffer:
            # Simple processing: aggregate inputs
            count = len(self.input_buffer)
            self.input_buffer.clear()
            
            return {
                "type": "processed_data",
                "inputs_processed": count,
                "processor": self.name
            }
        return None


class ActuatorDevice(Device):
    """Generic actuator device that performs actions."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.actions_performed = 0

    def receive_input(self, data: Any, source: str):
        """Receive input and trigger action."""
        super().receive_input(data, source)
        self.actions_performed += 1

    def process_logic(self) -> Optional[Any]:
        """Perform actuator action."""
        if self.actions_performed > 0:
            return {
                "type": "actuator_action",
                "action": self.config.get("action_type", "default_action"),
                "count": self.actions_performed
            }
        return None


# Device type registry
DEVICE_TYPES = {
    "sensor": SensorDevice,
    "processor": ProcessorDevice,
    "actuator": ActuatorDevice,
}


def create_device(
    device_type: str,
    env: simpy.Environment,
    name: str,
    interval: float,
    failure_probability: float = 0.0,
    config: Optional[Dict[str, Any]] = None,
    logger: Optional[Callable] = None
) -> Device:
    """Factory function to create devices.
    
    Args:
        device_type: Type of device to create
        env: SimPy environment
        name: Device name
        interval: Processing interval
        failure_probability: Failure probability
        config: Device configuration
        logger: Logger function
        
    Returns:
        Created device instance
        
    Raises:
        ValueError: If device type is unknown
    """
    device_class = DEVICE_TYPES.get(device_type)
    if not device_class:
        raise ValueError(f"Unknown device type: {device_type}")
    
    return device_class(env, name, interval, failure_probability, config, logger)
