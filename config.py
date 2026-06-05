"""
Configuration module for Biologics Discovery Platform Dashboard
Loads settings from environment variables with sensible defaults
"""

import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB Configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "biologics_platform")

if MONGODB_URL.strip() == "":
    raise ValueError(
        "MONGODB_URL environment variable not set. "
        "Copy .env.example to .env and set MONGODB_URL to your MongoDB connection string."
    )

# API Keys
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")

# Dashboard Configuration
DASHBOARD_TITLE = os.getenv("DASHBOARD_TITLE", "Biologics Discovery Platform Analytics")
DEFAULT_THEME = os.getenv("DEFAULT_THEME", "dark")
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
MONGODB_DNS_SERVERS = [s.strip() for s in os.getenv("MONGODB_DNS_SERVERS", "").split(",") if s.strip()]

# Expected Collections
EXPECTED_COLLECTIONS = [
    "users",
    "user_activities",
    "access_logs",
    "targets",
    "screenings",
    "docking_jobs",
    "optimizations",
    "admet_jobs",
    "preformulation_reports",
    "formulation_designs",
    "experiments",
    "report_registry"
]

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Validation
if not MONGODB_URL:
    raise ValueError(
        "MONGODB_URL environment variable not set. "
        "Copy .env.example to .env and set MONGODB_URL to your MongoDB connection string."
    )

logger.info(
    f"Dashboard initialized with database: {DATABASE_NAME} and MongoDB URL: {MONGODB_URL}"
)
