import React, { useState, useEffect } from 'react';
import './App.css';
import ConfigurationEditor from './components/ConfigurationEditor';
import SimulationControl from './components/SimulationControl';

function App() {
  const [config, setConfig] = useState(null);
  const [simulationStatus, setSimulationStatus] = useState({
    running: false,
    current_time: 0,
    duration: 100
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load initial configuration
  useEffect(() => {
    loadConfiguration();
    // Poll simulation status every 2 seconds
    const interval = setInterval(loadSimulationStatus, 2000);
    return () => clearInterval(interval);
  }, []);

  const loadConfiguration = async () => {
    try {
      const response = await fetch('/api/config');
      if (response.ok) {
        const data = await response.json();
        setConfig(data);
        setError(null);
      } else {
        setError('No configuration found');
      }
    } catch (err) {
      setError('Failed to load configuration: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadSimulationStatus = async () => {
    try {
      const response = await fetch('/api/simulation/status');
      if (response.ok) {
        const data = await response.json();
        setSimulationStatus(data);
      }
    } catch (err) {
      console.error('Failed to load simulation status:', err);
    }
  };

  const handleConfigUpdate = async (updatedConfig) => {
    try {
      const response = await fetch('/api/config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedConfig),
      });
      
      if (response.ok) {
        setConfig(updatedConfig);
        setError(null);
        alert('Configuration updated successfully!');
      } else {
        const error = await response.json();
        setError('Failed to update configuration: ' + error.error);
      }
    } catch (err) {
      setError('Failed to update configuration: ' + err.message);
    }
  };

  const handleStartSimulation = async (duration) => {
    try {
      const response = await fetch('/api/simulation/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ duration }),
      });
      
      if (response.ok) {
        setError(null);
        loadSimulationStatus();
      } else {
        const error = await response.json();
        setError('Failed to start simulation: ' + error.error);
      }
    } catch (err) {
      setError('Failed to start simulation: ' + err.message);
    }
  };

  const handleStopSimulation = async () => {
    try {
      const response = await fetch('/api/simulation/stop', {
        method: 'POST',
      });
      
      if (response.ok) {
        setError(null);
        loadSimulationStatus();
      } else {
        const error = await response.json();
        setError('Failed to stop simulation: ' + error.error);
      }
    } catch (err) {
      setError('Failed to stop simulation: ' + err.message);
    }
  };

  if (loading) {
    return (
      <div className="App">
        <div className="loading">Loading...</div>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Generic Simulator Configuration</h1>
      </header>
      
      {error && (
        <div className="error-banner">
          {error}
        </div>
      )}

      <div className="content">
        <SimulationControl
          status={simulationStatus}
          onStart={handleStartSimulation}
          onStop={handleStopSimulation}
        />

        {config && (
          <ConfigurationEditor
            config={config}
            onUpdate={handleConfigUpdate}
            disabled={simulationStatus.running}
          />
        )}
      </div>
    </div>
  );
}

export default App;
