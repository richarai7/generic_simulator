# Simulator API - Azure Functions

A Python-based Azure Functions API for the Generic Simulator POC asset. This API provides endpoints for serving simulator event data and managing process/device configurations to web frontends and dashboards.

## Overview

This API serves as the backend interface for the simulator, enabling:
- Real-time access to simulation event logs for dashboards and 3D visualizations
- Configuration management (read and update process/device parameters)
- Integration with web frontends for interactive simulation control

## Features

- **Event Data API**: Serve simulator output JSON logs (event records) to web dashboards
- **Configuration Management**: Read and update process/device configurations via REST API
- **Azure Functions**: Serverless, scalable Python implementation
- **Validation**: Built-in configuration validation before saving
- **Error Handling**: Comprehensive error messages and logging

## API Endpoints

### 1. GET /api/events

Returns simulator event log data for dashboard and 3D view updates.

**Query Parameters:**
- `file` (optional): Specific filename to load (e.g., `results.json`)
- Default behavior: Returns the most recently modified event log

**Example Requests:**
```bash
# Get latest event log
curl http://localhost:7071/api/events

# Get specific event log
curl http://localhost:7071/api/events?file=sample_results.json
```

**Response Format:**
```json
{
  "simulation_metadata": {
    "generated_at": "2026-01-31T04:55:20.112505",
    "total_events": 42
  },
  "events": [
    {
      "timestamp": 0,
      "device_id": "SYSTEM",
      "event_type": "simulation_start",
      "details": {
        "entry_devices": ["collection"],
        "total_devices": 8
      }
    },
    ...
  ],
  "staff_utilization": {
    "technician": {
      "count": 3,
      "total_busy_time": 56.95,
      "utilization_percentage": 10.74
    }
  },
  "file_info": {
    "filename": "sample_results.json",
    "path": "/path/to/outputs/sample_results.json"
  }
}
```

### 2. GET /api/config

Returns process/device configuration for viewing and editing.

**Query Parameters:**
- `file` (optional): Specific config filename to load (e.g., `platelet_pooling.json`)
- `list` (optional): If `true`, returns list of available config files
- Default behavior: Returns the most recently modified config

**Example Requests:**
```bash
# Get latest config
curl http://localhost:7071/api/config

# List all available configs
curl http://localhost:7071/api/config?list=true

# Get specific config
curl http://localhost:7071/api/config?file=platelet_pooling.json
```

**Response Format (single config):**
```json
{
  "config": {
    "name": "Platelet Pooling Process",
    "description": "Lifeblood platelet pooling simulation",
    "version": "1.0",
    "devices": [
      {
        "id": "collection",
        "type": "collection_station",
        "wait_start": 2.0,
        "wait_execution_min": 15.0,
        "wait_execution_max": 30.0,
        "wait_exit": 1.0,
        "fail_prob": 0.01,
        "outputs": ["quality_check_1"]
      },
      ...
    ]
  },
  "file_info": {
    "filename": "platelet_pooling.json",
    "path": "/path/to/configs/platelet_pooling.json"
  }
}
```

**Response Format (list):**
```json
{
  "configs": [
    "platelet_pooling.json",
    "platelet_pooling_with_staff.json",
    "manufacturing_example.json"
  ]
}
```

### 3. POST /api/config

Receives and saves updated configuration files.

**Query Parameters:**
- `filename` (optional): Custom filename to save as (default: auto-generated with timestamp)
- `validate_only` (optional): If `true`, only validates without saving

**Request Body:** JSON configuration object (same structure as GET /api/config response)

**Example Requests:**
```bash
# Save new config with auto-generated filename
curl -X POST http://localhost:7071/api/config \
  -H "Content-Type: application/json" \
  -d @new_config.json

# Save with custom filename
curl -X POST http://localhost:7071/api/config?filename=my_process.json \
  -H "Content-Type: application/json" \
  -d @new_config.json

# Validate only (don't save)
curl -X POST http://localhost:7071/api/config?validate_only=true \
  -H "Content-Type: application/json" \
  -d @new_config.json
```

**Response Format (success):**
```json
{
  "success": true,
  "message": "Configuration saved successfully",
  "file_info": {
    "filename": "config_20260131_045520.json",
    "path": "/path/to/configs/config_20260131_045520.json"
  }
}
```

**Response Format (validation error):**
```json
{
  "error": "Configuration validation failed",
  "details": "Device collection: wait_execution_max must be >= wait_execution_min"
}
```

## Configuration Validation

The POST /api/config endpoint validates configurations before saving:

✅ **Validated:**
- Required fields (`devices`, `id`, `type`)
- Unique device IDs
- Valid timing parameters (max >= min)
- Output device references exist
- Proper data types

❌ **Rejected:**
- Duplicate device IDs
- Invalid timing parameters
- References to non-existent devices
- Missing required fields
- Invalid JSON structure

## Installation & Setup

### Prerequisites

- Python 3.9 or higher
- Azure Functions Core Tools (for local development)
- Azure account (for deployment)

### Local Development Setup

1. **Install Azure Functions Core Tools:**

```bash
# macOS
brew tap azure/functions
brew install azure-functions-core-tools@4

# Windows (with Chocolatey)
choco install azure-functions-core-tools-4

# Linux (Ubuntu/Debian)
wget -q https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb
sudo apt-get update
sudo apt-get install azure-functions-core-tools-4
```

2. **Install Python Dependencies:**

```bash
cd api_function_app
pip install -r requirements.txt
```

3. **Configure Local Settings:**

Edit `local.settings.json` to set paths to your simulator configs and outputs:

```json
{
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "SIMULATOR_CONFIGS_PATH": "../configs",
    "SIMULATOR_OUTPUTS_PATH": "../outputs"
  }
}
```

