"""Main Flask application for WizardLightYearsCalculator API."""

from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from typing import Tuple, Dict, Any
import logging
from database import Database
from esi_client import ESIClient
from calculator import calculate_distance
from config import (
    MIN_SYSTEM_ID, MAX_SYSTEM_ID, API_HOST, API_PORT, DEBUG,
    RATE_LIMIT_ENABLED, RATE_LIMIT_PER_MINUTE, RATE_LIMIT_PER_HOUR
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize rate limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[f"{RATE_LIMIT_PER_HOUR}/hour"],
    storage_uri="memory://",
    enabled=RATE_LIMIT_ENABLED
)

db = Database()
esi = ESIClient()


def validate_system_id(system_id: int) -> Tuple[bool, str]:
    """
    Validate that a system ID is within the acceptable range.
    
    Args:
        system_id: The system ID to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(system_id, int):
        return False, "System ID must be an integer"
    
    if system_id < MIN_SYSTEM_ID or system_id > MAX_SYSTEM_ID:
        return False, f"System ID must be between {MIN_SYSTEM_ID:,} and {MAX_SYSTEM_ID:,}"
    
    return True, ""


def get_or_fetch_system(system_id: int) -> Dict[str, Any]:
    """
    Get system data from database or fetch from ESI if not present.
    
    Args:
        system_id: The EVE Online system ID
        
    Returns:
        Dictionary with system information
        
    Raises:
        ValueError: If system not found
        RuntimeError: If ESI API fails
    """
    # Check database first
    system_data = db.get_system(system_id)
    
    if system_data:
        # Update last_update timestamp
        db.update_system_timestamp(system_id)
        return system_data
    
    # Fetch from ESI API
    esi_data = esi.get_system_info(system_id)
    
    # Store in database
    db.insert_system(
        system_id=esi_data["system_id"],
        name=esi_data["name"],
        x=esi_data["x"],
        y=esi_data["y"],
        z=esi_data["z"]
    )
    
    # Fetch complete record with timestamps
    db_record = db.get_system(system_id)
    if db_record is None:
        raise RuntimeError(f"Failed to retrieve system {system_id} after inserting")
    return db_record


@app.route("/", methods=["GET"])
def index():
    """API information endpoint."""
    return jsonify({
        "api": "WizardLightYearsCalculator",
        "version": "1.0.0",
        "description": "Calculate distances between EVE Online solar systems",
        "endpoints": {
            "/calculate-distance": "POST with system_id_1 and system_id_2"
        }
    })


@app.route("/calculate-distance", methods=["POST", "GET"])
@limiter.limit(f"{RATE_LIMIT_PER_MINUTE}/minute")
def calculate_distance_endpoint():
    """
    Calculate distance between two EVE Online systems.
    
    Request Parameters (JSON or query params):
        system_id_1: First system ID (30,000,000 - 31,000,000)
        system_id_2: Second system ID (30,000,000 - 31,000,000)
        
    Returns:
        JSON response with system information and calculated distance
    """
    # Get parameters from JSON body or query params
    if request.method == "POST" and request.is_json:
        data = request.get_json()
        system_id_1 = data.get("system_id_1")
        system_id_2 = data.get("system_id_2")
    else:
        system_id_1 = request.args.get("system_id_1", type=int)
        system_id_2 = request.args.get("system_id_2", type=int)
    
    # Validate parameters are provided
    if system_id_1 is None or system_id_2 is None:
        return jsonify({
            "error": "Both system_id_1 and system_id_2 are required"
        }), 400
    
    # Convert to integers if needed
    try:
        system_id_1 = int(system_id_1)
        system_id_2 = int(system_id_2)
    except (ValueError, TypeError):
        return jsonify({
            "error": "System IDs must be valid integers"
        }), 400
    
    # Validate system_id_1
    is_valid, error_msg = validate_system_id(system_id_1)
    if not is_valid:
        return jsonify({"error": f"system_id_1: {error_msg}"}), 400
    
    # Validate system_id_2
    is_valid, error_msg = validate_system_id(system_id_2)
    if not is_valid:
        return jsonify({"error": f"system_id_2: {error_msg}"}), 400
    
    try:
        # Get or fetch both systems
        system1 = get_or_fetch_system(system_id_1)
        system2 = get_or_fetch_system(system_id_2)
        
        # Calculate distance
        distance = calculate_distance(system1, system2)
        
        # Build response
        response = {
            "system_1": {
                "system_id": system1["system_id"],
                "name": system1["name"]
            },
            "system_2": {
                "system_id": system2["system_id"],
                "name": system2["name"]
            },
            "distance_meters": distance["distance_meters"],
            "distance_lightyears": distance["distance_lightyears"]
        }
        
        return jsonify(response), 200
        
    except ValueError as e:
        # Sanitize error message - only expose user-friendly info
        error_str = str(e)
        if "not found" in error_str.lower():
            logger.warning(f"System not found: {error_str}")
            return jsonify({"error": "One or more system IDs not found in EVE Online universe"}), 404
        logger.error(f"ValueError in distance calculation: {error_str}")
        return jsonify({"error": "Invalid system data"}), 400
        
    except RuntimeError as e:
        # Sanitize runtime errors - don't expose API details
        error_str = str(e)
        logger.error(f"RuntimeError: {error_str}")
        if "ESI" in error_str or "fetch" in error_str.lower():
            return jsonify({"error": "Unable to retrieve system information. Please try again later."}), 502
        return jsonify({"error": "A service error occurred"}), 500
        
    except Exception as e:
        # Log detailed error but return generic message
        logger.error(f"Unexpected error in calculate_distance: {type(e).__name__}: {str(e)}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred"}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit exceeded errors."""
    logger.warning(f"Rate limit exceeded: {request.remote_addr}")
    return jsonify({
        "error": "Rate limit exceeded. Please try again later.",
        "retry_after": e.description
    }), 429


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(host=API_HOST, port=API_PORT, debug=DEBUG)
