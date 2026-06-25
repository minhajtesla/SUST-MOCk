"""Quick smoke test of the running service."""
import httpx

BASE = "http://127.0.0.1:8765"

r = httpx.get(f"{BASE}/", timeout=5)
print("GET / ->", r.status_code, "len:", len(r.text))

r = httpx.get(f"{BASE}/health", timeout=5)
print("GET /health ->", r.status_code, r.json())

for path in ["/static/style.css", "/static/app.js", "/static/index.html"]:
    r = httpx.get(f"{BASE}{path}", timeout=5)
    print(f"GET {path} ->", r.status_code)

payload = {
    "ticket_id": "T-001",
    "channel": "app",
    "locale": "en",
    "message": "I sent 5000 to wrong number, please help",
}
r = httpx.post(f"{BASE}/sort-ticket", json=payload, timeout=10)
print("POST /sort-ticket ->", r.status_code, r.json())