# requirements.txt addition
flask-limiter==3.3.0

# paradox_loop_server.py
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379",
    strategy="fixed-window"
)

# Apply rate limits
@app.route("/session", methods=["POST"])
@limiter.limit("5 per minute")
def api_new_session():
    ...

@app.route("/respond", methods=["POST"])
@limiter.limit("10 per minute")
def api_respond():
    ...

# Custom exception handler
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        "error": "rate_limit_exceeded",
        "message": "Too many requests. Please slow down."
    }), 429
