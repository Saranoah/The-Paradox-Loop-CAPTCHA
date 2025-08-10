
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
✨ Enhanced Paradox Loop CAPTHA - Production Ready
With Prometheus metrics, Redis resilience, and container support
"""

import hmac
from flask import Flask, jsonify, request, abort, has_request_context
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import secrets
import time
import hashlib
import random
import threading
import math
import json
import os
from collections import deque
import redis
import pickle
import logging
import base64
from prometheus_client import generate_latest, REGISTRY, Counter, Gauge, Histogram  # Prometheus metrics

# -----------------------
# Configure Logging
# -----------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------
# Initialize Flask App
# -----------------------
app = Flask(__name__)

# -----------------------
# Prometheus Metrics
# -----------------------
METRICS_PREFIX = "paradox_"
sessions_total = Counter(f'{METRICS_PREFIX}sessions_total', 'Total sessions created')
rounds_total = Counter(f'{METRICS_PREFIX}rounds_total', 'Total rounds processed', ['type', 'trap_mode'])
session_trap_depth = Gauge(f'{METRICS_PREFIX}session_trap_depth', 'Current trap depth of sessions', ['token'])
bot_likelihood_score = Histogram(f'{METRICS_PREFIX}bot_likelihood_score', 'Bot likelihood scores', buckets=[0.1, 0.3, 0.5, 0.7, 0.9, 1.0])
challenge_success = Counter(f'{METRICS_PREFIX}challenge_success', 'Challenge success rate', ['type', 'success'])

# -----------------------
# Security Enhancements
# -----------------------
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
try:
    redis_conn = redis.from_url(REDIS_URL, decode_responses=True)
    redis_conn.ping()
    logger.info("Redis connection established")
except redis.exceptions.RedisError as e:
    logger.error(f"Redis connection failed: {e} - falling back to in-memory storage")
    redis_conn = None

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri=REDIS_URL if redis_conn else "memory://",
    default_limits=["500 per hour", "100 per minute"],
    headers_enabled=True
)

@app.after_request
def add_security_headers(response):
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

HMAC_SECRET = os.environ.get("HMAC_SECRET", "fallback-dev-key-change-in-production").encode()
if len(HMAC_SECRET) < 32:
    HMAC_SECRET = hashlib.sha256(HMAC_SECRET).digest()

# -----------------------
# Enhanced Configuration
# -----------------------
SESSION_EXPIRY = 600
MAX_ROUNDS = 20
REQUIRED_HUMAN_SCORE = 5
REQUIRED_CONSECUTIVE_PASSES = 3
TRAP_MODE_THRESHOLD = 0.55
RNG = random.SystemRandom()
QUANTUM_ENTANGLEMENT_DEPTH = 3
TIME_DILATION_FACTOR = 1.5

memory_sessions = {}
session_cleanup_lock = threading.Lock()

# -----------------------
# Error Handlers
# -----------------------
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        "error": "rate_limit_exceeded",
        "kintsugi_wisdom": "Even golden repair takes time",
        "retry_after": getattr(e, 'retry_after', 60)
    }), 429

@app.errorhandler(400)
def bad_request_handler(e):
    return jsonify({
        "error": "bad_request",
        "kintsugi_wisdom": "Perfect cracks reveal hidden beauty"
    }), 400

@app.errorhandler(403)
def forbidden_handler(e):
    return jsonify({
        "error": "forbidden",
        "kintsugi_wisdom": "Some paths are meant to be walked differently"
    }), 403

@app.errorhandler(404)
def not_found_handler(e):
    return jsonify({
        "error": "not_found",
        "kintsugi_wisdom": "What is lost can be rebuilt with gold"
    }), 404

@app.errorhandler(500)
def internal_error_handler(e):
    logger.error(f"Internal server error: {e}")
    return jsonify({
        "error": "internal_server_error",
        "kintsugi_wisdom": "From the deepest breaks comes the strongest repair"
    }), 500

# -----------------------
# Session Management
# -----------------------
def store_session(session):
    """Store session with metrics integration"""
    try:
        # Update trap depth metric
        session_trap_depth.labels(token=session['token']).set(session.get('trap_depth', 0))
        
        if redis_conn:
            serialized = base64.b64encode(pickle.dumps(session)).decode('utf-8')
            redis_conn.setex(f"session:{session['token']}", SESSION_EXPIRY, serialized)
        else:
            with session_cleanup_lock:
                memory_sessions[session['token']] = {
                    'data': session,
                    'expires': time.time() + SESSION_EXPIRY
                }
            cleanup_memory_sessions()
    except Exception as e:
        logger.error(f"Failed to store session: {e}")
        with session_cleanup_lock:
            memory_sessions[session['token']] = {
                'data': session,
                'expires': time.time() + SESSION_EXPIRY
            }

def get_session(token):
    try:
        if redis_conn:
            encoded_data = redis_conn.get(f"session:{token}")
            if encoded_data:
                serialized = base64.b64decode(encoded_data.encode('utf-8'))
                return pickle.loads(serialized)
            return None
        else:
            with session_cleanup_lock:
                session_data = memory_sessions.get(token)
                if session_data and session_data['expires'] > time.time():
                    return session_data['data']
                elif session_data:
                    del memory_sessions[token]
            return None
    except Exception as e:
        logger.error(f"Failed to get session: {e}")
        return None

def delete_session(token):
    try:
        if redis_conn:
            redis_conn.delete(f"session:{token}")
        else:
            with session_cleanup_lock:
                memory_sessions.pop(token, None)
    except Exception as e:
        logger.error(f"Failed to delete session: {e}")

def cleanup_memory_sessions():
    with session_cleanup_lock:
        current_time = time.time()
        expired_tokens = [
            token for token, data in memory_sessions.items()
            if data['expires'] <= current_time
        ]
        for token in expired_tokens:
            del memory_sessions[token]
        
        if len(memory_sessions) > 10000:
            sorted_sessions = sorted(
                memory_sessions.items(), 
                key=lambda x: x[1]['expires']
            )
            to_remove = len(sorted_sessions) // 5
            for token, _ in sorted_sessions[:to_remove]:
                del memory_sessions[token]

# -----------------------
# Enhanced Utilities
# -----------------------
def now_ts():
    return time.time()

def mk_token():
    base_token = secrets.token_urlsafe(32)
    if has_request_context() and request.remote_addr:
        try:
            ip_hash = hashlib.sha256(request.remote_addr.encode()).hexdigest()[:8]
            return f"{base_token}_{ip_hash}"
        except Exception as e:
            logger.warning(f"Failed to add IP hash to token: {e}")
    return base_token

def quantum_hash(s):
    h = hashlib.sha256(s.encode()).digest()
    return ''.join(f"{b:02x}" for b in h[:8])

def recursive_hash(seed, depth=3):
    for _ in range(depth):
        seed = hashlib.sha256(seed.encode()).hexdigest()[:16]
    return seed

def canonical_json_obj(obj):
    return json.dumps(obj, separators=(',', ':'), sort_keys=True)

def generate_hmac_signature(payload_obj):
    payload = canonical_json_obj(payload_obj).encode()
    return hmac.new(HMAC_SECRET, payload, hashlib.sha256).hexdigest()

def verify_hmac_signature(payload_obj, signature):
    try:
        expected = generate_hmac_signature(payload_obj)
        return hmac.compare_digest(expected, signature)
    except Exception as e:
        logger.error(f"HMAC verification failed: {e}")
        return False

# -----------------------
# Challenge Templates
# -----------------------
def challenge_creative_input():
    return {
        "type": "creative_input",
        "text": "Name something that doesn't exist but should",
        "input": True,
        "validator_key": "creative_input",
        "context": {}
    }

def challenge_meta_loop(session):
    prev_answers = [r["result"]["answer"] for r in session["rounds"] if r.get("result")]
    
    if prev_answers:
        ref_answer = RNG.choice(prev_answers[-QUANTUM_ENTANGLEMENT_DEPTH:])
        ref_hash = quantum_hash(ref_answer)
        return {
            "type": "meta_loop",
            "text": f"The answer to this is related to your previous answer '{ref_hash[:4]}...'. What did you enter 3 steps ago?",
            "input": True,
            "validator_key": "meta_loop",
            "context": {"ref_hash": ref_hash, "prev_answers": prev_answers}
        }
    return challenge_creative_input()

def challenge_recursive_paradox(session):
    round_num = len(session["rounds"])
    return {
        "type": "recursive_paradox",
        "text": f"This statement has exactly {round_num} correct answers in this session.",
        "options": ["True", "False", f"{round_num}", "It's impossible"],
        "input": False,
        "validator_key": "recursive_paradox",
        "context": {"round_num": round_num}
    }

def challenge_quantum_state(session):
    session["quantum_state"] = RNG.choice(["superposition", "collapsed", "entangled"])
    return {
        "type": "quantum_state",
        "text": "If you choose YES, you'll get an easier challenge next. What do you choose?",
        "options": ["YES", "NO", "MAYBE", "SCHRÖDINGER"],
        "input": False,
        "validator_key": "quantum_state",
        "context": {"state": session["quantum_state"]}
    }

def challenge_temporal_paradox():
    return {
        "type": "temporal_paradox",
        "text": "You solved this 5 seconds ago. What was your answer?",
        "input": True,
        "validator_key": "temporal_paradox",
        "context": {}
    }

def challenge_infinite_regress():
    return {
        "type": "infinite_regress",
        "text": "The correct answer is the first option of the next challenge",
        "options": ["Continue"],
        "input": False,
        "validator_key": "infinite_regress",
        "context": {}
    }

ALL_CHALLENGE_FACTORIES = [
    challenge_meta_loop,
    challenge_recursive_paradox,
    challenge_quantum_state,
    challenge_temporal_paradox,
    challenge_infinite_regress,
    challenge_creative_input
]

# -----------------------
# Validators
# -----------------------
def validate_creative_input(answer, meta, session, context):
    return 4, "creative response", 0.2

def validate_meta_loop(answer, meta, session, context):
    if not isinstance(answer, str) or len(answer) == 0:
        return 1, "invalid answer type", 0.8
    
    prev_answers = context.get("prev_answers", [])
    similarity = 0
    if prev_answers:
        target = prev_answers[-min(QUANTUM_ENTANGLEMENT_DEPTH, len(prev_answers))]
        if isinstance(target, str) and len(target) > 0:
            for i in range(min(len(answer), len(target))):
                if answer[i] == target[i]:
                    similarity += 1
            similarity_score = similarity / max(len(target), 1)
        else:
            similarity_score = 0
    else:
        similarity_score = 0
    
    if 0.2 < similarity_score < 0.8:
        return 4, "human-like recall", 0.2
    return 1, "exact or no match", 0.8

def validate_recursive_paradox(answer, meta, session, context):
    round_num = context["round_num"]
    correct_count = sum(1 for r in session["rounds"] if r.get("result", {}).get("human_score", 0) >= 3)
    
    if answer == f"{round_num}":
        valid = correct_count == round_num
    elif answer == "True":
        valid = correct_count > round_num/2
    elif answer == "False":
        valid = correct_count <= round_num/2
    else:
        valid = True
        
    return 4 if valid else 1, "recursive validation", 0.3 if valid else 0.7

def validate_quantum_state(answer, meta, session, context):
    state = session.get("quantum_state", "superposition")
    
    if answer == "YES":
        session["quantum_future"] = "easier"
    elif answer == "NO":
        session["quantum_future"] = "harder"
    elif answer == "MAYBE":
        session["quantum_future"] = "paradox"
    else:
        session["quantum_future"] = "both"
    
    return 3, f"quantum {state}", 0.4

def validate_temporal_paradox(answer, meta, session, context):
    time_elapsed = now_ts() - session["created_at"]
    imagined_past = time_elapsed - 5
    
    closest = None
    for r in session["rounds"]:
        if not r.get("result"):
            continue
        time_diff = abs(r["result"]["answered_at"] - imagined_past)
        if closest is None or time_diff < closest[0]:
            closest = (time_diff, r["result"]["answer"])
    
    if closest and answer == closest[1]:
        return 2, "time match", 0.5
    return 3, "human time variance", 0.3

def validate_infinite_regress(answer, meta, session, context):
    return 2, "infinite regress", 0.6

VALIDATORS = {
    "creative_input": validate_creative_input,
    "meta_loop": validate_meta_loop,
    "recursive_paradox": validate_recursive_paradox,
    "quantum_state": validate_quantum_state,
    "temporal_paradox": validate_temporal_paradox,
    "infinite_regress": validate_infinite_regress
}

# -----------------------
# Core Logic
# -----------------------
def pick_challenge(session, trap=False):
    future = session.get("quantum_future", "random")
    
    try:
        if trap:
            available_factories = ALL_CHALLENGE_FACTORIES
            weights = [1, 1, 3, 3, 2, 3][:len(available_factories)]
            factories = random.choices(available_factories, weights, k=min(5, len(available_factories))
        else:
            factories = ALL_CHALLENGE_FACTORIES
        
        challenge_factory = RNG.choice(factories)
        
        if challenge_factory.__name__ in [
            "challenge_meta_loop", "challenge_recursive_paradox", "challenge_quantum_state"
        ]:
            challenge = challenge_factory(session)
        else:
            challenge = challenge_factory()
            
    except Exception as e:
        logger.error(f"Error creating challenge: {e}")
        challenge = challenge_creative_input()
    
    if trap:
        challenge["time_dilation"] = TIME_DILATION_FACTOR
    
    return challenge

def score_round(session, challenge, answer, meta):
    validator = VALIDATORS.get(challenge["validator_key"])
    if not validator:
        logger.warning(f"No validator found for {challenge['validator_key']}")
        return 0, "no validator", 0.5

    context = challenge.get("context", {})
    
    try:
        human_score, explanation, bot_likelihood = validator(
            answer, meta, session, context
        )
    except Exception as e:
        logger.error(f"Validator error: {e}")
        return 2, f"validator error: {str(e)}", 0.5

    # Record metrics
    challenge_type = challenge["type"]
    trap_mode = "trap" if challenge.get("time_dilation") else "normal"
    rounds_total.labels(type=challenge_type, trap_mode=trap_mode).inc()
    bot_likelihood_score.observe(bot_likelihood)
    challenge_success.labels(type=challenge_type, success="pass" if human_score >= 3 else "fail").inc()

    # Apply time dilation analysis
    if challenge.get("time_dilation"):
        time_ms = meta.get("time_ms", 0)
        expected_time = time_ms / challenge["time_dilation"]
        if abs(time_ms - expected_time) > 1000:
            bot_likelihood = min(1.0, bot_likelihood + 0.3)

    # Recursion depth penalty
    recursion_depth = len(session["rounds"])
    if recursion_depth > 5:
        if human_score > 3 and meta.get("time_ms", 0) < 1500:
            bot_likelihood = min(1.0, bot_likelihood + 0.2 * (recursion_depth / 10))

    return human_score, explanation, bot_likelihood

def create_round(session, challenge):
    round_id = recursive_hash(session["token"] + str(len(session["rounds"]))
    round_obj = {
        "round_id": round_id,
        "issued_at": now_ts(),
        "challenge": challenge,
        "result": None
    }
    session["rounds"].append(round_obj)
    session["last_seen"] = now_ts()
    return round_obj

def paradox_decide_next(session, latest_round):
    res = latest_round["result"]
    round_num = len(session["rounds"])

    passed = res["human_score"] >= REQUIRED_HUMAN_SCORE and res["bot_likelihood"] < TRAP_MODE_THRESHOLD
    if passed:
        session["consecutive_passes"] += 1
    else:
        session["consecutive_passes"] = 0

    if res["bot_likelihood"] >= TRAP_MODE_THRESHOLD:
        session["trap_mode"] = True
        session["trap_depth"] = session.get("trap_depth", 0) + 1

    if session.get("trap_depth", 0) > 2:
        next_ch = challenge_infinite_regress()
        next_round = create_round(session, next_ch)
        return False, "deep_trap", sanitize_challenge(next_ch), next_round["round_id"]

    if session["consecutive_passes"] >= REQUIRED_CONSECUTIVE_PASSES:
        session["accepted"] = True
        return True, "accepted", None, None

    if round_num >= MAX_ROUNDS:
        if session["trap_mode"]:
            return False, "fallback_traditional", None, None
        session["accepted"] = True
        return True, "accepted_after_limit", None, None

    next_ch = pick_challenge(session, trap=session["trap_mode"])
    next_round = create_round(session, next_ch)
    return False, "continue", sanitize_challenge(next_ch), next_round["round_id"]

def sanitize_challenge(challenge):
    sanitized = challenge.copy()
    sanitized.pop("context", None)
    sanitized.pop("validator_key", None)
    return sanitized

def monitor_recursion_loops():
    """Fixed Redis SCAN implementation"""
    while True:
        try:
            time.sleep(30)
            
            if redis_conn:
                cursor = 0
                while True:
                    cursor, keys = redis_conn.scan(cursor=cursor, match="session:*", count=100)
                    for key in keys:
                        try:
                            encoded_data = redis_conn.get(key)
                            if not encoded_data:
                                continue
                                
                            serialized = base64.b64decode(encoded_data.encode('utf-8'))
                            session = pickle.loads(serialized)
                            
                            if (len(session["rounds"]) > 15 and 
                                session.get("trap_depth", 0) > 3 and
                                not session.get("accepted")):
                                session["rounds"] = session["rounds"][-5:]
                                session["trap_depth"] = max(0, session["trap_depth"] - 1)
                                store_session(session)
                        except Exception as e:
                            logger.error(f"Error processing session {key}: {e}")
                    
                    if cursor == 0:
                        break
            else:
                cleanup_memory_sessions()
                with session_cleanup_lock:
                    sessions_to_process = list(memory_sessions.items())
                
                for token, data in sessions_to_process:
                    try:
                        session = data['data']
                        if (len(session["rounds"]) > 15 and 
                            session.get("trap_depth", 0) > 3 and
                            not session.get("accepted")):
                            session["rounds"] = session["rounds"][-5:]
                            session["trap_depth"] = max(0, session["trap_depth"] - 1)
                            with session_cleanup_lock:
                                if token in memory_sessions:
                                    memory_sessions[token]['data'] = session
                    except Exception as e:
                        logger.error(f"Error processing memory session {token}: {e}")
                        
        except Exception as e:
            logger.error(f"Monitor loop error: {e}")

# -----------------------
# Session Management
# -----------------------
def new_session():
    token = mk_token()
    session = {
        "token": token,
        "created_at": now_ts(),
        "expiry": now_ts() + SESSION_EXPIRY,
        "rounds": [],
        "consecutive_passes": 0,
        "trap_mode": False,
        "trap_depth": 0,
        "accepted": False,
        "last_seen": now_ts()
    }
    sessions_total.inc()
    store_session(session)
    return session

# -----------------------
# API Endpoints
# -----------------------
@app.route("/session", methods=["POST"])
@limiter.limit("5 per minute")
def api_new_session():
    try:
        session = new_session()
        challenge = pick_challenge(session)
        round_obj = create_round(session, challenge)
        store_session(session)
        return jsonify({
            "token": session["token"],
            "challenge": sanitize_challenge(challenge),
            "round_id": round_obj["round_id"],
            "expires_in": int(session["expiry"] - now_ts())
        })
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        abort(500)

@app.route("/respond", methods=["POST"])
@limiter.limit("10 per minute")
def api_respond():
    try:
        payload = request.get_json(force=True)
        if not payload:
            abort(400, "Invalid JSON payload")
            
        token = payload.get("token")
        if not token:
            abort(400, "Missing token")
        
        client_signature = request.headers.get("X-Payload-Signature")
        if client_signature:
            if not verify_hmac_signature(payload, client_signature):
                abort(403, "Payload signature verification failed")
        
        session = get_session(token)
        if not session:
            abort(404, "Session not found or expired")
        
        round_id = payload.get("round_id")
        if not round_id:
            abort(400, "Missing round_id")
            
        round_obj = next((r for r in session["rounds"] if r["round_id"] == round_id), None)
        if not round_obj:
            abort(404, "Round not found")
        
        if round_obj.get("result"):
            abort(400, "Round already answered")
        
        answer = payload.get("answer", "")
        meta = payload.get("meta", {})
        
        if not isinstance(meta, dict):
            meta = {}
        
        human_score, explanation, bot_likelihood = score_round(
            session, round_obj["challenge"], answer, meta
        )

        round_obj["result"] = {
            "answered_at": now_ts(),
            "answer": answer,
            "meta": meta,
            "human_score": human_score,
            "explanation": explanation,
            "bot_likelihood": bot_likelihood
        }

        accepted, action, next_challenge, next_round_id = paradox_decide_next(session, round_obj)
        
        store_session(session)
        
        response = {
            "round_result": {
                "human_score": round_obj["result"]["human_score"],
                "explanation": round_obj["result"]["explanation"],
                "bot_likelihood": round_obj["result"]["bot_likelihood"]
            },
            "accepted": accepted,
            "action": action,
            "trap_depth": session.get("trap_depth", 0),
            "consecutive_passes": session.get("consecutive_passes", 0)
        }
        
        if next_challenge:
            response["next_challenge"] = next_challenge
            response["next_round_id"] = next_round_id

        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in respond endpoint: {e}")
        if isinstance(e, tuple):
            raise
        abort(500)

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": now_ts(),
        "redis_connected": redis_conn is not None,
        "active_sessions": len(memory_sessions) if not redis_conn else "redis"
    })

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest(REGISTRY), 200, {'Content-Type': 'text/plain'}

# -----------------------
# Background Services
# -----------------------
def start_background_threads():
    try:
        monitor_thread = threading.Thread(target=monitor_recursion_loops, daemon=True)
        monitor_thread.start()
        logger.info("Background monitoring thread started")
    except Exception as e:
        logger.error(f"Failed to start background threads: {e}")

# -----------------------
# Entry Point
# -----------------------
if __name__ == "__main__":
    start_background_threads()
    app.run(host="0.0.0.0", port=5000, threaded=True)
```

### Dockerfile
```Dockerfile
# Production Dockerfile
FROM python:3.11-slim-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV REDIS_URL="redis://redis:6379"

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1001 paradox
USER paradox
WORKDIR /app

# Install Python dependencies
COPY --chown=paradox:paradox requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY --chown=paradox:paradox . .

# Expose port and run
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s CMD curl --fail http://localhost:8000/health || exit 1

CMD ["gunicorn", "paradox_loop_server:app", \
     "--workers", "4", \
     "--worker-class", "gevent", \
     "--bind", "0.0.0.0:8000", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--timeout", "120"]
```

### requirements.txt
```
Flask==2.3.2
Flask-Limiter==2.6.3
redis==4.6.0
gevent==22.10.2
gunicorn==20.1.0
prometheus_client==0.18.0
pyOpenSSL==23.2.0
```

### Deployment Instructions
1. Save the Python code as `paradox_loop_server.py`
2. Save the Dockerfile as `Dockerfile`
3. Save the requirements as `requirements.txt`
4. Build the Docker image:
   ```bash
   docker build -t paradox-captcha .
   ```
5. Run Redis:
   ```bash
   docker run -d --name redis -p 6379:6379 redis:7-alpine
   ```
6. Run the application:
   ```bash
   docker run -d --name captcha -p 8000:8000 --link redis \
     -e REDIS_URL=redis://redis:6379 \
     -e HMAC_SECRET=$(openssl rand -hex 32) \
     paradox-captcha
   ```

