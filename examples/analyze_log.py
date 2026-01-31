#!/usr/bin/env python3
"""
Example script to analyze simulation event logs.
Demonstrates how to process the JSON output for insights.
"""

import json
import sys
from collections import defaultdict


def analyze_event_log(filepath):
    """Analyze a simulation event log and print statistics."""
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    events = data['events']
    metadata = data['simulation_metadata']
    
    print("=" * 60)
    print("SIMULATION ANALYSIS")
    print("=" * 60)
    print(f"Generated: {metadata['generated_at']}")
    print(f"Total Events: {metadata['total_events']}")
    print()
    
    # Find simulation duration
    sim_start = None
    sim_end = None
    for event in events:
        if event['event_type'] == 'simulation_start':
            sim_start = event['timestamp']
        elif event['event_type'] == 'simulation_end':
            sim_end = event['timestamp']
    
    if sim_start is not None and sim_end is not None:
        print(f"Simulation Duration: {sim_end - sim_start:.2f} seconds")
        print()
    
    # Device statistics
    device_stats = defaultdict(lambda: {
        'starts': 0,
        'completes': 0,
        'failures': 0,
        'total_execution_time': 0.0,
        'execution_count': 0
    })
    
    for event in events:
        device_id = event['device_id']
        event_type = event['event_type']
        
        if event_type == 'start':
            device_stats[device_id]['starts'] += 1
        elif event_type == 'complete':
            device_stats[device_id]['completes'] += 1
        elif event_type == 'failure':
            device_stats[device_id]['failures'] += 1
        elif event_type == 'execution_start':
            duration = event['details'].get('duration', 0)
            device_stats[device_id]['total_execution_time'] += duration
            device_stats[device_id]['execution_count'] += 1
    
    # Print device statistics
    print("DEVICE STATISTICS")
    print("-" * 60)
    print(f"{'Device ID':<20} {'Starts':<8} {'Completes':<10} {'Failures':<10} {'Avg Exec Time':<15}")
    print("-" * 60)
    
    for device_id in sorted(device_stats.keys()):
        if device_id == 'SYSTEM':
            continue
        
        stats = device_stats[device_id]
        avg_exec = (stats['total_execution_time'] / stats['execution_count'] 
                   if stats['execution_count'] > 0 else 0)
        
        print(f"{device_id:<20} {stats['starts']:<8} {stats['completes']:<10} "
              f"{stats['failures']:<10} {avg_exec:<15.2f}")
    
    print()
    
    # Calculate success rate
    total_starts = sum(stats['starts'] for did, stats in device_stats.items() if did != 'SYSTEM')
    total_failures = sum(stats['failures'] for did, stats in device_stats.items() if did != 'SYSTEM')
    
    if total_starts > 0:
        success_rate = ((total_starts - total_failures) / total_starts) * 100
        print(f"Overall Success Rate: {success_rate:.1f}%")
        print(f"Total Failures: {total_failures}")
    
    print("=" * 60)
    
    # Show staff utilization if available
    staff_util = data.get('staff_utilization', {})
    if staff_util:
        print()
        print("STAFF UTILIZATION")
        print("-" * 60)
        print(f"{'Staff Type':<20} {'Count':<8} {'Utilization':<15} {'Allocations':<12}")
        print("-" * 60)
        
        for staff_type in sorted(staff_util.keys()):
            util = staff_util[staff_type]
            print(f"{staff_type:<20} {util['count']:<8} "
                  f"{util['utilization_percentage']:<14.2f}% "
                  f"{util['allocations']:<12}")
        
        print("=" * 60)
    else:
        print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python analyze_log.py <path_to_event_log.json>")
        sys.exit(1)
    
    analyze_event_log(sys.argv[1])
