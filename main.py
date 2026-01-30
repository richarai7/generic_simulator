#!/usr/bin/env python3
"""
Generic Simulation CLI
Provides command-line interface to run simulations from config files.
"""

import argparse
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from simulator import Simulator, load_config


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generic SimPy-based Simulation Environment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --config configs/platelet_pooling.json --output outputs/results.json
  %(prog)s -c configs/my_process.json -o outputs/my_results.json --max-time 1000
        """
    )
    
    parser.add_argument(
        "-c", "--config",
        required=True,
        help="Path to the JSON configuration file"
    )
    
    parser.add_argument(
        "-o", "--output",
        required=True,
        help="Path to the output JSON event log file"
    )
    
    parser.add_argument(
        "--max-time",
        type=float,
        default=None,
        help="Maximum simulation time (optional). If not set, runs until completion."
    )
    
    args = parser.parse_args()
    
    # Validate config file exists
    if not os.path.exists(args.config):
        print(f"Error: Config file not found: {args.config}", file=sys.stderr)
        sys.exit(1)
    
    # Ensure output directory exists
    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Load configuration
        print(f"Loading configuration from: {args.config}")
        config = load_config(args.config)
        
        # Create and run simulator
        print("Initializing simulator...")
        simulator = Simulator(config)
        
        print(f"Running simulation (max_time={args.max_time or 'unlimited'})...")
        simulator.run(max_time=args.max_time)
        
        # Save results
        print(f"Saving event log to: {args.output}")
        simulator.save_events(args.output)
        
        print("Simulation completed successfully!")
        print(f"Total events logged: {len(simulator.event_logger.events)}")
        
    except Exception as e:
        print(f"Error during simulation: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
