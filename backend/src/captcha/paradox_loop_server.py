from prometheus_client import Counter, Gauge, start_http_server

# --- Metrics ---
paradox_sessions_total = Counter('paradox_sessions_total', 'Total sessions created')
paradox_rounds_total = Counter('paradox_rounds_total', 'Rounds processed by type and trap mode', ['type', 'trap_mode'])
paradox_session_trap_depth = Gauge('paradox_session_trap_depth', 'Distribution of trap depths')
paradox_bot_likelihood_score = Gauge('paradox_bot_likelihood_score', 'Bot likelihood scores')
paradox_challenge_success = Counter('paradox_challenge_success', 'Challenge success rate by type', ['type'])

# Start metrics endpoint
start_http_server(8000)
