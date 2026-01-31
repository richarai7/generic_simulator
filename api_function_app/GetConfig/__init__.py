"""
GetConfig Azure Function
Returns the latest process/device configuration.
"""

import azure.functions as func
import json
import os
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


def get_latest_config_file(configs_path: str) -> str:
    """Find the most recently modified config JSON file."""
    config_files = list(Path(configs_path).glob("*.json"))
    
    if not config_files:
        raise FileNotFoundError(f"No config files found in {configs_path}")
    
    # Get the most recently modified file
    latest_file = max(config_files, key=lambda p: p.stat().st_mtime)
    return str(latest_file)


def list_config_files(configs_path: str) -> list:
    """List all available config files."""
    config_files = list(Path(configs_path).glob("*.json"))
    return [f.name for f in config_files]


def load_config(file_path: str) -> Dict[str, Any]:
    """Load configuration from JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    GET /api/config
    
    Returns process/device configuration.
    
    Query Parameters:
    - file: Optional filename to load specific config
    - list: If true, returns list of available config files
    - latest: If true (default), returns the latest config
    """
    logger.info('GetConfig function triggered')
    
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
        
        # Check if listing all configs
        if req.params.get('list') == 'true':
            try:
                config_files = list_config_files(str(configs_dir))
                logger.info(f"Found {len(config_files)} config files")
                return func.HttpResponse(
                    json.dumps({"configs": config_files}),
                    status_code=200,
                    mimetype="application/json"
                )
            except Exception as e:
                logger.error(f"Error listing configs: {str(e)}")
                return func.HttpResponse(
                    json.dumps({"error": str(e)}),
                    status_code=500,
                    mimetype="application/json"
                )
        
        # Get specific file or latest
        file_param = req.params.get('file')
        
        if file_param:
            # Load specific file
            file_path = configs_dir / file_param
            if not file_path.exists():
                logger.error(f"Config file not found: {file_path}")
                return func.HttpResponse(
                    json.dumps({"error": f"Config file not found: {file_param}"}),
                    status_code=404,
                    mimetype="application/json"
                )
        else:
            # Load latest file
            try:
                file_path = get_latest_config_file(str(configs_dir))
                logger.info(f"Loading latest config: {file_path}")
            except FileNotFoundError as e:
                logger.error(str(e))
                return func.HttpResponse(
                    json.dumps({"error": str(e)}),
                    status_code=404,
                    mimetype="application/json"
                )
        
        # Load the config
        config = load_config(file_path)
        
        # Add metadata about the file
        response = {
            "config": config,
            "file_info": {
                "filename": Path(file_path).name,
                "path": str(file_path)
            }
        }
        
        logger.info(f"Successfully loaded config: {Path(file_path).name}")
        
        return func.HttpResponse(
            json.dumps(response, indent=2),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logger.error(f"Error in GetConfig: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({"error": f"Internal server error: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )
