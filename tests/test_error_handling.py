"""Error handling tests for the application."""

import unittest
import sys
import os
import json
from unittest.mock import patch, Mock
import sqlite3

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, validate_system_id, get_or_fetch_system
from database import Database
from config import MIN_SYSTEM_ID, MAX_SYSTEM_ID


class TestErrorHandling(unittest.TestCase):
    """Test cases for error handling throughout the application."""
    
    def setUp(self):
        """Set up test fixtures."""
        app.config['TESTING'] = True
        app.config['RATE_LIMIT_ENABLED'] = False
        self.client = app.test_client()
    
    # Validation Error Tests
    
    def test_validate_system_id_valid(self):
        """Test validation passes for valid system ID."""
        is_valid, error_msg = validate_system_id(30000142)
        self.assertTrue(is_valid)
        self.assertEqual(error_msg, "")
    
    def test_validate_system_id_minimum_valid(self):
        """Test validation at minimum valid value."""
        is_valid, error_msg = validate_system_id(MIN_SYSTEM_ID)
        self.assertTrue(is_valid)
    
    def test_validate_system_id_maximum_valid(self):
        """Test validation at maximum valid value."""
        is_valid, error_msg = validate_system_id(MAX_SYSTEM_ID)
        self.assertTrue(is_valid)
    
    def test_validate_system_id_below_minimum(self):
        """Test validation fails below minimum."""
        is_valid, error_msg = validate_system_id(MIN_SYSTEM_ID - 1)
        self.assertFalse(is_valid)
        self.assertIn("between", error_msg.lower())
    
    def test_validate_system_id_above_maximum(self):
        """Test validation fails above maximum."""
        is_valid, error_msg = validate_system_id(MAX_SYSTEM_ID + 1)
        self.assertFalse(is_valid)
        self.assertIn("between", error_msg.lower())
    
    def test_validate_system_id_not_integer(self):
        """Test validation fails for non-integer."""
        is_valid, error_msg = validate_system_id("not_a_number")
        self.assertFalse(is_valid)
        self.assertIn("integer", error_msg.lower())
    
    # API Error Response Tests
    
    def test_error_response_format(self):
        """Test that error responses have correct format."""
        response = self.client.post('/calculate-distance',
                                   data=json.dumps({}),
                                   content_type='application/json')
        
        data = json.loads(response.data)
        self.assertIn("error", data)
        self.assertIsInstance(data["error"], str)
    
    def test_error_message_sanitization_no_stack_trace(self):
        """Test that error messages don't expose stack traces."""
        with patch('app.get_or_fetch_system') as mock_fetch:
            mock_fetch.side_effect = Exception("Internal error with sensitive path /home/user/db")
            
            response = self.client.post('/calculate-distance',
                                       data=json.dumps({
                                           'system_id_1': 30000142,
                                           'system_id_2': 30000144
                                       }),
                                       content_type='application/json')
            
            data = json.loads(response.data)
            # Should get generic error, not the internal path
            self.assertNotIn("/home/user/db", data["error"])
            self.assertIn("unexpected", data["error"].lower())
    
    def test_error_message_sanitization_esi_details(self):
        """Test that ESI API details are not exposed."""
        with patch('app.get_or_fetch_system') as mock_fetch:
            mock_fetch.side_effect = RuntimeError("ESI API connection failed: timeout at 10.5s")
            
            response = self.client.post('/calculate-distance',
                                       data=json.dumps({
                                           'system_id_1': 30000142,
                                           'system_id_2': 30000144
                                       }),
                                       content_type='application/json')
            
            data = json.loads(response.data)
            # Should get generic message, not timeout details
            self.assertNotIn("10.5s", data["error"])
            self.assertIn("retrieve system information", data["error"].lower())
    
    def test_value_error_sanitization(self):
        """Test that ValueError messages are sanitized."""
        with patch('app.get_or_fetch_system') as mock_fetch:
            mock_fetch.side_effect = ValueError("System 30000142 not found in database table 'systems'")
            
            response = self.client.post('/calculate-distance',
                                       data=json.dumps({
                                           'system_id_1': 30000142,
                                           'system_id_2': 30000144
                                       }),
                                       content_type='application/json')
            
            data = json.loads(response.data)
            # Should not expose database table name
            self.assertNotIn("systems", data["error"])
    
    # HTTP Status Code Tests
    
    def test_400_for_invalid_input(self):
        """Test 400 status for invalid input."""
        response = self.client.post('/calculate-distance',
                                   data=json.dumps({
                                       'system_id_1': 'invalid',
                                       'system_id_2': 30000144
                                   }),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
    
    def test_404_for_not_found(self):
        """Test 404 status for system not found."""
        with patch('app.get_or_fetch_system') as mock_fetch:
            mock_fetch.side_effect = ValueError("System not found")
            
            response = self.client.post('/calculate-distance',
                                       data=json.dumps({
                                           'system_id_1': 30000142,
                                           'system_id_2': 30000144
                                       }),
                                       content_type='application/json')
            
            self.assertEqual(response.status_code, 404)
    
    def test_502_for_esi_failure(self):
        """Test 502 status for ESI API failure."""
        with patch('app.get_or_fetch_system') as mock_fetch:
            mock_fetch.side_effect = RuntimeError("Failed to fetch from ESI")
            
            response = self.client.post('/calculate-distance',
                                       data=json.dumps({
                                           'system_id_1': 30000142,
                                           'system_id_2': 30000144
                                       }),
                                       content_type='application/json')
            
            self.assertEqual(response.status_code, 502)
    
    def test_500_for_unexpected_error(self):
        """Test 500 status for unexpected errors."""
        with patch('app.get_or_fetch_system') as mock_fetch:
            mock_fetch.side_effect = Exception("Unexpected error")
            
            response = self.client.post('/calculate-distance',
                                       data=json.dumps({
                                           'system_id_1': 30000142,
                                           'system_id_2': 30000144
                                       }),
                                       content_type='application/json')
            
            self.assertEqual(response.status_code, 500)
    
    # Database Error Tests
    
    def test_database_connection_error_handling(self):
        """Test handling of database connection errors."""
        with patch('app.db.get_system') as mock_get:
            mock_get.side_effect = sqlite3.OperationalError("Database locked")
            
            with self.assertRaises(sqlite3.OperationalError):
                get_or_fetch_system(30000142)
    
    # Edge Case Tests
    
    def test_zero_system_id(self):
        """Test handling of zero as system ID."""
        response = self.client.post('/calculate-distance',
                                   data=json.dumps({
                                       'system_id_1': 0,
                                       'system_id_2': 30000144
                                   }),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
    
    def test_negative_system_id(self):
        """Test handling of negative system ID."""
        response = self.client.post('/calculate-distance',
                                   data=json.dumps({
                                       'system_id_1': -30000142,
                                       'system_id_2': 30000144
                                   }),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
    
    def test_float_system_id(self):
        """Test handling of float as system ID."""
        response = self.client.post('/calculate-distance',
                                   data=json.dumps({
                                       'system_id_1': 30000142.5,
                                       'system_id_2': 30000144
                                   }),
                                   content_type='application/json')
        
        # Should either accept (converting to int) or reject
        self.assertIn(response.status_code, [200, 400])
    
    def test_null_system_id(self):
        """Test handling of null system ID."""
        response = self.client.post('/calculate-distance',
                                   data=json.dumps({
                                       'system_id_1': None,
                                       'system_id_2': 30000144
                                   }),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
    
    def test_empty_json_body(self):
        """Test handling of empty JSON body."""
        response = self.client.post('/calculate-distance',
                                   data=json.dumps({}),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("required", data["error"].lower())
    
    def test_malformed_json(self):
        """Test handling of malformed JSON."""
        response = self.client.post('/calculate-distance',
                                   data='{"system_id_1": invalid json}',
                                   content_type='application/json')
        
        # Flask should return 400 for malformed JSON
        self.assertEqual(response.status_code, 400)
    
    def test_extra_fields_in_request(self):
        """Test that extra fields in request are ignored."""
        with patch('app.get_or_fetch_system') as mock_fetch:
            mock_fetch.side_effect = [
                {"system_id": 30000142, "name": "Jita", "x": 0, "y": 0, "z": 0, 
                 "added": "2026-02-20", "last_update": "2026-02-20"},
                {"system_id": 30000144, "name": "Perimeter", "x": 100, "y": 100, "z": 100,
                 "added": "2026-02-20", "last_update": "2026-02-20"}
            ]
            
            response = self.client.post('/calculate-distance',
                                       data=json.dumps({
                                           'system_id_1': 30000142,
                                           'system_id_2': 30000144,
                                           'extra_field': 'should_be_ignored'
                                       }),
                                       content_type='application/json')
            
            self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
