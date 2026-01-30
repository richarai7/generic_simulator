"""Tests for Simulator."""

import unittest
import tempfile
import os
import json
from pathlib import Path

from generic_simulator.simulator import Simulator
from generic_simulator.config_manager import ConfigManager


class TestSimulator(unittest.TestCase):
    """Test cases for Simulator."""

    def setUp(self):
        """Create test configuration."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        
        # Create test configuration
        manager = ConfigManager(self.db_path)
        config_id = manager.create_configuration("test_sim", "Test simulation")
        
        manager.add_device(config_id, "sensor1", "sensor", 5.0, 0.0, 
                          {"min_value": 0, "max_value": 100})
        manager.add_device(config_id, "processor1", "processor", 10.0, 0.0)
        manager.add_device(config_id, "actuator1", "actuator", 15.0, 0.0)
        
        manager.add_connection(config_id, "sensor1", "processor1")
        manager.add_connection(config_id, "processor1", "actuator1")
        
        self.config = manager.get_configuration(config_id)
        self.log_file = os.path.join(self.temp_dir, "test_log.json")

    def tearDown(self):
        """Clean up temporary files."""
        for file in [self.db_path, self.log_file]:
            if os.path.exists(file):
                os.remove(file)
        os.rmdir(self.temp_dir)

    def test_simulator_initialization(self):
        """Test simulator initializes correctly."""
        simulator = Simulator(self.config, self.log_file)
        
        self.assertEqual(len(simulator.devices), 3)
        self.assertIn("sensor1", simulator.devices)
        self.assertIn("processor1", simulator.devices)
        self.assertIn("actuator1", simulator.devices)

    def test_simulator_connections(self):
        """Test simulator sets up connections correctly."""
        simulator = Simulator(self.config, self.log_file)
        
        sensor = simulator.devices["sensor1"]
        processor = simulator.devices["processor1"]
        
        self.assertEqual(len(sensor.outputs), 1)
        self.assertEqual(sensor.outputs[0], processor)

    def test_simulator_run(self):
        """Test simulator runs and generates logs."""
        simulator = Simulator(self.config, self.log_file)
        simulator.run(until=50.0)
        
        # Check log file was created
        self.assertTrue(os.path.exists(self.log_file))
        
        # Check log contents
        with open(self.log_file, 'r') as f:
            log_data = json.load(f)
        
        self.assertIn("simulation_log", log_data)
        self.assertGreater(log_data["event_count"], 0)

    def test_simulator_device_states(self):
        """Test getting device states."""
        simulator = Simulator(self.config, self.log_file)
        simulator.run(until=30.0)
        
        states = simulator.get_device_states()
        
        self.assertEqual(len(states), 3)
        for device_name in ["sensor1", "processor1", "actuator1"]:
            self.assertIn(device_name, states)

    def test_simulator_with_failures(self):
        """Test simulator handles device failures."""
        # Create config with high failure probability
        manager = ConfigManager(self.db_path)
        config_id = manager.create_configuration("fail_test", "Failure test")
        manager.add_device(config_id, "failing_sensor", "sensor", 5.0, 0.5)
        
        config = manager.get_configuration(config_id)
        simulator = Simulator(config, self.log_file)
        simulator.run(until=100.0)
        
        # Check if failure was logged
        with open(self.log_file, 'r') as f:
            log_data = json.load(f)
        
        events = log_data["simulation_log"]
        # May or may not fail due to randomness, but should run without errors
        self.assertGreater(len(events), 0)


if __name__ == "__main__":
    unittest.main()
