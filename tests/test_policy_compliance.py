"""Tests for policy compliance scenarios using mock request fixtures."""

from __future__ import annotations

from data.loader import load_requests
from models import PurchaseRequest
from tools.policy_compliance import check_policy_compliance


def _request_by_id(request_id: str) -> dict[str, object]:
    """Return a single request fixture by request ID."""
    return next(
        request for request in load_requests() if str(request.get("request_id")) == request_id
    )


def test_pol_004_catering_prohibition_req_009_at_3200_denied() -> None:
    """POL-004: REQ-009 catering remains denied at $3,200."""
    req_009 = dict(_request_by_id("REQ-009"))
    req_009["total_amount"] = 3_200.00

    result = check_policy_compliance(PurchaseRequest(**req_009))

    assert result["outcome"] == "deny"
    policy_ids = [violation["policy_id"] for violation in result["violations"]]
    assert "POL-004" in policy_ids
    pol004 = [v for v in result["violations"] if v["policy_id"] == "POL-004"]
    assert pol004[0]["forced_decision"] == "deny"


def test_pol_002_manager_approval_threshold_range_is_evaluated() -> None:
    """POL-002: requests in $10,000-$49,999 are covered by policy evaluation."""
    req_005 = _request_by_id("REQ-005")

    result = check_policy_compliance(PurchaseRequest(**req_005))

    assert 10_000.00 <= PurchaseRequest(**req_005).total_amount <= 49_999.99
    assert "POL-002" in result["evaluated_policy_ids"]
    pol002 = [v for v in result["violations"] if v["policy_id"] == "POL-002"]
    assert pol002 == []


def test_pol_005_expired_contract_req_007_crestview_denied() -> None:
    """POL-005: REQ-007 from Crestview Print (expired contract) is denied."""
    req_007 = _request_by_id("REQ-007")

    result = check_policy_compliance(PurchaseRequest(**req_007))

    assert result["outcome"] == "deny"
    policy_ids = [violation["policy_id"] for violation in result["violations"]]
    assert "POL-005" in policy_ids
    pol005 = [v for v in result["violations"] if v["policy_id"] == "POL-005"]
    assert pol005[0]["forced_decision"] == "deny"
