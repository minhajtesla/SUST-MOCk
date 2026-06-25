"""
Smoke tests for the classifier against the 5 sample cases in the
problem statement. Run with: `python -m pytest tests/ -q`
or just import and call run() from a script.
"""
from app.schemas import TicketRequest, TicketResponse
from app.main import sort_ticket  # FastAPI app object re-uses handler via TestClient


EXPECTED = [
    # (message, expected_case_type, expected_severity)
    ("I sent 3000 to wrong number",                     "wrong_transfer",                  "high"),
    ("Payment failed but balance deducted",            "payment_failed",                  "high"),
    ("Someone called asking my OTP, is that bKash?",   "phishing_or_social_engineering",  "critical"),
    ("Please refund my last transaction, I changed my mind", "refund_request",            "low"),
    ("App crashed when I opened it",                   "other",                           "low"),
]


def check_one(message: str, expected_case: str, expected_sev: str) -> bool:
    resp: TicketResponse = sort_ticket(TicketRequest(ticket_id="T", message=message))
    ok = resp.case_type == expected_case and resp.severity == expected_sev
    flag = "✅" if ok else "❌"
    print(f"{flag}  msg={message!r:55s} got={resp.case_type}/{resp.severity}  expect={expected_case}/{expected_sev}")
    if resp.case_type == "phishing_or_social_engineering":
        print(f"    human_review_required={resp.human_review_required}  (must be True)")
    return ok


def run() -> int:
    passed = 0
    for msg, case, sev in EXPECTED:
        if check_one(msg, case, sev):
            passed += 1
    print(f"\n{passed}/{len(EXPECTED)} sample cases passed")
    return 0 if passed == len(EXPECTED) else 1


if __name__ == "__main__":
    raise SystemExit(run())
