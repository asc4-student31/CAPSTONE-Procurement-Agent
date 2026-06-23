"""Pydantic v2 models for procurement agent input and output contracts."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PurchaseRequest(BaseModel):
    """Canonical input contract for procurement request pre-screening."""

    request_id: str
    requestor: str
    cost_center_id: str
    vendor_name: str
    vendor_id: str
    category: str
    item_description: str
    quantity: int
    unit_price: float
    total_amount: float


class ProcurementRecommendation(BaseModel):
    """Structured recommendation output contract for procurement decisions."""

    model_config = ConfigDict(str_strip_whitespace=True)

    decision: Literal["approve", "deny", "escalate"]
    rationale: str = Field(min_length=1)
