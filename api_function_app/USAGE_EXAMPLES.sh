#!/bin/bash
# Example API usage with curl
# This script demonstrates how to interact with the Simulator API
# Note: These examples assume the API is running on http://localhost:7071

API_BASE="http://localhost:7071/api"

echo "=========================================="
echo "Simulator API - Usage Examples"
echo "=========================================="

echo ""
echo "1. GET /api/events - Retrieve latest event log"
echo "   curl $API_BASE/events"
echo ""

echo "2. GET /api/events - Retrieve specific event log"
echo "   curl $API_BASE/events?file=sample_results.json"
echo ""

echo "3. GET /api/config - List all available configs"
echo "   curl $API_BASE/config?list=true"
echo ""

echo "4. GET /api/config - Get latest config"
echo "   curl $API_BASE/config"
echo ""

echo "5. GET /api/config - Get specific config"
echo "   curl $API_BASE/config?file=platelet_pooling.json"
echo ""

echo "6. POST /api/config - Validate a config (without saving)"
echo "   curl -X POST $API_BASE/config?validate_only=true \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d @configs/platelet_pooling.json"
echo ""

echo "7. POST /api/config - Save new config with auto-generated name"
echo "   curl -X POST $API_BASE/config \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d @configs/platelet_pooling.json"
echo ""

echo "8. POST /api/config - Save config with custom filename"
echo "   curl -X POST $API_BASE/config?filename=my_custom_config.json \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d @configs/platelet_pooling.json"
echo ""

echo "=========================================="
echo "To run the API locally:"
echo "  cd api_function_app"
echo "  func start"
echo "=========================================="
