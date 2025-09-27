import os
from dotenv import load_dotenv

load_dotenv()

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-change-in-production")
HMAC_SECRET = os.getenv("HMAC_SECRET", "fallback-dev-key-change-in-production")

# Redis Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Session Settings
SESSION_EXPIRY = int(os.getenv("SESSION_EXPIRY", "600"))

# CAPTCHA Settings
MAX_ROUNDS = int(os.getenv("MAX_ROUNDS", "20"))
REQUIRED_HUMAN_SCORE = int(os.getenv("REQUIRED_HUMAN_SCORE", "5"))
REQUIRED_CONSECUTIVE_PASSES = int(os.getenv("REQUIRED_CONSECUTIVE_PASSES", "3"))
TRAP_MODE_THRESHOLD = float(os.getenv("TRAP_MODE_THRESHOLD", "0.55"))

# Rate Limiting
RATE_LIMIT_STORAGE_URL = REDIS_URL
