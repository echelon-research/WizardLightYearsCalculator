"""Integration tests for the ESI client."""

import unittest
import sys
import os
from unittest.mock import patch, Mock
import requests

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from esi_client import ESIClient
from config import ESI_BASE_URL, ESI_COMPATIBILITY_DATE, ESI_USER_AGENT


class TestESIClient(unittest.TestCase):
    """Test cases for ESI API client."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = ESIClient()
        self.test_system_id = 30000142
        self.mock_response_data = {
            "system_id": 30000142,
            "name": "Jita",
            "position": {
                "x": -129400292875304960.0,
                "y": 61596815791300400.0,
                "z": 1720986748719556600.0
            },
            "constellation_id": 20000020,
            "star_id": 40009077
        }
    
    def test_client_initialization(self):
        """Test that client initializes with correct headers."""
        self.assertEqual(self.client.base_url, ESI_BASE_URL)
        self.assertEqual(self.client.headers["X-Compatibility-Date"], ESI_COMPATIBILITY_DATE)
        self.assertEqual(self.client.headers["user-agent"], ESI_USER_AGENT)
    
    @patch('esi_client.requests.get')
    def test_get_system_info_success(self, mock_get):
        """Test successful system info retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.mock_response_data
        mock_get.return_value = mock_response
        
        result = self.client.get_system_info(self.test_system_id)
        
        # Verify request was made correctly
        expected_url = f"{ESI_BASE_URL}/universe/systems/{self.test_system_id}/"
        mock_get.assert_called_once_with(expected_url, headers=self.client.headers, timeout=10)
        
        # Verify response format
        self.assertEqual(result["system_id"], 30000142)
        self.assertEqual(result["name"], "Jita")
        self.assertIn("x", result)
        self.assertIn("y", result)
        self.assertIn("z", result)
        self.assertEqual(len(result), 5)  # Only 5 fields should be returned
    
    @patch('esi_client.requests.get')
    def test_get_system_info_404_not_found(self, mock_get):
        """Test handling of system not found (404 error)."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_get.return_value = mock_response
        
        with self.assertRaises(ValueError) as context:
            self.client.get_system_info(99999999)
        
        self.assertIn("not found", str(context.exception).lower())
    
    @patch('esi_client.requests.get')
    def test_get_system_info_500_server_error(self, mock_get):
        """Test handling of ESI server error (500)."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_get.return_value = mock_response
        
        with self.assertRaises(requests.exceptions.HTTPError):
            self.client.get_system_info(self.test_system_id)
    
    @patch('esi_client.requests.get')
    def test_get_system_info_timeout(self, mock_get):
        """Test handling of request timeout."""
        mock_get.side_effect = requests.exceptions.Timeout("Connection timeout")
        
        with self.assertRaises(RuntimeError) as context:
            self.client.get_system_info(self.test_system_id)
        
        self.assertIn("Failed to fetch", str(context.exception))
    
    @patch('esi_client.requests.get')
    def test_get_system_info_connection_error(self, mock_get):
        """Test handling of connection errors."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Network unreachable")
        
        with self.assertRaises(RuntimeError) as context:
            self.client.get_system_info(self.test_system_id)
        
        self.assertIn("Failed to fetch", str(context.exception))
    
    @patch('esi_client.requests.get')
    def test_get_system_info_invalid_json(self, mock_get):
        """Test handling of invalid JSON response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response
        
        with self.assertRaises(RuntimeError) as context:
            self.client.get_system_info(self.test_system_id)
        
        self.assertIn("Invalid response format", str(context.exception))
    
    @patch('esi_client.requests.get')
    def test_get_system_info_missing_fields(self, mock_get):
        """Test handling of response with missing required fields."""
        mock_response = Mock()
        mock_response.status_code = 200
        # Missing 'position' field
        mock_response.json.return_value = {
            "system_id": 30000142,
            "name": "Jita"
        }
        mock_get.return_value = mock_response
        
        with self.assertRaises(RuntimeError) as context:
            self.client.get_system_info(self.test_system_id)
        
        self.assertIn("Invalid response format", str(context.exception))
    
    @patch('esi_client.requests.get')
    def test_headers_sent_correctly(self, mock_get):
        """Test that all required headers are sent."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.mock_response_data
        mock_get.return_value = mock_response
        
        self.client.get_system_info(self.test_system_id)
        
        # Get the call arguments
        call_args = mock_get.call_args
        headers = call_args[1]['headers']
        
        # Verify all required headers present
        self.assertIn("X-Compatibility-Date", headers)
        self.assertIn("user-agent", headers)
        self.assertEqual(headers["X-Compatibility-Date"], "2026-02-02")
        self.assertIn("WizardLightYearsCalculator", headers["user-agent"])


if __name__ == "__main__":
    unittest.main()
