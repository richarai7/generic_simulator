/**
 * Dashboard page functionality
 */

let currentSimulation = null;

document.addEventListener('DOMContentLoaded', async () => {
    await loadLatestSimulation();
});

async function loadLatestSimulation() {
    const infoEl = document.getElementById('simulationInfo');
    infoEl.innerHTML = '<div class="spinner"></div>';

    try {
        const data = await api.getEvents();
        currentSimulation = data;
        
        displaySimulationInfo(data);
        displayMetrics(data);
        displayStaffUtilization(data);
        displayDeviceActivity(data);
        displayTimeline(data);
        displayRecentEvents(data);

        infoEl.style.display = 'none';
    } catch (error) {
        console.error('Error loading simulation:', error);
        infoEl.innerHTML = '<div class="alert alert-error">Failed to load simulation data. Make sure you have run a simulation first.</div>';
    }
}

function displaySimulationInfo(data) {
    if (data.file_info) {
        const infoEl = document.getElementById('simulationInfo');
        infoEl.innerHTML = `
            <div class="alert alert-info">
                <strong>Loaded:</strong> ${data.file_info.filename}
            </div>
        `;
        infoEl.style.display = 'block';
    }
}

function displayMetrics(data) {
    const section = document.getElementById('metricsSection');
    
    if (data.simulation_metadata) {
        document.getElementById('totalEvents').textContent = data.simulation_metadata.total_events || 0;
        document.getElementById('generatedAt').textContent = utils.formatDate(data.simulation_metadata.generated_at);
    }

    // Calculate simulation time and devices from events
    if (data.events && data.events.length > 0) {
        // Find simulation end event
        const endEvent = data.events.find(e => e.event_type === 'simulation_end');
        if (endEvent) {
            document.getElementById('simTime').textContent = utils.formatDuration(endEvent.timestamp);
        }

        // Find start event to get device count
        const startEvent = data.events.find(e => e.event_type === 'simulation_start');
        if (startEvent && startEvent.details) {
            document.getElementById('totalDevices').textContent = startEvent.details.total_devices || 'N/A';
        }
    }

    section.style.display = 'block';
}

function displayStaffUtilization(data) {
    if (!data.staff_utilization) {
        document.getElementById('staffSection').style.display = 'none';
        return;
    }

    const metricsEl = document.getElementById('staffMetrics');
    let html = '<table class="table"><thead><tr><th>Staff Type</th><th>Count</th><th>Utilization</th><th>Busy Time</th><th>Allocations</th></tr></thead><tbody>';

    for (const [staffType, stats] of Object.entries(data.staff_utilization)) {
        const utilPct = stats.utilization_percentage.toFixed(1);
        let badgeClass = 'badge-success';
        if (utilPct > 70) {
            badgeClass = 'badge-warning';
        } else if (utilPct < 20) {
            badgeClass = 'badge-info';
        }

        html += `
            <tr>
                <td><strong>${staffType}</strong></td>
                <td>${stats.count}</td>
                <td><span class="badge ${badgeClass}">${utilPct}%</span></td>
                <td>${utils.formatDuration(stats.total_busy_time)}</td>
                <td>${stats.allocations}</td>
            </tr>
        `;
    }

    html += '</tbody></table>';
    metricsEl.innerHTML = html;
    document.getElementById('staffSection').style.display = 'block';
}

