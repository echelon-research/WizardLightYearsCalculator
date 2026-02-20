"""Distance calculation module for EVE Online systems."""

import math
from typing import Dict
from config import LIGHTYEAR_IN_METERS


def calculate_distance(system1: Dict, system2: Dict) -> Dict[str, float]:
    """
    Calculate the distance between two EVE Online systems.
    
    Uses the EVE Online specific lightyear value of 9.46 × 10^15 meters,
    as specified in the EVE Online developer documentation for jump drive
    range calculations.
    
    Args:
        system1: Dictionary with keys x, y, z for first system
        system2: Dictionary with keys x, y, z for second system
        
    Returns:
        Dictionary containing:
            - distance_meters: Distance in meters
            - distance_lightyears: Distance in light-years
            
    Reference:
        https://developers.eveonline.com/docs/guides/map-data/#jump-drives
    """
    # Extract coordinates
    x1, y1, z1 = system1["x"], system1["y"], system1["z"]
    x2, y2, z2 = system2["x"], system2["y"], system2["z"]
    
    # Calculate Euclidean distance in 3D space
    distance_meters = math.sqrt(
        (x2 - x1) ** 2 +
        (y2 - y1) ** 2 +
        (z2 - z1) ** 2
    )
    
    # Convert to light-years using EVE Online's specific value
    distance_lightyears = distance_meters / LIGHTYEAR_IN_METERS
    
    return {
        "distance_meters": distance_meters,
        "distance_lightyears": distance_lightyears
    }
