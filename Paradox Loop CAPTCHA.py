#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
✨ Enhanced Paradox Loop CAPTCHA - Backend Maze
Now with recursive trapping and quantum entanglement
"""
# Add to server initialization

# Create managed Redis instance (AWS example)
aws elasticache create-cache-cluster \
  --cluster-id paradox-redis \
  --engine redis \
  --cache-node-type cache.t3.micro \
  --num-cache-nodes 1
# Kubernetes secret example
kubectl create secret generic captcha-secrets \
  --from-literal=HMAC_SECRET=$STRONG_SECRET \
  --from-literal=SESSION_SECRET=$ANOTHER_SECRET

# Prometheus metrics endpoint
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Paradox Loop CAPTCHA', version='2.0')

@app.after_request
def add_security_headers(response):
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response
from flask import Flask, jsonify, request, abort 
import secrets# Custom rate limit strategy
limiter = Limiter(
    app=app,
    key_func=lambda: request.headers.get("X-Forwarded-For", get_remote_address()),
    storage_uri="redis://localhost:6379",
    strategy="moving-window",  # More accurate than fixed-window
    default_limits=["500 per hour", "100 per minute"],
    headers_enabled=True  # Show rate limit headers in responses
)
import time
import hashlib
import random
import threading
import math
import json
from collections import deque

app = Flask(__name__)

# -----------------------
# Enhanced Configuration
# -----------------------
SESSION_EXPIRY = 600            # Increased session timeout
MAX_ROUNDS = 20                 # Higher limit for deeper recursion
REQUIRED_HUMAN_SCORE = 5        # More stringent scoring
REQUIRED_CONSECUTIVE_PASSES = 3 # Require more consistent human behavior
TRAP_MODE_THRESHOLD = 0.55      # More sensitive bot detection
RNG = random.SystemRandom()
QUANTUM_ENTANGLEMENT_DEPTH = 3  # Levels of answer dependency
TIME_DILATION_FACTOR = 1.5      # Time distortion in trap mode

# -----------------------
# In-memory stores with recursion tracking
# -----------------------
sessions = {}
sessions_lock = threading.Lock()
recursion_chains = deque(maxlen=1000)  # Track challenge sequences for pattern detection

# -----------------------
# Enhanced Utilities
# -----------------------
def now_ts():
    return time.time()

def mk_token():
    return secrets.token_urlsafe(32)  # Longer tokens

def quantum_hash(s):
    """Hash that preserves some similarity for entangled answers"""
    h = hashlib.sha256(s.encode()).digest()
    return ''.join(f"{b:02x}" for b in h[:8])

def recursive_hash(seed, depth=3):
    """Generate hash with recursive properties"""
    for _ in range(depth):
        seed = hashlib.sha256(seed.encode()).hexdigest()[:16]
    return seed

# -----------------------
# Enhanced Challenge Templates with Recursive Dependencies
# -----------------------
def challenge_meta_loop(session):
    """Challenge that references previous answers"""
    prev_answers = [r["result"]["answer"] for r in session["rounds"] if r.get("result")]
    
    # Build recursive question based on history
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
    return challenge_creative_input()  # Fallback

def challenge_recursive_paradox(session):
    """Self-referential paradox"""
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
    """Answer depends on future choices"""
    session["quantum_state"] = RNG.choice(["superposition", "collapsed", "entangled"])
    return {
        "type": "quantum_state",
        "text": f"If you choose YES, you'll get an easier challenge next. What do you choose?",
        "options": ["YES", "NO", "MAYBE", "SCHRÖDINGER"],
        "input": False,
        "validator_key": "quantum_state",
        "context": {"state": session["quantum_state"]}
    }

def challenge_temporal_paradox():
    """Time-warped challenge"""
    return {
        "type": "temporal_paradox",
        "text": "You solved this 5 seconds ago. What was your answer?",
        "input": True,
        "validator_key": "temporal_paradox"
    }

def challenge_infinite_regress():
    return {
        "type": "infinite_regress",
        "text": "The correct answer is the first option of the next challenge",
        "options": ["Continue"],
        "input": False,
        "validator_key": "infinite_regress"
    }

# Add to factories
ALL_CHALLENGE_FACTORIES = [
    # ... keep previous challenges ...
    challenge_meta_loop,
    challenge_recursive_paradox,
    challenge_quantum_state,
    challenge_temporal_paradox,
    challenge_infinite_regress
]

# -----------------------
# Enhanced Validators with Recursive Checks
# -----------------------
def validate_meta_loop(answer, meta, session, context):
    """Validate based on previous answers"""
    prev_answers = context.get("prev_answers", [])
    ref_hash = context.get("ref_hash", "")
    
    # Check similarity to referenced answer
    similarity = 0
    if prev_answers:
        target = prev_answers[-min(QUANTUM_ENTANGLEMENT_DEPTH, len(prev_answers))]
        for i in range(min(len(answer), len(target))):
            if answer[i] == target[i]:
                similarity += 1
        similarity_score = similarity / max(len(target), 1)
    else:
        similarity_score = 0
    
    # Humans will have partial matches, bots will have 0 or 100%
    if 0.2 < similarity_score < 0.8:
        return 4, "human-like recall", 0.2
    return 1, "exact or no match", 0.8

def validate_recursive_paradox(answer, meta, session, context):
    """Self-referential validation"""
    round_num = context["round_num"]
    correct_count = sum(1 for r in session["rounds"] if r.get("result", {}).get("human_score", 0) >= 3)
    
    # Paradox logic
    if answer == f"{round_num}":
        valid = correct_count == round_num
    elif answer == "True":
        valid = correct_count > round_num/2
    elif answer == "False":
        valid = correct_count <= round_num/2
    else:  # "It's impossible"
        valid = True  # Always accept this human response
        
    return 4 if valid else 1, "recursive validation", 0.3 if valid else 0.7

def validate_quantum_state(answer, meta, session, context):
    """Quantum entangled validation"""
    state = session.get("quantum_state", "superposition")
    
    # Future state depends on answer
    if answer == "YES":
        session["quantum_future"] = "easier"
    elif answer == "NO":
        session["quantum_future"] = "harder"
    elif answer == "MAYBE":
        session["quantum_future"] = "paradox"
    else:  # SCHRÖDINGER
        session["quantum_future"] = "both"
    
    # All answers are valid but score differently
    return 3, f"quantum {state}", 0.4

def validate_temporal_paradox(answer, meta, session, context):
    """Validate against past actions"""
    time_elapsed = now_ts() - session["created_at"]
    imagined_past = time_elapsed - 5  # "5 seconds ago"
    
    # Find closest historical answer
    closest = None
    for r in session["rounds"]:
        if not r.get("result"):
            continue
        time_diff = abs(r["result"]["answered_at"] - imagined_past)
        if closest is None or time_diff < closest[0]:
            closest = (time_diff, r["result"]["answer"])
    
    # Compare to given answer
    if closest and answer == closest[1]:
        return 2, "time match", 0.5  # Suspiciously perfect
    return 3, "human time variance", 0.3

def validate_infinite_regress(answer, meta, session, context):
    """Always triggers next challenge"""
    return 2, "infinite regress", 0.6

# Update validator mapping
VALIDATORS = {
    # ... previous validators ...
    "meta_loop": validate_meta_loop,
    "recursive_paradox": validate_recursive_paradox,
    "quantum_state": validate_quantum_state,
    "temporal_paradox": validate_temporal_paradox,
    "infinite_regress": validate_infinite_regress
}

# -----------------------
# Core Logic Enhancements
# -----------------------
def pick_challenge(session, trap=False):
    """Select challenge with recursive dependencies"""
    # Quantum state influences selection
    future = session.get("quantum_future", "random")
    
    if trap:
        # Prefer recursive traps in trap mode
        weights = [1, 1, 3, 3, 2, 3, 2, 4, 4]  # Higher weights for new traps
        factories = RNG.choices(ALL_CHALLENGE_FACTORIES, weights, k=5)
    else:
        factories = ALL_CHALLENGE_FACTORIES
    
    # Create context-aware challenge
    challenge_factory = RNG.choice(factories)
    challenge = challenge_factory(session) if challenge_factory.__name__ in [
        "challenge_meta_loop", "challenge_recursive_paradox", "challenge_quantum_state"
    ] else challenge_factory()
    
    # Apply time dilation in trap mode
    if trap:
        challenge["time_dilation"] = TIME_DILATION_FACTOR
    
    return challenge

def score_round(session, challenge, answer, meta):
    """Enhanced scoring with context"""
    validator = VALIDATORS.get(challenge["validator_key"])
    if not validator:
        return 0, "no validator", 0.5

    # Add recursive context
    context = challenge.get("context", {})
    human_score, explanation, bot_likelihood = validator(
        answer, meta, session, context
    )

    # Time dilation effect
    if challenge.get("time_dilation"):
        time_ms = meta.get("time_ms", 0)
        expected_time = time_ms / challenge["time_dilation"]
        if abs(time_ms - expected_time) > 1000:  # Too precise or too slow
            bot_likelihood = min(1.0, bot_likelihood + 0.3)

    # Recursion penalty
    recursion_depth = len(session["rounds"])
    if recursion_depth > 5:
        # Humans get fatigued, bots stay consistent
        if human_score > 3 and meta.get("time_ms", 0) < 1500:
            bot_likelihood = min(1.0, bot_likelihood + 0.2 * recursion_depth)

    return human_score, explanation, bot_likelihood

# -----------------------
# Enhanced Loop Logic
# -----------------------
def paradox_decide_next(session, latest_round):
    """Recursive trap decision engine"""
    res = latest_round["result"]
    round_num = len(session["rounds"])

    # Update consecutive passes
    passed = res["human_score"] >= REQUIRED_HUMAN_SCORE and res["bot_likelihood"] < TRAP_MODE_THRESHOLD
    if passed:
        session["consecutive_passes"] += 1
    else:
        session["consecutive_passes"] = 0

    # Enter trap mode if bot detected
    if res["bot_likelihood"] >= TRAP_MODE_THRESHOLD:
        session["trap_mode"] = True
        session["trap_depth"] = session.get("trap_depth", 0) + 1

    # Recursive trap escalation
    if session.get("trap_depth", 0) > 2:
        # Deep trap - force infinite regress
        next_ch = challenge_infinite_regress()
        next_round = create_round(session, next_ch)
        return False, "deep_trap", sanitize_challenge(next_ch), next_round["round_id"]

    # Consecutive passes escape
    if session["consecutive_passes"] >= REQUIRED_CONSECUTIVE_PASSES:
        session["accepted"] = True
        return True, "accepted", None, None

    # Max rounds fallback
    if round_num >= MAX_ROUNDS:
        if session["trap_mode"]:
            return False, "fallback_traditional", None, None
        session["accepted"] = True
        return True, "accepted_after_limit", None, None

    # Next challenge with escalation
    next_ch = pick_challenge(session, trap=session["trap_mode"])
    next_round = create_round(session, next_ch)
    return False, "continue", sanitize_challenge(next_ch), next_round["round_id"]

def create_round(session, challenge):
    """Create new round with recursive ID"""
    round_id = recursive_hash(session["token"] + str(len(session["rounds"])))
    round_obj = {
        "round_id": round_id,
        "issued_at": now_ts(),
        "challenge": challenge,
        "result": None
    }
    session["rounds"].append(round_obj)
    session["last_seen"] = now_ts()
    return round_obj

# -----------------------
# Enhanced API Endpoints
# -----------------------
@app.route("/session", methods=["POST"])
def api_new_session():
    session = new_session()
    challenge = pick_challenge(session)
    round_obj = create_round(session, challenge)
    return jsonify({
        "token": session["token"],
        "challenge": sanitize_challenge(challenge),
        "round_id": round_obj["round_id"],
        "expires_in": session["expiry"] - now_ts()
    })

@app.route("/respond", methods=["POST"])
def api_respond():
    payload = request.get_json(force=True)
    token = payload.get("token")
    # ... existing token validation ...

    # Find round
    round_id = payload.get("round_id")
    round_obj = next((r for r in session["rounds"] if r["round_id"] == round_id), None)
    
    # ... existing validation ...

    # Score with enhanced context
    human_score, explanation, bot_likelihood = score_round(
        session, round_obj["challenge"], payload["answer"], payload["meta"]
    )

    # Save result
    round_obj["result"] = {
        "answered_at": now_ts(),
        "answer": payload["answer"],
        "meta": payload["meta"],
        "human_score": human_score,
        "explanation": explanation,
        "bot_likelihood": bot_likelihood
    }

    # Recursive decision
    accepted, action, next_challenge, next_round_id = paradox_decide_next(session, round_obj)
    
    response = {
        "round_result": round_obj["result"],
        "accepted": accepted,
        "action": action,
        "trap_depth": session.get("trap_depth", 0)
    }
    
    if next_challenge:
        response["next_challenge"] = next_challenge
        response["next_round_id"] = next_round_id

    return jsonify(response)

# -----------------------
# Recursion Monitoring Thread
# -----------------------
def monitor_recursion_loops():
    """Detect and break infinite bot loops"""
    while True:
        time.sleep(30)
        with sessions_lock:
            now = now_ts()
            for token, session in list(sessions.items()):
                # Break infinite loops
                if (len(session["rounds"]) > 15 and 
                    session.get("trap_depth", 0) > 3 and
                    not session.get("accepted")):
                    session["rounds"] = session["rounds"][-5:]  # Reset history
                    session["trap_depth"] = max(0, session["trap_depth"] - 1)

# Start monitoring thread
monitor_thread = threading.Thread(target=monitor_recursion_loops, daemon=True)
monitor_thread.start()

# -----------------------
# Updated Housekeeping
# -----------------------
def cleanup_loop():
    while True:
        time.sleep(60)
        with sessions_lock:
            now = now_ts()
            expired = [k for k,v in sessions.items() if v["expiry"] < now]
            for k in expired:
                # Save recursion patterns before deletion
                if len(sessions[k]["rounds"]) > 5:
                    recursion_chains.append({
                        "pattern": [r["challenge"]["type"] for r in sessions[k]["rounds"]],
                        "depth": sessions[k].get("trap_depth", 0)
                    })
                del sessions[k]

# ... rest of the code remains with updated sanitize_challenge ...
