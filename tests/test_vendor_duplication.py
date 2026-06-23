"""Tests for vendor duplication tool behavior using real mock data."""

from __future__ import annotations

from tools.vendor_duplication import check_vendor_duplication


def test_check_vendor_duplication_req008_conflicts() -> None:
    """REQ-008 should detect active office_supplies conflicts for NovaPrint over POL-001 threshold."""
    result = check_vendor_duplication(
        vendor_id="V-012",
        category="office_supplies",
        amount=28_500.00,
    )

    assert set(result["conflicting_vendor_ids"]) == {"V-001", "V-003"}
