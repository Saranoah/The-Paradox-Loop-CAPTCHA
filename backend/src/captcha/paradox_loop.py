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
from typing import Dict, Optional, List, Tuple, Callable, Any
from collections import deque
import redis
import logging
import base64
from prometheus_client import generate_latest, REGISTRY, Counter, Gauge, Histogram
from uuid import uuid4
from functools import wraps
from redis.exceptions import RedisError
from tenacity import retry, stop_after_attempt, wait_exponential

# -----------------------
# Constants
# -----------------------
SESSION_EXPIRY_SECONDS = 600
MAX_ROUNDS = 20
REQUIRED_HUMAN_SCORE = 5
REQUIRED_CONSECUTIVE_PASSES = 3
TRAP_MODE_THRESHOLD = 0.55
TIME_DILATION_FACTOR = 1.5
QUANTUM_ENTANGLEMENT_DEPTH = 3
MAX_ANSWER_LENGTH = 1000
TIME_VARIANCE_THRESHOLD_MS = 1000
RECURSION_DEPTH_WARNING = 5
BOT_TIMING_TOLERANCE_MS = 1000
MAX_STORED_ROUNDS = 5
METRICS_PREFIX = "paradox_"

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
sessions_total = Counter(f'{METRICS_PREFIX}sessions_total', 'Total sessions created')
rounds_total = Counter(f'{METRICS_PREFIX}rounds_total', 'Total rounds processed', ['type', 'trap_mode'])
session_trap_depth_distribution = Histogram(
    f'{METRICS_PREFIX}session_trap_depth',
    'Distribution of trap depths',
    buckets=[0, 1, 2, 3, 5, 10, 15, 20]
)
bot_likelihood_score = Histogram(
    f'{METRICS_PREFIX}bot_likelihood_score',
    'Bot likelihood scores',
    buckets=[0.1, 0.3, 0.5, 0.7, 0.9, 1.0]
)
challenge_success = Counter(f'{METRICS_PREFIX}challenge_success', 'Challenge success rate', ['type', 'success'])

# -----------------------
# Security Enhancements
# -----------------------
HMAC_SECRET = os.environ.get("HMAC_SECRET")
if not HMAC_SECRET:
    logger.critical("HMAC_SECRET environment variable not set")
    raise RuntimeError("HMAC_SECRET environment variable required")
HMAC_SECRET = HMAC_SECRET.encode()
if len(HMAC_SECRET) < 32:
    HMAC_SECRET = hashlib.sha256(HMAC_SECRET).digest()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
try:
    redis_pool = redis.ConnectionPool.from_url(REDIS_URL, decode_responses=True)
    redis_conn = redis.Redis(connection_pool=redis_pool)
    redis_conn.ping()
    logger.info("Redis connection established")
except RedisError as e:
    logger.error(f"Redis connection failed: {e} - falling back to in-memory storage")
    redis_conn = None

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri=REDIS_URL if redis_conn else "memory://",
    default_limits=["500 per hour", "100 per minute"],
    headers_enabled=True
)

_rng_lock = threading.Lock()
memory_sessions: Dict[str, Dict[str, Any]] = {}
session_cleanup_lock = threading.Lock()

@app.after_request
def add_security_headers(response):
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['X-Request-ID'] = str(uuid4())
    return response

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
    logger.error(f"Internal server error: {e}", exc_info=True)
    return jsonify({
        "error": "internal_server_error",
        "kintsugi_wisdom": "From the deepest breaks comes the strongest repair"
    }), 500

# -----------------------
# Session Management
# -----------------------
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
def store_session(session: Dict[str, Any]) -> None:
    """Store session with metrics integration."""
    try:
        session_trap_depth_distribution.observe(session.get('trap_depth', 0))
        if redis_conn:
            serialized = json.dumps(session)
            redis_conn.setex(f"session:{session['token']}", SESSION_EXPIRY_SECONDS, serialized)
            if session.get('trap_depth', 0) > 3:
                redis_conn.zadd("trap_depths", {session['token']: session['trap_depth']})
        else:
            with session_cleanup_lock:
                memory_sessions[session['token']] = {
                    'data': session,
                    'expires': time.time() + SESSION_EXPIRY_SECONDS
                }
            cleanup_memory_sessions()
    except Exception as e:
        logger.error(f"Failed to store session: {e}")
        with session_cleanup_lock:
            memory_sessions[session['token']] = {
                'data': session,
                'expires': time.time() + SESSION_EXPIRY_SECONDS
            }

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
def get_session(token: str) -> Optional[Dict[str, Any]]:
    """Retrieve session from storage."""
    try:
        if redis_conn:
            data = redis_conn.get(f"session:{token}")
            if data:
                return json.loads(data)
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

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
def delete_session(token: str) -> None:
    """Delete session from storage."""
    try:
        if redis_conn:
            redis_conn.delete(f"session:{token}")
            redis_conn.zrem("trap_depths", token)
        else:
            with session_cleanup_lock:
                memory_sessions.pop(token, None)
    except Exception as e:
        logger.error(f"Failed to delete session: {e}")

