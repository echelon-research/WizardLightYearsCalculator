"""Configuration settings for WizardLightYearsCalculator API."""

import os

# Database
DATABASE_PATH = os.getenv("DATABASE_PATH", "wizard_calculator.db")

# ESI API Configuration
ESI_BASE_URL = "https://esi.evetech.net/latest"
ESI_COMPATIBILITY_DATE = "2026-02-02"
ESI_USER_AGENT = "WizardLightYearsCalculator, Username=Dusty Meg"

# System ID Validation
MIN_SYSTEM_ID = 30000000
MAX_SYSTEM_ID = 31000000

# Distance Calculation
# EVE Online specific lightyear value (9.46 × 10^15 meters)
LIGHTYEAR_IN_METERS = 9460000000000000.0

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "5000"))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Rate Limiting
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "True").lower() == "true"
RATE_LIMIT_PER_MINUTE = os.getenv("RATE_LIMIT_PER_MINUTE", "60")
RATE_LIMIT_PER_HOUR = os.getenv("RATE_LIMIT_PER_HOUR", "1000")
