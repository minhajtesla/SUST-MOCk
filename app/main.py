"""
FastAPI app entry point for the QueueStorm Warmup service.

Endpoints:
    GET  /health        -> service liveness probe
    POST /sort-ticket   -> classify one CRM ticket
"""
from __future__ import annotations
from fastapi import FastAPI, HTTPException

from .schemas import TicketRequest, TicketResponse
from .classifier import classify
from .summarizer import summarize, make_summary_safe


app = FastAPI(
    title="QueueStorm Warmup",
    description="Mock CRM ticket triage service for the SUST CSE Carnival 2026 warmup.",
    version="1.0.0",
)


@app.get("/health")
def health() -> dict:
    """Simple liveness check used by graders and uptime monitors."""
    return {"status": "ok", "service": "queuestorm-warmup", "version": "1.0.0"}


@app.post("/sort-ticket", response_model=TicketResponse)
def sort_ticket(req: TicketRequest) -> TicketResponse:
    """Classify a single customer ticket and return a structured response."""
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="message must not be empty")

    case_type, severity, department, confidence = classify(req.message)
    summary = make_summary_safe(summarize(req.message, case_type))

    # Rule from the problem statement:
    # human_review_required = true when severity is critical OR case is phishing.
    human_review = severity == "critical" or case_type == "phishing_or_social_engineering"

    return TicketResponse(
        ticket_id=req.ticket_id,
        case_type=case_type,
        severity=severity,
        department=department,
        agent_summary=summary,
        human_review_required=human_review,
        confidence=confidence,
    )
