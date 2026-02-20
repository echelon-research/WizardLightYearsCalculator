# WizardLightYearsCalculator

A Python REST API that calculates the distance in light-years between two EVE Online solar systems using data from the ESI API.

## Features

- ✅ Single endpoint to calculate distances between two EVE systems
- ✅ SQLite database caching to minimize ESI API calls
- ✅ Input validation for system IDs (30,000,000 - 31,000,000 range)
- ✅ Accurate distance calculation using EVE Online's lightyear definition
- ✅ Automatic data caching with timestamps
- ✅ **Security Features:**
  - Rate limiting (60 req/min, 1000 req/hour by default)
  - SQL injection prevention (parameterized queries)
  - Sanitized error messages (no internal details exposed)
  - Request logging and monitoring

## Installation

1. **Clone the repository:**
```bash
cd /home/matt/dev/projects/WizardLightYearsCalculator
```

2. **Create a virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate  # On Windows
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment (optional):**
```bash
cp .env.example .env
# Edit .env if you need to change default settings
```

## Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Build and start the container
docker compose up -d

# View logs
docker compose logs -f

# Stop the container
docker compose down
```

The API will be available at `http://localhost:5000`.

### Using Docker CLI

```bash
# Build the image
docker build -t wizard-lightyears-calculator .

# Run the container
docker run -d \
  --name wizard-calculator \
  -p 5000:5000 \
  -v wizard-data:/app/data \
  wizard-lightyears-calculator

# View logs
docker logs -f wizard-calculator

# Stop the container
docker stop wizard-calculator
docker rm wizard-calculator
```

### Using Pre-built Image from GitHub

```bash
# Pull image from GitHub Container Registry
docker pull ghcr.io/dusty-meg/wizardlightyearscalculator:latest

# Run the container
docker run -d \
  --name wizard-calculator \
  -p 5000:5000 \
  -v wizard-data:/app/data \
  ghcr.io/dusty-meg/wizardlightyearscalculator:latest
```

## Usage

### Start the API Server

**Local Development:**
```bash
python app.py
```

The API will start on `http://0.0.0.0:5000` by default.

### API Endpoints

#### GET `/`
Returns API information and available endpoints.

#### POST `/calculate-distance`
Calculate the distance between two EVE Online systems.

**Request Body (JSON):**
```json
{
    "system_id_1": 30000142,
    "system_id_2": 30000144
}
```

**Or use GET with query parameters:**
```
GET /calculate-distance?system_id_1=30000142&system_id_2=30000144
```

**Success Response (200 OK):**
```json
{
    "system_1": {
        "system_id": 30000142,
        "name": "Jita"
    },
    "system_2": {
        "system_id": 30000144,
        "name": "Perimeter"
    },
    "distance_meters": 9460000000000000.0,
    "distance_lightyears": 1.0
}
```

**Error Response (400 Bad Request):**
```json
{
    "error": "System ID must be between 30,000,000 and 31,000,000"
}
```

### Example Usage with curl

```bash
# Using POST
curl -X POST http://localhost:5000/calculate-distance \
  -H "Content-Type: application/json" \
  -d '{"system_id_1": 30000142, "system_id_2": 30000144}'

# Using GET
curl "http://localhost:5000/calculate-distance?system_id_1=30000142&system_id_2=30000144"
```

### Example Usage with Python

```python
import requests

response = requests.post(
    "http://localhost:5000/calculate-distance",
    json={
        "system_id_1": 30000142,
        "system_id_2": 30000144
    }
)

data = response.json()
print(f"Distance: {data['distance_lightyears']:.2f} light-years")
```

## Technical Details

### Distance Calculation

The API uses EVE Online's specific lightyear definition for jump drive calculations:
- **1 light-year = 9,460,000,000,000,000.0 meters** (9.46 × 10^15)

This is slightly less than the real-world scientific definition.

**Formula:**
```
distance_meters = √[(x₂-x₁)² + (y₂-y₁)² + (z₂-z₁)²]
distance_lightyears = distance_meters / 9,460,000,000,000,000.0
```

