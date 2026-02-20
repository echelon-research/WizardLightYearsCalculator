"""ESI API client for fetching EVE Online system data."""

import requests
from typing import Dict
from config import ESI_BASE_URL, ESI_COMPATIBILITY_DATE, ESI_USER_AGENT


class ESIClient:
    """Client for interacting with EVE Online ESI API."""
    
    def __init__(self):
        """Initialize ESI client with required headers."""
        self.base_url = ESI_BASE_URL
        self.headers = {
            "X-Compatibility-Date": ESI_COMPATIBILITY_DATE,
            "user-agent": ESI_USER_AGENT
        }
    
    def get_system_info(self, system_id: int) -> Dict:
        """
        Fetch system information from ESI API.
        
        Args:
            system_id: The EVE Online system ID
            
        Returns:
            Dictionary containing system information
            
        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        url = f"{self.base_url}/universe/systems/{system_id}/"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract only the fields we need
            return {
                "system_id": data["system_id"],
                "name": data["name"],
                "x": data["position"]["x"],
                "y": data["position"]["y"],
                "z": data["position"]["z"]
            }
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise ValueError(f"System ID {system_id} not found")
            raise
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to fetch system data from ESI: {str(e)}")
        except (KeyError, ValueError) as e:
            raise RuntimeError(f"Invalid response format from ESI: {str(e)}")
