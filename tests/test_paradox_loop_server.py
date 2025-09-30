import pytest
import time
import json
from typing import Dict
from flask import Response
from paradox_loop_server import app, verify_hmac_signature, mk_token, store_session, get_session, new_session, create_round, pick_challenge, score_round, VALIDATORS

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def valid_session():
    """Create a valid session for testing."""
    return new_session()

def generate_valid_signature(payload: Dict) -> str:
    """Generate a valid HMAC signature for a payload."""
    return verify_hmac_signature(payload, 'test')  # Note: Requires HMAC_SECRET set

def test_hmac_signature_required(client: Response, valid_session: Dict):
    """Test that requests without signature are rejected."""
    payload = {'token': valid_session['token'], 'round_id': 'test', 'answer': 'test'}
    response = client.post('/respond', json=payload)
    assert response.status_code == 403
    assert json.loads(response.data)['error'] == 'forbidden'

def test_invalid_hmac_signature(client: Response, valid_session: Dict):
    """Test that requests with invalid signature are rejected."""
    payload = {'token': valid_session['token'], 'round_id': 'test', 'answer': 'test'}
    response = client.post('/respond', json=payload, headers={'X-Payload-Signature': 'invalid'})
    assert response.status_code == 403
    assert json.loads(response.data)['error'] == 'forbidden'

def test_oversized_answer(client: Response, valid_session: Dict):
    """Test that oversized answers are rejected."""
    store_session(valid_session)
    payload = {'token': valid_session['token'], 'round_id': 'test', 'answer': 'A' * 1001}
    signature = generate_valid_signature(payload)
    response = client.post('/respond', json=payload, headers={'X-Payload-Signature': signature})
    assert response.status_code == 400
    assert json.loads(response.data)['error'] == 'bad_request'

def test_invalid_answer_type(client: Response, valid_session: Dict):
    """Test that non-string answers are rejected."""
    store_session(valid_session)
    payload = {'token': valid_session['token'], 'round_id': 'test', 'answer': 123}
    signature = generate_valid_signature(payload)
    response = client.post('/respond', json=payload, headers={'X-Payload-Signature': signature})
    assert response.status_code == 400
    assert json.loads(response.data)['error'] == 'bad_request'

def test_session_creation(client: Response):
    """Test session creation endpoint."""
    response = client.post('/session')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'token' in data
    assert 'challenge' in data
    assert 'round_id' in data
    assert 'expires_in' in data
    assert isinstance(data['token'], str)
    assert isinstance(data['challenge'], dict)
    assert isinstance(data['round_id'], str)
    assert isinstance(data['expires_in'], int)

def test_session_expiry(client: Response, valid_session: Dict):
    """Test that expired sessions are rejected."""
    valid_session['expiry'] = time.time() - 1
    store_session(valid_session)
    payload = {'token': valid_session['token'], 'round_id': 'test', 'answer': 'test'}
    signature = generate_valid_signature(payload)
    response = client.post('/respond', json=payload, headers={'X-Payload-Signature': signature})
    assert response.status_code == 404
    assert json.loads(response.data)['error'] == 'not_found'

def test_session_not_found(client: Response):
    """Test that non-existent sessions are rejected."""
    payload = {'token': 'nonexistent', 'round_id': 'test', 'answer': 'test'}
    signature = generate_valid_signature(payload)
    response = client.post('/respond', json=payload, headers={'X-Payload-Signature': signature})
    assert response.status_code == 404
    assert json.loads(response.data)['error'] == 'not_found'

def test_round_already_answered(client: Response, valid_session: Dict):
    """Test that already answered rounds are rejected."""
    challenge = pick_challenge(valid_session)
    round_obj = create_round(valid_session, challenge)
    round_obj['result'] = {'answered_at': time.time(), 'answer': 'test', 'meta': {}, 'human_score': 4, 'explanation': 'test', 'bot_likelihood': 0.2}
    store_session(valid_session)
    payload = {'token': valid_session['token'], 'round_id': round_obj['round_id'], 'answer': 'test'}
    signature = generate_valid_signature(payload)
    response = client.post('/respond', json=payload, headers={'X-Payload-Signature': signature})
    assert response.status_code == 400
    assert json.loads(response.data)['error'] == 'bad_request'

