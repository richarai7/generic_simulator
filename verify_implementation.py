#!/usr/bin/env python3
"""
Verification script for the Generic Simulator implementation.
This script demonstrates all major features and verifies they work correctly.
"""

import sys
import json
from pathlib import Path

def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def verify_imports():
    """Verify all modules can be imported."""
    print_header("1. Verifying Module Imports")
    
    try:
        from generic_simulator import Device, Simulator, ConfigManager
        from generic_simulator.device import SensorDevice, ProcessorDevice, ActuatorDevice
        from generic_simulator.event_logger import EventLogger
        from generic_simulator.simulator import run_simulation
        print("✅ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def verify_database():
    """Verify database configuration."""
    print_header("2. Verifying Database Configuration")
    
    try:
        from generic_simulator.config_manager import ConfigManager
        
        db_path = "configs/simulator.db"
        if not Path(db_path).exists():
            print(f"⚠️  Database not found at {db_path}")
            print("   Run: python examples/create_examples.py")
            return False
        
        manager = ConfigManager(db_path)
        configs = manager.list_configurations()
        
        print(f"✅ Database loaded: {len(configs)} configurations found")
        for config in configs:
            print(f"   - {config['name']}: {config['description']}")
        
        return len(configs) > 0
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return False

def verify_configuration():
    """Verify configuration loading."""
    print_header("3. Verifying Configuration Loading")
    
    try:
        from generic_simulator.config_manager import ConfigManager
        
        manager = ConfigManager("configs/simulator.db")
        config = manager.get_configuration_by_name("simple_chain")
        
        print(f"✅ Configuration loaded: {config['name']}")
        print(f"   Devices: {len(config['devices'])}")
        print(f"   Connections: {len(config['connections'])}")
        
        return True
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False

def verify_simulation():
    """Verify simulation execution."""
    print_header("4. Verifying Simulation Execution")
    
    try:
        from generic_simulator import Simulator, ConfigManager
        
        manager = ConfigManager("configs/simulator.db")
        config = manager.get_configuration_by_name("simple_chain")
        
        log_file = "/tmp/verification_test.json"
        simulator = Simulator(config, log_file=log_file)
        simulator.run(until=30.0)
        
        # Verify log file
        with open(log_file, 'r') as f:
            log_data = json.load(f)
        
        events = log_data["simulation_log"]
        event_count = log_data["event_count"]
        
        print(f"✅ Simulation completed successfully")
        print(f"   Events logged: {event_count}")
        print(f"   Log file: {log_file}")
        
        # Clean up
        Path(log_file).unlink()
        
        return event_count > 0
    except Exception as e:
        print(f"❌ Simulation execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_device_types():
    """Verify all device types work."""
    print_header("5. Verifying Device Types")
    
    try:
        import simpy
        from generic_simulator.device import SensorDevice, ProcessorDevice, ActuatorDevice
        
        env = simpy.Environment()
        events = []
        
        # Create devices
        sensor = SensorDevice(env, "test_sensor", 5.0, logger=lambda e: events.append(e))
        processor = ProcessorDevice(env, "test_processor", 10.0, logger=lambda e: events.append(e))
        actuator = ActuatorDevice(env, "test_actuator", 15.0, logger=lambda e: events.append(e))
        
        # Connect them
        sensor.add_output(processor)
        processor.add_output(actuator)
        
        # Run simulation
        env.run(until=30)
        
        print(f"✅ All device types working")
        print(f"   Sensor events: {len([e for e in events if e.get('device') == 'test_sensor'])}")
        print(f"   Processor events: {len([e for e in events if e.get('device') == 'test_processor'])}")
        print(f"   Actuator events: {len([e for e in events if e.get('device') == 'test_actuator'])}")
        
        return len(events) > 0
    except Exception as e:
        print(f"❌ Device type verification failed: {e}")
        return False

def verify_event_logging():
    """Verify event logging functionality."""
    print_header("6. Verifying Event Logging")
    
    try:
        from generic_simulator.event_logger import EventLogger
        
        log_file = "/tmp/test_logger.json"
        logger = EventLogger(log_file)
        
        # Log some events
        logger.log({"event_type": "test", "data": "test1"})
        logger.log({"event_type": "test", "data": "test2"})
        logger.save()
        
        # Verify
        with open(log_file, 'r') as f:
            data = json.load(f)
        
        print(f"✅ Event logging working")
        print(f"   Events logged: {data['event_count']}")
        print(f"   Log file created: {log_file}")
        
        # Clean up
        Path(log_file).unlink()
        
        return data['event_count'] == 2
    except Exception as e:
        print(f"❌ Event logging failed: {e}")
        return False

def verify_output_chaining():
    """Verify output chaining works."""
    print_header("7. Verifying Output Chaining")
    
    try:
        import simpy
        from generic_simulator.device import SensorDevice, ProcessorDevice
        
        env = simpy.Environment()
        events = []
        
        # Create devices
        sensor = SensorDevice(env, "sensor", 5.0, logger=lambda e: events.append(e))
        processor1 = ProcessorDevice(env, "proc1", 10.0, logger=lambda e: events.append(e))
        processor2 = ProcessorDevice(env, "proc2", 10.0, logger=lambda e: events.append(e))
        
        # Setup chaining: sensor -> proc1 and sensor -> proc2
        sensor.add_output(processor1)
        sensor.add_output(processor2)
        
        # Run
        env.run(until=20)
        
        # Check that both processors received inputs
        proc1_inputs = [e for e in events if e.get('device') == 'proc1' and e.get('event_type') == 'received_input']
        proc2_inputs = [e for e in events if e.get('device') == 'proc2' and e.get('event_type') == 'received_input']
        
        print(f"✅ Output chaining working")
        print(f"   Processor 1 received: {len(proc1_inputs)} inputs")
        print(f"   Processor 2 received: {len(proc2_inputs)} inputs")
        
        return len(proc1_inputs) > 0 and len(proc2_inputs) > 0
    except Exception as e:
        print(f"❌ Output chaining failed: {e}")
        return False

def verify_failure_simulation():
    """Verify failure simulation works."""
    print_header("8. Verifying Failure Simulation")
    
    try:
        import simpy
        from generic_simulator.device import SensorDevice
        
        env = simpy.Environment()
        events = []
        
        # Create device with 100% failure probability
        sensor = SensorDevice(
            env, 
            "failing_sensor", 
            5.0, 
            failure_probability=1.0,  # Will fail immediately
            logger=lambda e: events.append(e)
        )
        
        # Run
        env.run(until=20)
        
        # Check for failure event
        failures = [e for e in events if e.get('event_type') == 'failed']
        
        print(f"✅ Failure simulation working")
        print(f"   Failure events: {len(failures)}")
        if failures:
            print(f"   Failed at time: {failures[0]['timestamp']}")
        
        return len(failures) > 0
    except Exception as e:
        print(f"❌ Failure simulation failed: {e}")
        return False

def main():
    """Run all verification tests."""
    print("\n╔════════════════════════════════════════════════════════════════╗")
    print("║  Generic Simulator - Comprehensive Verification Suite         ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    
    results = []
    
    results.append(("Module Imports", verify_imports()))
    results.append(("Database Configuration", verify_database()))
    results.append(("Configuration Loading", verify_configuration()))
    results.append(("Simulation Execution", verify_simulation()))
    results.append(("Device Types", verify_device_types()))
    results.append(("Event Logging", verify_event_logging()))
    results.append(("Output Chaining", verify_output_chaining()))
    results.append(("Failure Simulation", verify_failure_simulation()))
    
    # Print summary
    print_header("Verification Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:8} - {name}")
    
    print("\n" + "=" * 70)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL VERIFICATIONS PASSED - Implementation is complete!")
        print("\n💡 Quick start:")
        print("   $ generic-simulator list")
        print("   $ generic-simulator run simple_chain --duration 100")
        return 0
    else:
        print(f"\n⚠️  {total - passed} verification(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
