"""Unit tests for the calculator module."""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from calculator import calculate_distance
from config import LIGHTYEAR_IN_METERS


class TestCalculator(unittest.TestCase):
    """Test cases for distance calculations."""
    
    def test_calculate_distance_same_point(self):
        """Test that distance between same coordinates is zero."""
        system1 = {"x": 1000.0, "y": 2000.0, "z": 3000.0}
        system2 = {"x": 1000.0, "y": 2000.0, "z": 3000.0}
        
        result = calculate_distance(system1, system2)
        
        self.assertEqual(result["distance_meters"], 0.0)
        self.assertEqual(result["distance_lightyears"], 0.0)
    
    def test_calculate_distance_one_lightyear(self):
        """Test calculation of exactly one lightyear."""
        system1 = {"x": 0.0, "y": 0.0, "z": 0.0}
        system2 = {"x": LIGHTYEAR_IN_METERS, "y": 0.0, "z": 0.0}
        
        result = calculate_distance(system1, system2)
        
        self.assertEqual(result["distance_meters"], LIGHTYEAR_IN_METERS)
        self.assertEqual(result["distance_lightyears"], 1.0)
    
    def test_calculate_distance_3d(self):
        """Test 3D distance calculation."""
        # Using a 3-4-5 right triangle
        system1 = {"x": 0.0, "y": 0.0, "z": 0.0}
        system2 = {"x": 3.0, "y": 4.0, "z": 0.0}
        
        result = calculate_distance(system1, system2)
        
        # 3-4-5 triangle, hypotenuse should be 5
        self.assertEqual(result["distance_meters"], 5.0)
    
    def test_calculate_distance_negative_coords(self):
        """Test calculation with negative coordinates."""
        system1 = {"x": -1000.0, "y": -2000.0, "z": -3000.0}
        system2 = {"x": 1000.0, "y": 2000.0, "z": 3000.0}
        
        result = calculate_distance(system1, system2)
        
        # Distance should be positive
        self.assertGreater(result["distance_meters"], 0)
        self.assertGreater(result["distance_lightyears"], 0)
    
    def test_calculate_distance_all_dimensions(self):
        """Test 3D calculation with all dimensions."""
        # 3D Pythagorean: sqrt(3^2 + 4^2 + 12^2) = sqrt(9 + 16 + 144) = sqrt(169) = 13
        system1 = {"x": 0.0, "y": 0.0, "z": 0.0}
        system2 = {"x": 3.0, "y": 4.0, "z": 12.0}
        
        result = calculate_distance(system1, system2)
        
        self.assertAlmostEqual(result["distance_meters"], 13.0, places=10)
    
    def test_lightyear_constant(self):
        """Verify the EVE Online lightyear constant is correct."""
        # Should be 9.46 × 10^15 as per EVE documentation
        self.assertEqual(LIGHTYEAR_IN_METERS, 9460000000000000.0)
    
    def test_distance_conversion_accuracy(self):
        """Test that lightyear conversion is accurate."""
        system1 = {"x": 0.0, "y": 0.0, "z": 0.0}
        system2 = {"x": LIGHTYEAR_IN_METERS * 5, "y": 0.0, "z": 0.0}
        
        result = calculate_distance(system1, system2)
        
        self.assertEqual(result["distance_lightyears"], 5.0)


if __name__ == "__main__":
    unittest.main()
