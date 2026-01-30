# Database Schema

This document describes the SQLite database schema used for storing simulator configurations.

## Schema Diagram

```
┌─────────────────────────────────┐
│      configurations             │
├─────────────────────────────────┤
│ id INTEGER PK                   │
│ name TEXT UNIQUE NOT NULL       │
│ description TEXT                │
│ created_at TIMESTAMP            │
└─────────────────────────────────┘
              │
              │ 1
              │
              │
              │ *
┌─────────────────────────────────┐
│          devices                │
├─────────────────────────────────┤
│ id INTEGER PK                   │
│ config_id INTEGER FK            │
│ device_name TEXT NOT NULL       │
│ device_type TEXT NOT NULL       │
│ interval REAL NOT NULL          │
│ failure_probability REAL        │
│ config_json TEXT                │
│ UNIQUE(config_id, device_name)  │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│       connections               │
├─────────────────────────────────┤
│ id INTEGER PK                   │
│ config_id INTEGER FK            │
│ source_device TEXT NOT NULL     │
│ target_device TEXT NOT NULL     │
└─────────────────────────────────┘
```

## Table Definitions

### configurations

Stores high-level simulation configuration metadata.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique configuration identifier |
| name | TEXT | UNIQUE NOT NULL | Human-readable configuration name |
| description | TEXT | | Optional description of the configuration |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

**Indexes**: Automatic index on `name` (UNIQUE constraint)

### devices

Stores individual device configurations within a simulation.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique device identifier |
| config_id | INTEGER | FOREIGN KEY, NOT NULL | References configurations(id) |
| device_name | TEXT | NOT NULL | Device name (unique within config) |
| device_type | TEXT | NOT NULL | Type of device (sensor, processor, actuator) |
| interval | REAL | NOT NULL | Processing interval in seconds |
| failure_probability | REAL | DEFAULT 0.0 | Probability of failure (0.0-1.0) |
| config_json | TEXT | | Device-specific configuration as JSON |

**Constraints**:
- `UNIQUE(config_id, device_name)`: Device names must be unique within a configuration
- `FOREIGN KEY (config_id) REFERENCES configurations(id)`: Ensures referential integrity

**Valid device_type values**:
- `sensor`: Generates periodic readings
- `processor`: Processes inputs from other devices
- `actuator`: Performs actions based on inputs

### connections

Defines output connections between devices (directed graph edges).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique connection identifier |
| config_id | INTEGER | FOREIGN KEY, NOT NULL | References configurations(id) |
| source_device | TEXT | NOT NULL | Name of source device |
| target_device | TEXT | NOT NULL | Name of target device |

**Constraints**:
- `FOREIGN KEY (config_id) REFERENCES configurations(id)`: Ensures referential integrity

**Notes**:
- Source and target devices must exist in the same configuration
- Multiple connections from one device are supported (fan-out)
- Multiple connections to one device are supported (fan-in)
- Cycles are allowed (feedback loops)

## JSON Configuration Format

The `config_json` field in the devices table stores device-specific configuration as JSON.

### Sensor Configuration Example

```json
{
  "min_value": 0.0,
  "max_value": 100.0,
  "unit": "celsius"
}
```

### Processor Configuration Example

```json
{
  "buffer_size": 10,
  "aggregation_method": "average"
}
```

### Actuator Configuration Example

```json
{
  "action_type": "adjust_temperature",
  "min_adjustment": -5.0,
  "max_adjustment": 5.0
}
```

## Queries

### Common Queries

**Get all configurations:**
```sql
SELECT * FROM configurations ORDER BY created_at DESC;
```

**Get configuration with devices:**
```sql
SELECT c.name, c.description, d.device_name, d.device_type, d.interval
FROM configurations c
LEFT JOIN devices d ON c.id = d.config_id
WHERE c.id = ?;
```

**Get device topology:**
```sql
SELECT source_device, target_device
FROM connections
WHERE config_id = ?;
```

**Find devices by type:**
```sql
SELECT device_name, interval, failure_probability
FROM devices
WHERE config_id = ? AND device_type = ?;
```

## Data Integrity

### Referential Integrity

- Deleting a configuration will fail if devices or connections reference it (need CASCADE or manual cleanup)
- Device names must be unique within a configuration
- Connections reference device names as strings (validated at runtime, not database level)

### Validation

The ConfigManager class performs additional validation:
- Device names must be valid identifiers
- Failure probability must be between 0.0 and 1.0
- Interval must be positive
- JSON configuration must be valid JSON
- Connection source/target devices must exist

## Migration Strategy

For future schema changes:

1. **Adding columns**: Use `ALTER TABLE ADD COLUMN` (SQLite limitation: can't drop columns easily)
2. **Changing constraints**: Create new table, copy data, drop old table, rename new table
3. **Adding indexes**: Use `CREATE INDEX` for performance optimization
4. **Version tracking**: Consider adding a `schema_version` table

## Performance Considerations

### Indexes

Current indexes (implicit):
- PRIMARY KEY indexes on all `id` columns
- UNIQUE index on `configurations.name`
- UNIQUE index on `devices(config_id, device_name)`

Recommended additional indexes for large deployments:
```sql
CREATE INDEX idx_devices_config_id ON devices(config_id);
CREATE INDEX idx_devices_type ON devices(device_type);
CREATE INDEX idx_connections_config_id ON connections(config_id);
```

### Query Optimization

- Use prepared statements (already implemented in ConfigManager)
- Batch inserts when creating multiple devices
- Use transactions for multi-row operations
- Consider connection pooling for concurrent access

## Backup and Recovery

### Backup

SQLite database can be backed up by simply copying the file:
```bash
cp configs/simulator.db configs/simulator.db.backup
```

Or use SQLite backup command:
```bash
sqlite3 configs/simulator.db ".backup configs/simulator.db.backup"
```

### Export to SQL

```bash
sqlite3 configs/simulator.db .dump > backup.sql
```

### Import from SQL

```bash
sqlite3 new_database.db < backup.sql
```

## Security Considerations

1. **SQL Injection**: All queries use parameterized statements
2. **File Permissions**: Ensure database file has appropriate permissions
3. **Input Validation**: Validate all user inputs before database operations
4. **Concurrency**: SQLite has limited write concurrency (single writer)

## Future Enhancements

Potential schema extensions:

1. **Versioning**: Add version tracking for configurations
2. **Tags**: Add tagging support for configurations
3. **Metrics**: Store simulation results/metrics
4. **User Management**: Add user/ownership tracking
5. **Scheduling**: Add scheduled simulation runs
6. **Parameters**: Support parameterized configurations
