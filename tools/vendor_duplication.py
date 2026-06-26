"""Vendor duplication and single-source policy check tool."""

from __future__ import annotations

from data.loader import load_policies, load_vendors


def check_vendor_duplication(
    vendor_id: str,
    category: str,
    amount: float = 0.0,
) -> dict[str, object]:
    """Check active-contract vendor conflicts and apply POL-001 threshold semantics.

    The check identifies other active vendors in the same category and applies the
    single-source policy trigger rule: a forced deny is triggered only when the
    request amount is strictly greater than the POL-001 threshold amount in a
    category covered by POL-001.

    Args:
        vendor_id: Requested vendor identifier.
        category: Requested purchase category.
        amount: Total requested amount in USD.

    Returns:
        A dictionary with duplication findings and policy outcome signals:
        - ``vendor_id`` (str): Requested vendor ID.
        - ``category`` (str): Requested category.
        - ``amount`` (float): Evaluated amount.
        - ``conflicting_vendor_ids`` (list[str]): Active vendor IDs in same category,
          excluding the requested vendor.
        - ``contract_details`` (list[dict[str, str]]): Contract context for each
          conflict entry with keys ``vendor_id``, ``contract_id``, ``contract_status``,
          and ``category``.
        - ``forced_decision`` (str | None): ``deny`` when POL-001 threshold is
          exceeded with conflicts, ``escalate`` when conflicts exist but amount is at
          or below threshold, otherwise ``None``.
        - ``rationale`` (str): Human-readable explanation of the result.
    """
    vendors = load_vendors()
    policies = load_policies()

    pol001 = next(
        (policy for policy in policies if policy.get("policy_id") == "POL-001"),
        None,
    )
    threshold = float(pol001["threshold_amount"]) if pol001 is not None else 25_000.0
    affected_categories = (
        set(pol001.get("affected_categories", [])) if pol001 is not None else set()
    )

    request_vendor_record = next(
        (
            vendor
            for vendor in vendors
            if vendor.get("vendor_id") == vendor_id
            and vendor.get("category") == category
            and vendor.get("contract_status") == "active"
        ),
        None,
    )

    conflicts = [
        vendor
        for vendor in vendors
        if vendor.get("vendor_id") != vendor_id
        and vendor.get("category") == category
        and vendor.get("contract_status") == "active"
    ]

    conflicting_vendor_ids = [str(vendor["vendor_id"]) for vendor in conflicts]
    contract_details = [
        {
            "vendor_id": str(vendor["vendor_id"]),
            "contract_id": str(vendor.get("contract_id", "")),
            "contract_status": str(vendor.get("contract_status", "")),
            "category": str(vendor.get("category", "")),
        }
        for vendor in conflicts
    ]

    category_is_contracted = category in affected_categories
    request_vendor_is_contracted = request_vendor_record is not None
    threshold_exceeded = amount > threshold

    if (
        conflicts
        and category_is_contracted
        and threshold_exceeded
        and not request_vendor_is_contracted
    ):
        forced_decision = "deny"
        rationale = (
            f"POL-001 triggered: amount ${amount:.2f} exceeds threshold ${threshold:.2f} "
            f"for contracted category '{category}' with active conflicting vendor(s): "
            f"{', '.join(conflicting_vendor_ids)}."
        )
    elif conflicts and request_vendor_is_contracted:
        forced_decision = None
        rationale = (
            f"Active alternate contracted vendor(s) found for category '{category}': "
            f"{', '.join(conflicting_vendor_ids)}. Requested vendor {vendor_id} is also "
            "active and contracted for this category, so no vendor-duplication policy "
            "trigger applies."
        )
    elif conflicts:
        forced_decision = "escalate"
        rationale = (
            f"Active conflicting vendor(s) found for category '{category}': "
            f"{', '.join(conflicting_vendor_ids)}. POL-001 deny trigger not met because "
            f"amount ${amount:.2f} is not above ${threshold:.2f} or category is not covered."
        )
    else:
        forced_decision = None
        rationale = (
            f"No active vendor conflicts found for category '{category}'. "
            "No vendor-duplication trigger detected."
        )

    return {
        "vendor_id": vendor_id,
        "category": category,
        "amount": float(amount),
        "conflicting_vendor_ids": conflicting_vendor_ids,
        "contract_details": contract_details,
        "forced_decision": forced_decision,
        "rationale": rationale,
    }
