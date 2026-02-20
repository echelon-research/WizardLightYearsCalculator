#!/usr/bin/env python3
"""Test runner script for WizardLightYearsCalculator."""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


def run_all_tests():
    """Discover and run all tests."""
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


def run_specific_test(test_module):
    """Run a specific test module."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(f'tests.{test_module}')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Run specific test module
        test_module = sys.argv[1]
        print(f"Running tests from: {test_module}")
        sys.exit(run_specific_test(test_module))
    else:
        # Run all tests
        print("Running all tests...")
        sys.exit(run_all_tests())