def cleanup_memory_sessions() -> None:
    """Remove expired sessions from memory storage."""
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
# Utilities
# -----------------------
def now_ts() -> float:
    """Return current timestamp."""
    return time.time()

def mk_token() -> str:
    """Generate secure session token."""
    return secrets.token_urlsafe(32)

def quantum_hash(s: str) -> str:
    """Generate a short hash for challenge context."""
    h = hashlib.sha256(s.encode()).digest()
    return ''.join(f"{b:02x}" for b in h[:8])

def recursive_hash(seed: str, depth: int = 3) -> str:
    """Generate recursive hash for round IDs."""
    for _ in range(depth):
        seed = hashlib.sha256(seed.encode()).hexdigest()[:16]
    return seed

def canonical_json_obj(obj: Any) -> str:
    """Create canonical JSON string for signing."""
    return json.dumps(obj, separators=(',', ':'), sort_keys=True)

def generate_hmac_signature(payload_obj: Any) -> str:
    """Generate HMAC signature for payload."""
    payload = canonical_json_obj(payload_obj).encode()
    return hmac.new(HMAC_SECRET, payload, hashlib.sha256).hexdigest()

def verify_hmac_signature(payload_obj: Any, signature: str) -> bool:
    """Verify HMAC signature for payload."""
    try:
        expected = generate_hmac_signature(payload_obj)
        return hmac.compare_digest(expected, signature)
    except Exception as e:
        logger.error(f"HMAC verification failed: {e}")
        return False

def safe_random_choice(items: List[Any]) -> Any:
    """Thread-safe random choice using SystemRandom."""
    with _rng_lock:
        return random.SystemRandom().choice(items)