4. **Run Locally:**

```bash
cd api_function_app
func start
```

The API will be available at `http://localhost:7071`

### Testing the API

```bash
# Test GET /api/events
curl http://localhost:7071/api/events

# Test GET /api/config
curl http://localhost:7071/api/config

# Test GET /api/config (list)
curl http://localhost:7071/api/config?list=true

# Test POST /api/config (validation only)
curl -X POST http://localhost:7071/api/config?validate_only=true \
  -H "Content-Type: application/json" \
  -d @../configs/platelet_pooling.json
```

## Deployment to Azure

### Option 1: Deploy via Azure CLI

1. **Login to Azure:**

```bash
az login
```

2. **Create Resource Group:**

```bash
az group create --name SimulatorAPIResourceGroup --location eastus
```

3. **Create Storage Account:**

```bash
az storage account create \
  --name simulatorapistorageacct \
  --resource-group SimulatorAPIResourceGroup \
  --location eastus \
  --sku Standard_LRS
```

4. **Create Function App:**

```bash
az functionapp create \
  --resource-group SimulatorAPIResourceGroup \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.9 \
  --functions-version 4 \
  --name simulator-api-app \
  --storage-account simulatorapistorageacct \
  --os-type Linux
```

5. **Deploy Code:**

```bash
cd api_function_app
func azure functionapp publish simulator-api-app
```

### Option 2: Deploy via VS Code

1. Install the **Azure Functions** extension in VS Code
2. Sign in to Azure
3. Click "Deploy to Function App" in the Azure Functions panel
4. Follow the prompts to create/select resources
5. Deploy the `api_function_app` folder

### Post-Deployment Configuration

After deployment, configure application settings:

```bash
az functionapp config appsettings set \
  --name simulator-api-app \
  --resource-group SimulatorAPIResourceGroup \
  --settings SIMULATOR_CONFIGS_PATH="/home/site/wwwroot/configs" \
              SIMULATOR_OUTPUTS_PATH="/home/site/wwwroot/outputs"
```

**Important:** You'll need to upload your configs and outputs directories to the Function App storage or mount Azure Blob Storage.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SIMULATOR_CONFIGS_PATH` | Path to configuration files directory | `../configs` |
| `SIMULATOR_OUTPUTS_PATH` | Path to output event logs directory | `../outputs` |
| `FUNCTIONS_WORKER_RUNTIME` | Runtime for Azure Functions | `python` |

## Architecture

```
api_function_app/
├── GetEvents/              # GET /api/events endpoint
│   ├── __init__.py        # Function implementation
│   └── function.json      # Function bindings
├── GetConfig/              # GET /api/config endpoint
│   ├── __init__.py        # Function implementation
│   └── function.json      # Function bindings
├── PostConfig/             # POST /api/config endpoint
│   ├── __init__.py        # Function implementation
│   └── function.json      # Function bindings
├── host.json               # Function app configuration
├── local.settings.json     # Local development settings
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Integration with Simulator

The API is designed to work seamlessly with the Generic Simulator:

1. **Run Simulation:** Use `main.py` to run simulations and generate event logs
   ```bash
   python main.py --config configs/platelet_pooling.json --output outputs/results.json
   ```

2. **Access via API:** The event log is immediately available via `/api/events`

3. **Update Config:** Use `/api/config` POST to update configuration from web UI

4. **Re-run Simulation:** Updated configs can be used for new simulation runs

## CORS Configuration

For web frontend integration, you may need to enable CORS:

**Local Development:** Add to `local.settings.json`:
```json
{
  "Host": {
    "CORS": "*"
  }
}
```

**Azure Deployment:**
```bash
az functionapp cors add \
  --name simulator-api-app \
  --resource-group SimulatorAPIResourceGroup \
  --allowed-origins https://your-frontend-domain.com
```

## Error Handling

All endpoints return appropriate HTTP status codes:

- **200**: Success
- **400**: Bad Request (validation errors, malformed JSON)
- **404**: Not Found (file/directory not found)
- **500**: Internal Server Error

Error responses include descriptive messages:
```json
{
  "error": "Configuration validation failed",
  "details": "Device collection: wait_execution_max must be >= wait_execution_min"
}
```

## Security Considerations

- **Authentication:** Functions use `authLevel: "function"` by default, requiring function keys
- **CORS:** Configure allowed origins for production
- **Input Validation:** All POST requests are validated before processing
- **Path Traversal:** File paths are validated and resolved to prevent directory traversal attacks

## Troubleshooting

### Issue: "Outputs directory not found"
**Solution:** Ensure `SIMULATOR_OUTPUTS_PATH` points to the correct directory and contains event log files.

### Issue: "No output files found"
**Solution:** Run at least one simulation to generate event logs:
```bash
python main.py --config configs/platelet_pooling.json --output outputs/results.json
```

### Issue: Functions not starting locally
**Solution:** Check that Azure Functions Core Tools is installed and Python dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: CORS errors from web frontend
**Solution:** Configure CORS settings in `local.settings.json` or Azure portal.

## Future Enhancements

- [ ] Real-time event streaming via WebSockets
- [ ] Run simulations directly via API endpoint
- [ ] Authentication/authorization with Azure AD
- [ ] Rate limiting and throttling
- [ ] Metrics and monitoring dashboard
- [ ] Database integration for config versioning
- [ ] Batch operations for multiple configs

## License

[Specify your license here]

## Support

For questions or issues:
- GitHub Issues: https://github.com/richarai7/generic_simulator/issues
- Documentation: See main project README.md

---

**Version**: 1.0  
**Last Updated**: 2026-01-31  
**Maintainer**: [Your name/team]
