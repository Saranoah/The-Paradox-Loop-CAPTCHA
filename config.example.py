"""
config.example.py
-----------------
Template configuration file for The-Paradox-Loop-CAPTCHA.

Copy this file to `config.py` and fill in the real values.
DO NOT commit `config.py` to version control.
"""

# ==============================
# SECRET KEYS & TOKENS
# ==============================
# Used for signing CAPTCHA tokens or session cookies.
SECRET_KEY = "your-secret-key-here"

# OpenAI API key or other model service keys
OPENAI_API_KEY = "your-openai-api-key-here"

# ==============================
# DATABASE CONFIGURATION
# ==============================
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "paradox_captcha"
DB_USER = "your-db-username"
DB_PASSWORD = "your-db-password"

# ==============================
# CAPTCHA SETTINGS
# ==============================
# Maximum number of retries before a user is locked out.
MAX_RETRIES = 5

# Timeout for challenge response (in seconds).
CHALLENGE_TIMEOUT = 120

# ==============================
# MONITORING
# ==============================
PROMETHEUS_ENABLED = True
PROMETHEUS_PORT = 9090

# ==============================
# DEBUG / DEVELOPMENT
# ==============================
DEBUG = True
