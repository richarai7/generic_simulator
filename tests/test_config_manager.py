"""Tests for ConfigManager."""

import unittest
import tempfile
import os
from pathlib import Path

from generic_simulator.config_manager import ConfigManager


class TestConfigManager(unittest.TestCase):
    """Test cases for ConfigManager."""

    def setUp(self):
        """Create temporary database for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.manager = ConfigManager(self.db_path)

    def tearDown(self):
        """Clean up temporary files."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)

    def test_create_configuration(self):
        """Test creating a configuration."""
        config_id = self.manager.create_configuration(
            name="test_config",
            description="Test configuration"
        )
        self.assertIsInstance(config_id, int)
        self.assertGreater(config_id, 0)

    def test_add_device(self):
        """Test adding a device to configuration."""
        config_id = self.manager.create_configuration("test", "Test")
        
        self.manager.add_device(
            config_id,
            device_name="sensor1",
            device_type="sensor",
            interval=5.0,
            failure_probability=0.05,
            config={"min": 0, "max": 100}
        )
        
        config = self.manager.get_configuration(config_id)
        self.assertEqual(len(config["devices"]), 1)
        self.assertEqual(config["devices"][0]["name"], "sensor1")

    def test_add_connection(self):
        """Test adding a connection between devices."""
        config_id = self.manager.create_configuration("test", "Test")
        
        self.manager.add_device(config_id, "sensor1", "sensor", 5.0)
        self.manager.add_device(config_id, "processor1", "processor", 10.0)
        self.manager.add_connection(config_id, "sensor1", "processor1")
        
        config = self.manager.get_configuration(config_id)
        self.assertEqual(len(config["connections"]), 1)
        self.assertEqual(config["connections"][0]["source"], "sensor1")
        self.assertEqual(config["connections"][0]["target"], "processor1")

    def test_list_configurations(self):
        """Test listing configurations."""
        self.manager.create_configuration("config1", "First")
        self.manager.create_configuration("config2", "Second")
        
        configs = self.manager.list_configurations()
        self.assertEqual(len(configs), 2)

    def test_get_configuration_by_name(self):
        """Test getting configuration by name."""
        self.manager.create_configuration("test_config", "Test")
        
        config = self.manager.get_configuration_by_name("test_config")
        self.assertEqual(config["name"], "test_config")

    def test_get_nonexistent_configuration(self):
        """Test getting non-existent configuration raises error."""
        with self.assertRaises(ValueError):
            self.manager.get_configuration(9999)

    def test_device_config_json(self):
        """Test device configuration is stored and retrieved as JSON."""
        config_id = self.manager.create_configuration("test", "Test")
        
        device_config = {"min_value": 10, "max_value": 50, "unit": "celsius"}
        self.manager.add_device(
            config_id,
            "sensor1",
            "sensor",
            5.0,
            config=device_config
        )
        
        config = self.manager.get_configuration(config_id)
        retrieved_config = config["devices"][0]["config"]
        self.assertEqual(retrieved_config, device_config)


if __name__ == "__main__":
    unittest.main()
