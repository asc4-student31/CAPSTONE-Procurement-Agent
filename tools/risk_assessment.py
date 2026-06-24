"""Risk assessment tool for vendor-level procurement screening."""

from __future__ import annotations

from data.loader import load_vendors


def assess_risk(vendor_id: str) -> dict[str, object]:
    """Return vendor compliance/contract risk signals for orchestration decisions.

    Args:
        vendor_id: Vendor identifier from a purchase request.

    Returns:
        Dictionary with deterministic risk fields:
        - vendor_id: Vendor identifier that was evaluated.
        - vendor_name: Vendor display name (or "Unknown").
        - compliance_flag: Whether the vendor has an active compliance issue.
        - compliance_flag_status: "flagged" or "clear" status label.
        - compliance_notes: Compliance context text.
        - contract_status: Vendor contract status from source data.
        - risk_level: One of "low", "medium", "high", "critical".
        - risk_summary: Human-readable rationale for the computed risk.
        - error (optional): Present when vendor lookup or data loading fails.
    """
    try:
        vendors = load_vendors()
    except Exception as exc:  # pragma: no cover - defensive path for loader/runtime failures
        return {
            "vendor_id": vendor_id,
            "vendor_name": "Unknown",
            "compliance_flag": False,
            "compliance_flag_status": "clear",
            "compliance_notes": "",
            "contract_status": "unknown",
            "risk_level": "critical",
            "risk_summary": "Unable to load vendor data; treat vendor as critical risk.",
            "error": f"Vendor data could not be loaded: {exc}",
        }

    vendor = next((record for record in vendors if record.get("vendor_id") == vendor_id), None)
    if vendor is None:
        return {
            "vendor_id": vendor_id,
            "vendor_name": "Unknown",
            "compliance_flag": False,
            "compliance_flag_status": "clear",
            "compliance_notes": "",
            "contract_status": "unknown",
            "risk_level": "high",
            "risk_summary": (
                f"Vendor '{vendor_id}' was not found in approved vendor data; "
                "treat as high risk and escalate for validation."
            ),
            "error": f"Vendor '{vendor_id}' not found in vendor database.",
        }

    compliance_flag = bool(vendor.get("compliance_flag", False))
    contract_status = str(vendor.get("contract_status", "none"))
    compliance_notes = str(vendor.get("compliance_notes", ""))

    if compliance_flag:
        risk_level = "critical"
        risk_summary = (
            f"Vendor has an active compliance flag: {compliance_notes or 'review required'}; "
            "escalate to compliance and legal."
        )
    elif contract_status == "expired":
        risk_level = "high"
        risk_summary = "Vendor contract is expired; high risk until contract is renewed."
    elif contract_status == "none":
        risk_level = "medium"
        risk_summary = "Vendor has no active contract; medium risk pending procurement review."
    else:
        risk_level = "low"
        risk_summary = "Vendor has an active contract and no compliance flags."

    return {
        "vendor_id": vendor_id,
        "vendor_name": str(vendor.get("name", "")),
        "compliance_flag": compliance_flag,
        "compliance_flag_status": "flagged" if compliance_flag else "clear",
        "compliance_notes": compliance_notes,
        "contract_status": contract_status,
        "risk_level": risk_level,
        "risk_summary": risk_summary,
    }
