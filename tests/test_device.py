"""Tests for Device models."""

import unittest
import simpy

from generic_simulator.device import Device, SensorDevice, ProcessorDevice, ActuatorDevice, create_device


class MockDevice(Device):
    """Mock device for testing."""
    
    def process_logic(self):
        return {"test": "data"}


class TestDevice(unittest.TestCase):
    """Test cases for Device base class."""

    def setUp(self):
        """Create SimPy environment."""
        self.env = simpy.Environment()
        self.logged_events = []

    def log_event(self, event):
        """Store logged events."""
        self.logged_events.append(event)

    def test_device_initialization(self):
        """Test device initialization."""
        device = MockDevice(
            self.env,
            name="test_device",
            interval=5.0,
            failure_probability=0.0,
            logger=self.log_event
        )
        
        self.assertEqual(device.name, "test_device")
        self.assertEqual(device.interval, 5.0)
        self.assertEqual(device.state, "initialized")

    def test_device_runs(self):
        """Test device runs process."""
        device = MockDevice(
            self.env,
            name="test_device",
            interval=10.0,
            failure_probability=0.0,
            logger=self.log_event
        )
        
        # Run for 25 time units (should process 2 times)
        self.env.run(until=25)
        
        # Check that events were logged
        self.assertGreater(len(self.logged_events), 0)
        
        # Check started event
        started_events = [e for e in self.logged_events if e["event_type"] == "started"]
        self.assertEqual(len(started_events), 1)

    def test_output_chaining(self):
        """Test output chaining between devices."""
        device1 = MockDevice(self.env, "device1", 10.0, logger=self.log_event)
        device2 = MockDevice(self.env, "device2", 15.0, logger=self.log_event)
        
        device1.add_output(device2)
        
        self.assertEqual(len(device1.outputs), 1)
        self.assertEqual(device1.outputs[0], device2)

    def test_sensor_device(self):
        """Test SensorDevice generates readings."""
        sensor = SensorDevice(
            self.env,
            name="temp_sensor",
            interval=5.0,
            config={"min_value": 10, "max_value": 20, "unit": "celsius"},
            logger=self.log_event
        )
        
        self.env.run(until=10)
        
        # Check processed events
        processed = [e for e in self.logged_events if e["event_type"] == "processed"]
        self.assertGreater(len(processed), 0)
        
        # Check output data format
        output = processed[0]["data"]["output"]
        self.assertEqual(output["type"], "sensor_reading")
        self.assertIn("value", output)
        self.assertEqual(output["unit"], "celsius")

    def test_processor_device(self):
        """Test ProcessorDevice processes inputs."""
        processor = ProcessorDevice(
            self.env,
            name="processor1",
            interval=10.0,
            logger=self.log_event
        )
        
        # Send some inputs
        processor.receive_input({"data": "test1"}, "sensor1")
        processor.receive_input({"data": "test2"}, "sensor2")
        
        self.env.run(until=15)
        
        # Check that inputs were received
        received = [e for e in self.logged_events if e["event_type"] == "received_input"]
        self.assertEqual(len(received), 2)

    def test_actuator_device(self):
        """Test ActuatorDevice performs actions."""
        actuator = ActuatorDevice(
            self.env,
            name="actuator1",
            interval=10.0,
            config={"action_type": "test_action"},
            logger=self.log_event
        )
        
        # Send input to trigger action
        actuator.receive_input({"command": "execute"}, "processor1")
        
        self.env.run(until=15)
        
        # Check action was logged
        processed = [e for e in self.logged_events if e["event_type"] == "processed"]
        self.assertGreater(len(processed), 0)

    def test_device_factory(self):
        """Test device factory creates correct types."""
        sensor = create_device("sensor", self.env, "s1", 5.0)
        self.assertIsInstance(sensor, SensorDevice)
        
        processor = create_device("processor", self.env, "p1", 10.0)
        self.assertIsInstance(processor, ProcessorDevice)
        
        actuator = create_device("actuator", self.env, "a1", 15.0)
        self.assertIsInstance(actuator, ActuatorDevice)

    def test_device_factory_unknown_type(self):
        """Test device factory raises error for unknown type."""
        with self.assertRaises(ValueError):
            create_device("unknown_type", self.env, "device", 5.0)


if __name__ == "__main__":
    unittest.main()