function displayDeviceActivity(data) {
    if (!data.events || data.events.length === 0) {
        document.getElementById('deviceSection').style.display = 'none';
        return;
    }

    // Analyze device activity
    const deviceStats = {};
    
    data.events.forEach(event => {
        const deviceId = event.device_id;
        if (deviceId === 'SYSTEM') return;
        
        if (!deviceStats[deviceId]) {
            deviceStats[deviceId] = {
                starts: 0,
                completions: 0,
                failures: 0,
                totalTime: 0,
                startTime: null
            };
        }

        if (event.event_type === 'start') {
            deviceStats[deviceId].starts++;
            deviceStats[deviceId].startTime = event.timestamp;
        } else if (event.event_type === 'complete') {
            deviceStats[deviceId].completions++;
            if (deviceStats[deviceId].startTime !== null) {
                deviceStats[deviceId].totalTime = event.timestamp - deviceStats[deviceId].startTime;
            }
        } else if (event.event_type === 'failure') {
            deviceStats[deviceId].failures++;
        }
    });

    const activityEl = document.getElementById('deviceActivity');
    let html = '<table class="table"><thead><tr><th>Device</th><th>Status</th><th>Execution Time</th><th>Events</th></tr></thead><tbody>';

    for (const [deviceId, stats] of Object.entries(deviceStats)) {
        const status = stats.failures > 0 
            ? '<span class="badge badge-danger">Failed</span>' 
            : stats.completions > 0 
                ? '<span class="badge badge-success">Completed</span>'
                : '<span class="badge badge-warning">In Progress</span>';

        html += `
            <tr>
                <td><strong>${deviceId}</strong></td>
                <td>${status}</td>
                <td>${utils.formatDuration(stats.totalTime)}</td>
                <td>Starts: ${stats.starts}, Completions: ${stats.completions}, Failures: ${stats.failures}</td>
            </tr>
        `;
    }

    html += '</tbody></table>';
    activityEl.innerHTML = html;
    document.getElementById('deviceSection').style.display = 'block';
}

function displayTimeline(data) {
    if (!data.events || data.events.length === 0) {
        document.getElementById('timelineSection').style.display = 'none';
        return;
    }

    const timelineEl = document.getElementById('timeline');
    
    // Create a simple ASCII-style timeline
    const maxEvents = 50; // Limit to recent events
    const recentEvents = data.events.slice(0, maxEvents);
    
    let html = '<div style="font-family: monospace; font-size: 0.875rem; overflow-x: auto;">';
    
    recentEvents.forEach((event, idx) => {
        const time = event.timestamp.toFixed(2);
        const device = event.device_id.padEnd(20);
        const type = event.event_type.padEnd(20);
        
        let color = 'var(--text-dark)';
        if (event.event_type === 'failure') {
            color = 'var(--danger-color)';
        } else if (event.event_type === 'complete') {
            color = 'var(--success-color)';
        } else if (event.event_type === 'simulation_start' || event.event_type === 'simulation_end') {
            color = 'var(--primary-color)';
        }
        
        html += `<div style="color: ${color}; padding: 0.25rem 0;">${time.padStart(8)}s | ${device} | ${type}</div>`;
    });
    
    if (data.events.length > maxEvents) {
        html += `<div style="padding: 0.5rem 0; color: var(--text-light);">... and ${data.events.length - maxEvents} more events</div>`;
    }
    
    html += '</div>';
    timelineEl.innerHTML = html;
    document.getElementById('timelineSection').style.display = 'block';
}

function displayRecentEvents(data) {
    if (!data.events || data.events.length === 0) {
        document.getElementById('eventsSection').style.display = 'none';
        return;
    }

    const eventsEl = document.getElementById('eventsList');
    const recentEvents = data.events.slice(0, 20);
    
    let html = '<table class="table"><thead><tr><th>Time</th><th>Device</th><th>Event Type</th><th>Details</th></tr></thead><tbody>';
    
    recentEvents.forEach(event => {
        let badgeClass = 'badge-info';
        if (event.event_type === 'failure') {
            badgeClass = 'badge-danger';
        } else if (event.event_type === 'complete') {
            badgeClass = 'badge-success';
        }

        const details = event.details ? JSON.stringify(event.details).substring(0, 100) : '-';
        
        html += `
            <tr>
                <td>${event.timestamp.toFixed(2)}s</td>
                <td><strong>${event.device_id}</strong></td>
                <td><span class="badge ${badgeClass}">${event.event_type}</span></td>
                <td style="font-size: 0.875rem; color: var(--text-light);">${details}</td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    eventsEl.innerHTML = html;
    document.getElementById('eventsSection').style.display = 'block';
}
