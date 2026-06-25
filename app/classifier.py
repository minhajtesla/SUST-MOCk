"""
Rule-based ticket classifier.

Uses keyword + phrase matching to map a free-text customer message
to one of the five case_types defined in the problem statement.
Severity and department are looked up from static tables.
"""
from __future__ import annotations
import re
from typing import Tuple

from .schemas import CaseType, Severity, Department


# Keywords/phrases grouped by case_type. Order matters: first strong
# match wins. Each list mixes English and Bangla (transliterated) terms
# so the same classifier handles mixed-locale messages.
RULES: list[Tuple[CaseType, list[str]]] = [
    (
        "phishing_or_social_engineering",
        [
            "otp", "pin", "password", "passcode", "cvv",
            "scammer", "fraud call", "fake call", "phishing",
            "asked for my", "asking for my", "share your", "send your",
            "verification code", "security code",
            "ওটিপি", "পিন", "পাসওয়ার্ড", "স্ক্যামার", "প্রতারণা",
        ],
    ),
    (
        "wrong_transfer",
        [
            "wrong number", "wrong account", "wrong recipient",
            "sent to wrong", "transferred to wrong", "mistakenly sent",
            "sent by mistake", "wrong person", "wrong bkash", "wrong mobile",
            "ভুল নাম্বার", "ভুল নম্বর", "ভুল একাউন্ট", "ভুল ব্যক্তি",
        ],
    ),
    (
        "payment_failed",
        [
            "payment failed", "transaction failed", "failed but",
            "money deducted", "balance deducted", "didn't receive",
            "did not receive", "not received", "amount deducted",
            "payment declined", "deducted but", "tk deducted",
            "কাটা হয়ে গেছে", "কেটে নিয়েছে", "পেমেন্ট ব্যর্থ",
        ],
    ),
    (
        "refund_request",
        [
            "refund", "return my money", "money back", "cash back",
            "changed my mind", "cancel and refund", "want my money back",
            "please return", "undo the transaction",
            "ফেরত", "রিফান্ড", "টাকা ফেরত",
        ],
    ),
]


def _score(message: str, keywords: list[str]) -> int:
    """Return how many distinct keyword patterns appear in the message."""
    msg = message.lower()
    hits = 0
    for kw in keywords:
        # word-ish match for short tokens, substring for phrases
        if len(kw) <= 4:
            if re.search(rf"\b{re.escape(kw)}\b", msg):
                hits += 1
        else:
            if kw in msg:
                hits += 1
    return hits


def classify(message: str) -> Tuple[CaseType, Severity, Department, float]:
    """
    Classify a message and return (case_type, severity, department, confidence).

    Confidence is a rough ratio: best-hit-count / second-best-hit-count
    (or 0.6 if only one rule matched, 0.4 if none).
    """
    scores = [(case, _score(message, kws)) for case, kws in RULES]

    # Sort by hits desc; first entry with score > 0 wins
    scores.sort(key=lambda x: x[1], reverse=True)
    best_case, best_hits = scores[0]
    second_hits = scores[1][1] if len(scores) > 1 else 0

    if best_hits == 0:
        return _result("other", "other")

    # Confidence heuristic: more unique matches -> higher confidence
    if second_hits == 0:
        confidence = 0.6 + min(best_hits, 4) * 0.08  # 0.68 .. 0.92
    else:
        ratio = best_hits / (best_hits + second_hits)
        confidence = 0.6 + 0.35 * ratio              # 0.75 .. 0.95
    confidence = round(min(confidence, 0.99), 2)

    return _result(best_case, confidence=confidence)


# Static lookup tables per the problem statement
SEVERITY_TABLE: dict[CaseType, Severity] = {
    "phishing_or_social_engineering": "critical",
    "wrong_transfer": "high",
    "payment_failed": "high",
    "refund_request": "low",
    "other": "low",
}

DEPARTMENT_TABLE: dict[CaseType, Department] = {
    "phishing_or_social_engineering": "fraud_risk",
    "wrong_transfer": "dispute_resolution",
    "payment_failed": "payments_ops",
    # refund routes to disputes when amount is contested, otherwise support.
    # Rule-based default = dispute_resolution (covers majority of cases).
    "refund_request": "dispute_resolution",
    "other": "customer_support",
}


def _result(case: CaseType, confidence: float) -> Tuple[CaseType, Severity, Department, float]:
    return case, SEVERITY_TABLE[case], DEPARTMENT_TABLE[case], confidence