### Database Schema

SQLite table `systems`:
```sql
CREATE TABLE systems (
    system_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    x REAL NOT NULL,
    y REAL NOT NULL,
    z REAL NOT NULL,
    added TIMESTAMP NOT NULL,
    last_update TIMESTAMP NOT NULL
);
```

### ESI API Integration

- **Base URL:** `https://esi.evetech.net/latest`
- **Headers:**
  - `X-Compatibility-Date: 2026-02-02`
  - `user-agent: WizardLightYearsCalculator, Username=Dusty Meg`

## Project Structure

```
WizardLightYearsCalculator/
├── app.py                  # Main Flask application
├── database.py             # Database operations
├── esi_client.py           # ESI API client
├── calculator.py           # Distance calculation logic
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── run_tests.py            # Test runner script
├── Dockerfile              # Docker image configuration
├── docker-compose.yml      # Docker Compose setup
├── .dockerignore          # Docker build exclusions
├── LICENSE                # MIT License
├── PROJECT_PLAN.md        # Detailed project plan
├── SECURITY.md            # Security documentation
├── README.md              # This file
├── .env.example           # Environment variables template
├── .github/
│   ├── dependabot.yml     # Dependabot configuration
│   └── workflows/
│       ├── test.yml       # CI testing workflow
│       └── docker-build.yml  # Docker build workflow
└── tests/                 # Test suite
    ├── test_calculator.py      # Calculator unit tests
    ├── test_esi_client.py      # ESI client integration tests
    ├── test_api.py             # API endpoint tests
    ├── test_error_handling.py  # Error handling tests
    └── README.md              # Testing documentation
```

## Configuration

Edit `.env` file to customize:
- `DATABASE_PATH`: SQLite database file path (default: `wizard_calculator.db`)
- `API_HOST`: API host address (default: `0.0.0.0`)
- `API_PORT`: API port (default: `5000`)
- `DEBUG`: Debug mode (default: `False`)
- `RATE_LIMIT_ENABLED`: Enable rate limiting (default: `True`)
- `RATE_LIMIT_PER_MINUTE`: Requests per minute per IP (default: `60`)
- `RATE_LIMIT_PER_HOUR`: Requests per hour per IP (default: `1000`)

## Security

This API implements several security measures:
- **Rate Limiting:** Prevents abuse and DoS attacks
- **SQL Injection Prevention:** All queries use parameterized statements
- **Error Sanitization:** Internal details not exposed in error messages
- **Input Validation:** Strict validation of all user inputs

For detailed security documentation, see [SECURITY.md](SECURITY.md).

## Testing

The project includes comprehensive test coverage (51 tests):
- **Unit tests** for distance calculations
- **Integration tests** for ESI API client
- **API endpoint tests** for Flask routes
- **Error handling tests** for validation and edge cases

### Run All Tests

```bash
# Activate virtual environment first
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run all tests
python3 run_tests.py

# Or use unittest directly
python3 -m unittest discover tests
```

### Run Specific Tests

```bash
# Run specific test module
python3 -m unittest tests.test_calculator
python3 -m unittest tests.test_esi_client
python3 -m unittest tests.test_api
python3 -m unittest tests.test_error_handling

# Run with verbose output
python3 -m unittest discover tests -v
```

### Test Results

```
Ran 51 tests in 0.079s
OK
```

For detailed testing documentation, see [tests/README.md](tests/README.md).

## Error Handling

The API handles various error scenarios:
- **400:** Invalid input (wrong range, missing parameters)
- **404:** System not found in ESI
- **429:** Rate limit exceeded
- **502:** ESI API unavailable or error
- **500:** Unexpected server error

## Credits

Based on EVE Online by CCP Games.
- [ESI Documentation](https://esi.evetech.net/)
- [Jump Drive Calculations](https://developers.eveonline.com/docs/guides/map-data/#jump-drives)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

You are free to use, modify, and distribute this software for any purpose, including commercial applications.
