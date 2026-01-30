"""Event logging to JSON file."""

import json
from typing import Dict, Any
from pathlib import Path
from datetime import datetime


class EventLogger:
    """Log simulation events to JSON file."""

    def __init__(self, log_file: str):
        """Initialize event logger.
        
        Args:
            log_file: Path to JSON log file
        """
        self.log_file = Path(log_file)
        self.events = []
        
        # Ensure parent directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def log(self, event: Dict[str, Any]):
        """Log an event.
        
        Args:
            event: Event data dictionary
        """
        # Add real timestamp
        event["real_timestamp"] = datetime.now().isoformat()
        self.events.append(event)

    def save(self):
        """Save all events to JSON file."""
        with open(self.log_file, 'w') as f:
            json.dump({
                "simulation_log": self.events,
                "event_count": len(self.events),
                "generated_at": datetime.now().isoformat()
            }, f, indent=2)

    def get_events(self):
        """Get all logged events.
        
        Returns:
            List of events
        """
        return self.events
