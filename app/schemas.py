"""
Pydantic schemas for the QueueStorm Warmup service.

Defines the request and response shapes for POST /sort-ticket
as specified in the hackathon problem statement.
"""
from typing import Literal, Optional
from pydantic import BaseModel, Field


# Allowed enums (kept as Literal for validation + OpenAPI docs)
Channel = Literal["app", "sms", "call_center", "merchant_portal"]
Locale = Literal["bn", "en", "mixed"]

CaseType = Literal[
    "wrong_transfer",
    "payment_failed",
    "refund_request",
    "phishing_or_social_engineering",
    "other",
]
Severity = Literal["low", "medium", "high", "critical"]
Department = Literal[
    "customer_support",
    "dispute_resolution",
    "payments_ops",
    "fraud_risk",
]


class TicketRequest(BaseModel):
    """Incoming CRM ticket payload."""
    ticket_id: str = Field(..., min_length=1, description="Unique ticket id; echoed back.")
    channel: Optional[Channel] = Field(default="app", description="Originating channel.")
    locale: Optional[Locale] = Field(default="en", description="Message locale.")
    message: str = Field(..., min_length=1, description="Free-text customer complaint.")


class TicketResponse(BaseModel):
    """Outgoing classification result."""
    ticket_id: str
    case_type: CaseType
    severity: Severity
    department: Department
    agent_summary: str
    human_review_required: bool
    confidence: float = Field(..., ge=0.0, le=1.0)
