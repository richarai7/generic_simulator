#!/bin/bash
# Startup script for Generic Simulator Web UI

echo "============================================"
echo "Generic Simulator - Web UI Startup"
echo "============================================"
echo ""

# Check if examples exist
if [ ! -f "configs/simulator.db" ]; then
    echo "Creating example configurations..."
    python examples/create_examples.py
    echo ""
fi

# Install Python dependencies if needed
if ! python -c "import flask" 2>/dev/null; then
    echo "Installing Python dependencies..."
    pip install -r requirements-web.txt
    echo ""
fi

# Start the API server
echo "Starting API server on http://localhost:5000..."
python -m generic_simulator.api_server &
API_PID=$!

# Wait a moment for the API to start
sleep 2

# Check if API is running
if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
    echo "✓ API server started successfully (PID: $API_PID)"
else
    echo "✗ Failed to start API server"
    kill $API_PID 2>/dev/null
    exit 1
fi

echo ""
echo "============================================"
echo "API Server: http://localhost:5000"
echo "Swagger API: http://localhost:5000/api"
echo ""
echo "To start the Web UI:"
echo "  cd web-ui"
echo "  npm install  # (first time only)"
echo "  npm start"
echo ""
echo "Then open: http://localhost:3000"
echo "============================================"
echo ""
echo "Press Ctrl+C to stop the API server"

# Wait for interrupt
wait $API_PID
