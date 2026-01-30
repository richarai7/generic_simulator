"""Database schema and configuration management."""

import sqlite3
import json
from typing import Dict, List, Any, Optional
from pathlib import Path


class ConfigManager:
    """Manage simulator configurations in SQLite database."""

    def __init__(self, db_path: str):
        """Initialize configuration manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize database schema if not exists."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create configurations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS configurations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create devices table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS devices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    config_id INTEGER NOT NULL,
                    device_name TEXT NOT NULL,
                    device_type TEXT NOT NULL,
                    interval REAL NOT NULL,
                    failure_probability REAL DEFAULT 0.0,
                    config_json TEXT,
                    FOREIGN KEY (config_id) REFERENCES configurations(id),
                    UNIQUE(config_id, device_name)
                )
            """)
            
            # Create connections table (for output chaining)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS connections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    config_id INTEGER NOT NULL,
                    source_device TEXT NOT NULL,
                    target_device TEXT NOT NULL,
                    FOREIGN KEY (config_id) REFERENCES configurations(id)
                )
            """)
            
            conn.commit()

    def create_configuration(self, name: str, description: str = "") -> int:
        """Create a new configuration.
        
        Args:
            name: Configuration name
            description: Optional description
            
        Returns:
            Configuration ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO configurations (name, description) VALUES (?, ?)",
                (name, description)
            )
            conn.commit()
            return cursor.lastrowid

    def add_device(
        self,
        config_id: int,
        device_name: str,
        device_type: str,
        interval: float,
        failure_probability: float = 0.0,
        config: Optional[Dict[str, Any]] = None
    ):
        """Add a device to a configuration.
        
        Args:
            config_id: Configuration ID
            device_name: Unique device name
            device_type: Type of device
            interval: Processing interval in seconds
            failure_probability: Probability of failure (0.0-1.0)
            config: Optional device-specific configuration
        """
        config_json = json.dumps(config) if config else None
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO devices 
                   (config_id, device_name, device_type, interval, failure_probability, config_json)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (config_id, device_name, device_type, interval, failure_probability, config_json)
            )
            conn.commit()

    def add_connection(self, config_id: int, source_device: str, target_device: str):
        """Add a connection between devices.
        
        Args:
            config_id: Configuration ID
            source_device: Source device name
            target_device: Target device name
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO connections (config_id, source_device, target_device) VALUES (?, ?, ?)",
                (config_id, source_device, target_device)
            )
            conn.commit()

    def list_configurations(self) -> List[Dict[str, Any]]:
        """List all available configurations.
        
        Returns:
            List of configuration dictionaries
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, description, created_at FROM configurations")
            rows = cursor.fetchall()
            
            return [
                {
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "created_at": row[3]
                }
                for row in rows
            ]

    def get_configuration(self, config_id: int) -> Dict[str, Any]:
        """Get a complete configuration with devices and connections.
        
        Args:
            config_id: Configuration ID
            
        Returns:
            Configuration dictionary with devices and connections
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get configuration info
            cursor.execute(
                "SELECT id, name, description FROM configurations WHERE id = ?",
                (config_id,)
            )
            config_row = cursor.fetchone()
            
            if not config_row:
                raise ValueError(f"Configuration {config_id} not found")
            
            # Get devices
            cursor.execute(
                """SELECT device_name, device_type, interval, failure_probability, config_json
                   FROM devices WHERE config_id = ?""",
                (config_id,)
            )
            device_rows = cursor.fetchall()
            
            devices = []
            for row in device_rows:
                device = {
                    "name": row[0],
                    "type": row[1],
                    "interval": row[2],
                    "failure_probability": row[3],
                    "config": json.loads(row[4]) if row[4] else {}
                }
                devices.append(device)
            
            # Get connections
            cursor.execute(
                "SELECT source_device, target_device FROM connections WHERE config_id = ?",
                (config_id,)
            )
            connection_rows = cursor.fetchall()
            
            connections = [
                {"source": row[0], "target": row[1]}
                for row in connection_rows
            ]
            
            return {
                "id": config_row[0],
                "name": config_row[1],
                "description": config_row[2],
                "devices": devices,
                "connections": connections
            }

    def get_configuration_by_name(self, name: str) -> Dict[str, Any]:
        """Get a configuration by name.
        
        Args:
            name: Configuration name
            
        Returns:
            Configuration dictionary
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM configurations WHERE name = ?", (name,))
            row = cursor.fetchone()
            
            if not row:
                raise ValueError(f"Configuration '{name}' not found")
            
            return self.get_configuration(row[0])
