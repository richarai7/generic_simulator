import React, { useState, useEffect } from 'react';
import './ConfigurationEditor.css';

function ConfigurationEditor({ config, onUpdate, disabled }) {
  const [editedConfig, setEditedConfig] = useState(config);
  const [editing, setEditing] = useState(false);

  useEffect(() => {
    setEditedConfig(config);
  }, [config]);

  const handleDeviceChange = (index, field, value) => {
    const newDevices = [...editedConfig.devices];
    newDevices[index] = {
      ...newDevices[index],
      [field]: value
    };
    setEditedConfig({
      ...editedConfig,
      devices: newDevices
    });
    setEditing(true);
  };

  const handleDeviceConfigChange = (index, configField, value) => {
    const newDevices = [...editedConfig.devices];
    newDevices[index] = {
      ...newDevices[index],
      config: {
        ...newDevices[index].config,
        [configField]: value
      }
    };
    setEditedConfig({
      ...editedConfig,
      devices: newDevices
    });
    setEditing(true);
  };

  const handleAddDevice = () => {
    const newDevice = {
      name: `device_${editedConfig.devices.length + 1}`,
      type: 'sensor',
      interval: 10.0,
      failure_probability: 0.01,
      config: {}
    };
    setEditedConfig({
      ...editedConfig,
      devices: [...editedConfig.devices, newDevice]
    });
    setEditing(true);
  };

  const handleRemoveDevice = (index) => {
    const deviceName = editedConfig.devices[index].name;
    const newDevices = editedConfig.devices.filter((_, i) => i !== index);
    const newConnections = editedConfig.connections.filter(
      conn => conn.source !== deviceName && conn.target !== deviceName
    );
    setEditedConfig({
      ...editedConfig,
      devices: newDevices,
      connections: newConnections
    });
    setEditing(true);
  };

  const handleAddConnection = () => {
    if (editedConfig.devices.length >= 2) {
      const newConnection = {
        source: editedConfig.devices[0].name,
        target: editedConfig.devices[1].name
      };
      setEditedConfig({
        ...editedConfig,
        connections: [...editedConfig.connections, newConnection]
      });
      setEditing(true);
    }
  };

  const handleConnectionChange = (index, field, value) => {
    const newConnections = [...editedConfig.connections];
    newConnections[index] = {
      ...newConnections[index],
      [field]: value
    };
    setEditedConfig({
      ...editedConfig,
      connections: newConnections
    });
    setEditing(true);
  };

  const handleRemoveConnection = (index) => {
    const newConnections = editedConfig.connections.filter((_, i) => i !== index);
    setEditedConfig({
      ...editedConfig,
      connections: newConnections
    });
    setEditing(true);
  };

  const handleSave = () => {
    onUpdate(editedConfig);
    setEditing(false);
  };

  const handleReset = () => {
    setEditedConfig(config);
    setEditing(false);
  };

  return (
    <div className="configuration-editor">
      <div className="editor-header">
        <h2>Configuration Editor</h2>
        {disabled && (
          <div className="disabled-notice">
            Configuration is locked while simulation is running
          </div>
        )}
      </div>

      <div className="config-info">
        <div className="info-row">
          <label>Name:</label>
          <span>{editedConfig.name}</span>
        </div>
        <div className="info-row">
          <label>Description:</label>
          <span>{editedConfig.description}</span>
        </div>
      </div>

      <div className="devices-section">
        <div className="section-header">
          <h3>Devices ({editedConfig.devices.length})</h3>
          <button
            className="btn-small btn-add"
            onClick={handleAddDevice}
            disabled={disabled}
          >
            + Add Device
          </button>
        </div>

        <div className="devices-list">
          {editedConfig.devices.map((device, index) => (
            <div key={index} className="device-card">
              <div className="device-header">
                <input
                  type="text"
                  value={device.name}
                  onChange={(e) => handleDeviceChange(index, 'name', e.target.value)}
                  disabled={disabled}
                  className="device-name-input"
                />
                <button
                  className="btn-remove"
                  onClick={() => handleRemoveDevice(index)}
                  disabled={disabled}
                >
                  ✕
                </button>
              </div>

              <div className="device-fields">
                <div className="field-group">
                  <label>Type:</label>
                  <select
                    value={device.type}
                    onChange={(e) => handleDeviceChange(index, 'type', e.target.value)}
                    disabled={disabled}
                  >
                    <option value="sensor">Sensor</option>
                    <option value="processor">Processor</option>
                    <option value="actuator">Actuator</option>
                  </select>
                </div>

                <div className="field-group">
                  <label>Interval:</label>
                  <input
                    type="number"
                    min="0.1"
                    step="0.1"
                    value={device.interval}
                    onChange={(e) => handleDeviceChange(index, 'interval', Number(e.target.value))}
                    disabled={disabled}
                  />
                </div>

                <div className="field-group">
                  <label>Failure Probability:</label>
                  <input
                    type="number"
                    min="0"
                    max="1"
                    step="0.01"
                    value={device.failure_probability}
                    onChange={(e) => handleDeviceChange(index, 'failure_probability', Number(e.target.value))}
                    disabled={disabled}
                  />
                </div>
              </div>

              {device.type === 'sensor' && (
                <div className="device-config">
                  <label>Sensor Configuration:</label>
                  <div className="config-fields">
                    <input
                      type="number"
                      placeholder="Min Value"
                      value={device.config.min_value || 0}
                      onChange={(e) => handleDeviceConfigChange(index, 'min_value', Number(e.target.value))}
                      disabled={disabled}
                    />
                    <input
                      type="number"
                      placeholder="Max Value"
                      value={device.config.max_value || 100}
                      onChange={(e) => handleDeviceConfigChange(index, 'max_value', Number(e.target.value))}
                      disabled={disabled}
                    />
                    <input
                      type="text"
                      placeholder="Unit"
                      value={device.config.unit || 'units'}
                      onChange={(e) => handleDeviceConfigChange(index, 'unit', e.target.value)}
                      disabled={disabled}
                    />
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="connections-section">
        <div className="section-header">
          <h3>Connections ({editedConfig.connections.length})</h3>
          <button
            className="btn-small btn-add"
            onClick={handleAddConnection}
            disabled={disabled || editedConfig.devices.length < 2}
          >
            + Add Connection
          </button>
        </div>

        <div className="connections-list">
          {editedConfig.connections.map((connection, index) => (
            <div key={index} className="connection-item">
              <select
                value={connection.source}
                onChange={(e) => handleConnectionChange(index, 'source', e.target.value)}
                disabled={disabled}
              >
                {editedConfig.devices.map(device => (
                  <option key={device.name} value={device.name}>
                    {device.name}
                  </option>
                ))}
              </select>
              <span className="arrow">→</span>
              <select
                value={connection.target}
                onChange={(e) => handleConnectionChange(index, 'target', e.target.value)}
                disabled={disabled}
              >
                {editedConfig.devices.map(device => (
                  <option key={device.name} value={device.name}>
                    {device.name}
                  </option>
                ))}
              </select>
              <button
                className="btn-remove"
                onClick={() => handleRemoveConnection(index)}
                disabled={disabled}
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      </div>

      {editing && !disabled && (
        <div className="editor-actions">
          <button className="btn btn-save" onClick={handleSave}>
            Save Configuration
          </button>
          <button className="btn btn-reset" onClick={handleReset}>
            Reset Changes
          </button>
        </div>
      )}
    </div>
  );
}

export default ConfigurationEditor;
