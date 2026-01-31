"""
PostConfig Azure Function
Receives and saves updated configuration files.
"""

import azure.functions as func
import json
import os
import logging
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


def validate_config(config: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate the configuration structure.
    
    Returns:
        (is_valid, error_message)
    """
    # Check required fields
    if "devices" not in config:
        return False, "Missing required field: devices"
    
    if not isinstance(config["devices"], list):
        return False, "Field 'devices' must be a list"
    
    # Validate each device
    device_ids = set()
    for idx, device in enumerate(config["devices"]):
        # Check required device fields
        required_fields = ["id", "type"]
        for field in required_fields:
            if field not in device:
                return False, f"Device at index {idx} missing required field: {field}"
        
        # Check for duplicate device IDs
        device_id = device["id"]
        if device_id in device_ids:
            return False, f"Duplicate device ID found: {device_id}"
        device_ids.add(device_id)
        
        # Validate timing parameters
        if "wait_execution_min" in device and "wait_execution_max" in device:
            if device["wait_execution_max"] < device["wait_execution_min"]:
                return False, f"Device {device_id}: wait_execution_max must be >= wait_execution_min"
        
        # Validate outputs reference existing devices
        if "outputs" in device:
            if not isinstance(device["outputs"], list):
                return False, f"Device {device_id}: outputs must be a list"
    
    # Validate that all output references exist
    for device in config["devices"]:
        for output_id in device.get("outputs", []):
            if output_id not in device_ids:
                return False, f"Device {device['id']} references non-existent output device: {output_id}"
    
    return True, ""


def save_config(config: Dict[str, Any], configs_dir: Path, filename: str = None) -> str:
    """
    Save configuration to file.
    
    Args:
        config: Configuration dictionary
        configs_dir: Path to configs directory
        filename: Optional filename (will generate timestamp-based name if not provided)
    
    Returns:
        Path to saved file
    """
    if filename is None:
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"config_{timestamp}.json"
    
    # Ensure filename has .json extension
    if not filename.endswith('.json'):
        filename += '.json'
    
    file_path = configs_dir / filename
    
    with open(file_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    return str(file_path)


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    POST /api/config
    
    Receives and saves updated configuration.
    
    Request Body: JSON configuration object
    Query Parameters:
    - filename: Optional filename to save as (default: auto-generated timestamp)
    - validate_only: If true, only validates without saving
    """
    logger.info('PostConfig function triggered')
    
    try:
        # Get configs path from environment or use default
        configs_path = os.environ.get('SIMULATOR_CONFIGS_PATH', '../configs')
        base_path = Path(__file__).parent.parent / configs_path
        
        # Resolve to absolute path
        configs_dir = base_path.resolve()
        
        if not configs_dir.exists():
            logger.error(f"Configs directory not found: {configs_dir}")
            return func.HttpResponse(
                json.dumps({"error": "Configs directory not found"}),
                status_code=404,
                mimetype="application/json"
            )
        
        # Parse request body
        try:
            config = req.get_json()
        except ValueError as e:
            logger.error(f"Invalid JSON in request body: {str(e)}")
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON in request body"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Validate configuration
        is_valid, error_message = validate_config(config)
        
        if not is_valid:
            logger.warning(f"Configuration validation failed: {error_message}")
            return func.HttpResponse(
                json.dumps({
                    "error": "Configuration validation failed",
                    "details": error_message
                }),
                status_code=400,
                mimetype="application/json"
            )
        
        # Check if validate-only mode
        if req.params.get('validate_only') == 'true':
            logger.info("Validation only - config is valid")
            return func.HttpResponse(
                json.dumps({
                    "valid": True,
                    "message": "Configuration is valid"
                }),
                status_code=200,
                mimetype="application/json"
            )
        
        # Save configuration
        filename = req.params.get('filename')
        try:
            saved_path = save_config(config, configs_dir, filename)
            logger.info(f"Configuration saved to: {saved_path}")
            
            return func.HttpResponse(
                json.dumps({
                    "success": True,
                    "message": "Configuration saved successfully",
                    "file_info": {
                        "filename": Path(saved_path).name,
                        "path": saved_path
                    }
                }),
                status_code=200,
                mimetype="application/json"
            )
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            return func.HttpResponse(
                json.dumps({
                    "error": f"Failed to save configuration: {str(e)}"
                }),
                status_code=500,
                mimetype="application/json"
            )
        
    except Exception as e:
        logger.error(f"Error in PostConfig: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({"error": f"Internal server error: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )
