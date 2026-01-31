#!/usr/bin/env python3
"""
Staff Utilization Analysis Script
Analyzes staff utilization from simulation event logs.
"""

import json
import sys
from collections import defaultdict


def analyze_staff_utilization(filepath):
    """Analyze staff utilization from event log."""
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    events = data['events']
    metadata = data['simulation_metadata']
    staff_util = data.get('staff_utilization', {})
    
    print("=" * 70)
    print("STAFF UTILIZATION ANALYSIS")
    print("=" * 70)
    print(f"Generated: {metadata['generated_at']}")
    print(f"Total Events: {metadata['total_events']}")
    print()
    
    # Find simulation duration
    sim_duration = None
    for event in events:
        if event['event_type'] == 'simulation_end':
            sim_duration = event['timestamp']
            break
    
    if sim_duration:
        print(f"Simulation Duration: {sim_duration:.2f} seconds")
        print()
    
    if not staff_util:
        print("No staff utilization data found in the event log.")
        print("Make sure the configuration includes a 'staff' section.")
        return
    
    # Print staff utilization summary
    print("STAFF UTILIZATION SUMMARY")
    print("-" * 70)
    print(f"{'Staff Type':<20} {'Count':<8} {'Utilization':<15} {'Busy Time':<15} {'Allocations':<12}")
    print("-" * 70)
    
    for staff_type in sorted(staff_util.keys()):
        util = staff_util[staff_type]
        print(f"{staff_type:<20} {util['count']:<8} "
              f"{util['utilization_percentage']:<14.2f}% "
              f"{util['total_busy_time']:<14.2f}s "
              f"{util['allocations']:<12}")
    
    print()
    
    # Calculate average utilization
    if staff_util:
        avg_util = sum(u['utilization_percentage'] for u in staff_util.values()) / len(staff_util)
        print(f"Average Staff Utilization: {avg_util:.2f}%")
        print()
    
    # Analyze staff allocation events
    staff_allocations = defaultdict(list)
    for event in events:
        if event['event_type'] == 'staff_allocated':
            staff_type = event['details']['staff_type']
            staff_allocations[staff_type].append({
                'timestamp': event['timestamp'],
                'device': event['device_id']
            })
    
    print("STAFF ALLOCATION DETAILS")
    print("-" * 70)
    for staff_type in sorted(staff_allocations.keys()):
        allocations = staff_allocations[staff_type]
        print(f"\n{staff_type.upper()} ({len(allocations)} allocations):")
        
        # Group by device
        by_device = defaultdict(int)
        for alloc in allocations:
            by_device[alloc['device']] += 1
        
        for device in sorted(by_device.keys()):
            count = by_device[device]
            print(f"  - {device}: {count} allocation(s)")
    
    print()
    
    # Identify bottlenecks (high utilization)
    print("RESOURCE BOTTLENECK ANALYSIS")
    print("-" * 70)
    high_util_threshold = 70.0
    bottlenecks = []
    underutilized = []
    
    for staff_type, util in staff_util.items():
        if util['utilization_percentage'] >= high_util_threshold:
            bottlenecks.append((staff_type, util['utilization_percentage']))
        elif util['utilization_percentage'] < 20.0:
            underutilized.append((staff_type, util['utilization_percentage']))
    
    if bottlenecks:
        print("⚠ High Utilization (>= 70%) - Potential Bottlenecks:")
        for staff_type, util_pct in sorted(bottlenecks, key=lambda x: x[1], reverse=True):
            print(f"  - {staff_type}: {util_pct:.1f}%")
    else:
        print("✓ No high utilization detected (all staff < 70%)")
    
    print()
    
    if underutilized:
        print("ℹ Low Utilization (< 20%) - Consider Reducing Staff:")
        for staff_type, util_pct in sorted(underutilized, key=lambda x: x[1]):
            print(f"  - {staff_type}: {util_pct:.1f}%")
    else:
        print("✓ No low utilization detected (all staff >= 20%)")
    
    print("=" * 70)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python analyze_staff_utilization.py <path_to_event_log.json>")
        sys.exit(1)
    
    analyze_staff_utilization(sys.argv[1])