def test_rate_limiting(client: Response):
    """Test rate limiting on /session endpoint."""
    for _ in range(6):  # Exceed 5/min limit
        response = client.post('/session')
    assert response.status_code == 429
    assert json.loads(response.data)['error'] == 'rate_limit_exceeded'

def test_creative_input_validator(valid_session: Dict):
    """Test creative input validator."""
    challenge = {'type': 'creative_input', 'validator_key': 'creative_input', 'context': {}}
    score, explanation, bot_likelihood = score_round(valid_session, challenge, 'Flying cars', {})
    assert score == 4
    assert explanation == 'creative response'
    assert bot_likelihood == 0.2

def test_creative_input_validator_too_short(valid_session: Dict):
    """Test creative input validator with short answer."""
    challenge = {'type': 'creative_input', 'validator_key': 'creative_input', 'context': {}}
    score, explanation, bot_likelihood = score_round(valid_session, challenge, 'a', {})
    assert score == 1
    assert explanation == 'too short'
    assert bot_likelihood == 0.9

def test_meta_loop_validator(valid_session: Dict):
    """Test meta loop validator."""
    valid_session['rounds'] = [{'result': {'answer': 'test_answer'}}]
    challenge = {'type': 'meta_loop', 'validator_key': 'meta_loop', 'context': {'prev_answers': ['test_answer']}}
    score, explanation, bot_likelihood = score_round(valid_session, challenge, 'test_answer', {})
    assert score == 4
    assert explanation == 'human-like recall'
    assert bot_likelihood == 0.2

def test_all_challenge_factories(valid_session: Dict):
    """Test that all challenge factories return valid challenges."""
    for factory in ALL_CHALLENGE_FACTORIES:
        challenge = factory(valid_session)
        assert isinstance(challenge, dict)
        assert 'type' in challenge
        assert 'validator_key' in challenge
        assert challenge['validator_key'] in VALIDATORS

def test_trap_mode_activation(valid_session: Dict):
    """Test trap mode activation."""
    challenge = {'type': 'creative_input', 'validator_key': 'creative_input', 'context': {}}
    valid_session['trap_depth'] = 0
    valid_session['trap_mode'] = False
    score_round(valid_session, challenge, 'test', {'time_ms': 100})
    assert not valid_session['trap_mode']  # Bot likelihood 0.2 < threshold
    score_round(valid_session, challenge, 'a' * 1000, {'time_ms': 100})
    assert valid_session['trap_mode']  # Bot likelihood 0.9 > threshold

def test_consecutive_passes(valid_session: Dict):
    """Test consecutive passes logic."""
    challenge = {'type': 'creative_input', 'validator_key': 'creative_input', 'context': {}}
    valid_session['consecutive_passes'] = 0
    score_round(valid_session, challenge, 'Flying cars', {})
    assert valid_session['consecutive_passes'] == 1
    score_round(valid_session, challenge, 'a', {})
    assert valid_session['consecutive_passes'] == 0

def test_health_endpoint(client: Response):
    """Test health endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert 'timestamp' in data
    assert 'redis_connected' in data
    assert 'active_sessions' in data

def test_metrics_endpoint(client: Response):
    """Test metrics endpoint."""
    response = client.get('/metrics')
    assert response.status_code == 200
    assert response.content_type == 'text/plain'
    assert b'paradox_sessions_total' in response.data

def test_session_endpoint_success(client: Response):
    """Test successful session creation."""
    response = client.post('/session')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['token']) >= 32
    assert 'challenge' in data
    assert data['expires_in'] > 0

def test_respond_endpoint_success(client: Response, valid_session: Dict):
    """Test successful response submission."""
    challenge = pick_challenge(valid_session)
    round_obj = create_round(valid_session, challenge)
    store_session(valid_session)
    payload = {'token': valid_session['token'], 'round_id': round_obj['round_id'], 'answer': 'Flying cars'}
    signature = generate_valid_signature(payload)
    response = client.post('/respond', json=payload, headers={'X-Payload-Signature': signature})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'round_result' in data
    assert data['round_result']['human_score'] == 4

def test_error_responses(client: Response):
    """Test error responses for invalid requests."""
    response = client.post('/respond')  # No JSON
    assert response.status_code == 400
    assert json.loads(response.data)['error'] == 'bad_request'

# Note: HMAC testing requires setting HMAC_SECRET in test environment
