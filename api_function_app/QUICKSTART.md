# Quick Start Guide - Simulator API

Get the Simulator API running locally in 5 minutes!

## Prerequisites

- Python 3.9+
- pip (Python package installer)

## Step 1: Install Dependencies

```bash
cd api_function_app
pip install -r requirements.txt
```

## Step 2: Run the Simulator (Optional)

Generate some sample data first:

```bash
cd ..
python main.py --config configs/platelet_pooling.json --output outputs/sample.json
```

## Step 3: Test the API Functions

Since Azure Functions Core Tools may not be installed, you can test the API logic directly:

```bash
cd api_function_app
python test_api.py
```

You should see:
```
============================================================
✓ All tests passed!
============================================================
```

## Step 4: (Optional) Run with Azure Functions Core Tools

If you have Azure Functions Core Tools installed:

```bash
cd api_function_app
func start
```

Then test with curl:

```bash
# Get latest events
curl http://localhost:7071/api/events

# List configs
curl http://localhost:7071/api/config?list=true

# Validate a config
curl -X POST http://localhost:7071/api/config?validate_only=true \
  -H "Content-Type: application/json" \
  -d @../configs/platelet_pooling.json
```

## API Endpoints

### GET /api/events
Returns simulator event logs for dashboards

```bash
curl http://localhost:7071/api/events
curl http://localhost:7071/api/events?file=sample_results.json
```

### GET /api/config
Returns process/device configuration

```bash
# List all configs
curl http://localhost:7071/api/config?list=true

# Get latest config
curl http://localhost:7071/api/config

# Get specific config
curl http://localhost:7071/api/config?file=platelet_pooling.json
```

### POST /api/config
Save or validate configuration

```bash
# Validate only
curl -X POST http://localhost:7071/api/config?validate_only=true \
  -H "Content-Type: application/json" \
  -d @../configs/platelet_pooling.json

# Save with auto-generated filename
curl -X POST http://localhost:7071/api/config \
  -H "Content-Type: application/json" \
  -d @../configs/platelet_pooling.json

# Save with custom filename
curl -X POST http://localhost:7071/api/config?filename=my_config.json \
  -H "Content-Type: application/json" \
  -d @../configs/platelet_pooling.json
```

## Example Workflow

### 1. Run a Simulation
```bash
python main.py --config configs/platelet_pooling.json --output outputs/my_sim.json
```

### 2. Access Results via API
```bash
curl http://localhost:7071/api/events?file=my_sim.json | jq
```

### 3. Get Config for Editing
```bash
curl http://localhost:7071/api/config?file=platelet_pooling.json > edit.json
```

### 4. Edit Config (in your editor)
```bash
vim edit.json  # or use your favorite editor
```

### 5. Validate Changes
```bash
curl -X POST http://localhost:7071/api/config?validate_only=true \
  -H "Content-Type: application/json" \
  -d @edit.json
```

### 6. Save Updated Config
```bash
curl -X POST http://localhost:7071/api/config?filename=my_updated_config.json \
  -H "Content-Type: application/json" \
  -d @edit.json
```

## Troubleshooting

### "No output files found"
Run the simulator first to generate event logs:
```bash
python main.py --config configs/platelet_pooling.json --output outputs/test.json
```

### "Module not found"
Install dependencies:
```bash
pip install -r requirements.txt
```

### Want to deploy to Azure?
See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed Azure deployment instructions.

## Next Steps

- Read [README.md](README.md) for complete API documentation
- See [DEPLOYMENT.md](DEPLOYMENT.md) for Azure deployment
- Check [USAGE_EXAMPLES.sh](USAGE_EXAMPLES.sh) for more curl examples

## Need Help?

- GitHub Issues: https://github.com/richarai7/generic_simulator/issues
- Documentation: See README.md and DEPLOYMENT.md
