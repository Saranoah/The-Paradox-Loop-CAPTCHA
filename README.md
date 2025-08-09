# 🌀 KINTSUGI PARADOX-LOOP CAPTCHA — v2.0

**An AI-Hardened, Recursive Human-Verification Ritual**
*Security through meaning. The cracks are the key.* ✨

[![Open in VS Code](https://img.shields.io/badge/Open-in%20VS%20Code-007ACC?style=for-the-badge\&logo=visual-studio-code\&logoColor=white)](https://vscode.dev/github/Saranoah/paradox-loop-captcha)

---

> *“We do not patch the fracture. We gild it.”*
> — The Kintsugi Reconciler

A dramatic README for the Paradox-Loop CAPTCHA: a living maze of paradoxes, behavioral biometrics, and AI-aware traps that seals bots in recursive loops while letting humans flow through by intuition.

---

## 🔮 Hero — What is this?

Paradox-Loop CAPTCHA (PLP) is a **post-Turing human-verification protocol** that treats authentication as a ritual.
Rather than brittle yes/no checks, PLP issues *paradoxical, creative, and self-referential* challenges that:

* favor **ambiguity** and **subjectivity** (humans excel),
* measure **behavioral nuance** (micro-motions, hesitation, velocity),
* adapt **dynamically** (AI adversarial mode and trap escalation),
* and **trap** automation in recursive mazes (the solver solves — the protocol spawns a new paradox).

Think of it as a shrine: one must *feel contradiction* to pass.

---

## 🎨 Visual / Aesthetic Intent

This repo is Kintsugi by design: golden cracks, soft gradients, and ritualized UX to make the verification *meaningful* and even beautiful.

> Visual motif: gold seams that glow when you pass, shiver when you falter.

(Frontend includes animated "kintsugi cracks", accessible audio paradox modes, and graceful emergency fallback to traditional CAPTCHA.)

---

## 🧭 Quickstart — Run locally (dev)

```bash
# clone (replace repo name if different)
git clone https://github.com/Saranoah/paradox-loop-captcha.git
cd paradox-loop-captcha

# create a virtualenv & install deps
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# start server
python paradox_loop_server.py
# open the demo client at http://localhost:5000 (or the provided HTML)
```

---

## 🏛️ Protocol Overview (short)

1. Client requests a session → server issues `challenge_1`.
2. Client answers plus behavioral telemetry (mouse path, timestamps, click pattern).
3. Server scores: **semantic validator + behavioral heuristics + adversarial LLM check (optional)**.
4. If score < threshold **or** bot-likelihood high → **trap**: issue `challenge_2` (mutated / recursive).
5. Repeat until: consecutive human rounds ≥ required → **accept**, or MAX\_ROUNDS → fallback.

---

## ⚙️ Core Design Principles

* **Recursive Trap** — single correct answers aren’t final. Bots get deeper puzzles.
* **Behavioral Fusion** — entropy, velocity, micro-movements, hesitation, and time-series analysis.
* **AI Adversarial Mode** — LLM in simulation mode to compute bot-likelihood and mutate challenges.
* **Graceful Fallbacks** — emergency traditional CAPTCHA & accessibility modes (audio & keyboard).
* **Privacy-First** — ephemeral session tokens, HMAC-signed payloads, optional opt-in dataset for ML.

---

## 🧪 Example Challenge Types

* **Logical Paradox** — *If this statement is false, click TRUE…*
* **Creative Input** — *Name something that doesn’t exist but should.*
* **Temporal Paradox** — *You solved this 5 seconds ago. What did you answer?*
* **Meta Loop** — *Reference a hash of your previous answer.*
* **Infinite Regress** — *“The answer is in the next challenge.”*
* **Audio Paradox** — accessible audio prompt for screen-readers.

---

## 🧮 Behavioral Scoring (tasteful heuristics)

A composed score uses:

* time analysis (reaction curves, decision latency)
* entropy of mouse path (spatial & directional change)
* velocity profile & micro-movement detection
* click hesitation and correction patterns
* challenge-specific validators (semantic & poetic acceptance)

Example JS heuristics (frontend):

```javascript
// velocity + micro movement flavor
const velocity = Math.sqrt(dx*dx + dy*dy) / dt;
entropyScore += velocity > 0.1 ? 0.2 * Math.log(velocity) : 0;
const microMovements = mousePath.filter(m => m.distance < 2);
if (microMovements.length > 3) humanScore += 1;
```

---

## 🛡 Security Model & Hardening

* HMAC-signed session payloads (prevent tampering)
* Rate limiting & IP reputation blocklist / adaptive throttling
* Optional invisible risk pre-check (reCAPTCHA v3 or internal quick classifier)
* Logging for human-labeled training (opt-in) & offline model retraining
* Replace in-memory sessions with Redis for production resilience

---

## 🧠 ML + Continuous Learning

We recommend a pipeline:

1. Collect anonymized session vectors and final human/robot labels.
2. Train a lightweight behavior classifier (not user identifiable).
3. Deploy model into `bot_likelihood` scoring step.
4. Use online A/B and safe-retraining to avoid feedback loops.

Storage model (Django example):

```python
class CaptchaPattern(models.Model):
    session_id = models.UUIDField()
    ip_address = models.GenericIPAddressField()
    entropy_score = models.FloatField()
    hesitation_index = models.FloatField()
    is_human = models.BooleanField()  # for training
    created_at = models.DateTimeField(auto_now_add=True)
```

---

## ♿ Accessibility

* **Audio paradox mode** (spoken riddles & sound puzzles)
* **Keyboard-only** flow with explicit timing capture
* Emergency fallback to classic CAPTCHA on request

---

## 🧾 Example API (summary)

```
POST /session        -> { token, challenge, round_id, expires_in }
POST /respond        -> { token, round_id, answer, meta } -> { round_result, accepted, action, next_challenge }
GET  /health         -> { ok, sessions }
GET  /debug/session/:token (dev-only)
```

Payload `meta` (client → server):

```json
{
  "mouse_moves": 42,
  "mouse_path": [{"x":12,"y":23,"t":1690000000}],
  "time_ms": 2100,
  "click_pattern_complex": true,
  "user_agent": "..."
}
```

---

## 🧩 UX — The Golden Badge

Add this to your site to declare ritual membership:

```markdown
![Verified by Paradox Loop](https://img.shields.io/badge/Verified-Paradox_Loop-gold?style=flat-square&logo=shield)
```

---

## 🔭 Roadmap (epic)

* v2.1: LLM adversarial engine integration (GPT-modeled bot simulation)
* v2.2: Cross-modal puzzles (image + audio + text hybrid paradoxes)
* v3.0: Federated behavioral models for privacy-preserving training

---

## 📜 Licensing & Ethos

**MIT** — fork, gild, and improve.
By using this project you accept the Kintsugi Oath: *Respect the human mind. Avoid surveillance. Train with consent.*

---

## 🧧 Contribute & Try it in VS Code

Click the badge at the top or open this repo in the browser VS Code:

➡️ [https://vscode.dev/github/Saranoah/paradox-loop-captcha](https://vscode.dev/github/Saranoah/paradox-loop-captcha)

(If your repo name differs, replace the path: `vscode.dev/github/<your-username>/<your-repo>`)

---

## ✨ Final Words

Paradox-Loop CAPTCHA is a ritualized defense: not just a gate, but a crucible where meaning is the metric and fracture becomes strength. If you want, I will:

* generate the full frontend (Kintsugi CSS + JS telemetry client),
* produce runnable Docker + Gunicorn recipe,
* add an `audit.md` explaining adversarial vectors and mitigation,
* and push a pretty `README.md` and `index.html` into your repo.

Which of those should I create next?
