# Configuration File Reference

This document provides a complete reference for creating simulation configuration files.

## File Format

Configuration files are JSON documents with the following top-level structure:

```json
{
  "name": "Process Name",
  "description": "Description of the process",
  "version": "1.0",
  "devices": [
    // Array of device objects
  ]
}
```

## Device Configuration

Each device in the `devices` array has the following structure:

### Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | string | Unique identifier for the device. Must be unique across all devices. | `"collection"` |
| `type` | string | Type/category of the device (for documentation/grouping). | `"collection_station"` |
| `wait_start` | number | Minimum time (seconds) device waits before starting execution. | `2.0` |
| `wait_execution_min` | number | Minimum execution time (seconds). | `15.0` |
| `wait_execution_max` | number | Maximum execution time (seconds). Actual time is random between min and max. | `30.0` |
| `wait_exit` | number | Minimum time (seconds) device waits after execution completes. | `1.0` |
| `fail_prob` | number | Probability of failure (0.0 to 1.0). 0.0 = never fails, 1.0 = always fails. | `0.01` |
| `outputs` | array of strings | List of device IDs that this device triggers upon completion. Empty array if no downstream devices. | `["quality_check_1"]` |

### Device Example

```json
{
  "id": "collection",
  "type": "collection_station",
  "wait_start": 2.0,
  "wait_execution_min": 15.0,
  "wait_execution_max": 30.0,
  "wait_exit": 1.0,
  "fail_prob": 0.01,
  "outputs": ["quality_check_1"]
}
```

## Device Timing Behavior

Each device goes through three states in sequence:

1. **START** (wait_start)
   - Fixed duration wait before execution
   - Use for setup, preparation time
   
2. **EXECUTION** (wait_execution_min to wait_execution_max)
   - Random duration between min and max
   - Actual processing time
   - Failure can occur during this state based on fail_prob
   
3. **EXIT** (wait_exit)
   - Fixed duration wait after execution
   - Use for cleanup, cooldown time

**Total device time = wait_start + random(wait_execution_min, wait_execution_max) + wait_exit**

## Process Flow Patterns

### Sequential Flow
Each device has exactly one output:

```json
{
  "devices": [
    {"id": "step1", "outputs": ["step2"]},
    {"id": "step2", "outputs": ["step3"]},
    {"id": "step3", "outputs": []}
  ]
}
```

Flow: step1 → step2 → step3

### Parallel Branching
One device triggers multiple downstream devices that run in parallel:

```json
{
  "devices": [
    {"id": "input", "outputs": ["process_a", "process_b"]},
    {"id": "process_a", "outputs": []},
    {"id": "process_b", "outputs": []}
  ]
}
```

Flow: input → (process_a + process_b in parallel)

### Convergent Flow
Multiple devices feed into one downstream device:

```json
{
  "devices": [
    {"id": "input_a", "outputs": ["merge"]},
    {"id": "input_b", "outputs": ["merge"]},
    {"id": "merge", "outputs": []}
  ]
}
```

Flow: (input_a + input_b) → merge

**Note**: merge waits for BOTH input_a AND input_b to complete before starting.

### Complex Workflow
Combine all patterns:

```json
{
  "devices": [
    {"id": "start", "outputs": ["branch_a", "branch_b"]},
    {"id": "branch_a", "outputs": ["merge"]},
    {"id": "branch_b", "outputs": ["intermediate"]},
    {"id": "intermediate", "outputs": ["merge"]},
    {"id": "merge", "outputs": ["final"]},
    {"id": "final", "outputs": []}
  ]
}
```

Flow: start → (branch_a, branch_b) → (branch_a + intermediate) → merge → final

## Entry Points

**Entry point devices** are devices with no upstream dependencies (i.e., no other device lists them in their `outputs` array).

The simulation automatically:
1. Identifies all entry point devices
2. Starts them simultaneously at time 0
3. Each entry point triggers its downstream chain

### Single Entry Point

```json
{
  "devices": [
    {"id": "start", "outputs": ["step2"]},
    {"id": "step2", "outputs": []}
  ]
}
```

