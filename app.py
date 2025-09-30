from flask import Flask, jsonify, request, render_template, abort
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from backend.src.captcha.paradox_loop import (
    new_session, pick_challenge, create_round, store_session, score_round,
    paradox_decide_next, sanitize_challenge, verify_hmac_signature, get_session
)
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='frontend', static_url_path='/static')
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri=os.getenv("REDIS_URL", "redis://localhost:6379"),
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

@app.route('/')
def serve_frontend():
    """Serve the CAPTCHA frontend."""
    return render_template('index.html')

@app.route('/session', methods=['POST'])
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
            "expires_in": int(session["expiry"] - session["created_at"])
        })
    except Exception as e:
        logger.error(f"Error creating session: {e}", exc_info=True)
        abort(500)

@app.route('/respond', methods=['POST'])
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
        if len(answer) > 1000:
            abort(400, "Answer too long (max 1000)")
        meta = payload.get("meta", {})
        if not isinstance(meta, dict):
            meta = {}
        human_score, explanation, bot_likelihood = score_round(session, round_obj["challenge"], answer, meta)
        round_obj["result"] = {
            "answered_at": session["last_seen"],
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
                "human_score": human_score,
                "explanation": explanation,
                "bot_likelihood": bot_likelihood
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
        abort(500)

@app.route('/health')
def health_check():
    from backend.src.captcha.paradox_loop import redis_conn, memory_sessions, now_ts
    return jsonify({
        "status": "healthy",
        "timestamp": now_ts(),
        "redis_connected": redis_conn is not None,
        "active_sessions": len(memory_sessions) if not redis_conn else "redis"
    })

@app.route('/metrics')
def metrics():
    from prometheus_client import generate_latest, REGISTRY
    return generate_latest(REGISTRY), 200, {'Content-Type': 'text/plain'}

if __name__ == "__main__":
    from backend.src.captcha.paradox_loop import validate_config, start_background_threads
    validate_config()
    start_background_threads()
    app.run(host="0.0.0.0", port=5000, threaded=True)
