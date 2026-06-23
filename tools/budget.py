"""Budget check tool for procurement pre-screening."""

from __future__ import annotations

from data.loader import load_budgets


def check_budget(cost_center_id: str, requested_amount: float) -> dict[str, object]:
    """Evaluate whether a request amount is covered by the cost center's remaining budget.

    This tool reads budget records through ``data.loader.load_budgets`` and compares the
    requested amount against the matching cost center's ``remaining_budget`` value.

    Args:
        cost_center_id: Cost center identifier to evaluate (for example, ``"CC-003"``).
        requested_amount: Total requested amount in USD.

    Returns:
        A dictionary describing budget evaluation results with these keys:
        - ``cost_center_id`` (str): The evaluated cost center identifier.
        - ``requested_amount`` (float): Requested amount passed to the tool.
        - ``remaining_budget`` (float): Remaining budget for the matched cost center.
        - ``overage`` (float): Positive amount over budget, or ``0.0`` when covered.
        - ``outcome`` (str): ``"pass"`` when covered, otherwise ``"deny"``.
        - ``detail`` (str): Human-readable explanatory message.

    Raises:
        ValueError: If ``cost_center_id`` is not found in budget data.
    """
    budgets = load_budgets()
    budget_record = next(
        (record for record in budgets if record.get("cost_center_id") == cost_center_id),
        None,
    )

    if budget_record is None:
        raise ValueError(f"Unknown cost center_id: {cost_center_id}")

    remaining_budget = float(budget_record["remaining"])
    overage = max(0.0, requested_amount - remaining_budget)

    if overage == 0.0:
        detail = (
            f"Request amount ${requested_amount:.2f} is within remaining budget "
            f"${remaining_budget:.2f} for {cost_center_id}."
        )
        outcome = "pass"
    else:
        detail = (
            f"Request amount ${requested_amount:.2f} exceeds remaining budget "
            f"${remaining_budget:.2f} for {cost_center_id} by ${overage:.2f}."
        )
        outcome = "deny"

    return {
        "cost_center_id": cost_center_id,
        "requested_amount": float(requested_amount),
        "remaining_budget": remaining_budget,
        "overage": round(overage, 2),
        "outcome": outcome,
        "detail": detail,
    }
