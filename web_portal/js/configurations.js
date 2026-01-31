/**
 * Configurations page functionality
 */

let currentConfig = null;
let currentFilename = null;

document.addEventListener('DOMContentLoaded', async () => {
    await loadConfigurations();
});

async function loadConfigurations() {
    const listEl = document.getElementById('configList');
    listEl.innerHTML = '<div class="spinner"></div>';

    try {
        const configs = await api.listConfigs();
        
        if (configs.length === 0) {
            listEl.innerHTML = '<div class="alert alert-info">No configurations found. Create your first configuration!</div>';
            return;
        }

        let html = '<div class="features-grid">';
        
        for (const filename of configs) {
            try {
                const data = await api.getConfig(filename);
                const config = data.config;
                
                html += `
                    <div class="feature-card">
                        <h3>${config.name || filename}</h3>
                        <p>${config.description || 'No description'}</p>
                        <div style="margin: 1rem 0;">
                            <span class="badge badge-info">${config.devices ? config.devices.length : 0} devices</span>
                            ${config.version ? `<span class="badge badge-success">v${config.version}</span>` : ''}
                        </div>
                        <button class="btn btn-primary" onclick="viewConfig('${filename}')">View Details</button>
                    </div>
                `;
            } catch (error) {
                console.error(`Error loading config ${filename}:`, error);
            }
        }
        
        html += '</div>';
        listEl.innerHTML = html;
    } catch (error) {
        console.error('Error loading configurations:', error);
        listEl.innerHTML = '<div class="alert alert-error">Failed to load configurations. Make sure the API is running.</div>';
    }
}

async function viewConfig(filename) {
    try {
        const data = await api.getConfig(filename);
        currentConfig = data.config;
        currentFilename = filename;

        // Update viewer
        document.getElementById('configName').textContent = currentConfig.name || filename;
        document.getElementById('configDescription').textContent = currentConfig.description || 'No description';
        document.getElementById('configVersion').textContent = currentConfig.version || 'N/A';

        // Display devices
        const devicesList = document.getElementById('devicesList');
        if (currentConfig.devices && currentConfig.devices.length > 0) {
            let html = '<table class="table"><thead><tr><th>Device ID</th><th>Type</th><th>Exec Time</th><th>Fail %</th><th>Outputs</th></tr></thead><tbody>';
            
            currentConfig.devices.forEach(device => {
                html += `
                    <tr>
                        <td><strong>${device.id}</strong></td>
                        <td>${device.type || 'N/A'}</td>
                        <td>${device.wait_execution_min || 0}s - ${device.wait_execution_max || 0}s</td>
                        <td>${((device.fail_prob || 0) * 100).toFixed(1)}%</td>
                        <td>${device.outputs ? device.outputs.join(', ') : 'None'}</td>
                    </tr>
                `;
            });
            
            html += '</tbody></table>';
            devicesList.innerHTML = html;
        } else {
            devicesList.innerHTML = '<p>No devices configured</p>';
        }

        // Display staff if present
        if (currentConfig.staff) {
            document.getElementById('staffSection').style.display = 'block';
            const staffList = document.getElementById('staffList');
            let html = '<table class="table"><thead><tr><th>Staff Type</th><th>Count</th></tr></thead><tbody>';
            
            for (const [type, count] of Object.entries(currentConfig.staff)) {
                html += `<tr><td>${type}</td><td>${count}</td></tr>`;
            }
            
            html += '</tbody></table>';
            staffList.innerHTML = html;
        } else {
            document.getElementById('staffSection').style.display = 'none';
        }

        // Show viewer
        document.getElementById('configViewer').style.display = 'block';
        document.getElementById('configEditor').style.display = 'none';
        
        // Scroll to viewer
        document.getElementById('configViewer').scrollIntoView({ behavior: 'smooth' });
    } catch (error) {
        console.error('Error viewing config:', error);
        alert('Failed to load configuration details');
    }
}

function closeViewer() {
    document.getElementById('configViewer').style.display = 'none';
    currentConfig = null;
    currentFilename = null;
}

