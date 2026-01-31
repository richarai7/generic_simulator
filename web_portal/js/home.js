/**
 * Home page functionality
 */

document.addEventListener('DOMContentLoaded', async () => {
    await loadSystemStatus();
});

async function loadSystemStatus() {
    // Check API status
    const apiStatusEl = document.getElementById('apiStatus');
    const configCountEl = document.getElementById('configCount');
    const lastSimEl = document.getElementById('lastSim');

    try {
        // Check API health
        const isHealthy = await api.checkHealth();
        if (isHealthy) {
            apiStatusEl.innerHTML = '<span class="badge badge-success">✓ Online</span>';
        } else {
            apiStatusEl.innerHTML = '<span class="badge badge-danger">✗ Offline</span>';
        }

        // Get config count
        try {
            const configs = await api.listConfigs();
            configCountEl.textContent = configs.length;
        } catch (error) {
            configCountEl.innerHTML = '<span class="badge badge-warning">N/A</span>';
        }

        // Get last simulation info
        try {
            const events = await api.getEvents();
            if (events && events.simulation_metadata) {
                const date = new Date(events.simulation_metadata.generated_at);
                lastSimEl.textContent = date.toLocaleString();
            } else {
                lastSimEl.textContent = 'No simulations yet';
            }
        } catch (error) {
            lastSimEl.innerHTML = '<span class="badge badge-warning">N/A</span>';
        }
    } catch (error) {
        console.error('Error loading system status:', error);
        apiStatusEl.innerHTML = '<span class="badge badge-danger">✗ Error</span>';
    }
}
