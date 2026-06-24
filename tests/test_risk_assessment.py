"""Tests for risk assessment tool behavior using real mock data."""

from __future__ import annotations

from tools.risk_assessment import assess_risk


def test_assess_risk_compliance_flagged_vendor_is_critical() -> None:
    """V-006 has a compliance flag and must evaluate to critical risk."""
    result = assess_risk("V-006")

    assert result["risk_level"] == "critical"
    assert result["compliance_flag"] is True
    assert result["compliance_flag_status"] == "flagged"
    assert "error" not in result


def test_assess_risk_expired_contract_vendor_is_high() -> None:
    """V-010 has an expired contract and must evaluate to high risk."""
    result = assess_risk("V-010")

    assert result["risk_level"] == "high"
    assert result["contract_status"] == "expired"
    assert "error" not in result


def test_assess_risk_active_contract_vendor_is_low() -> None:
    """V-002 has active contract/no flag and should evaluate to low risk."""
    result = assess_risk("V-002")

    assert result["risk_level"] == "low"
    assert result["compliance_flag"] is False
    assert result["contract_status"] == "active"


def test_assess_risk_unknown_vendor_returns_error() -> None:
    """Unknown vendor IDs should return explicit error details for escalation."""
    result = assess_risk("V-999")

    assert "error" in result
    assert result["risk_level"] == "high"
    assert "V-999" in str(result["error"])


def test_assess_risk_result_contains_expected_keys() -> None:
    """Known vendor responses include the complete deterministic output shape."""
    result = assess_risk("V-007")

    required_keys = {
        "vendor_id",
        "vendor_name",
        "compliance_flag",
        "compliance_flag_status",
        "compliance_notes",
        "contract_status",
        "risk_level",
        "risk_summary",
    }
    assert required_keys.issubset(result.keys())
