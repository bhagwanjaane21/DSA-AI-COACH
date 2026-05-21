"""
Configuration loader for the backend service.
Loads environment variables from .env and exposes them as module-level constants.
"""
import os
from dotenv import load_dotenv

load_dotenv(override=True)

SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
AI_SERVICE_URL: str = os.getenv("AI_SERVICE_URL", "http://localhost:8000")
BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8001"))
