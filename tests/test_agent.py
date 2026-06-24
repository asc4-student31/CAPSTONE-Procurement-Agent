"""Unit tests for procurement agent orchestration logic."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

import agent
from models import ProcurementRecommendation, PurchaseRequest


def _sample_request() -> PurchaseRequest:
    """Build a canonical purchase request fixture for agent unit tests."""
    return PurchaseRequest(
        request_id="REQ-UNIT-001",
        requestor="unit.tester@fedex.com",
        cost_center_id="CC-001",
        vendor_name="BlueSky Cloud Solutions",
        vendor_id="V-002",
        category="software_licenses",
        item_description="Unit test request",
        quantity=10,
        unit_price=100.0,
        total_amount=1_000.0,
    )


def test_collect_tool_results_executes_all_tools(monkeypatch: pytest.MonkeyPatch) -> None:
    """All four tools are called once and results are recorded by key."""
    calls: list[tuple[str, tuple[object, ...], dict[str, object]]] = []

    def fake_budget(*args: object, **kwargs: object) -> dict[str, object]:
        calls.append(("budget", args, kwargs))
        return {"outcome": "pass"}

    def fake_vendor(*args: object, **kwargs: object) -> dict[str, object]:
        calls.append(("vendor_duplication", args, kwargs))
        return {"forced_decision": None}

    def fake_policy(*args: object, **kwargs: object) -> dict[str, object]:
        calls.append(("policy_compliance", args, kwargs))
        return {"outcome": "pass"}

    def fake_risk(*args: object, **kwargs: object) -> dict[str, object]:
        calls.append(("risk", args, kwargs))
        return {"risk_level": "low"}

    monkeypatch.setattr(agent, "check_budget", fake_budget)
    monkeypatch.setattr(agent, "check_vendor_duplication", fake_vendor)
    monkeypatch.setattr(agent, "check_policy_compliance", fake_policy)
    monkeypatch.setattr(agent, "assess_risk", fake_risk)

    result = agent._collect_tool_results(_sample_request())

    assert set(result.keys()) == {"budget", "vendor_duplication", "policy_compliance", "risk"}
    assert [call[0] for call in calls] == [
        "budget",
        "vendor_duplication",
        "policy_compliance",
        "risk",
    ]


def test_collect_tool_results_records_error_and_continues(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A tool exception is converted to a structured error and remaining checks still run."""
    calls: list[str] = []

    def fake_budget(*args: object, **kwargs: object) -> dict[str, object]:
        calls.append("budget")
        raise RuntimeError("budget service unavailable")

    def fake_vendor(*args: object, **kwargs: object) -> dict[str, object]:
        calls.append("vendor_duplication")
        return {"forced_decision": None}

    def fake_policy(*args: object, **kwargs: object) -> dict[str, object]:
        calls.append("policy_compliance")
        return {"outcome": "pass"}

    def fake_risk(*args: object, **kwargs: object) -> dict[str, object]:
        calls.append("risk")
        return {"risk_level": "low"}

    monkeypatch.setattr(agent, "check_budget", fake_budget)
    monkeypatch.setattr(agent, "check_vendor_duplication", fake_vendor)
    monkeypatch.setattr(agent, "check_policy_compliance", fake_policy)
    monkeypatch.setattr(agent, "assess_risk", fake_risk)

    result = agent._collect_tool_results(_sample_request())

    assert calls == ["budget", "vendor_duplication", "policy_compliance", "risk"]
    assert result["budget"]["outcome"] == "escalate"
    assert "RuntimeError" in str(result["budget"]["error"])


@pytest.mark.parametrize(
    ("candidates", "expected"),
    [
        ({"approve"}, "approve"),
        ({"deny", "approve"}, "deny"),
        ({"escalate", "deny", "approve"}, "escalate"),
    ],
)
def test_resolve_final_decision_precedence(candidates: set[str], expected: str) -> None:
    """Decision precedence is escalate > deny > approve."""
    assert agent._resolve_final_decision(candidates) == expected


def test_derive_decision_candidates_escalate_overrides_other_signals() -> None:
    """Escalate-equivalent tool signals are included in candidates."""
    tool_results = {
        "budget": {"outcome": "deny"},
        "vendor_duplication": {"forced_decision": "deny"},
        "policy_compliance": {"outcome": "escalate"},
        "risk": {"risk_level": "high"},
    }

    candidates = agent._derive_decision_candidates(tool_results)

    assert "escalate" in candidates
    assert "deny" in candidates


def test_fallback_recommendation_is_schema_valid_and_error_aware() -> None:
    """Fallback returns a typed recommendation and includes tool/model failure context."""
    tool_results = {
        "budget": {"error": "RuntimeError: budget failed", "outcome": "escalate"},
        "vendor_duplication": {"forced_decision": None},
        "policy_compliance": {"outcome": "pass"},
        "risk": {"risk_level": "low"},
    }

    recommendation = agent._fallback_recommendation(
        purchase_request=_sample_request(),
        tool_results=tool_results,
        model_error=ValueError("model exploded"),
    )

    assert isinstance(recommendation, ProcurementRecommendation)
    assert recommendation.decision == "escalate"
    assert "Model execution failed" in recommendation.rationale
    assert "budget failed" in recommendation.rationale


def test_recommend_procurement_returns_model_data_on_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Successful model execution returns result.data without fallback."""

    expected = ProcurementRecommendation(decision="approve", rationale="All checks passed")

    monkeypatch.setattr(agent, "_collect_tool_results", lambda request: {"budget": {"outcome": "pass"}})
    monkeypatch.setattr(agent, "_build_user_prompt", lambda request, results: "prompt")
    monkeypatch.setattr(agent.agent, "run_sync", lambda prompt: SimpleNamespace(data=expected))

    recommendation = agent.recommend_procurement(_sample_request())

    assert recommendation == expected


def test_recommend_procurement_uses_fallback_when_model_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Model errors are caught and converted into structured fallback recommendations."""
    tool_results = {
        "budget": {"error": "RuntimeError: budget down", "outcome": "escalate"},
        "vendor_duplication": {"forced_decision": None},
        "policy_compliance": {"outcome": "pass"},
        "risk": {"risk_level": "low"},
    }

    monkeypatch.setattr(agent, "_collect_tool_results", lambda request: tool_results)
    monkeypatch.setattr(agent, "_build_user_prompt", lambda request, results: "prompt")

    def _raise_model_error(prompt: str) -> None:
        raise RuntimeError("simulated model failure")

    monkeypatch.setattr(agent.agent, "run_sync", _raise_model_error)

    recommendation = agent.recommend_procurement(_sample_request())

    assert recommendation.decision == "escalate"
    assert "simulated model failure" in recommendation.rationale


def test_system_prompt_contains_required_operational_constraints() -> None:
    """System prompt explicitly includes decision set and mandatory tool workflow text."""
    prompt = agent.SYSTEM_PROMPT

    assert "approve, deny, escalate" in prompt
    assert "check_budget" in prompt
    assert "check_vendor_duplication" in prompt
    assert "check_policy_compliance" in prompt
    assert "assess_risk" in prompt
