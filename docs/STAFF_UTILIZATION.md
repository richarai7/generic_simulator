# Staff Utilization Feature - Implementation Summary

## Overview

The Generic SimPy Simulator now includes comprehensive staff utilization tracking, allowing users to:
- Define shared staff resources (technicians, nurses, specialists, etc.)
- Assign staff requirements to devices
- Track staff allocation and release events
- Calculate utilization metrics
- Identify bottlenecks and optimization opportunities

## What Was Added

### 1. Core Simulation Engine (`src/simulator.py`)

**Staff Resource Management:**
- Staff resources defined globally in config
- SimPy Resource objects manage staff availability
- Devices wait for staff if all are busy
- Automatic allocation/release tracking

**New Features:**
- `staff_resources`: Dict of SimPy resources by staff type
- `staff_config`: Staff counts by type
- `staff_utilization_data`: Tracks allocation periods
- `_load_staff()`: Loads staff from config
- `_calculate_staff_utilization()`: Computes metrics

**Device Process Updates:**
- Staff allocated before device execution
- Staff released after completion or failure
- Events logged for all allocations/releases

### 2. Configuration Schema

**Global Staff Section:**
```json
"staff": {
  "technician": 3,
  "nurse": 2,
  "quality_specialist": 1
}
```

**Device Staff Requirements:**
```json
"staff_required": {
  "technician": 2,
  "nurse": 1
}
```

### 3. Event Logging

**New Event Types:**
- `staff_allocated`: When staff is assigned to a device
- `staff_released`: When staff is freed from a device

**Event Structure:**
```json
{
  "timestamp": 26.92,
  "device_id": "pooling",
  "event_type": "staff_allocated",
  "details": {
    "job_id": 1,
    "staff_type": "technician",
    "staff_index": 0,
    "total_count": 2
  }
}
```

### 4. Staff Utilization Metrics

**Metrics Calculated:**
- Utilization percentage: (busy time / available time) × 100
- Total busy time: Sum of all allocation durations
- Total available time: Staff count × simulation duration
- Allocation count: Number of times staff was assigned

**Output Format:**
```json
"staff_utilization": {
  "technician": {
    "count": 3,
    "total_busy_time": 56.95,
    "total_available_time": 530.47,
    "utilization_percentage": 10.74,
    "allocations": 4
  }
}
```

### 5. Analysis Scripts

**Updated `examples/analyze_log.py`:**
- Now displays staff utilization if available
- Maintains backward compatibility

**New `examples/analyze_staff_utilization.py`:**
- Detailed staff utilization analysis
- Allocation breakdown by device
- Bottleneck detection (>70% utilization)
- Over-staffing alerts (<20% utilization)
- Optimization recommendations

### 6. Sample Configurations

**`configs/platelet_pooling_with_staff.json`:**
- 3 technicians, 2 nurses, 2 quality specialists
- Staff assigned to appropriate devices
- Demonstrates realistic healthcare workflow

**`configs/platelet_understaffed.json`:**
- Minimal staffing (1 of each type)
- Shows higher utilization percentages
- Useful for bottleneck analysis

### 7. Documentation Updates

**CONFIG_REFERENCE.md:**
- Staff configuration section
- Staff assignment patterns
- Utilization metrics explanation
- Bottleneck detection guidelines

**README.md:**
- Staff utilization in key features
- Updated config examples
- Analysis examples
- Event types updated

**QUICKSTART.md:**
- Quick staff utilization demo
- Analysis command examples

## Usage Examples

### Basic Staff Configuration

```json
{
  "name": "My Process",
  "staff": {
    "operator": 2,
    "supervisor": 1
  },
  "devices": [
    {
      "id": "device1",
      "staff_required": {
        "operator": 1
      }
    }
  ]
}
```

### Running with Staff

```bash
# Run simulation
python main.py -c configs/platelet_pooling_with_staff.json -o outputs/results.json

# View device and staff statistics
python examples/analyze_log.py outputs/results.json

# Detailed staff analysis
python examples/analyze_staff_utilization.py outputs/results.json
```

### Analysis Output

```
STAFF UTILIZATION SUMMARY
----------------------------------------------------------------------
Staff Type           Count    Utilization     Busy Time       Allocations 
----------------------------------------------------------------------
nurse                2        8.97          % 29.72         s 1           
quality_specialist   2        3.42          % 11.33         s 2           
technician           3        11.35         % 56.38         s 4           

Average Staff Utilization: 7.91%

RESOURCE BOTTLENECK ANALYSIS
----------------------------------------------------------------------
✓ No high utilization detected (all staff < 70%)

ℹ Low Utilization (< 20%) - Consider Reducing Staff:
  - quality_specialist: 3.4%
  - nurse: 9.0%
  - technician: 11.3%
```

## Key Benefits

1. **Resource Optimization**: Identify over-staffing and under-staffing
2. **Bottleneck Detection**: Find constraints limiting throughput
3. **What-if Analysis**: Test different staffing scenarios
4. **Cost Analysis**: Link utilization to labor costs
5. **Capacity Planning**: Plan for growth with data

## Backward Compatibility

- Configurations without staff continue to work
- No breaking changes to existing functionality
- Staff features are purely additive
- Legacy configs produce identical results

## Future Enhancements

Potential improvements:
- Multiple job simulation (batch processing)
- Staff shift scheduling
- Staff skill levels and cross-training
- Real-time staff monitoring dashboard
- Staff fatigue modeling
- Break time allocation

## Technical Notes

- Staff resources use SimPy Resource with capacity = count
- Staff allocation is FIFO (first-in-first-out)
- Staff is allocated before device START state
- Staff is released after device EXIT state (or on failure)
- Utilization tracks actual busy time vs. total available time
- Zero-count staff types are rejected during validation

## Testing

All features tested with:
- ✅ Single job simulations
- ✅ Parallel device execution
- ✅ Device failures (staff released properly)
- ✅ Various staffing levels
- ✅ Backward compatibility (no staff config)
- ✅ Utilization calculations
- ✅ Analysis scripts

## Files Changed

**Core:**
- `src/simulator.py`: Staff resource management, tracking, metrics

**Configuration:**
- `configs/platelet_pooling_with_staff.json`: Main example
- `configs/platelet_understaffed.json`: Bottleneck scenario

**Analysis:**
- `examples/analyze_log.py`: Added staff utilization display
- `examples/analyze_staff_utilization.py`: New detailed analysis

**Documentation:**
- `README.md`: Feature overview and examples
- `docs/CONFIG_REFERENCE.md`: Complete staff reference
- `QUICKSTART.md`: Quick start with staff

## Conclusion

The staff utilization feature is a powerful addition that enables:
- Data-driven workforce optimization
- Process improvement insights
- Resource constraint identification
- Cost-effective capacity planning

All while maintaining the simplicity and flexibility of the config-driven approach.
