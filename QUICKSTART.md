# Quick Start Guide

Get started with the Generic SimPy Simulation Environment in 5 minutes.

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/richarai7/generic_simulator.git
cd generic_simulator

# 2. Install dependencies
pip install -r requirements.txt
```

## Run Your First Simulation

```bash
# Run the platelet pooling example
python main.py --config configs/platelet_pooling.json --output outputs/my_results.json
```

You should see:
```
Loading configuration from: configs/platelet_pooling.json
Initializing simulator...
Running simulation (max_time=unlimited)...
Saving event log to: outputs/my_results.json
Simulation completed successfully!
Total events logged: 42
```

## Analyze Results

```bash
# View device statistics and staff utilization
python examples/analyze_log.py outputs/my_results.json

# Detailed staff utilization analysis
python examples/analyze_staff_utilization.py outputs/my_results.json

# Visualize timeline
python examples/visualize_timeline.py outputs/my_results.json
```

## Try Staff Utilization

Run the platelet pooling example with staff tracking:

```bash
python main.py -c configs/platelet_pooling_with_staff.json -o outputs/staff_results.json

# Analyze staff metrics
python examples/analyze_staff_utilization.py outputs/staff_results.json
```

This shows:
- How busy each staff type is
- Which devices use which staff
- Bottleneck detection
- Optimization opportunities

## Create Your Own Process

1. **Copy an example config**:
   ```bash
   cp configs/platelet_pooling.json configs/my_process.json
   ```

2. **Edit the config** to define your devices:
   ```json
   {
     "name": "My Process",
     "description": "Custom workflow",
     "version": "1.0",
     "devices": [
       {
         "id": "input",
         "type": "loader",
         "wait_start": 1.0,
         "wait_execution_min": 5.0,
         "wait_execution_max": 10.0,
         "wait_exit": 1.0,
         "fail_prob": 0.01,
         "outputs": ["process"]
       },
       {
         "id": "process",
         "type": "processor",
         "wait_start": 2.0,
         "wait_execution_min": 10.0,
         "wait_execution_max": 20.0,
         "wait_exit": 1.0,
         "fail_prob": 0.02,
         "outputs": []
       }
     ]
   }
   ```

3. **Run your simulation**:
   ```bash
   python main.py -c configs/my_process.json -o outputs/my_process_results.json
   ```

## Common Commands

```bash
# Run with time limit
python main.py -c configs/my_process.json -o outputs/results.json --max-time 100

# Run with reproducible random seed
python main.py -c configs/my_process.json -o outputs/results.json --seed 42

# Get help
python main.py --help
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- See [docs/CONFIG_REFERENCE.md](docs/CONFIG_REFERENCE.md) for complete config reference
- Try the manufacturing example: `configs/manufacturing_example.json`
- Experiment with different timing parameters and failure probabilities

## Tips

- Start with `fail_prob: 0.0` to test your process flow without failures
- Use `--seed` for reproducible results during testing
- Check event logs to debug unexpected behavior
- Use the analysis and visualization scripts to understand your process

## Getting Help

- Check the [README.md](README.md) troubleshooting section
- Review example configs in the `configs/` directory
- Look at the example scripts in `examples/` for ideas

Happy simulating! 🚀
