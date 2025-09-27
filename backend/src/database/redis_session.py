# requirements.txt additions
redis==5.0.1
hiredis==2.2.3

# paradox_loop_server.py
import redis
import pickle
import os

# Initialize Redis connection
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_conn = redis.from_url(REDIS_URL, decode_responses=False)

def store_session(token, session_data, expiry=SESSION_EXPIRY):
    """Securely store session in Redis"""
    serialized = pickle.dumps(session_data)
    redis_conn.setex(f"session:{token}", expiry, serialized)

def get_session(token):
    """Retrieve session from Redis"""
    serialized = redis_conn.get(f"session:{token}")
    return pickle.loads(serialized) if serialized else None

def delete_session(token):
    """Remove session from Redis"""
    redis_conn.delete(f"session:{token}")

# Replace all sessions references
# Example in api_new_session():
session = new_session()
store_session(session["token"], session)
