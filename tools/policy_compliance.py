"""Policy compliance tool for procurement request validation."""

from __future__ import annotations

from typing import Literal

from data.loader import load_budgets, load_policies, load_vendors
from models import PurchaseRequest


ForcedDecision = Literal["deny", "escalate"]


def _add_violation(
    violations: list[dict[str, str]],
    policy_id: str,
    rule_description: str,
    forced_decision: ForcedDecision,
) -> None:
    """Append a policy violation entry in the required output shape."""
    violations.append(
        {
            "policy_id": policy_id,
            "rule_description": rule_description,
            "forced_decision": forced_decision,
        }
    )


def check_policy_compliance(purchase_request: PurchaseRequest) -> dict[str, object]:
    """Evaluate a purchase request against all eight procurement policies.

    The function evaluates policy records loaded from ``data/loader.py`` and
    returns one violation entry per triggered policy.

    Args:
        purchase_request: Validated purchase request input model.

    Returns:
        A dictionary with:
        - ``violations``: list of violations, each containing ``policy_id``,
          ``rule_description``, and ``forced_decision`` (``deny`` or ``escalate``).
        - ``evaluated_policy_ids``: ordered list of policy IDs evaluated.
        - ``outcome``: aggregate outcome based on violations:
          ``escalate`` if any escalate violation exists,
          ``deny`` if only deny violations exist,
          otherwise ``pass``.
    """
    policies = load_policies()
    vendors = load_vendors()
    budgets = load_budgets()

    policy_by_id = {
        str(policy["policy_id"]): policy
        for policy in policies
        if "policy_id" in policy
    }
    evaluated_policy_ids = [str(policy.get("policy_id", "")) for policy in policies]

    vendor = next(
        (
            record
            for record in vendors
            if str(record.get("vendor_id")) == purchase_request.vendor_id
        ),
        None,
    )
    budget = next(
        (
            record
            for record in budgets
            if str(record.get("cost_center_id")) == purchase_request.cost_center_id
        ),
        None,
    )

    violations: list[dict[str, str]] = []

    # POL-001: Single-source restriction for contracted categories over threshold.
    pol001 = policy_by_id.get("POL-001")
    if pol001 is not None:
        threshold = float(pol001.get("threshold_amount", 0.0))
        affected_categories = {
            str(category)
            for category in pol001.get("affected_categories", [])
        }
        conflicting_active_vendors = [
            record
            for record in vendors
            if str(record.get("vendor_id")) != purchase_request.vendor_id
            and str(record.get("category")) == purchase_request.category
            and str(record.get("contract_status")) == "active"
        ]
        request_vendor_is_contracted = (
            vendor is not None
            and str(vendor.get("category")) == purchase_request.category
            and str(vendor.get("contract_status")) == "active"
        )
        if (
            purchase_request.category in affected_categories
            and purchase_request.total_amount > threshold
            and conflicting_active_vendors
            and not request_vendor_is_contracted
        ):
            conflict_ids = ", ".join(
                str(record.get("vendor_id", "")) for record in conflicting_active_vendors
            )
            _add_violation(
                violations,
                "POL-001",
                (
                    f"Amount ${purchase_request.total_amount:.2f} exceeds POL-001 threshold "
                    f"${threshold:.2f} in contracted category '{purchase_request.category}'. "
                    f"Active contracted vendor(s): {conflict_ids}."
                ),
                "deny",
            )

    # POL-002: Manager approval threshold; no approval metadata is present in input model.
    policy_by_id.get("POL-002")

    # POL-003: Director approval threshold.
    pol003 = policy_by_id.get("POL-003")
    if pol003 is not None:
        threshold = float(pol003.get("threshold_amount", 0.0))
        if purchase_request.total_amount >= threshold:
            _add_violation(
                violations,
                "POL-003",
                (
                    f"Amount ${purchase_request.total_amount:.2f} meets or exceeds director "
                    f"approval threshold ${threshold:.2f}."
                ),
                "escalate",
            )

    # POL-004: Prohibited category (catering).
    pol004 = policy_by_id.get("POL-004")
    if pol004 is not None:
        affected_categories = {
            str(category)
            for category in pol004.get("affected_categories", [])
        }
        if purchase_request.category in affected_categories:
            _add_violation(
                violations,
                "POL-004",
                (
                    f"Category '{purchase_request.category}' is prohibited by policy POL-004."
                ),
                "deny",
            )

    # POL-005: Expired contract vendor.
    if vendor is not None and str(vendor.get("contract_status")) == "expired":
        _add_violation(
            violations,
            "POL-005",
            (
                f"Vendor {purchase_request.vendor_id} has expired contract "
                f"{vendor.get('contract_id', '')}."
            ),
            "deny",
        )

    # POL-006: Compliance-flagged vendor hold.
    if vendor is not None and bool(vendor.get("compliance_flag")):
        _add_violation(
            violations,
            "POL-006",
            f"Vendor {purchase_request.vendor_id} has an active compliance flag.",
            "escalate",
        )

    # POL-007: Staffing single-source threshold (engagement over 40 units/hours).
    if (
        purchase_request.category == "staffing"
        and purchase_request.quantity > 40
        and (vendor is None or str(vendor.get("contract_status")) != "active")
    ):
        _add_violation(
            violations,
            "POL-007",
            (
                "Staffing engagement exceeds 40 and requested vendor is not under an active "
                "staffing contract."
            ),
            "deny",
        )

    # POL-008: Budget overage prohibition.
    if budget is None:
        _add_violation(
            violations,
            "POL-008",
            (
                f"Budget record for cost center {purchase_request.cost_center_id} was not found; "
                "manual review required."
            ),
            "escalate",
        )
    else:
        remaining = float(budget.get("remaining", 0.0))
        if purchase_request.total_amount > remaining:
            overage = purchase_request.total_amount - remaining
            _add_violation(
                violations,
                "POL-008",
                (
                    f"Request amount ${purchase_request.total_amount:.2f} exceeds remaining "
                    f"budget ${remaining:.2f} by ${overage:.2f}."
                ),
                "deny",
            )

    forced_decisions = {entry["forced_decision"] for entry in violations}
    if "escalate" in forced_decisions:
        outcome = "escalate"
    elif "deny" in forced_decisions:
        outcome = "deny"
    else:
        outcome = "pass"

    return {
        "violations": violations,
        "evaluated_policy_ids": evaluated_policy_ids,
        "outcome": outcome,
    }
