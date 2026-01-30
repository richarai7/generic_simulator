"""Command-line interface for the generic simulator."""

import argparse
import sys
from pathlib import Path

from .config_manager import ConfigManager
from .simulator import run_simulation


def list_configs(args):
    """List all available configurations."""
    manager = ConfigManager(args.config_db)
    configs = manager.list_configurations()
    
    if not configs:
        print("No configurations found in database.")
        return
    
    print(f"\nAvailable configurations in {args.config_db}:")
    print("-" * 80)
    for config in configs:
        print(f"ID: {config['id']}")
        print(f"  Name: {config['name']}")
        print(f"  Description: {config['description']}")
        print(f"  Created: {config['created_at']}")
        print()


def show_config(args):
    """Show details of a specific configuration."""
    manager = ConfigManager(args.config_db)
    
    try:
        if args.config_id:
            config = manager.get_configuration(args.config_id)
        else:
            config = manager.get_configuration_by_name(args.name)
        
        print(f"\nConfiguration: {config['name']}")
        print(f"Description: {config['description']}")
        print(f"\nDevices ({len(config['devices'])}):")
        print("-" * 80)
        
        for device in config['devices']:
            print(f"  {device['name']} ({device['type']})")
            print(f"    Interval: {device['interval']}s")
            print(f"    Failure Probability: {device['failure_probability']}")
            if device['config']:
                print(f"    Config: {device['config']}")
        
        print(f"\nConnections ({len(config['connections'])}):")
        print("-" * 80)
        
        for conn in config['connections']:
            print(f"  {conn['source']} -> {conn['target']}")
        
        print()
        
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def run_config(args):
    """Run a simulation configuration."""
    try:
        print(f"Running configuration: {args.name}")
        print(f"Duration: {args.duration} time units")
        print()
        
        simulator = run_simulation(
            config_path=args.config_db,
            config_name=args.name,
            duration=args.duration
        )
        
        print("\nDevice Final States:")
        print("-" * 80)
        for device_name, state in simulator.get_device_states().items():
            print(f"  {device_name}: {state}")
        
    except Exception as e:
        print(f"Error running simulation: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generic Device Simulator - SimPy-based simulation framework"
    )
    
    parser.add_argument(
        "--config-db",
        default="configs/simulator.db",
        help="Path to SQLite configuration database (default: configs/simulator.db)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List available configurations")
    list_parser.set_defaults(func=list_configs)
    
    # Show command
    show_parser = subparsers.add_parser("show", help="Show configuration details")
    show_group = show_parser.add_mutually_exclusive_group(required=True)
    show_group.add_argument("--name", help="Configuration name")
    show_group.add_argument("--config-id", type=int, help="Configuration ID")
    show_parser.set_defaults(func=show_config)
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run a simulation")
    run_parser.add_argument("name", help="Configuration name to run")
    run_parser.add_argument(
        "--duration",
        type=float,
        default=100.0,
        help="Simulation duration in time units (default: 100.0)"
    )
    run_parser.set_defaults(func=run_config)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    args.func(args)


if __name__ == "__main__":
    main()
