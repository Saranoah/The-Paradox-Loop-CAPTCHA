import hmac
import hashlib
import base64

# Generate secret key (store in environment)
SECRET_KEY = os.environ.get("HMAC_SECRET", secrets.token_bytes(32))

def generate_hmac_signature(payload):
    """Generate HMAC signature for payload"""
    if isinstance(payload, str):
        payload = payload.encode()
    return hmac.new(SECRET_KEY, payload, hashlib.sha256).hexdigest()

def verify_hmac_signature(payload, signature):
    """Verify HMAC signature"""
    expected = generate_hmac_signature(payload)
    return hmac.compare_digest(expected, signature)

# In api_respond()
@app.route("/respond", methods=["POST"])
def api_respond():
    payload = request.get_json(force=True)
    
    # Verify HMAC signature
    client_signature = request.headers.get("X-Payload-Signature")
    if not verify_hmac_signature(json.dumps(payload), client_signature):
        abort(403, "Payload signature verification failed")
    
    ... # existing logic
