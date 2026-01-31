"""
GetEvents Azure Function
Returns simulator event log data for dashboard and 3D view.
"""

import azure.functions as func
import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def get_latest_output_file(outputs_path: str) -> str:
    """Find the most recently modified output JSON file."""
    output_files = list(Path(outputs_path).glob("*.json"))
    
    if not output_files:
        raise FileNotFoundError(f"No output files found in {outputs_path}")
    
    # Get the most recently modified file
    latest_file = max(output_files, key=lambda p: p.stat().st_mtime)
    return str(latest_file)


def load_event_log(file_path: str) -> Dict[str, Any]:
    """Load event log from JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    GET /api/events
    
    Returns simulator event log data.
    
    Query Parameters:
    - file: Optional filename to load specific event log
    - latest: If true (default), returns the latest event log
    """
    logger.info('GetEvents function triggered')
    
    try:
        # Get outputs path from environment or use default
        outputs_path = os.environ.get('SIMULATOR_OUTPUTS_PATH', '../outputs')
        base_path = Path(__file__).parent.parent / outputs_path
        
        # Resolve to absolute path
        outputs_dir = base_path.resolve()
        
        if not outputs_dir.exists():
            logger.error(f"Outputs directory not found: {outputs_dir}")
            return func.HttpResponse(
                json.dumps({"error": "Outputs directory not found"}),
                status_code=404,
                mimetype="application/json"
            )
        
        # Get specific file or latest
        file_param = req.params.get('file')
        
        if file_param:
            # Load specific file
            file_path = outputs_dir / file_param
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return func.HttpResponse(
                    json.dumps({"error": f"File not found: {file_param}"}),
                    status_code=404,
                    mimetype="application/json"
                )
        else:
            # Load latest file
            try:
                file_path = get_latest_output_file(str(outputs_dir))
                logger.info(f"Loading latest file: {file_path}")
            except FileNotFoundError as e:
                logger.error(str(e))
                return func.HttpResponse(
                    json.dumps({"error": str(e)}),
                    status_code=404,
                    mimetype="application/json"
                )
        
        # Load the event log
        event_log = load_event_log(file_path)
        
        # Add metadata about the file
        event_log["file_info"] = {
            "filename": Path(file_path).name,
            "path": str(file_path)
        }
        
        logger.info(f"Successfully loaded event log with {len(event_log.get('events', []))} events")
        
        return func.HttpResponse(
            json.dumps(event_log, indent=2),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logger.error(f"Error in GetEvents: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({"error": f"Internal server error: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )
