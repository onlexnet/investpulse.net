"""
Global pytest configuration and fixtures.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from secrets/.env at the start of test session
secrets_env = Path(__file__).parent.parent.parent / "secrets" / ".env"
if secrets_env.exists():
    load_dotenv(secrets_env)
    print(f"✅ Loaded environment variables from {secrets_env}")
else:
    print(f"⚠️  Secrets file not found: {secrets_env}")