# -----------------------
# Challenge Factories
# -----------------------
def challenge_creative_input(session: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Generate creative input challenge."""
    return {
        "type": "creative_input",
        "text": "Name something that doesn't exist but should",
        "input": True,
        "validator_key": "creative_input",
        "context": {}
    }

def challenge_meta_loop(session: Dict[str, Any]) -> Dict[str, Any]:
    """Generate meta loop challenge referencing previous answers."""
    prev_answers = [r["result"]["answer"] for r in session["rounds"] if r.get("result")]
    if prev_answers:
        ref_answer = safe_random_choice(prev_answers[-QUANTUM_ENTANGLEMENT_DEPTH:])
        ref_hash = quantum_hash(ref_answer)
        return {
            "type": "meta_loop",
            "text": f"The answer to this is related to your previous answer '{ref_hash[:4]}...'. What did you enter 3 steps ago?",
            "input": True,
            "validator_key": "meta_loop",
            "context": {"ref_hash": ref_hash, "prev_answers": prev_answers}
        }
    return challenge_creative_input()

def challenge_recursive_paradox(session: Dict[str, Any]) -> Dict[str, Any]:
    """Generate recursive paradox challenge."""
    round_num = len(session["rounds"])
    return {
        "type": "recursive_paradox",
        "text": f"This statement has exactly {round_num} correct answers in this session.",
        "options": ["True", "False", f"{round_num}", "It's impossible"],
        "input": False,
        "validator_key": "recursive_paradox",
        "context": {"round_num": round_num}
    }

def challenge_quantum_state(session: Dict[str, Any]) -> Dict[str, Any]:
    """Generate quantum state challenge."""
    session["quantum_state"] = safe_random_choice(["superposition", "collapsed", "entangled"])
    return {
        "type": "quantum_state",
        "text": "If you choose YES, you'll get an easier challenge next. What do you choose?",
        "options": ["YES", "NO", "MAYBE", "SCHRÖDINGER"],
        "input": False,
        "validator_key": "quantum_state",
        "context": {"state": session["quantum_state"]}
    }

def challenge_temporal_paradox(session: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Generate temporal paradox challenge."""
    return {
        "type": "temporal_paradox",
        "text": "You solved this 5 seconds ago. What was your answer?",
        "input": True,
        "validator_key": "temporal_paradox",
        "context": {}
    }

def challenge_infinite_regress(session: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Generate infinite regress challenge."""
    return {
        "type": "infinite_regress",
        "text": "The correct answer is the first option of the next challenge",
        "options": ["Continue"],
        "input": False,
        "validator_key": "infinite_regress",
        "context": {}
    }

ALL_CHALLENGE_FACTORIES: List[Callable[[Optional[Dict[str, Any]]], Dict[str, Any]]] = [
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
def validate_creative_input(answer: str, meta: Dict[str, Any], session: Dict[str, Any], context: Dict[str, Any]) -> Tuple[int, str, float]:
    """Validate creative input challenge."""
    if not answer or len(answer) < 3:
        return 1, "too short", 0.9
    if len(answer) > 100:
        return 1, "suspiciously long", 0.8
    if len(set(answer)) < 3:
        return 1, "low entropy", 0.9
    return 4, "creative response", 0.2

def validate_meta_loop(answer: str, meta: Dict[str, Any], session: Dict[str, Any], context: Dict[str, Any]) -> Tuple[int, str, float]:
    """Validate meta loop challenge."""
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

def validate_recursive_paradox(answer: str, meta: Dict[str, Any], session: Dict[str, Any], context: Dict[str, Any]) -> Tuple[int, str, float]:
    """Validate recursive paradox challenge."""
    round_num = context["round_num"]
    correct_count = sum(1 for r in session["rounds"] if r.get("result", {}).get("human_score", 0) >= 3)
    if answer == f"{round_num}":
        valid = correct_count == round_num
    elif answer == "True":
        valid = correct_count > round_num / 2
    elif answer == "False":
        valid = correct_count <= round_num / 2
    else:
        valid = True
    return 4 if valid else 1, "recursive validation", 0.3 if valid else 0.7

def validate_quantum_state(answer: str, meta: Dict[str, Any], session: Dict[str, Any], context: Dict[str, Any]) -> Tuple[int, str, float]:
    """Validate quantum state challenge."""
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

def validate_temporal_paradox(answer: str, meta: Dict[str, Any], session: Dict[str, Any], context: Dict[str, Any]) -> Tuple[int, str, float]:
    """Validate temporal paradox challenge."""
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

def validate_infinite_regress(answer: str, meta: Dict[str, Any], session: Dict[str, Any], context: Dict[str, Any]) -> Tuple[int, str, float]:
    """Validate infinite regress challenge."""
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
def pick_challenge(session: Dict[str, Any], trap: bool = False) -> Dict[str, Any]:
    """Select a challenge based on session state."""
    future = session.get("quantum_future", "random")
    try:
        if trap:
            available_factories = ALL_CHALLENGE_FACTORIES
            weights = [1, 1, 3, 3, 2, 3][:len(available_factories)]
            factories = random.choices(available_factories, weights, k=min(5, len(available_factories)))
        else:
            factories = ALL_CHALLENGE_FACTORIES
        challenge_factory = safe_random_choice(factories)
        challenge = challenge_factory(session)
    except Exception as e:
        logger.error(f"Error creating challenge: {e}")
        challenge = challenge_creative_input()
    if trap:
        challenge["time_dilation"] = TIME_DILATION_FACTOR
    return challenge

def score_round(session: Dict[str, Any], challenge: Dict[str, Any], answer: str, meta: Dict[str, Any]) -> Tuple[int, str, float]:
    """Score a challenge response."""
    validator = VALIDATORS.get(challenge["validator_key"])
    if not validator:
        logger.error(f"No validator found for {challenge['validator_key']}")
        raise ValueError(f"Invalid validator key: {challenge['validator_key']}")
    context = challenge.get("context", {})
    try:
        human_score, explanation, bot_likelihood = validator(answer, meta, session, context)
    except Exception as e:
        logger.error(f"Validator error: {e}")
        return 2, f"validator error: {str(e)}", 0.5
    challenge_type = challenge["type"]
    trap_mode = "trap" if challenge.get("time_dilation") else "normal"
    rounds_total.labels(type=challenge_type, trap_mode=trap_mode).inc()
    bot_likelihood_score.observe(bot_likelihood)
    challenge_success.labels(type=challenge_type, success="pass" if human_score >= 3 else "fail").inc()
    if challenge.get("time_dilation"):
        time_ms = meta.get("time_ms", 0)
        expected_time = time_ms / challenge["time_dilation"]
        if abs(time_ms - expected_time) > BOT_TIMING_TOLERANCE_MS:
            bot_likelihood = min(1.0, bot_likelihood + 0.3)
    recursion_depth = len(session["rounds"])
    if recursion_depth > RECURSION_DEPTH_WARNING:
        if human_score > 3 and meta.get("time_ms", 0) < 1500:
            bot_likelihood = min(1.0, bot_likelihood + 0.2 * (recursion_depth / 10))
    return human_score, explanation, bot_likelihood

def create_round(session: Dict[str, Any], challenge: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new challenge round."""
    round_id = recursive_hash(session["token"] + str(len(session["rounds"])))
    round_obj = {
        "round_id": round_id,
        "issued_at": now_ts(),
        "challenge": challenge,
        "result": None
    }
    session["rounds"].append(round_obj)
    if len(session["rounds"]) > MAX_STORED_ROUNDS:
        session["rounds"] = session["rounds"][-MAX_STORED_ROUNDS:]
    session["last_seen"] = now_ts()
    return round_obj

def paradox_decide_next(session: Dict[str, Any], latest_round: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict[str, Any]], Optional[str]]:
    """Determine next action based on round result."""
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
    if session.get("trap_depth", 0) > 3:
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

def sanitize_challenge(challenge: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize challenge for client response."""
    sanitized = challenge.copy()
    sanitized.pop("context", None)
    sanitized.pop("validator_key", None)
    return sanitized

def monitor_recursion_loops() -> None:
    """Monitor sessions with high trap depth."""
    while True:
        try:
            time.sleep(30)
            if redis_conn:
                deep_trap_sessions = redis_conn.zrangebyscore("trap_depths", 3, float('inf'))
                for token in deep_trap_sessions:
                    try:
                        data = redis_conn.get(f"session:{token}")
                        if not data:
                            redis_conn.zrem("trap_depths", token)
                            continue
                        session = json.loads(data)
                        if len(session["rounds"]) > 15 and session.get("trap_depth", 0) > 3 and not session.get("accepted"):
                            session["rounds"] = session["rounds"][-MAX_STORED_ROUNDS:]
                            session["trap_depth"] = max(0, session["trap_depth"] - 1)
                            store_session(session)
                    except Exception as e:
                        logger.error(f"Error processing session {token}: {e}")
            else:
                cleanup_memory_sessions()
                with session_cleanup_lock:
                    sessions_to_process = list(memory_sessions.items())
                for token, data in sessions_to_process:
                    try:
                        session = data['data']
                        if len(session["rounds"]) > 15 and session.get("trap_depth", 0) > 3 and not session.get("accepted"):
                            session["rounds"] = session["rounds"][-MAX_STORED_ROUNDS:]
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
def new_session() -> Dict[str, Any]:
    """Create a new session."""
    token = mk_token()
    session = {
        "token": token,
        "created_at": now_ts(),
        "expiry": now_ts() + SESSION_EXPIRY_SECONDS,
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
    """Create a new CAPTCHA session.
    ---
    post:
      summary: Create a new CAPTCHA session
      responses:
        200:
          description: Session created successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  token: {type: string}
                  challenge: {type: object}
                  round_id: {type: string}
                  expires_in: {type: integer}
        429:
          description: Rate limit exceeded
        500:
          description: Internal server error
    """
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
        logger.error(f"Error creating session: {e}", exc_info=True)
        abort(500)

@app.route("/respond", methods=["POST"])
@limiter.limit("10 per minute")
def api_respond():
    """Respond to a CAPTCHA challenge.
    ---
    post:
      summary: Submit a response to a CAPTCHA challenge
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                token: {type: string}
                round_id: {type: string}
                answer: {type: string}
                meta: {type: object}
      responses:
        200:
          description: Response processed
          content:
            application/json:
              schema:
                type: object
                properties:
                  round_result: {type: object}
                  accepted: {type: boolean}
                  action: {type: string}
                  trap_depth: {type: integer}
                  consecutive_passes: {type: integer}
                  next_challenge: {type: object, nullable: true}
                  next_round_id: {type: string, nullable: true}
        400:
          description: Invalid request
        403:
          description: Invalid signature or missing
        404:
          description: Session or round not found
        429:
          description: Rate limit exceeded
        500:
          description: Internal server error
    """
    try:
        payload = request.get_json(force=True)
        if not payload:
            abort(400, "Invalid JSON payload")
        token = payload.get("token")
        if not token:
            abort(400, "Missing token")
        client_signature = request.headers.get("X-Payload-Signature")
        if not client_signature:
            abort(403, "Missing X-Payload-Signature header")
        if not verify_hmac_signature(payload, client_signature):
            abort(403, "Invalid signature")
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
        if not isinstance(answer, str):
            abort(400, "Answer must be string")
        if len(answer) > MAX_ANSWER_LENGTH:
            abort(400, f"Answer too long (max {MAX_ANSWER_LENGTH})")
        meta = payload.get("meta", {})
        if not isinstance(meta, dict):
            meta = {}
        human_score, explanation, bot_likelihood = score_round(session, round_obj["challenge"], answer, meta)
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
        logger.error(f"Error in respond endpoint: {e}", exc_info=True)
        if isinstance(e, tuple):
            raise
        abort(500)

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": now_ts(),
        "redis_connected": redis_conn is not None,
        "active_sessions": len(memory_sessions) if not redis_conn else "redis"
    })

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint."""
    return generate_latest(REGISTRY), 200, {'Content-Type': 'text/plain'}

# -----------------------
# Background Services
# -----------------------
def start_background_threads():
    """Start background monitoring threads."""
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
