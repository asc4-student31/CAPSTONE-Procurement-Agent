"""Tests for budget tool behavior using real mock data files."""

from __future__ import annotations

from tools.budget import check_budget


def test_check_budget_within_and_over_budget_for_cc003() -> None:
    """Verify CC-003 yields pass within budget and deny when amount exceeds remaining funds."""
    within_budget_result = check_budget(cost_center_id="CC-003", requested_amount=6_900.00)
    assert within_budget_result["outcome"] == "pass"
    assert within_budget_result["remaining_budget"] == 6_900.00
    assert within_budget_result["overage"] == 0.0

    over_budget_result = check_budget(cost_center_id="CC-003", requested_amount=11_200.00)
    assert over_budget_result["outcome"] == "deny"
    assert over_budget_result["remaining_budget"] == 6_900.00
    assert over_budget_result["overage"] == 4_300.00