Only `start` is an entry point.

### Multiple Entry Points

```json
{
  "devices": [
    {"id": "entry_a", "outputs": ["process_a"]},
    {"id": "entry_b", "outputs": ["process_b"]},
    {"id": "process_a", "outputs": []},
    {"id": "process_b", "outputs": []}
  ]
}
```

Both `entry_a` and `entry_b` are entry points and start simultaneously.

## Failure Behavior

When a device fails:
1. Device logs a `failure` event
2. Device stops processing (no exit state)
3. Downstream devices are NOT triggered
4. Other parallel branches continue normally
5. Simulation ends when all active processes complete

Example with failure probability:

```json
{
  "id": "risky_device",
  "type": "quality_check",
  "wait_start": 1.0,
  "wait_execution_min": 5.0,
  "wait_execution_max": 10.0,
  "wait_exit": 1.0,
  "fail_prob": 0.05,  // 5% chance of failure
  "outputs": ["next_step"]
}
```

If `risky_device` fails, `next_step` will never execute.

## Best Practices

### Naming Conventions
- Use descriptive IDs: `platelet_collection` not `dev1`
- Use consistent naming: snake_case or camelCase
- Group related devices: `qa_check_1`, `qa_check_2`

### Timing Values
- Use realistic time units (seconds recommended)
- Ensure wait_execution_max > wait_execution_min
- Start with min = max for deterministic processes
- Add randomness for realistic variability

### Failure Probabilities
- Start with 0.0 (no failures) for initial testing
- Add realistic failure rates based on domain knowledge
- Use higher rates (0.5+) for stress testing
- Typical real-world values: 0.001 to 0.05 (0.1% to 5%)

### Process Design
- Keep processes modular and reusable
- Avoid circular dependencies (A → B → A)
- Document complex flows with comments in your JSON
- Test each device individually before combining

## Validation

The simulator validates:
- All device IDs are unique
- All output IDs reference existing devices
- No circular dependencies (checked at runtime)

The simulator does NOT validate:
- Timing value ranges (negative values allowed but not recommended)
- Disconnected device graphs (orphaned devices are OK)

## Common Patterns

### Quality Check Pattern
```json
{
  "id": "main_process",
  "outputs": ["quality_check"]
},
{
  "id": "quality_check",
  "fail_prob": 0.05,  // Represents rejection rate
  "outputs": ["next_step"]
}
```

### Parallel Processing Pattern
```json
{
  "id": "distributor",
  "outputs": ["worker_1", "worker_2", "worker_3"]
},
{
  "id": "worker_1",
  "outputs": ["collector"]
},
// ... worker_2, worker_3 similar ...
{
  "id": "collector",
  "outputs": []
}
```

### Buffer/Storage Pattern
```json
{
  "id": "process",
  "outputs": ["storage"]
},
{
  "id": "storage",
  "wait_execution_min": 3600,  // 1 hour storage
  "wait_execution_max": 7200,  // 2 hours storage
  "outputs": ["next_process"]
}
```

## Migration to SQLite

For future assetization, the JSON structure maps directly to database tables:

**Config Table**
- id, name, description, version

**Device Table**
- id, config_id, device_id, type, wait_start, wait_execution_min, wait_execution_max, wait_exit, fail_prob

**Device_Output Table**
- id, device_id, output_device_id

This allows:
- Version control of configurations
- Multi-user access
- Historical tracking
- Easier querying and reporting

## Complete Example

See `configs/platelet_pooling.json` and `configs/manufacturing_example.json` for complete, working examples.

## Troubleshooting

### "Device not found in outputs"
- Check that all IDs in `outputs` arrays match an existing device `id`

### "Simulation never completes"
- Check for circular dependencies
- Use `--max-time` to limit simulation duration
- Review event log to see where simulation is stuck

### "No entry points found"
- Every device is listed in some other device's `outputs`
- Add at least one device with no upstream dependencies

### "Results not as expected"
- Check random seed (each run is different due to random execution times)
- Verify timing parameters are in correct units
- Review event log timestamps to understand actual flow
