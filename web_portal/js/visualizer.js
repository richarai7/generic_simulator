/**
 * Process Flow Visualizer functionality
 */

let currentConfig = null;
let devicePositions = {};
let selectedDevice = null;

document.addEventListener('DOMContentLoaded', async () => {
    await loadConfigurationsList();
});

async function loadConfigurationsList() {
    const selectEl = document.getElementById('configSelect');
    
    try {
        const configs = await api.listConfigs();
        
        configs.forEach(filename => {
            const option = document.createElement('option');
            option.value = filename;
            option.textContent = filename;
            selectEl.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading configurations:', error);
    }
}

async function loadSelectedConfig() {
    const selectEl = document.getElementById('configSelect');
    const filename = selectEl.value;
    
    if (!filename) {
        document.getElementById('flowSection').style.display = 'none';
        document.getElementById('flowInfo').style.display = 'block';
        return;
    }

    const infoEl = document.getElementById('flowInfo');
    infoEl.innerHTML = '<div class="spinner"></div>';
    infoEl.style.display = 'block';

    try {
        const data = await api.getConfig(filename);
        currentConfig = data.config;
        
        document.getElementById('flowTitle').textContent = currentConfig.name || 'Process Flow';
        
        await renderFlow();
        
        infoEl.style.display = 'none';
    } catch (error) {
        console.error('Error loading config:', error);
        infoEl.innerHTML = '<div class="alert alert-error">Failed to load configuration.</div>';
    }
}

function renderFlow() {
    if (!currentConfig || !currentConfig.devices) {
        return;
    }

    const canvas = document.getElementById('flowCanvas');
    const ctx = canvas.getContext('2d');
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Calculate layout
    calculateLayout();
    
    // Draw connections first
    drawConnections(ctx);
    
    // Draw devices
    drawDevices(ctx);
    
    // Show sections
    document.getElementById('flowSection').style.display = 'block';
    document.getElementById('flowLegend').style.display = 'block';
    
    // Add click handler
    canvas.onclick = (event) => handleCanvasClick(event, canvas, ctx);
}

function calculateLayout() {
    const devices = currentConfig.devices;
    devicePositions = {};
    
    // Build dependency graph
    const dependencies = {};
    const dependents = {};
    
    devices.forEach(device => {
        dependencies[device.id] = [];
        dependents[device.id] = device.outputs || [];
    });
    
    devices.forEach(device => {
        (device.outputs || []).forEach(outputId => {
            if (dependencies[outputId]) {
                dependencies[outputId].push(device.id);
            }
        });
    });
    
    // Topological sort to determine layers
    const layers = [];
    const visited = new Set();
    const entryDevices = devices.filter(d => dependencies[d.id].length === 0);
    
    function assignLayer(deviceId, layer) {
        if (visited.has(deviceId)) return;
        visited.add(deviceId);
        
        if (!layers[layer]) {
            layers[layer] = [];
        }
        layers[layer].push(deviceId);
        
        const device = devices.find(d => d.id === deviceId);
        if (device) {
            (device.outputs || []).forEach(outputId => {
                assignLayer(outputId, layer + 1);
            });
        }
    }
    
    // Start from entry devices
    entryDevices.forEach(device => {
        assignLayer(device.id, 0);
    });
    
    // Position devices
    const horizontalSpacing = 200;
    const verticalSpacing = 100;
    const marginX = 100;
    const marginY = 80;
    
    layers.forEach((layer, layerIndex) => {
        const x = marginX + layerIndex * horizontalSpacing;
        layer.forEach((deviceId, deviceIndex) => {
            const y = marginY + deviceIndex * verticalSpacing;
            devicePositions[deviceId] = { x, y };
        });
    });
}

function drawConnections(ctx) {
    const devices = currentConfig.devices;
    
    ctx.strokeStyle = '#6b7280';
    ctx.lineWidth = 2;
    
    devices.forEach(device => {
        const fromPos = devicePositions[device.id];
        if (!fromPos) return;
        
        (device.outputs || []).forEach(outputId => {
            const toPos = devicePositions[outputId];
            if (!toPos) return;
            
            // Draw arrow
            drawArrow(ctx, fromPos.x + 60, fromPos.y + 20, toPos.x - 10, toPos.y + 20);
        });
    });
}

function drawArrow(ctx, fromX, fromY, toX, toY) {
    const headLength = 10;
    const angle = Math.atan2(toY - fromY, toX - fromX);
    
    // Draw line
    ctx.beginPath();
    ctx.moveTo(fromX, fromY);
    ctx.lineTo(toX, toY);
    ctx.stroke();
    
    // Draw arrowhead
    ctx.beginPath();
    ctx.moveTo(toX, toY);
    ctx.lineTo(toX - headLength * Math.cos(angle - Math.PI / 6), toY - headLength * Math.sin(angle - Math.PI / 6));
    ctx.moveTo(toX, toY);
    ctx.lineTo(toX - headLength * Math.cos(angle + Math.PI / 6), toY - headLength * Math.sin(angle + Math.PI / 6));
    ctx.stroke();
}

function drawDevices(ctx) {
    const devices = currentConfig.devices;
    
    // Find entry devices
    const dependencies = {};
    devices.forEach(device => {
        dependencies[device.id] = [];
    });
    devices.forEach(device => {
        (device.outputs || []).forEach(outputId => {
            if (dependencies[outputId]) {
                dependencies[outputId].push(device.id);
            }
        });
    });
    
    devices.forEach(device => {
        const pos = devicePositions[device.id];
        if (!pos) return;
        
        const isEntry = dependencies[device.id].length === 0;
        const isSelected = selectedDevice === device.id;
        
        // Draw device box
        ctx.fillStyle = isSelected ? '#d1fae5' : 'white';
        ctx.strokeStyle = isSelected ? '#10b981' : (isEntry ? '#10b981' : '#2563eb');
        ctx.lineWidth = isSelected ? 3 : 2;
        
        const boxWidth = 120;
        const boxHeight = 40;
        
        // Rounded rectangle
        roundRect(ctx, pos.x, pos.y, boxWidth, boxHeight, 8, true, true);
        
        // Draw text
        ctx.fillStyle = '#111827';
        ctx.font = 'bold 12px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(device.id, pos.x + boxWidth / 2, pos.y + boxHeight / 2);
    });
}

function roundRect(ctx, x, y, width, height, radius, fill, stroke) {
    ctx.beginPath();
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + width - radius, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
    ctx.lineTo(x + width, y + height - radius);
    ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
    ctx.lineTo(x + radius, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
    ctx.lineTo(x, y + radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
    ctx.closePath();
    
    if (fill) {
        ctx.fill();
    }
    if (stroke) {
        ctx.stroke();
    }
}

function handleCanvasClick(event, canvas, ctx) {
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    // Check if click is on a device
    let clickedDevice = null;
    
    for (const [deviceId, pos] of Object.entries(devicePositions)) {
        if (x >= pos.x && x <= pos.x + 120 && y >= pos.y && y <= pos.y + 40) {
            clickedDevice = deviceId;
            break;
        }
    }
    
    if (clickedDevice) {
        selectedDevice = clickedDevice;
        showDeviceInfo(clickedDevice);
        renderFlow(); // Redraw to show selection
    } else {
        selectedDevice = null;
        document.getElementById('deviceInfo').style.display = 'none';
        renderFlow();
    }
}

function showDeviceInfo(deviceId) {
    const device = currentConfig.devices.find(d => d.id === deviceId);
    if (!device) return;
    
    document.getElementById('deviceId').textContent = device.id;
    document.getElementById('deviceType').textContent = device.type || 'N/A';
    
    const timing = `Start: ${device.wait_start || 0}s, Execution: ${device.wait_execution_min || 0}s - ${device.wait_execution_max || 0}s, Exit: ${device.wait_exit || 0}s`;
    document.getElementById('deviceTiming').textContent = timing;
    
    document.getElementById('deviceFailProb').textContent = `${((device.fail_prob || 0) * 100).toFixed(1)}%`;
    
    const outputs = device.outputs && device.outputs.length > 0 ? device.outputs.join(', ') : 'None (Terminal device)';
    document.getElementById('deviceOutputs').textContent = outputs;
    
    if (device.staff_required && Object.keys(device.staff_required).length > 0) {
        const staffText = Object.entries(device.staff_required)
            .map(([type, count]) => `${type}: ${count}`)
            .join(', ');
        document.getElementById('deviceStaff').textContent = staffText;
        document.getElementById('deviceStaffGroup').style.display = 'block';
    } else {
        document.getElementById('deviceStaffGroup').style.display = 'none';
    }
    
    document.getElementById('deviceInfo').style.display = 'block';
    document.getElementById('deviceInfo').scrollIntoView({ behavior: 'smooth' });
}
