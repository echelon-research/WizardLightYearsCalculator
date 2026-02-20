# Testing Documentation

## Overview

This project includes comprehensive test coverage for Phase 4 of the project plan:
- Unit tests for calculator logic
- Integration tests for ESI client
- API endpoint tests
- Error handling tests

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── test_calculator.py       # Distance calculation unit tests
├── test_esi_client.py       # ESI API integration tests
├── test_api.py              # Flask API endpoint tests
└── test_error_handling.py   # Error handling and validation tests
```

## Running Tests

### Run All Tests

```bash
# Using the test runner script
python run_tests.py

# Or using unittest directly
python -m unittest discover tests

# Or run from tests directory
cd tests
python -m unittest discover
```

### Run Specific Test Module

```bash
# Using test runner
python run_tests.py test_calculator
python run_tests.py test_esi_client
python run_tests.py test_api
python run_tests.py test_error_handling

# Using unittest
python -m unittest tests.test_calculator
python -m unittest tests.test_esi_client
python -m unittest tests.test_api
python -m unittest tests.test_error_handling
```

### Run Specific Test Class or Method

```bash
# Run a specific test class
python -m unittest tests.test_calculator.TestCalculator

# Run a specific test method
python -m unittest tests.test_calculator.TestCalculator.test_calculate_distance_same_point
```

### Verbose Output

```bash
# Add -v flag for verbose output
python -m unittest discover tests -v
```

## Test Coverage

### test_calculator.py (8 tests)
- ✅ Distance calculation with same coordinates (zero distance)
- ✅ Calculation of exactly one lightyear
- ✅ 3D distance calculation (Pythagorean theorem)
- ✅ Distance with negative coordinates
- ✅ All three dimensions calculation
- ✅ Lightyear constant verification
- ✅ Distance conversion accuracy

### test_esi_client.py (10 tests)
- ✅ Client initialization with correct headers
- ✅ Successful system info retrieval
- ✅ 404 error handling (system not found)
- ✅ 500 error handling (server error)
- ✅ Request timeout handling
- ✅ Connection error handling
- ✅ Invalid JSON response handling
- ✅ Missing required fields handling
- ✅ Headers sent correctly verification

### test_api.py (15 tests)
- ✅ Index endpoint information
- ✅ POST request with JSON data
- ✅ GET request with query parameters
- ✅ Missing system_id_1 error
- ✅ Missing system_id_2 error
- ✅ Invalid system ID type error
- ✅ System ID below range error
- ✅ System ID above range error
- ✅ System not found in ESI error
- ✅ ESI API unavailable error
- ✅ 404 for non-existent endpoint
- ✅ Same system distance (zero)
- ✅ Response includes system names

### test_error_handling.py (20+ tests)
- ✅ Validation functions (min, max, type checking)
- ✅ Error response format consistency
- ✅ Error message sanitization (no stack traces)
- ✅ ESI details not exposed in errors
- ✅ Database details not exposed
- ✅ Correct HTTP status codes (400, 404, 429, 502, 500)
- ✅ Edge cases (zero, negative, float, null values)
- ✅ Malformed JSON handling
- ✅ Empty request body handling
- ✅ Extra fields ignored properly

## Test Dependencies

All tests use Python's built-in `unittest` framework:
- `unittest` - Test framework
- `unittest.mock` - Mocking for external dependencies

No additional test dependencies required!

## Writing New Tests

### Test Template

```python
import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from your_module import your_function


class TestYourFeature(unittest.TestCase):
    """Test cases for your feature."""
    
    def setUp(self):
        """Set up test fixtures."""
        pass
    
    def tearDown(self):
        """Clean up after tests."""
        pass
    
    def test_something(self):
        """Test description."""
        result = your_function()
        self.assertEqual(result, expected_value)


if __name__ == "__main__":
    unittest.main()
```

### Best Practices

1. **Use descriptive test names** - `test_calculate_distance_same_point` not `test_1`
2. **One assertion per test** - Focus on testing one thing
3. **Use setUp/tearDown** - For common test initialization
4. **Mock external dependencies** - Don't make real API calls in tests
5. **Test edge cases** - Zero, negative, null, empty values
6. **Test error conditions** - Ensure proper error handling
7. **Add docstrings** - Explain what each test does

## Mocking Examples

### Mock External API Call

```python
from unittest.mock import patch, Mock

@patch('esi_client.requests.get')
def test_api_call(self, mock_get):
    mock_response = Mock()
    mock_response.json.return_value = {"data": "value"}
    mock_get.return_value = mock_response
    
    # Your test code here
```

### Mock Database Call

```python
@patch('app.db.get_system')
def test_database(self, mock_get_system):
    mock_get_system.return_value = {"system_id": 30000142}
    
    # Your test code here
```

## Continuous Integration

To integrate with CI/CD pipelines:

```yaml
# Example .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: python run_tests.py
```

## Troubleshooting

### Import Errors

If you get import errors, ensure you're running tests from the project root:
```bash
cd /home/matt/dev/projects/WizardLightYearsCalculator
python run_tests.py
```

### Module Not Found

Make sure all test files have the path insertion:
```python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
```

### Rate Limiting in Tests

API tests disable rate limiting automatically:
```python
app.config['RATE_LIMIT_ENABLED'] = False
```

## Test Results Example

```
test_calculate_distance_3d (tests.test_calculator.TestCalculator) ... ok
test_calculate_distance_same_point (tests.test_calculator.TestCalculator) ... ok
test_client_initialization (tests.test_esi_client.TestESIClient) ... ok
test_get_system_info_success (tests.test_esi_client.TestESIClient) ... ok
test_index_endpoint (tests.test_api.TestAPIEndpoints) ... ok
test_missing_system_id_1 (tests.test_api.TestAPIEndpoints) ... ok
...

----------------------------------------------------------------------
Ran 53 tests in 0.345s

OK
```

## Code Coverage (Optional)

To measure code coverage, install coverage:

```bash
pip install coverage
```

Run tests with coverage:

```bash
coverage run -m unittest discover tests
coverage report
coverage html  # Generate HTML report
```

## Future Test Additions

Potential areas for additional testing:
- Performance/load testing
- Database concurrency tests
- Rate limiting behavior tests
- Security penetration tests
- Integration tests with real ESI API (in staging)