function editConfig() {
    if (!currentConfig) return;

    // Populate editor
    document.getElementById('editConfigName').value = currentConfig.name || '';
    document.getElementById('editConfigDescription').value = currentConfig.description || '';
    document.getElementById('editConfigVersion').value = currentConfig.version || '';
    document.getElementById('editConfigJSON').value = JSON.stringify(currentConfig, null, 2);

    // Show editor
    document.getElementById('configViewer').style.display = 'none';
    document.getElementById('configEditor').style.display = 'block';
    document.getElementById('editorMessages').innerHTML = '';
    
    // Scroll to editor
    document.getElementById('configEditor').scrollIntoView({ behavior: 'smooth' });
}

function createNewConfig() {
    currentConfig = {
        name: "New Process",
        description: "Description of the process",
        version: "1.0",
        devices: [
            {
                id: "device_1",
                type: "processor",
                wait_start: 1.0,
                wait_execution_min: 5.0,
                wait_execution_max: 10.0,
                wait_exit: 1.0,
                fail_prob: 0.01,
                outputs: []
            }
        ]
    };
    currentFilename = null;

    // Populate editor
    document.getElementById('editConfigName').value = currentConfig.name;
    document.getElementById('editConfigDescription').value = currentConfig.description;
    document.getElementById('editConfigVersion').value = currentConfig.version;
    document.getElementById('editConfigJSON').value = JSON.stringify(currentConfig, null, 2);

    // Show editor
    document.getElementById('configViewer').style.display = 'none';
    document.getElementById('configEditor').style.display = 'block';
    document.getElementById('editorMessages').innerHTML = '';
    
    // Scroll to editor
    document.getElementById('configEditor').scrollIntoView({ behavior: 'smooth' });
}

function closeEditor() {
    document.getElementById('configEditor').style.display = 'none';
    if (currentConfig && currentFilename) {
        document.getElementById('configViewer').style.display = 'block';
    }
}

async function validateConfiguration() {
    const messagesEl = document.getElementById('editorMessages');
    messagesEl.innerHTML = '<div class="spinner"></div>';

    try {
        // Parse JSON
        const jsonText = document.getElementById('editConfigJSON').value;
        let config;
        
        try {
            config = JSON.parse(jsonText);
        } catch (error) {
            messagesEl.innerHTML = '<div class="alert alert-error">Invalid JSON: ' + error.message + '</div>';
            return;
        }

        // Update basic fields
        config.name = document.getElementById('editConfigName').value || config.name;
        config.description = document.getElementById('editConfigDescription').value || config.description;
        config.version = document.getElementById('editConfigVersion').value || config.version;

        // Validate via API
        const result = await api.saveConfig(config, null, true);
        
        if (result.valid) {
            messagesEl.innerHTML = '<div class="alert alert-success">✓ Configuration is valid!</div>';
        } else {
            messagesEl.innerHTML = '<div class="alert alert-error">✗ Validation failed</div>';
        }
    } catch (error) {
        messagesEl.innerHTML = '<div class="alert alert-error">✗ Validation failed: ' + error.message + '</div>';
    }
}

async function saveConfiguration() {
    const messagesEl = document.getElementById('editorMessages');
    messagesEl.innerHTML = '<div class="spinner"></div>';

    try {
        // Parse JSON
        const jsonText = document.getElementById('editConfigJSON').value;
        let config;
        
        try {
            config = JSON.parse(jsonText);
        } catch (error) {
            messagesEl.innerHTML = '<div class="alert alert-error">Invalid JSON: ' + error.message + '</div>';
            return;
        }

        // Update basic fields
        config.name = document.getElementById('editConfigName').value || config.name;
        config.description = document.getElementById('editConfigDescription').value || config.description;
        config.version = document.getElementById('editConfigVersion').value || config.version;

        // Determine filename
        let filename = currentFilename;
        if (!filename) {
            // Create new filename from name
            filename = (config.name || 'config').toLowerCase().replace(/\s+/g, '_') + '.json';
        }

        // Save via API
        const result = await api.saveConfig(config, filename, false);
        
        messagesEl.innerHTML = '<div class="alert alert-success">✓ Configuration saved successfully!</div>';
        
        // Reload configurations list
        setTimeout(() => {
            closeEditor();
            loadConfigurations();
        }, 1500);
    } catch (error) {
        messagesEl.innerHTML = '<div class="alert alert-error">✗ Save failed: ' + error.message + '</div>';
    }
}
