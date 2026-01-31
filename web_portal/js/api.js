/**
 * API Client for Generic Simulator
 * Handles communication with Azure Functions backend
 */

class SimulatorAPI {
    constructor(baseUrl = 'http://localhost:7071/api') {
        this.baseUrl = baseUrl;
    }

    /**
     * Get all available configurations
     */
    async listConfigs() {
        try {
            const response = await fetch(`${this.baseUrl}/config?list=true`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            return data.configs || [];
        } catch (error) {
            console.error('Error listing configs:', error);
            throw error;
        }
    }

    /**
     * Get a specific configuration
     * @param {string} filename - Optional filename, gets latest if not provided
     */
    async getConfig(filename = null) {
        try {
            const url = filename 
                ? `${this.baseUrl}/config?file=${filename}`
                : `${this.baseUrl}/config`;
            
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error getting config:', error);
            throw error;
        }
    }

    /**
     * Save a configuration
     * @param {object} config - Configuration object
     * @param {string} filename - Optional filename
     * @param {boolean} validateOnly - Only validate, don't save
     */
    async saveConfig(config, filename = null, validateOnly = false) {
        try {
            let url = `${this.baseUrl}/config`;
            const params = new URLSearchParams();
            
            if (filename) {
                params.append('filename', filename);
            }
            if (validateOnly) {
                params.append('validate_only', 'true');
            }
            
            if (params.toString()) {
                url += `?${params.toString()}`;
            }

            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(config)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.details || error.error || 'Failed to save config');
            }

            return await response.json();
        } catch (error) {
            console.error('Error saving config:', error);
            throw error;
        }
    }

    /**
     * Get simulation events/results
     * @param {string} filename - Optional filename, gets latest if not provided
     */
    async getEvents(filename = null) {
        try {
            const url = filename 
                ? `${this.baseUrl}/events?file=${filename}`
                : `${this.baseUrl}/events`;
            
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error getting events:', error);
            throw error;
        }
    }

    /**
     * Check if API is available
     */
    async checkHealth() {
        try {
            await this.listConfigs();
            return true;
        } catch (error) {
            return false;
        }
    }
}

// Utility functions
const utils = {
    /**
     * Format timestamp to readable date
     */
    formatDate(timestamp) {
        if (!timestamp) return 'N/A';
        const date = new Date(timestamp);
        return date.toLocaleString();
    },

    /**
     * Format duration in seconds to readable format
     */
    formatDuration(seconds) {
        if (seconds < 60) {
            return `${seconds.toFixed(1)}s`;
        } else if (seconds < 3600) {
            const mins = Math.floor(seconds / 60);
            const secs = Math.floor(seconds % 60);
            return `${mins}m ${secs}s`;
        } else {
            const hours = Math.floor(seconds / 3600);
            const mins = Math.floor((seconds % 3600) / 60);
            return `${hours}h ${mins}m`;
        }
    },

    /**
     * Show loading spinner
     */
    showLoading(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = '<div class="spinner"></div>';
        }
    },

    /**
     * Show error message
     */
    showError(elementId, message) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = `<div class="alert alert-error">${message}</div>`;
        }
    },

    /**
     * Show success message
     */
    showSuccess(elementId, message) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = `<div class="alert alert-success">${message}</div>`;
        }
    }
};

// Create global API instance
const api = new SimulatorAPI();
