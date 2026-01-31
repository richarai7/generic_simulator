# Azure Functions Deployment Guide

This guide walks you through deploying the Simulator API to Azure.

## Prerequisites

Before you begin, ensure you have:

- An Azure account (create one at https://azure.microsoft.com/free/)
- Azure CLI installed (https://docs.microsoft.com/cli/azure/install-azure-cli)
- Python 3.9 or higher
- Azure Functions Core Tools v4 (for local testing)

## Quick Start (Local Development)

### 1. Install Azure Functions Core Tools

**macOS:**
```bash
brew tap azure/functions
brew install azure-functions-core-tools@4
```

**Windows (Chocolatey):**
```bash
choco install azure-functions-core-tools-4
```

**Linux (Ubuntu/Debian):**
```bash
wget -q https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb
sudo apt-get update
sudo apt-get install azure-functions-core-tools-4
```

### 2. Install Python Dependencies

```bash
cd api_function_app
pip install -r requirements.txt
```

### 3. Run Locally

```bash
func start
```

Your API will be available at `http://localhost:7071`

### 4. Test the API

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

## Azure Deployment

### Method 1: Azure CLI (Recommended)

#### Step 1: Login to Azure

```bash
az login
```

#### Step 2: Set Variables

```bash
# Edit these to match your preferences
RESOURCE_GROUP="SimulatorAPIResourceGroup"
LOCATION="eastus"
STORAGE_ACCOUNT="simulatorapistg$(date +%s)"  # Must be globally unique
FUNCTION_APP="simulator-api-$(date +%s)"       # Must be globally unique
```

#### Step 3: Create Resource Group

```bash
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION
```

#### Step 4: Create Storage Account

```bash
az storage account create \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard_LRS
```

#### Step 5: Create Function App

```bash
az functionapp create \
  --resource-group $RESOURCE_GROUP \
  --consumption-plan-location $LOCATION \
  --runtime python \
  --runtime-version 3.9 \
  --functions-version 4 \
  --name $FUNCTION_APP \
  --storage-account $STORAGE_ACCOUNT \
  --os-type Linux
```

#### Step 6: Deploy Code

```bash
cd api_function_app
func azure functionapp publish $FUNCTION_APP
```

#### Step 7: Configure Application Settings

```bash
# Note: You'll need to upload config/output files to Azure Storage
# or mount a file share to make them accessible
az functionapp config appsettings set \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --settings \
    SIMULATOR_CONFIGS_PATH="/home/site/wwwroot/configs" \
    SIMULATOR_OUTPUTS_PATH="/home/site/wwwroot/outputs"
```

#### Step 8: Get Function URL

```bash
FUNCTION_URL=$(az functionapp show \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --query "defaultHostName" -o tsv)

echo "Your API is available at: https://$FUNCTION_URL"
```

### Method 2: VS Code

1. Install the **Azure Functions** extension for VS Code
2. Sign in to Azure (click Azure icon in sidebar)
3. Click "Deploy to Function App" in Azure Functions panel
4. Follow prompts to:
   - Create new Function App or select existing
   - Choose subscription
   - Enter Function App name (must be globally unique)
   - Select Python 3.9 runtime
   - Select region
5. Wait for deployment to complete
6. Configure app settings in Azure Portal

### Method 3: Azure Portal (Manual)

1. Go to https://portal.azure.com
2. Click "Create a resource" → "Function App"
3. Fill in details:
   - **Subscription**: Your subscription
   - **Resource Group**: Create new or use existing
   - **Function App name**: Globally unique name
   - **Runtime stack**: Python
   - **Version**: 3.9
   - **Region**: Choose closest to users
4. Click "Review + Create" → "Create"
5. Wait for deployment
6. Use VS Code or Azure CLI to deploy code (see methods above)

## Post-Deployment Configuration

### Upload Config and Output Files

You have several options for making simulator configs and outputs available to the Function App:

#### Option 1: Include in Deployment (Simple)

1. Copy config files to `api_function_app/configs/`
2. Copy output files to `api_function_app/outputs/`
3. Redeploy the Function App

```bash
# From repository root
mkdir -p api_function_app/configs api_function_app/outputs
cp -r configs/* api_function_app/configs/
cp -r outputs/*.json api_function_app/outputs/

# Redeploy
cd api_function_app
func azure functionapp publish $FUNCTION_APP
```

#### Option 2: Azure Files (Recommended for Production)

1. Create Azure Files share
2. Mount to Function App
3. Upload configs and outputs to the share

```bash
# Create file share
SHARE_NAME="simulator-data"
az storage share create \
  --name $SHARE_NAME \
  --account-name $STORAGE_ACCOUNT

# Upload files
az storage file upload-batch \
  --destination $SHARE_NAME/configs \
  --source ../configs \
  --account-name $STORAGE_ACCOUNT

# Mount to function app (requires Azure Portal or advanced CLI)
```

#### Option 3: Azure Blob Storage

1. Create blob container
2. Upload files
3. Update function code to read from blob storage
4. Use Azure Storage SDK in functions

### Configure CORS

To allow web frontends to access the API:

```bash
# Allow all origins (development only)
az functionapp cors add \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --allowed-origins "*"

# Or allow specific domain (production)
az functionapp cors add \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --allowed-origins "https://your-frontend-domain.com"
```

### Enable Authentication (Optional)

For production deployments, enable authentication:

```bash
# Enable Azure AD authentication
az functionapp auth update \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --enabled true \
  --action LoginWithAzureActiveDirectory
```

## Monitoring and Logs

### View Logs in Real-Time

```bash
func azure functionapp logstream $FUNCTION_APP
```

### View Logs in Azure Portal

1. Go to Azure Portal
2. Navigate to your Function App
3. Click "Monitor" → "Logs"
4. View real-time logs and metrics

### Application Insights

Application Insights is automatically configured. View in Azure Portal:
1. Navigate to Function App
2. Click "Application Insights"
3. View requests, failures, performance, etc.

## Testing Your Deployment

```bash
# Get your function app URL
FUNCTION_URL=$(az functionapp show \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --query "defaultHostName" -o tsv)

# Get function key (for authenticated requests)
FUNCTION_KEY=$(az functionapp keys list \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --query "functionKeys.default" -o tsv)

# Test GET /api/events
curl "https://$FUNCTION_URL/api/events?code=$FUNCTION_KEY"

# Test GET /api/config
curl "https://$FUNCTION_URL/api/config?code=$FUNCTION_KEY"

# Test POST /api/config
curl -X POST "https://$FUNCTION_URL/api/config?code=$FUNCTION_KEY&validate_only=true" \
  -H "Content-Type: application/json" \
  -d @../configs/platelet_pooling.json
```

## Troubleshooting

### Issue: "Function app not found"
**Solution:** Verify the function app name and resource group are correct.

### Issue: "Deployment failed"
**Solution:** 
- Check Python version is 3.9
- Ensure requirements.txt is present
- Check Azure Functions Core Tools version (should be v4)

### Issue: "No output files found"
**Solution:** Upload output files to the Function App or configure Azure Files mount.

### Issue: CORS errors
**Solution:** Configure CORS settings (see above)

### Issue: "Authentication failed"
**Solution:** 
- For development: Use function keys (append `?code=<key>` to URL)
- Get keys: `az functionapp keys list --name $FUNCTION_APP --resource-group $RESOURCE_GROUP`

## Cost Optimization

Azure Functions Consumption Plan pricing (as of 2024):
- First 1 million executions: Free
- After: $0.20 per million executions
- Memory usage: $0.000016 per GB-second

For small-scale usage, the API will likely stay within the free tier.

### Cost-saving tips:
1. Use Consumption Plan (serverless) rather than dedicated App Service Plan
2. Monitor usage in Azure Portal
3. Set up budget alerts
4. Delete unused resources

## Cleanup

To delete all Azure resources:

```bash
# This will delete EVERYTHING in the resource group
az group delete \
  --name $RESOURCE_GROUP \
  --yes --no-wait
```

## Next Steps

- Set up CI/CD with GitHub Actions
- Add API versioning
- Implement rate limiting
- Set up automated testing
- Configure custom domain
- Enable HTTPS only mode
- Set up backup and disaster recovery

## Support

For issues or questions:
- Check Function App logs in Azure Portal
- Review Application Insights for errors
- GitHub Issues: https://github.com/richarai7/generic_simulator/issues

---

**Last Updated:** 2026-01-31
