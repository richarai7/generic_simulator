#!/usr/bin/env python3
"""
Example script to visualize simulation timeline.
Creates a simple text-based timeline of device execution.
"""

import json
import sys


def visualize_timeline(filepath, max_width=80):
    """Create a text-based timeline visualization of the simulation."""
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    events = data['events']
    
    # Find simulation duration
    sim_end = None
    for event in events:
        if event['event_type'] == 'simulation_end':
            sim_end = event['timestamp']
            break
    
    if not sim_end:
        print("Error: Could not find simulation end time")
        return
    
    # Collect device execution intervals
    device_intervals = {}
    device_starts = {}
    
    for event in events:
        device_id = event['device_id']
        if device_id == 'SYSTEM':
            continue
        
        event_type = event['event_type']
        timestamp = event['timestamp']
        
        if event_type == 'start':
            device_starts[device_id] = timestamp
        elif event_type in ['complete', 'failure']:
            if device_id in device_starts:
                start = device_starts[device_id]
                device_intervals[device_id] = (start, timestamp)
                del device_starts[device_id]
    
    # Print header
    print()
    print("=" * max_width)
    print("SIMULATION TIMELINE")
    print("=" * max_width)
    print(f"Total Duration: {sim_end:.2f} seconds")
    print()
    
    # Calculate scale
    timeline_width = max_width - 25  # Reserve space for device names
    scale = timeline_width / sim_end
    
    # Print timeline
    print(f"{'Device':<22} Timeline (0 to {sim_end:.1f}s)")
    print("-" * max_width)
    
    for device_id in sorted(device_intervals.keys()):
        start, end = device_intervals[device_id]
        
        # Calculate positions
        start_pos = int(start * scale)
        end_pos = int(end * scale)
        duration = end_pos - start_pos
        
        # Build timeline string
        timeline = ' ' * start_pos
        if duration > 0:
            timeline += '█' * duration
        else:
            timeline += '█'
        
        # Add marker
        marker = f" ({start:.1f}s - {end:.1f}s)"
        
        print(f"{device_id:<22} {timeline}{marker}")
    
    print("=" * max_width)
    print()
    
    # Print legend
    print("Legend: █ = Device active")
    print()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python visualize_timeline.py <path_to_event_log.json>")
        sys.exit(1)
    
    visualize_timeline(sys.argv[1])
