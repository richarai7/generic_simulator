import React, { useState } from 'react';
import './SimulationControl.css';

function SimulationControl({ status, onStart, onStop }) {
  const [duration, setDuration] = useState(100);

  const handleStart = () => {
    onStart(duration);
  };

  const getStatusColor = () => {
    if (status.running) return '#4caf50';
    return '#9e9e9e';
  };

  const getProgress = () => {
    if (status.duration > 0) {
      return (status.current_time / status.duration) * 100;
    }
    return 0;
  };

  return (
    <div className="simulation-control">
      <h2>Simulation Control</h2>
      
      <div className="status-section">
        <div className="status-indicator">
          <div 
            className="status-dot" 
            style={{ backgroundColor: getStatusColor() }}
          />
          <span className="status-text">
            {status.running ? 'Running' : 'Stopped'}
          </span>
        </div>

        {status.running && (
          <div className="progress-section">
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${getProgress()}%` }}
              />
            </div>
            <div className="progress-text">
              Time: {status.current_time.toFixed(1)} / {status.duration}
            </div>
          </div>
        )}
      </div>

      <div className="control-section">
        <div className="duration-input">
          <label htmlFor="duration">Duration:</label>
          <input
            id="duration"
            type="number"
            min="1"
            max="10000"
            value={duration}
            onChange={(e) => setDuration(Number(e.target.value))}
            disabled={status.running}
          />
          <span className="unit">time units</span>
        </div>

        <div className="button-group">
          <button
            className="btn btn-start"
            onClick={handleStart}
            disabled={status.running}
          >
            Start Simulation
          </button>
          
          <button
            className="btn btn-stop"
            onClick={onStop}
            disabled={!status.running}
          >
            Stop Simulation
          </button>
        </div>
      </div>

      {status.device_states && (
        <div className="device-states">
          <h3>Device States</h3>
          <div className="device-grid">
            {Object.entries(status.device_states).map(([name, state]) => (
              <div key={name} className="device-state-item">
                <span className="device-name">{name}</span>
                <span className={`device-state state-${state}`}>{state}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default SimulationControl;
