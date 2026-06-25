# QueueStorm Warmup — SUST CSE Carnival 2026 (Mock)

A tiny FastAPI service that classifies a single CRM ticket into:

- `case_type` — wrong_transfer / payment_failed / refund_request / phishing_or_social_engineering / other
- `severity` — low / medium / high / critical
- `department` — customer_support / dispute_resolution / payments_ops / fraud_risk
- `agent_summary` — one neutral sentence, **never** asking for PIN/OTP/password
- `human_review_required` — `true` when critical or phishing
- `confidence` — float 0..1

LLM is **not** required; this is a pure rule-based solution.

---

## 1. Project layout

```
.
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app + endpoints
│   ├── schemas.py        # Pydantic request / response models
│   ├── classifier.py     # Keyword → case_type + severity/department lookup
│   └── summarizer.py     # Template summary + safety filter
├── tests/
│   └── test_samples.py   # 5 sample cases from the problem statement
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 2. Run locally (Windows / macOS / Linux)

Requires **Python 3.10+**.

```bash
# 1. Clone
git clone <your-repo-url>
cd <repo-folder>

# 2. (recommended) create a virtualenv
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS / Linux:
source .venv/bin/activate

# 3. Install deps
pip install -r requirements.txt

# 4. Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open:

- Health probe: <http://localhost:8000/health>
- Interactive docs: <http://localhost:8000/docs>
- Sort endpoint: `POST http://localhost:8000/sort-ticket`

### Quick curl test

```bash
curl -X POST http://localhost:8000/sort-ticket \
  -H "Content-Type: application/json" \
  -d "{\"ticket_id\":\"T-001\",\"channel\":\"app\",\"locale\":\"en\",\"message\":\"I sent 5000 to wrong number, please help\"}"
```

Expected:

```json
{
  "ticket_id": "T-001",
  "case_type": "wrong_transfer",
  "severity": "high",
  "department": "dispute_resolution",
  "agent_summary": "Customer reports sending 5000 BDT to a wrong recipient and requests recovery.",
  "human_review_required": false,
  "confidence": 0.92
}
```

---

## 3. Run the 5 sample test cases

```bash
python tests/test_samples.py
```

Expected: `5/5 sample cases passed`.

---

## 4. Deploy to Render (free, gives HTTPS URL)

1. Push the repo to a **public** GitHub repo.
2. Go to <https://render.com> → **New +** → **Web Service** → connect your repo.
3. Settings:
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Click **Deploy**. After ~2 minutes you'll get an HTTPS URL like
   `https://queuestorm-warmup.onrender.com`.
5. Verify:
   - `GET  https://<your-url>/health` → `{"status":"ok",...}`
   - `POST https://<your-url>/sort-ticket` with the sample payload above.

### Other supported platforms

The same start command works on Railway, Fly.io, Poridhi Lab, AWS EC2, etc.
The only requirement is exposing port via the `$PORT` env var.

---

## 5. Safety rule (enforced by the grader)

The `agent_summary` field must **never** ask for PIN / OTP / password / card number.

Implementation: `summarizer.summarize(...)` only generates neutral descriptions,
and `summarizer.make_summary_safe(...)` post-filters any unsafe imperative
phrase. See `tests/test_samples.py` for the phishing sample (must produce
`human_review_required: true`).

---

## 6. Submission checklist

- [ ] Public GitHub repo with this README.
- [ ] Live HTTPS URL where `/health` returns `ok`.
- [ ] `LLM used: No (rule-based keyword matching)`.
- [ ] All 5 sample cases pass.
