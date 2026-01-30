"""Create example configurations in the database."""

from pathlib import Path
from generic_simulator.config_manager import ConfigManager


def create_example_configs(db_path: str = "configs/simulator.db"):
    """Create example simulation configurations."""
    
    # Ensure configs directory exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    manager = ConfigManager(db_path)
    
    # Example 1: Simple sensor-processor chain
    print("Creating Example 1: Simple Sensor-Processor Chain")
    config1_id = manager.create_configuration(
        name="simple_chain",
        description="A simple chain of sensor -> processor -> actuator"
    )
    
    # Add devices
    manager.add_device(
        config1_id,
        device_name="temperature_sensor",
        device_type="sensor",
        interval=5.0,
        failure_probability=0.05,
        config={"min_value": 15.0, "max_value": 30.0, "unit": "celsius"}
    )
    
    manager.add_device(
        config1_id,
        device_name="data_processor",
        device_type="processor",
        interval=10.0,
        failure_probability=0.02,
        config={}
    )
    
    manager.add_device(
        config1_id,
        device_name="hvac_actuator",
        device_type="actuator",
        interval=15.0,
        failure_probability=0.01,
        config={"action_type": "adjust_temperature"}
    )
    
    # Add connections
    manager.add_connection(config1_id, "temperature_sensor", "data_processor")
    manager.add_connection(config1_id, "data_processor", "hvac_actuator")
    
    print(f"  Created configuration ID: {config1_id}")
    
    # Example 2: Multiple sensors to one processor
    print("\nCreating Example 2: Multi-Sensor Network")
    config2_id = manager.create_configuration(
        name="multi_sensor",
        description="Multiple sensors feeding into a central processor"
    )
    
    # Add multiple sensors
    for i in range(3):
        manager.add_device(
            config2_id,
            device_name=f"sensor_{i+1}",
            device_type="sensor",
            interval=5.0 + i,
            failure_probability=0.03,
            config={"min_value": 0.0, "max_value": 100.0, "unit": "units"}
        )
    
    # Add central processor
    manager.add_device(
        config2_id,
        device_name="central_processor",
        device_type="processor",
        interval=8.0,
        failure_probability=0.01,
        config={}
    )
    
    # Add output actuators
    manager.add_device(
        config2_id,
        device_name="actuator_1",
        device_type="actuator",
        interval=12.0,
        failure_probability=0.02,
        config={"action_type": "action_A"}
    )
    
    manager.add_device(
        config2_id,
        device_name="actuator_2",
        device_type="actuator",
        interval=12.0,
        failure_probability=0.02,
        config={"action_type": "action_B"}
    )
    
    # Create connections: all sensors -> processor -> both actuators
    for i in range(3):
        manager.add_connection(config2_id, f"sensor_{i+1}", "central_processor")
    
    manager.add_connection(config2_id, "central_processor", "actuator_1")
    manager.add_connection(config2_id, "central_processor", "actuator_2")
    
    print(f"  Created configuration ID: {config2_id}")
    
    # Example 3: Complex network with parallel paths
    print("\nCreating Example 3: Complex Network")
    config3_id = manager.create_configuration(
        name="complex_network",
        description="Complex network with multiple paths and processors"
    )
    
    # Primary sensors
    manager.add_device(
        config3_id,
        device_name="pressure_sensor",
        device_type="sensor",
        interval=3.0,
        failure_probability=0.04,
        config={"min_value": 0.0, "max_value": 100.0, "unit": "psi"}
    )
    
    manager.add_device(
        config3_id,
        device_name="flow_sensor",
        device_type="sensor",
        interval=4.0,
        failure_probability=0.04,
        config={"min_value": 0.0, "max_value": 50.0, "unit": "l/min"}
    )
    
    # Multiple processors
    manager.add_device(
        config3_id,
        device_name="processor_A",
        device_type="processor",
        interval=7.0,
        failure_probability=0.02,
        config={}
    )
    
    manager.add_device(
        config3_id,
        device_name="processor_B",
        device_type="processor",
        interval=9.0,
        failure_probability=0.02,
        config={}
    )
    
    # Final actuator
    manager.add_device(
        config3_id,
        device_name="main_actuator",
        device_type="actuator",
        interval=15.0,
        failure_probability=0.01,
        config={"action_type": "control_system"}
    )
    
    # Create complex connections
    manager.add_connection(config3_id, "pressure_sensor", "processor_A")
    manager.add_connection(config3_id, "pressure_sensor", "processor_B")
    manager.add_connection(config3_id, "flow_sensor", "processor_B")
    manager.add_connection(config3_id, "processor_A", "main_actuator")
    manager.add_connection(config3_id, "processor_B", "main_actuator")
    
    print(f"  Created configuration ID: {config3_id}")
    
    print(f"\nExample configurations created successfully in {db_path}")
    print("\nYou can now run:")
    print("  generic-simulator list")
    print("  generic-simulator show --name simple_chain")
    print("  generic-simulator run simple_chain --duration 100")


if __name__ == "__main__":
    create_example_configs()
