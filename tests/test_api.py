"""API endpoint tests for the Flask application."""

import unittest
import sys
import os
import json
from unittest.mock import patch, Mock
import tempfile

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from config import MIN_SYSTEM_ID, MAX_SYSTEM_ID


class TestAPIEndpoints(unittest.TestCase):
    """Test cases for API endpoints."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a test database in memory
        app.config['TESTING'] = True
        app.config['RATE_LIMIT_ENABLED'] = False  # Disable rate limiting for tests
        self.client = app.test_client()
        
        # Sample test data
        self.valid_system_1 = 30000142  # Jita
        self.valid_system_2 = 30000144  # Perimeter
        
        self.mock_system_data_1 = {
            "system_id": 30000142,
            "name": "Jita",
            "x": -129400292875304960.0,
            "y": 61596815791300400.0,
            "z": 1720986748719556600.0,
            "added": "2026-02-20T00:00:00",
            "last_update": "2026-02-20T00:00:00"
        }
        
        self.mock_system_data_2 = {
            "system_id": 30000144,
            "name": "Perimeter",
            "x": -129524275563970560.0,
            "y": 61576851935436800.0,
            "z": 1721076251935088640.0,
            "added": "2026-02-20T00:00:00",
            "last_update": "2026-02-20T00:00:00"
        }
    
    def test_index_endpoint(self):
        """Test the index endpoint returns API information."""
        response = self.client.get('/')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertIn("api", data)
        self.assertIn("version", data)
        self.assertIn("description", data)
        self.assertEqual(data["api"], "WizardLightYearsCalculator")
    
    def test_calculate_distance_post_json(self):
        """Test POST request with JSON data."""
        with patch('app.get_or_fetch_system') as mock_fetch:
            mock_fetch.side_effect = [self.mock_system_data_1, self.mock_system_data_2]
            
            response = self.client.post('/calculate-distance',
                                       data=json.dumps({
                                           'system_id_1': self.valid_system_1,
                                           'system_id_2': self.valid_system_2
                                       }),
                                       content_type='application/json')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            
            self.assertIn("system_1", data)
            self.assertIn("system_2", data)
            self.assertIn("distance_meters", data)
            self.assertIn("distance_lightyears", data)
            
            self.assertEqual(data["system_1"]["system_id"], self.valid_system_1)
            self.assertEqual(data["system_2"]["system_id"], self.valid_system_2)
            self.assertIsInstance(data["distance_meters"], (int, float))
            self.assertIsInstance(data["distance_lightyears"], (int, float))
    
    def test_calculate_distance_get_query_params(self):
        """Test GET request with query parameters."""
        with patch('app.get_or_fetch_system') as mock_fetch:
            mock_fetch.side_effect = [self.mock_system_data_1, self.mock_system_data_2]
            
            response = self.client.get(
                f'/calculate-distance?system_id_1={self.valid_system_1}&system_id_2={self.valid_system_2}'
            )
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            
            self.assertIn("distance_lightyears", data)
            self.assertEqual(data["system_1"]["name"], "Jita")
            self.assertEqual(data["system_2"]["name"], "Perimeter")
    
    def test_missing_system_id_1(self):
        """Test error when system_id_1 is missing."""
        response = self.client.post('/calculate-distance',
                                   data=json.dumps({'system_id_2': self.valid_system_2}),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)
        self.assertIn("required", data["error"].lower())
    
    def test_missing_system_id_2(self):
        """Test error when system_id_2 is missing."""
        response = self.client.post('/calculate-distance',
                                   data=json.dumps({'system_id_1': self.valid_system_1}),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)
    
    def test_invalid_system_id_type(self):
        """Test error when system ID is not an integer."""
        response = self.client.post('/calculate-distance',
                                   data=json.dumps({
                                       'system_id_1': "not_a_number",
                                       'system_id_2': self.valid_system_2
                                   }),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)
    
    def test_system_id_below_range(self):
        """Test error when system ID is below valid range."""
        response = self.client.post('/calculate-distance',
                                   data=json.dumps({
                                       'system_id_1': MIN_SYSTEM_ID - 1,
                                       'system_id_2': self.valid_system_2
                                   }),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)
        self.assertIn("between", data["error"].lower())
    
    def test_system_id_above_range(self):
        """Test error when system ID is above valid range."""
        response = self.client.post('/calculate-distance',
                                   data=json.dumps({
                                       'system_id_1': self.valid_system_1,
                                       'system_id_2': MAX_SYSTEM_ID + 1
                                   }),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)
    
    def test_system_not_found_in_esi(self):
        """Test handling when system is not found in ESI."""
        with patch('app.get_or_fetch_system') as mock_fetch:
            mock_fetch.side_effect = ValueError("System ID 30000142 not found")
            
            response = self.client.post('/calculate-distance',
                                       data=json.dumps({
                                           'system_id_1': self.valid_system_1,
                                           'system_id_2': self.valid_system_2
                                       }),
                                       content_type='application/json')
            
            self.assertEqual(response.status_code, 404)
            data = json.loads(response.data)
            self.assertIn("error", data)
    
    def test_esi_api_unavailable(self):
        """Test handling when ESI API is unavailable."""
        with patch('app.get_or_fetch_system') as mock_fetch:
            mock_fetch.side_effect = RuntimeError("Failed to fetch system data from ESI")
            
            response = self.client.post('/calculate-distance',
                                       data=json.dumps({
                                           'system_id_1': self.valid_system_1,
                                           'system_id_2': self.valid_system_2
                                       }),
                                       content_type='application/json')
            
            self.assertEqual(response.status_code, 502)
            data = json.loads(response.data)
            self.assertIn("error", data)
    
    def test_404_endpoint(self):
        """Test 404 error for non-existent endpoint."""
        response = self.client.get('/nonexistent-endpoint')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn("error", data)
    
    def test_both_systems_same(self):
        """Test calculating distance between the same system."""
        with patch('app.get_or_fetch_system') as mock_fetch:
            mock_fetch.return_value = self.mock_system_data_1
            
            response = self.client.post('/calculate-distance',
                                       data=json.dumps({
                                           'system_id_1': self.valid_system_1,
                                           'system_id_2': self.valid_system_1
                                       }),
                                       content_type='application/json')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            
            # Distance should be 0
            self.assertEqual(data["distance_meters"], 0.0)
            self.assertEqual(data["distance_lightyears"], 0.0)
    
    def test_response_includes_system_names(self):
        """Test that response includes system names."""
        with patch('app.get_or_fetch_system') as mock_fetch:
            mock_fetch.side_effect = [self.mock_system_data_1, self.mock_system_data_2]
            
            response = self.client.post('/calculate-distance',
                                       data=json.dumps({
                                           'system_id_1': self.valid_system_1,
                                           'system_id_2': self.valid_system_2
                                       }),
                                       content_type='application/json')
            
            data = json.loads(response.data)
            
            self.assertEqual(data["system_1"]["name"], "Jita")
            self.assertEqual(data["system_2"]["name"], "Perimeter")


if __name__ == "__main__":
    unittest.main()
